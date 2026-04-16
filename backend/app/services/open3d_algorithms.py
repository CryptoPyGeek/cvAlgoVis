from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np


def _require_open3d():
    try:
        import open3d as o3d  # type: ignore

        return o3d
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Open3D dependency is not installed.") from exc


def _copy_cloud(cloud):
    return deepcopy(cloud)


def _transformation_matrix(params: dict[str, Any]) -> np.ndarray:
    tx = float(params.get("tx", 0.0))
    ty = float(params.get("ty", 0.0))
    tz = float(params.get("tz", 0.0))
    roll = np.deg2rad(float(params.get("roll_deg", 0.0)))
    pitch = np.deg2rad(float(params.get("pitch_deg", 0.0)))
    yaw = np.deg2rad(float(params.get("yaw_deg", 0.0)))

    cx, sx = np.cos(roll), np.sin(roll)
    cy, sy = np.cos(pitch), np.sin(pitch)
    cz, sz = np.cos(yaw), np.sin(yaw)

    rx = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]])
    ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
    rz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])

    transform = np.eye(4, dtype=np.float64)
    transform[:3, :3] = rz @ ry @ rx
    transform[:3, 3] = np.array([tx, ty, tz], dtype=np.float64)
    return transform


def _points_to_cloud(points):
    o3d = _require_open3d()
    output = o3d.geometry.PointCloud()
    if len(points) == 0:
        return output
    output.points = o3d.utility.Vector3dVector(np.asarray(points, dtype=np.float64))
    return output


def voxel_down_sample(cloud, params: dict[str, Any]):
    voxel_size = float(params.get("voxel_size", 0.05))
    processed = cloud.voxel_down_sample(voxel_size=voxel_size)
    return processed, {"voxel_size": voxel_size}


def estimate_normals(cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    radius = float(params.get("radius", 0.2))
    max_nn = int(params.get("max_nn", 30))
    processed = _copy_cloud(cloud)
    processed.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn)
    )
    return processed, {"radius": radius, "max_nn": max_nn, "has_normals": True}


def remove_statistical_outlier(cloud, params: dict[str, Any]):
    nb_neighbors = int(params.get("nb_neighbors", 20))
    std_ratio = float(params.get("std_ratio", 2.0))
    processed, inlier_indices = cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    return processed, {
        "nb_neighbors": nb_neighbors,
        "std_ratio": std_ratio,
        "inlier_count": len(inlier_indices),
    }


def uniform_down_sample(cloud, params: dict[str, Any]):
    every_k_points = int(params.get("every_k_points", 5))
    processed = cloud.uniform_down_sample(every_k_points=every_k_points)
    return processed, {"every_k_points": every_k_points}


def random_down_sample(cloud, params: dict[str, Any]):
    sampling_ratio = float(params.get("sampling_ratio", 0.5))
    sampling_ratio = min(max(sampling_ratio, 0.0), 1.0)
    processed = cloud.random_down_sample(sampling_ratio=sampling_ratio)
    return processed, {"sampling_ratio": sampling_ratio}


def remove_radius_outlier(cloud, params: dict[str, Any]):
    nb_points = int(params.get("nb_points", 8))
    radius = float(params.get("radius", 0.12))
    processed, inlier_indices = cloud.remove_radius_outlier(nb_points=nb_points, radius=radius)
    return processed, {
        "nb_points": nb_points,
        "radius": radius,
        "inlier_count": len(inlier_indices),
    }


def crop_axis_aligned_bbox(cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    min_bound = [
        float(params.get("min_x", -0.25)),
        float(params.get("min_y", -0.25)),
        float(params.get("min_z", -0.25)),
    ]
    max_bound = [
        float(params.get("max_x", 0.25)),
        float(params.get("max_y", 0.25)),
        float(params.get("max_z", 0.25)),
    ]
    bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=min_bound, max_bound=max_bound)
    processed = cloud.crop(bbox)
    return processed, {"min_bound": min_bound, "max_bound": max_bound}


