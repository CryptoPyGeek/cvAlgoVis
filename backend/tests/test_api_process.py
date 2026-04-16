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
    filter_module = next((module for module in open3d_library["modules"] if module["id"] == "point_cloud_filter_sampling"), None)
    assert filter_module is not None
    filter_algorithm_ids = {item["id"] for item in filter_module["algorithms"]}
    assert {"uniform_down_sample", "random_down_sample", "remove_radius_outlier", "crop_axis_aligned_bbox"} <= filter_algorithm_ids
    clustering_module = next((module for module in open3d_library["modules"] if module["id"] == "point_cloud_segmentation_clustering"), None)
    assert clustering_module is not None
    clustering_algorithm_ids = {item["id"] for item in clustering_module["algorithms"]}
    assert {"cluster_dbscan", "segment_plane_outliers", "hidden_point_removal"} <= clustering_algorithm_ids
    geometry_module = next((module for module in open3d_library["modules"] if module["id"] == "point_cloud_geometry_analysis"), None)
    assert geometry_module is not None
    geometry_algorithm_ids = {item["id"] for item in geometry_module["algorithms"]}
    assert {
        "get_axis_aligned_bounding_box",
        "get_oriented_bounding_box",
        "compute_convex_hull",
        "compute_mahalanobis_distance",
        "compute_nearest_neighbor_distance",
        "compute_point_cloud_distance",
    } <= geometry_algorithm_ids
    registration_module = next((module for module in open3d_library["modules"] if module["id"] == "point_cloud_registration"), None)
    assert registration_module is not None
    registration_algorithm_ids = {item["id"] for item in registration_module["algorithms"]}
    assert {
        "transform_point_cloud",
        "registration_icp_point_to_point",
        "registration_icp_point_to_plane",
        "compute_fpfh_feature",
        "registration_ransac_based_on_feature_matching",
        "registration_fast_based_on_feature_matching",
        "registration_colored_icp",
        "registration_ransac_then_icp_point_to_plane",
        "registration_fast_then_icp_point_to_plane",
        "evaluate_registration",
    } <= registration_algorithm_ids


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
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "voxel_down_sample"
        assert payload.filename == "cloud.ply"
        assert file_bytes == b"ply-data"
        assert target_file_bytes is None
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


