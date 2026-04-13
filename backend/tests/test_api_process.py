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