def cluster_dbscan(cloud, params: dict[str, Any]):
    eps = float(params.get("eps", 0.12))
    min_points = int(params.get("min_points", 6))
    labels = np.asarray(cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=False), dtype=np.int32)
    if labels.size == 0:
        return _copy_cloud(cloud), {"eps": eps, "min_points": min_points, "cluster_count": 0, "noise_count": 0}

    non_noise_mask = labels >= 0
    noise_count = int((~non_noise_mask).sum())
    cluster_count = int(labels[non_noise_mask].max() + 1) if non_noise_mask.any() else 0
    cluster_sizes = []
    largest_cluster_label = None
    largest_cluster_size = 0
    for cluster_id in range(cluster_count):
        size = int((labels == cluster_id).sum())
        cluster_sizes.append(size)
        if size > largest_cluster_size:
            largest_cluster_size = size
            largest_cluster_label = cluster_id

    if largest_cluster_label is None:
        processed = _copy_cloud(cloud)
    else:
        indices = np.where(labels == largest_cluster_label)[0].tolist()
        processed = cloud.select_by_index(indices)

    return processed, {
        "eps": eps,
        "min_points": min_points,
        "cluster_count": cluster_count,
        "noise_count": noise_count,
        "largest_cluster_size": largest_cluster_size,
        "cluster_sizes": cluster_sizes[:10],
    }


def segment_plane_outliers(cloud, params: dict[str, Any]):
    distance_threshold = float(params.get("distance_threshold", 0.02))
    ransac_n = int(params.get("ransac_n", 3))
    num_iterations = int(params.get("num_iterations", 1000))
    plane_model, inlier_indices = cloud.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=ransac_n,
        num_iterations=num_iterations,
    )
    processed = cloud.select_by_index(inlier_indices, invert=True)
    return processed, {
        "distance_threshold": distance_threshold,
        "ransac_n": ransac_n,
        "num_iterations": num_iterations,
        "plane_model": [float(v) for v in plane_model],
        "inlier_count": len(inlier_indices),
        "outlier_count": len(processed.points),
    }


def hidden_point_removal(cloud, params: dict[str, Any]):
    camera_location = np.array(
        [
            float(params.get("camera_x", 1.6)),
            float(params.get("camera_y", 1.4)),
            float(params.get("camera_z", 1.8)),
        ],
        dtype=np.float64,
    )
    radius = float(params.get("radius", 3.0))
    _, visible_indices = cloud.hidden_point_removal(camera_location=camera_location, radius=radius)
    processed = cloud.select_by_index(list(visible_indices))
    return processed, {
        "camera_location": camera_location.tolist(),
        "radius": radius,
        "visible_count": len(visible_indices),
    }


def _bbox_to_corners(bbox) -> np.ndarray:
    return np.asarray(bbox.get_box_points(), dtype=np.float64)


def get_axis_aligned_bounding_box(cloud, params: dict[str, Any]):
    bbox = cloud.get_axis_aligned_bounding_box()
    corners = _bbox_to_corners(bbox)
    processed = _points_to_cloud(corners)
    return processed, {
        "min_bound": [float(v) for v in bbox.min_bound],
        "max_bound": [float(v) for v in bbox.max_bound],
        "extent": [float(v) for v in bbox.get_extent()],
        "volume": float(bbox.volume()),
    }


def get_oriented_bounding_box(cloud, params: dict[str, Any]):
    robust = bool(int(params.get("robust", 0)))
    bbox = cloud.get_oriented_bounding_box(robust=robust)
    corners = _bbox_to_corners(bbox)
    processed = _points_to_cloud(corners)
    return processed, {
        "robust": robust,
        "center": [float(v) for v in bbox.center],
        "extent": [float(v) for v in bbox.extent],
        "volume": float(bbox.volume()),
    }