def test_open3d_process_new_filter_sampling_algorithm(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "uniform_down_sample"
        assert payload.params["every_k_points"] == 4
        assert target_file_bytes is None
        return {
            "result_kind": "point_cloud_summary",
            "summary": "点云处理完成，点数从 100 变为 25。",
            "meta": {
                "elapsed_ms": 8,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "file_type": "ply",
                "points_before": 100,
                "points_after": 25,
            },
            "stats": {"every_k_points": 4},
            "source_points": [[0.0, 0.0, 0.0], [0.2, 0.0, 0.0]],
            "processed_points": [[0.0, 0.0, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={"algorithm_id": "uniform_down_sample", "params": '{"every_k_points": 4}'},
        files={"file": ("cloud.ply", b"ply-data", "application/octet-stream")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["algorithm"] == "uniform_down_sample"
    assert payload["stats"]["every_k_points"] == 4


def test_open3d_process_new_segmentation_algorithm(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "cluster_dbscan"
        assert payload.params["eps"] == 0.12
        assert payload.params["min_points"] == 6
        assert target_file_bytes is None
        return {
            "result_kind": "point_cloud_summary",
            "summary": "聚类完成，识别出 2 个簇。",
            "meta": {
                "elapsed_ms": 10,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "file_type": "ply",
                "points_before": 80,
                "points_after": 30,
            },
            "stats": {"cluster_count": 2, "largest_cluster_size": 30},
            "source_points": [[0.0, 0.0, 0.0], [0.1, 0.1, 0.0]],
            "processed_points": [[0.0, 0.0, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={"algorithm_id": "cluster_dbscan", "params": '{"eps": 0.12, "min_points": 6}'},
        files={"file": ("cloud.ply", b"ply-data", "application/octet-stream")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["algorithm"] == "cluster_dbscan"
    assert payload["stats"]["cluster_count"] == 2


def test_open3d_process_transform_algorithm(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "transform_point_cloud"
        assert payload.params["tx"] == 0.15
        assert target_file_bytes is None
        return {
            "result_kind": "point_cloud_summary",
            "summary": "点云变换完成。",
            "meta": {
                "elapsed_ms": 6,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "target_filename": None,
                "file_type": "ply",
                "points_before": 18,
                "points_after": 18,
            },
            "stats": {"transformation": [[1, 0, 0, 0.15], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]},
            "source_points": [[0.0, 0.0, 0.0]],
            "target_points": [],
            "processed_points": [[0.15, 0.0, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={"algorithm_id": "transform_point_cloud", "params": '{"tx": 0.15, "ty": 0, "tz": 0, "roll_deg": 0, "pitch_deg": 0, "yaw_deg": 0}'},
        files={"file": ("cloud.ply", b"ply-data", "application/octet-stream")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["algorithm"] == "transform_point_cloud"
    assert payload["processed_points"] == [[0.15, 0.0, 0.0]]


def test_open3d_process_registration_algorithm_with_target(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "registration_icp_point_to_point"
        assert payload.target_filename == "target.ply"
        assert target_file_bytes == b"target-data"
        return {
            "result_kind": "point_cloud_summary",
            "summary": "ICP 配准完成。",
            "meta": {
                "elapsed_ms": 12,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "target_filename": payload.target_filename,
                "file_type": "ply",
                "points_before": 18,
                "points_after": 18,
            },
            "stats": {"fitness": 0.98, "inlier_rmse": 0.01},
            "source_points": [[0.0, 0.0, 0.0]],
            "target_points": [[0.2, 0.0, 0.0]],
            "processed_points": [[0.19, 0.0, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={"algorithm_id": "registration_icp_point_to_point", "params": '{"max_correspondence_distance": 0.18, "max_iteration": 40}'},
        files={
            "file": ("source.ply", b"source-data", "application/octet-stream"),
            "target_file": ("target.ply", b"target-data", "application/octet-stream"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["target_filename"] == "target.ply"
    assert payload["target_points"] == [[0.2, 0.0, 0.0]]


def test_open3d_process_point_to_plane_registration(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "registration_icp_point_to_plane"
        assert payload.params["normal_radius"] == 0.2
        assert target_file_bytes == b"target-data"
        return {
            "result_kind": "point_cloud_summary",
            "summary": "点到面 ICP 配准完成。",
            "meta": {
                "elapsed_ms": 15,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "target_filename": payload.target_filename,
                "file_type": "ply",
                "points_before": 18,
                "points_after": 18,
            },
            "stats": {"fitness": 0.97, "inlier_rmse": 0.02, "normal_radius": 0.2},
            "source_points": [[0.0, 0.0, 0.0]],
            "target_points": [[0.2, 0.0, 0.0]],
            "processed_points": [[0.18, 0.0, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={
            "algorithm_id": "registration_icp_point_to_plane",
            "params": '{"max_correspondence_distance": 0.18, "max_iteration": 40, "normal_radius": 0.2, "normal_max_nn": 30}',
        },
        files={
            "file": ("source.ply", b"source-data", "application/octet-stream"),
            "target_file": ("target.ply", b"target-data", "application/octet-stream"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["algorithm"] == "registration_icp_point_to_plane"
    assert payload["stats"]["normal_radius"] == 0.2


def test_open3d_process_compute_fpfh_feature(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "compute_fpfh_feature"
        assert payload.params["feature_radius"] == 0.5
        assert target_file_bytes is None
        return {
            "result_kind": "point_cloud_summary",
            "summary": "FPFH 特征计算完成。",
            "meta": {
                "elapsed_ms": 9,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "target_filename": None,
                "file_type": "ply",
                "points_before": 18,
                "points_after": 18,
            },
            "stats": {"feature_dimension": 33, "feature_count": 18},
            "source_points": [[0.0, 0.0, 0.0]],
            "target_points": [],
            "processed_points": [[0.0, 0.0, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={
            "algorithm_id": "compute_fpfh_feature",
            "params": '{"normal_radius": 0.2, "normal_max_nn": 30, "feature_radius": 0.5, "feature_max_nn": 50}',
        },
        files={"file": ("source.ply", b"source-data", "application/octet-stream")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["stats"]["feature_dimension"] == 33


def test_open3d_process_ransac_registration_with_target(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "registration_ransac_based_on_feature_matching"
        assert payload.target_filename == "target.ply"
        assert payload.params["ransac_n"] == 3
        assert target_file_bytes == b"target-data"
        return {
            "result_kind": "point_cloud_summary",
            "summary": "RANSAC 粗配准完成。",
            "meta": {
                "elapsed_ms": 22,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "target_filename": payload.target_filename,
                "file_type": "ply",
                "points_before": 18,
                "points_after": 18,
            },
            "stats": {"fitness": 1.0, "ransac_n": 3},
            "source_points": [[0.0, 0.0, 0.0]],
            "target_points": [[0.2, 0.0, 0.0]],
            "processed_points": [[0.12, -0.02, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={
            "algorithm_id": "registration_ransac_based_on_feature_matching",
            "params": '{"normal_radius": 0.2, "normal_max_nn": 30, "feature_radius": 0.5, "feature_max_nn": 50, "max_correspondence_distance": 0.3, "ransac_n": 3, "max_iteration": 10000}',
        },
        files={
            "file": ("source.ply", b"source-data", "application/octet-stream"),
            "target_file": ("target.ply", b"target-data", "application/octet-stream"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["algorithm"] == "registration_ransac_based_on_feature_matching"
    assert payload["meta"]["target_filename"] == "target.ply"


def test_open3d_process_colored_icp_with_target(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "registration_colored_icp"
        assert payload.target_filename == "target.ply"
        assert payload.params["lambda_geometric"] == 0.968
        assert target_file_bytes == b"target-data"
        return {
            "result_kind": "point_cloud_summary",
            "summary": "彩色 ICP 配准完成。",
            "meta": {
                "elapsed_ms": 20,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "target_filename": payload.target_filename,
                "file_type": "ply",
                "points_before": 18,
                "points_after": 18,
            },
            "stats": {"fitness": 0.99, "lambda_geometric": 0.968},
            "source_points": [[0.0, 0.0, 0.0]],
            "target_points": [[0.2, 0.0, 0.0]],
            "processed_points": [[0.12, -0.02, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={
            "algorithm_id": "registration_colored_icp",
            "params": '{"max_correspondence_distance": 0.18, "max_iteration": 30, "normal_radius": 0.2, "normal_max_nn": 30, "lambda_geometric": 0.968}',
        },
        files={
            "file": ("source.ply", b"source-data", "application/octet-stream"),
            "target_file": ("target.ply", b"target-data", "application/octet-stream"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["algorithm"] == "registration_colored_icp"
    assert payload["stats"]["lambda_geometric"] == 0.968


def test_open3d_process_ransac_then_icp_pipeline(monkeypatch):
    def fake_process_point_cloud_file(payload, file_bytes, target_file_bytes=None):
        assert payload.algorithm_id == "registration_ransac_then_icp_point_to_plane"
        assert payload.params["coarse_max_iteration"] == 10000
        assert target_file_bytes == b"target-data"
        return {
            "result_kind": "point_cloud_summary",
            "summary": "RANSAC + 点到面 ICP 完成。",
            "meta": {
                "elapsed_ms": 28,
                "algorithm": payload.algorithm_id,
                "filename": payload.filename,
                "target_filename": payload.target_filename,
                "file_type": "ply",
                "points_before": 18,
                "points_after": 18,
            },
            "stats": {
                "coarse_fitness": 0.91,
                "refined_fitness": 0.99,
                "initial_transformation": [[1, 0, 0, 0.1], [0, 1, 0, -0.02], [0, 0, 1, 0], [0, 0, 0, 1]],
                "transformation": [[1, 0, 0, 0.12], [0, 1, 0, -0.02], [0, 0, 1, 0], [0, 0, 0, 1]],
            },
            "source_points": [[0.0, 0.0, 0.0]],
            "target_points": [[0.2, 0.0, 0.0]],
            "processed_points": [[0.12, -0.02, 0.0]],
        }

    monkeypatch.setattr("app.main.process_point_cloud_file", fake_process_point_cloud_file)

    response = client.post(
        "/open3d/process",
        data={
            "algorithm_id": "registration_ransac_then_icp_point_to_plane",
            "params": '{"normal_radius": 0.2, "normal_max_nn": 30, "feature_radius": 0.5, "feature_max_nn": 50, "max_correspondence_distance": 0.3, "ransac_n": 3, "coarse_max_iteration": 10000, "icp_max_iteration": 40}',
        },
        files={
            "file": ("source.ply", b"source-data", "application/octet-stream"),
            "target_file": ("target.ply", b"target-data", "application/octet-stream"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["algorithm"] == "registration_ransac_then_icp_point_to_plane"
    assert payload["stats"]["refined_fitness"] == 0.99
