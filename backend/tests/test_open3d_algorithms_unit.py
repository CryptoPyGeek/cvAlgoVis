import numpy as np
import pytest

o3d = pytest.importorskip("open3d")

from app.services.open3d_algorithms import (
    cluster_dbscan,
    compute_convex_hull,
    compute_fpfh_feature,
    compute_nearest_neighbor_distance,
    compute_point_cloud_distance,
    evaluate_registration,
    get_axis_aligned_bounding_box,
    hidden_point_removal,
    registration_colored_icp,
    registration_fast_based_on_feature_matching,
    registration_fast_then_icp_point_to_plane,
    registration_icp_point_to_point,
    registration_icp_point_to_plane,
    registration_ransac_based_on_feature_matching,
    registration_ransac_then_icp_point_to_plane,
    segment_plane_outliers,
    transform_point_cloud,
)


def make_point_cloud(points: list[list[float]]):
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(np.asarray(points, dtype=np.float64))
    return cloud


def sample_cluster_cloud():
    return make_point_cloud(
        [
            [0.0, 0.0, 0.0],
            [0.02, 0.01, 0.0],
            [0.01, -0.01, 0.0],
            [0.03, 0.0, 0.01],
            [1.0, 1.0, 1.0],
            [1.02, 1.01, 0.98],
            [0.98, 1.03, 1.01],
            [3.5, 3.5, 3.5],
        ]
    )


def sample_plane_cloud():
    points = []
    for x in (-0.4, -0.2, 0.0, 0.2, 0.4):
        for y in (-0.4, -0.2, 0.0, 0.2, 0.4):
            points.append([x, y, 0.0])
    points.extend([[0.5, 0.5, 0.4], [-0.5, -0.5, -0.35], [0.45, -0.45, 0.5]])
    return make_point_cloud(points)


def sample_shape_cloud():
    return make_point_cloud(
        [
            [-0.4, -0.4, -0.2],
            [0.4, -0.4, -0.2],
            [-0.4, 0.4, -0.2],
            [0.4, 0.4, -0.2],
            [-0.4, -0.4, 0.2],
            [0.4, -0.4, 0.2],
            [-0.4, 0.4, 0.2],
            [0.4, 0.4, 0.2],
            [0.0, 0.0, 0.0],
        ]
    )


def sample_registration_pair():
    source = make_point_cloud(
        [
            [-0.30, -0.10, 0.00],
            [-0.10, -0.10, 0.00],
            [0.10, -0.10, 0.00],
            [0.30, -0.10, 0.00],
            [-0.30, 0.10, 0.00],
            [-0.10, 0.10, 0.08],
            [0.10, 0.10, 0.08],
            [0.30, 0.10, 0.00],
        ]
    )
    target = make_point_cloud(
        [
            [-0.18, -0.12, 0.00],
            [0.02, -0.12, 0.00],
            [0.22, -0.12, 0.00],
            [0.42, -0.12, 0.00],
            [-0.18, 0.08, 0.00],
            [0.02, 0.08, 0.08],
            [0.22, 0.08, 0.08],
            [0.42, 0.08, 0.00],
        ]
    )
    return source, target


def test_cluster_dbscan_returns_cluster_summary():
    processed, stats = cluster_dbscan(sample_cluster_cloud(), {"eps": 0.08, "min_points": 3})
    assert len(processed.points) >= 3
    assert stats["cluster_count"] >= 2
    assert stats["largest_cluster_size"] >= 3
    assert "cluster_sizes" in stats


def test_segment_plane_outliers_extracts_non_plane_points():
    processed, stats = segment_plane_outliers(
        sample_plane_cloud(),
        {"distance_threshold": 0.05, "ransac_n": 3, "num_iterations": 300},
    )
    assert len(processed.points) == stats["outlier_count"]
    assert stats["inlier_count"] >= 20
    assert len(processed.points) >= 2


def test_hidden_point_removal_returns_visible_subset():
    processed, stats = hidden_point_removal(
        sample_shape_cloud(),
        {"camera_x": 1.2, "camera_y": 1.1, "camera_z": 1.4, "radius": 3.0},
    )
    assert 0 < len(processed.points) <= len(sample_shape_cloud().points)
    assert stats["visible_count"] == len(processed.points)


def test_axis_aligned_bounding_box_returns_eight_corners():
    processed, stats = get_axis_aligned_bounding_box(sample_shape_cloud(), {})
    assert len(processed.points) == 8
    assert len(stats["min_bound"]) == 3
    assert len(stats["max_bound"]) == 3
    assert stats["volume"] > 0


def test_convex_hull_returns_hull_vertices():
    processed, stats = compute_convex_hull(sample_shape_cloud(), {"joggle_inputs": 0})
    assert len(processed.points) == stats["hull_vertex_count"]
    assert stats["triangle_count"] > 0


def test_transform_point_cloud_changes_positions():
    source, _ = sample_registration_pair()
    processed, stats = transform_point_cloud(source, {"tx": 0.1, "ty": 0.0, "tz": 0.0, "yaw_deg": 0})
    source_points = np.asarray(source.points)
    processed_points = np.asarray(processed.points)
    assert not np.allclose(source_points, processed_points)
    assert pytest.approx(stats["transformation"][0][3], rel=1e-6) == 0.1