def compute_convex_hull(cloud, params: dict[str, Any]):
    joggle_inputs = bool(int(params.get("joggle_inputs", 0)))
    mesh, point_indices = cloud.compute_convex_hull(joggle_inputs=joggle_inputs)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    processed = _points_to_cloud(vertices)
    return processed, {
        "joggle_inputs": joggle_inputs,
        "hull_vertex_count": int(len(mesh.vertices)),
        "triangle_count": int(len(mesh.triangles)),
        "support_point_count": int(len(point_indices)),
    }


def compute_mahalanobis_distance(cloud, params: dict[str, Any]):
    distances = np.asarray(cloud.compute_mahalanobis_distance(), dtype=np.float64)
    processed = _copy_cloud(cloud)
    if distances.size == 0:
        stats = {"distance_mean": 0.0, "distance_max": 0.0, "distance_min": 0.0}
    else:
        stats = {
            "distance_mean": float(distances.mean()),
            "distance_max": float(distances.max()),
            "distance_min": float(distances.min()),
            "distance_p95": float(np.percentile(distances, 95)),
        }
    return processed, stats


def transform_point_cloud(cloud, params: dict[str, Any]):
    processed = _copy_cloud(cloud)
    transform = _transformation_matrix(params)
    processed.transform(transform)
    return processed, {"transformation": transform.tolist()}


def _estimate_normals_if_needed(cloud, radius: float, max_nn: int):
    o3d = _require_open3d()
    processed = _copy_cloud(cloud)
    if not processed.has_normals():
        processed.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn)
        )
    return processed


def _compute_fpfh_feature_internal(cloud, normal_radius: float, normal_max_nn: int, feature_radius: float, feature_max_nn: int):
    o3d = _require_open3d()
    cloud_with_normals = _estimate_normals_if_needed(cloud, normal_radius, normal_max_nn)
    feature = o3d.pipelines.registration.compute_fpfh_feature(
        cloud_with_normals,
        o3d.geometry.KDTreeSearchParamHybrid(radius=feature_radius, max_nn=feature_max_nn),
    )
    return cloud_with_normals, feature


def _ensure_colors(cloud):
    o3d = _require_open3d()
    processed = _copy_cloud(cloud)
    if processed.has_colors():
        return processed
    points = np.asarray(processed.points, dtype=np.float64)
    if points.size == 0:
        processed.colors = o3d.utility.Vector3dVector(np.empty((0, 3), dtype=np.float64))
        return processed
    min_bound = points.min(axis=0)
    max_bound = points.max(axis=0)
    span = np.where((max_bound - min_bound) == 0, 1.0, max_bound - min_bound)
    colors = np.clip((points - min_bound) / span, 0.0, 1.0)
    processed.colors = o3d.utility.Vector3dVector(colors)
    return processed


def registration_icp_point_to_point(source_cloud, target_cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    max_correspondence_distance = float(params.get("max_correspondence_distance", 0.18))
    max_iteration = int(params.get("max_iteration", 40))
    result = o3d.pipelines.registration.registration_icp(
        source_cloud,
        target_cloud,
        max_correspondence_distance,
        np.eye(4, dtype=np.float64),
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=max_iteration),
    )
    processed = _copy_cloud(source_cloud)
    processed.transform(result.transformation)
    return processed, {
        "max_correspondence_distance": max_correspondence_distance,
        "max_iteration": max_iteration,
        "fitness": float(result.fitness),
        "inlier_rmse": float(result.inlier_rmse),
        "transformation": np.asarray(result.transformation, dtype=np.float64).tolist(),
    }


