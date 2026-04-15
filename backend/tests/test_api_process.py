import base64

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def make_data_url() -> str:
    image = np.zeros((40, 40, 3), dtype=np.uint8)
    image[:, :20] = (255, 255, 255)
    ok, buf = cv2.imencode(".png", image)
    assert ok
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode("utf-8")


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_catalog():
    response = client.get("/catalog")
    assert response.status_code == 200
    payload = response.json()
    assert payload["libraries"][0]["id"] == "opencv"
    open3d_library = next((item for item in payload["libraries"] if item["id"] == "open3d"), None)
    assert open3d_library is not None
    assert open3d_library["input_kind"] == "point_cloud"
    assert open3d_library["modules"][0]["id"] == "point_cloud_basic"


def test_process_canny_success():
    response = client.post(
        "/process",
        json={
            "library_id": "opencv",
            "algorithm_id": "canny",
            "params": {"threshold1": 60, "threshold2": 120, "aperture_size": 3},
            "image": make_data_url(),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["processed_image"].startswith("data:image/png;base64,")
    assert payload["meta"]["algorithm"] == "canny"


def test_process_watershed_success():
    response = client.post(
        "/process",
        json={
            "library_id": "opencv",
            "algorithm_id": "watershed_segmentation",
            "params": {},
            "image": make_data_url(),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["processed_image"].startswith("data:image/png;base64,")
    assert payload["meta"]["algorithm"] == "watershed_segmentation"


def test_process_color_conversion_success():
    response = client.post(
        "/process",
        json={
            "library_id": "opencv",
            "algorithm_id": "bgr_to_lab",
            "params": {},
            "image": make_data_url(),
        },
    )
    assert response.status_code == 200


def test_process_unknown_algorithm():
    response = client.post(
        "/process",
        json={
            "library_id": "opencv",
            "algorithm_id": "unknown_algo",
            "params": {},
            "image": make_data_url(),
        },
    )
    assert response.status_code == 400


def test_process_open3d_redirected_to_dedicated_endpoint():
    response = client.post(
        "/process",
        json={
            "library_id": "open3d",
            "algorithm_id": "voxel_down_sample",
            "params": {"voxel_size": 0.05},
            "image": make_data_url(),
        },
    )
    assert response.status_code == 400
    assert "/open3d/process" in response.text


def test_open3d_process_rejects_invalid_extension():
    response = client.post(
        "/open3d/process",
        data={"algorithm_id": "voxel_down_sample", "params": "{}"},
        files={"file": ("cloud.txt", b"not-a-point-cloud", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported point-cloud file type" in response.text


def test_open3d_process_success(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes):
        assert payload.algorithm_id == "voxel_down_sample"
        assert payload.filename == "cloud.ply"
        assert file_bytes == b"ply-data"
        return {
            "result_kind": "point_cloud_summary",
            "summary": "点云处理完成，点数从 120 变为 48。",
            "meta": {
                "elapsed_ms": 12,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "file_type": "ply",
                "points_before": 120,
                "points_after": 48,
            },
            "stats": {"voxel_size": 0.05},
            "source_points": [[0.0, 0.0, 0.0], [0.1, 0.0, 0.0]],
            "processed_points": [[0.0, 0.0, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={"algorithm_id": "voxel_down_sample", "params": '{"voxel_size": 0.05}'},
        files={"file": ("cloud.ply", b"ply-data", "application/octet-stream")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_kind"] == "point_cloud_summary"
    assert payload["meta"]["algorithm"] == "voxel_down_sample"
    assert payload["meta"]["file_type"] == "ply"
    assert payload["source_points"] == [[0.0, 0.0, 0.0], [0.1, 0.0, 0.0]]
    assert payload["processed_points"] == [[0.0, 0.0, 0.0]]