def test_registration_icp_point_to_point_returns_metrics():
    source, target = sample_registration_pair()
    processed, stats = registration_icp_point_to_point(
        source,
        target,
        {"max_correspondence_distance": 0.5, "max_iteration": 50},
    )
    assert len(processed.points) == len(source.points)
    assert "fitness" in stats
    assert "inlier_rmse" in stats
    assert len(stats["transformation"]) == 4


def test_registration_icp_point_to_plane_returns_metrics():
    source, target = sample_registration_pair()
    processed, stats = registration_icp_point_to_plane(
        source,
        target,
        {"max_correspondence_distance": 0.5, "max_iteration": 50, "normal_radius": 0.3, "normal_max_nn": 8},
    )
    assert len(processed.points) == len(source.points)
    assert "fitness" in stats
    assert "inlier_rmse" in stats
    assert stats["normal_max_nn"] == 8


def test_compute_fpfh_feature_reports_feature_stats():
    source, _ = sample_registration_pair()
    processed, stats = compute_fpfh_feature(
        source,
        {"normal_radius": 0.3, "normal_max_nn": 8, "feature_radius": 0.5, "feature_max_nn": 12},
    )
    assert len(processed.points) == len(source.points)
    assert stats["feature_dimension"] == 33
    assert stats["feature_count"] == len(source.points)


def test_registration_ransac_based_on_feature_matching_returns_metrics():
    source, target = sample_registration_pair()
    processed, stats = registration_ransac_based_on_feature_matching(
        source,
        target,
        {
            "normal_radius": 0.3,
            "normal_max_nn": 8,
            "feature_radius": 0.5,
            "feature_max_nn": 12,
            "max_correspondence_distance": 0.3,
            "ransac_n": 3,
            "max_iteration": 10000,
        },
    )
    assert len(processed.points) == len(source.points)
    assert stats["fitness"] >= 0
    assert len(stats["transformation"]) == 4


def test_registration_fast_based_on_feature_matching_returns_metrics():
    source, target = sample_registration_pair()
    processed, stats = registration_fast_based_on_feature_matching(
        source,
        target,
        {
            "normal_radius": 0.3,
            "normal_max_nn": 8,
            "feature_radius": 0.5,
            "feature_max_nn": 12,
            "max_correspondence_distance": 0.3,
            "iteration_number": 32,
        },
    )
    assert len(processed.points) == len(source.points)
    assert stats["fitness"] >= 0
    assert stats["iteration_number"] == 32


def test_registration_colored_icp_returns_metrics():
    source, target = sample_registration_pair()
    processed, stats = registration_colored_icp(
        source,
        target,
        {
            "max_correspondence_distance": 0.3,
            "max_iteration": 30,
            "normal_radius": 0.3,
            "normal_max_nn": 8,
            "lambda_geometric": 0.968,
        },
    )
    assert len(processed.points) == len(source.points)
    assert "fitness" in stats
    assert "inlier_rmse" in stats
    assert stats["lambda_geometric"] == 0.968


def test_registration_ransac_then_icp_point_to_plane_returns_both_stage_metrics():
    source, target = sample_registration_pair()
    processed, stats = registration_ransac_then_icp_point_to_plane(
        source,
        target,
        {
            "normal_radius": 0.3,
            "normal_max_nn": 8,
            "feature_radius": 0.5,
            "feature_max_nn": 12,
            "max_correspondence_distance": 0.3,
            "ransac_n": 3,
            "coarse_max_iteration": 10000,
            "icp_max_iteration": 40,
        },
    )
    assert len(processed.points) == len(source.points)
    assert "coarse_fitness" in stats
    assert "refined_fitness" in stats
    assert len(stats["initial_transformation"]) == 4
    assert len(stats["transformation"]) == 4


def test_registration_fast_then_icp_point_to_plane_returns_both_stage_metrics():
    source, target = sample_registration_pair()
    processed, stats = registration_fast_then_icp_point_to_plane(
        source,
        target,
        {
            "normal_radius": 0.3,
            "normal_max_nn": 8,
            "feature_radius": 0.5,
            "feature_max_nn": 12,
            "max_correspondence_distance": 0.3,
            "iteration_number": 32,
            "icp_max_iteration": 40,
        },
    )
    assert len(processed.points) == len(source.points)
    assert "coarse_fitness" in stats
    assert "refined_fitness" in stats
    assert stats["iteration_number"] == 32


def test_evaluate_registration_reports_summary_metrics():
    source, target = sample_registration_pair()
    processed, stats = evaluate_registration(source, target, {"max_correspondence_distance": 0.5})
    assert len(processed.points) == len(source.points)
    assert stats["fitness"] >= 0
    assert stats["correspondence_set_size"] >= 0


def test_compute_nearest_neighbor_distance_reports_stats():
    processed, stats = compute_nearest_neighbor_distance(sample_cluster_cloud(), {})
    assert len(processed.points) == len(sample_cluster_cloud().points)
    assert stats["distance_max"] >= stats["distance_min"]
    assert stats["distance_mean"] >= 0


def test_compute_point_cloud_distance_reports_stats():
    source, target = sample_registration_pair()
    processed, stats = compute_point_cloud_distance(source, target, {})
    assert len(processed.points) == len(source.points)
    assert stats["distance_count"] == len(source.points)
    assert stats["distance_mean"] >= 0