def registration_icp_point_to_plane(source_cloud, target_cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    max_correspondence_distance = float(params.get("max_correspondence_distance", 0.18))
    max_iteration = int(params.get("max_iteration", 40))
    normal_radius = float(params.get("normal_radius", 0.2))
    normal_max_nn = int(params.get("normal_max_nn", 30))
    return _run_icp_point_to_plane(
        source_cloud,
        target_cloud,
        max_correspondence_distance=max_correspondence_distance,
        max_iteration=max_iteration,
        normal_radius=normal_radius,
        normal_max_nn=normal_max_nn,
        initial_transformation=np.eye(4, dtype=np.float64),
    )


def _run_icp_point_to_plane(
    source_cloud,
    target_cloud,
    *,
    max_correspondence_distance: float,
    max_iteration: int,
    normal_radius: float,
    normal_max_nn: int,
    initial_transformation: np.ndarray,
):
    o3d = _require_open3d()
    source_with_normals = _estimate_normals_if_needed(source_cloud, normal_radius, normal_max_nn)
    target_with_normals = _estimate_normals_if_needed(target_cloud, normal_radius, normal_max_nn)
    result = o3d.pipelines.registration.registration_icp(
        source_with_normals,
        target_with_normals,
        max_correspondence_distance,
        initial_transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=max_iteration),
    )
    processed = _copy_cloud(source_cloud)
    processed.transform(result.transformation)
    return processed, {
        "max_correspondence_distance": max_correspondence_distance,
        "max_iteration": max_iteration,
        "normal_radius": normal_radius,
        "normal_max_nn": normal_max_nn,
        "fitness": float(result.fitness),
        "inlier_rmse": float(result.inlier_rmse),
        "transformation": np.asarray(result.transformation, dtype=np.float64).tolist(),
    }


def compute_fpfh_feature(cloud, params: dict[str, Any]):
    normal_radius = float(params.get("normal_radius", 0.2))
    normal_max_nn = int(params.get("normal_max_nn", 30))
    feature_radius = float(params.get("feature_radius", 0.5))
    feature_max_nn = int(params.get("feature_max_nn", 50))
    processed, feature = _compute_fpfh_feature_internal(
        cloud, normal_radius, normal_max_nn, feature_radius, feature_max_nn
    )
    feature_data = np.asarray(feature.data, dtype=np.float64)
    return processed, {
        "normal_radius": normal_radius,
        "normal_max_nn": normal_max_nn,
        "feature_radius": feature_radius,
        "feature_max_nn": feature_max_nn,
        "feature_dimension": int(feature_data.shape[0]) if feature_data.ndim == 2 else 0,
        "feature_count": int(feature_data.shape[1]) if feature_data.ndim == 2 else 0,
    }


def registration_ransac_based_on_feature_matching(source_cloud, target_cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    normal_radius = float(params.get("normal_radius", 0.2))
    normal_max_nn = int(params.get("normal_max_nn", 30))
    feature_radius = float(params.get("feature_radius", 0.5))
    feature_max_nn = int(params.get("feature_max_nn", 50))
    max_correspondence_distance = float(params.get("max_correspondence_distance", 0.3))
    ransac_n = int(params.get("ransac_n", 3))
    max_iteration = int(params.get("max_iteration", 10000))
    source_processed, source_feature = _compute_fpfh_feature_internal(
        source_cloud, normal_radius, normal_max_nn, feature_radius, feature_max_nn
    )
    target_processed, target_feature = _compute_fpfh_feature_internal(
        target_cloud, normal_radius, normal_max_nn, feature_radius, feature_max_nn
    )
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_processed,
        target_processed,
        source_feature,
        target_feature,
        True,
        max_correspondence_distance,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        ransac_n,
        [o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(max_correspondence_distance)],
        o3d.pipelines.registration.RANSACConvergenceCriteria(max_iteration, 0.999),
    )
    processed = _copy_cloud(source_cloud)
    processed.transform(result.transformation)
    return processed, {
        "normal_radius": normal_radius,
        "normal_max_nn": normal_max_nn,
        "feature_radius": feature_radius,
        "feature_max_nn": feature_max_nn,
        "max_correspondence_distance": max_correspondence_distance,
        "ransac_n": ransac_n,
        "max_iteration": max_iteration,
        "fitness": float(result.fitness),
        "inlier_rmse": float(result.inlier_rmse),
        "transformation": np.asarray(result.transformation, dtype=np.float64).tolist(),
    }


def registration_fast_based_on_feature_matching(source_cloud, target_cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    normal_radius = float(params.get("normal_radius", 0.2))
    normal_max_nn = int(params.get("normal_max_nn", 30))
    feature_radius = float(params.get("feature_radius", 0.5))
    feature_max_nn = int(params.get("feature_max_nn", 50))
    max_correspondence_distance = float(params.get("max_correspondence_distance", 0.3))
    iteration_number = int(params.get("iteration_number", 32))
    source_processed, source_feature = _compute_fpfh_feature_internal(
        source_cloud, normal_radius, normal_max_nn, feature_radius, feature_max_nn
    )
    target_processed, target_feature = _compute_fpfh_feature_internal(
        target_cloud, normal_radius, normal_max_nn, feature_radius, feature_max_nn
    )
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_processed,
        target_processed,
        source_feature,
        target_feature,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=max_correspondence_distance,
            iteration_number=iteration_number,
        ),
    )
    processed = _copy_cloud(source_cloud)
    processed.transform(result.transformation)
    return processed, {
        "normal_radius": normal_radius,
        "normal_max_nn": normal_max_nn,
        "feature_radius": feature_radius,
        "feature_max_nn": feature_max_nn,
        "max_correspondence_distance": max_correspondence_distance,
        "iteration_number": iteration_number,
        "fitness": float(result.fitness),
        "inlier_rmse": float(result.inlier_rmse),
        "transformation": np.asarray(result.transformation, dtype=np.float64).tolist(),
    }


def registration_colored_icp(source_cloud, target_cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    max_correspondence_distance = float(params.get("max_correspondence_distance", 0.18))
    max_iteration = int(params.get("max_iteration", 30))
    normal_radius = float(params.get("normal_radius", 0.2))
    normal_max_nn = int(params.get("normal_max_nn", 30))
    lambda_geometric = float(params.get("lambda_geometric", 0.968))
    source_colored = _ensure_colors(_estimate_normals_if_needed(source_cloud, normal_radius, normal_max_nn))
    target_colored = _ensure_colors(_estimate_normals_if_needed(target_cloud, normal_radius, normal_max_nn))
    result = o3d.pipelines.registration.registration_colored_icp(
        source_colored,
        target_colored,
        max_correspondence_distance,
        np.eye(4, dtype=np.float64),
        o3d.pipelines.registration.TransformationEstimationForColoredICP(lambda_geometric=lambda_geometric),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=max_iteration),
    )
    processed = _copy_cloud(source_cloud)
    processed.transform(result.transformation)
    return processed, {
        "max_correspondence_distance": max_correspondence_distance,
        "max_iteration": max_iteration,
        "normal_radius": normal_radius,
        "normal_max_nn": normal_max_nn,
        "lambda_geometric": lambda_geometric,
        "fitness": float(result.fitness),
        "inlier_rmse": float(result.inlier_rmse),
        "transformation": np.asarray(result.transformation, dtype=np.float64).tolist(),
    }


def registration_ransac_then_icp_point_to_plane(source_cloud, target_cloud, params: dict[str, Any]):
    coarse_params = {
        "normal_radius": params.get("normal_radius", 0.2),
        "normal_max_nn": params.get("normal_max_nn", 30),
        "feature_radius": params.get("feature_radius", 0.5),
        "feature_max_nn": params.get("feature_max_nn", 50),
        "max_correspondence_distance": params.get("max_correspondence_distance", 0.3),
        "ransac_n": params.get("ransac_n", 3),
        "max_iteration": params.get("coarse_max_iteration", 10000),
    }
    _, coarse_stats = registration_ransac_based_on_feature_matching(source_cloud, target_cloud, coarse_params)
    initial_transformation = np.asarray(coarse_stats["transformation"], dtype=np.float64)
    _, refined_stats = _run_icp_point_to_plane(
        source_cloud,
        target_cloud,
        max_correspondence_distance=float(params.get("max_correspondence_distance", 0.3)),
        max_iteration=int(params.get("icp_max_iteration", 40)),
        normal_radius=float(params.get("normal_radius", 0.2)),
        normal_max_nn=int(params.get("normal_max_nn", 30)),
        initial_transformation=initial_transformation,
    )
    processed = _copy_cloud(source_cloud)
    final_transformation = np.asarray(refined_stats["transformation"], dtype=np.float64)
    processed.transform(final_transformation)
    return processed, {
        "coarse_fitness": float(coarse_stats["fitness"]),
        "coarse_inlier_rmse": float(coarse_stats["inlier_rmse"]),
        "refined_fitness": float(refined_stats["fitness"]),
        "refined_inlier_rmse": float(refined_stats["inlier_rmse"]),
        "initial_transformation": coarse_stats["transformation"],
        "transformation": refined_stats["transformation"],
        "max_correspondence_distance": float(params.get("max_correspondence_distance", 0.3)),
        "coarse_max_iteration": int(params.get("coarse_max_iteration", 10000)),
        "icp_max_iteration": int(params.get("icp_max_iteration", 40)),
    }


def registration_fast_then_icp_point_to_plane(source_cloud, target_cloud, params: dict[str, Any]):
    coarse_params = {
        "normal_radius": params.get("normal_radius", 0.2),
        "normal_max_nn": params.get("normal_max_nn", 30),
        "feature_radius": params.get("feature_radius", 0.5),
        "feature_max_nn": params.get("feature_max_nn", 50),
        "max_correspondence_distance": params.get("max_correspondence_distance", 0.3),
        "iteration_number": params.get("iteration_number", 32),
    }
    _, coarse_stats = registration_fast_based_on_feature_matching(source_cloud, target_cloud, coarse_params)
    initial_transformation = np.asarray(coarse_stats["transformation"], dtype=np.float64)
    _, refined_stats = _run_icp_point_to_plane(
        source_cloud,
        target_cloud,
        max_correspondence_distance=float(params.get("max_correspondence_distance", 0.3)),
        max_iteration=int(params.get("icp_max_iteration", 40)),
        normal_radius=float(params.get("normal_radius", 0.2)),
        normal_max_nn=int(params.get("normal_max_nn", 30)),
        initial_transformation=initial_transformation,
    )
    processed = _copy_cloud(source_cloud)
    final_transformation = np.asarray(refined_stats["transformation"], dtype=np.float64)
    processed.transform(final_transformation)
    return processed, {
        "coarse_fitness": float(coarse_stats["fitness"]),
        "coarse_inlier_rmse": float(coarse_stats["inlier_rmse"]),
        "refined_fitness": float(refined_stats["fitness"]),
        "refined_inlier_rmse": float(refined_stats["inlier_rmse"]),
        "initial_transformation": coarse_stats["transformation"],
        "transformation": refined_stats["transformation"],
        "max_correspondence_distance": float(params.get("max_correspondence_distance", 0.3)),
        "iteration_number": int(params.get("iteration_number", 32)),
        "icp_max_iteration": int(params.get("icp_max_iteration", 40)),
    }


def evaluate_registration(source_cloud, target_cloud, params: dict[str, Any]):
    o3d = _require_open3d()
    max_correspondence_distance = float(params.get("max_correspondence_distance", 0.18))
    evaluation = o3d.pipelines.registration.evaluate_registration(
        source_cloud,
        target_cloud,
        max_correspondence_distance,
        np.eye(4, dtype=np.float64),
    )
    processed = _copy_cloud(source_cloud)
    return processed, {
        "max_correspondence_distance": max_correspondence_distance,
        "fitness": float(evaluation.fitness),
        "inlier_rmse": float(evaluation.inlier_rmse),
        "correspondence_set_size": int(len(evaluation.correspondence_set)),
    }


def compute_nearest_neighbor_distance(cloud, params: dict[str, Any]):
    distances = np.asarray(cloud.compute_nearest_neighbor_distance(), dtype=np.float64)
    processed = _copy_cloud(cloud)
    if distances.size == 0:
        return processed, {"distance_mean": 0.0, "distance_min": 0.0, "distance_max": 0.0}
    return processed, {
        "distance_mean": float(distances.mean()),
        "distance_min": float(distances.min()),
        "distance_max": float(distances.max()),
        "distance_p95": float(np.percentile(distances, 95)),
    }


def compute_point_cloud_distance(source_cloud, target_cloud, params: dict[str, Any]):
    distances = np.asarray(source_cloud.compute_point_cloud_distance(target_cloud), dtype=np.float64)
    processed = _copy_cloud(source_cloud)
    if distances.size == 0:
        return processed, {"distance_mean": 0.0, "distance_min": 0.0, "distance_max": 0.0}
    return processed, {
        "distance_mean": float(distances.mean()),
        "distance_min": float(distances.min()),
        "distance_max": float(distances.max()),
        "distance_p95": float(np.percentile(distances, 95)),
        "distance_count": int(distances.size),
    }


def segment_plane(cloud, params: dict[str, Any]):
    distance_threshold = float(params.get("distance_threshold", 0.02))
    ransac_n = int(params.get("ransac_n", 3))
    num_iterations = int(params.get("num_iterations", 1000))
    plane_model, inlier_indices = cloud.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=ransac_n,
        num_iterations=num_iterations,
    )
    processed = cloud.select_by_index(inlier_indices)
    return processed, {
        "distance_threshold": distance_threshold,
        "ransac_n": ransac_n,
        "num_iterations": num_iterations,
        "plane_model": [float(v) for v in plane_model],
        "inlier_count": len(inlier_indices),
    }


OPEN3D_ALGORITHM_HANDLERS = {
    "voxel_down_sample": voxel_down_sample,
    "estimate_normals": estimate_normals,
    "remove_statistical_outlier": remove_statistical_outlier,
    "uniform_down_sample": uniform_down_sample,
    "random_down_sample": random_down_sample,
    "remove_radius_outlier": remove_radius_outlier,
    "crop_axis_aligned_bbox": crop_axis_aligned_bbox,
    "cluster_dbscan": cluster_dbscan,
    "segment_plane_outliers": segment_plane_outliers,
    "hidden_point_removal": hidden_point_removal,
    "get_axis_aligned_bounding_box": get_axis_aligned_bounding_box,
    "get_oriented_bounding_box": get_oriented_bounding_box,
    "compute_convex_hull": compute_convex_hull,
    "compute_mahalanobis_distance": compute_mahalanobis_distance,
    "transform_point_cloud": transform_point_cloud,
    "registration_icp_point_to_point": registration_icp_point_to_point,
    "registration_icp_point_to_plane": registration_icp_point_to_plane,
    "compute_fpfh_feature": compute_fpfh_feature,
    "registration_ransac_based_on_feature_matching": registration_ransac_based_on_feature_matching,
    "registration_fast_based_on_feature_matching": registration_fast_based_on_feature_matching,
    "registration_colored_icp": registration_colored_icp,
    "registration_ransac_then_icp_point_to_plane": registration_ransac_then_icp_point_to_plane,
    "registration_fast_then_icp_point_to_plane": registration_fast_then_icp_point_to_plane,
    "evaluate_registration": evaluate_registration,
    "compute_nearest_neighbor_distance": compute_nearest_neighbor_distance,
    "compute_point_cloud_distance": compute_point_cloud_distance,
    "segment_plane": segment_plane,
}
