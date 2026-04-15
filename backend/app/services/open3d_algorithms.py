from __future__ import annotations

from copy import deepcopy
from typing import Any


def _require_open3d():
    try:
        import open3d as o3d  # type: ignore

        return o3d
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Open3D dependency is not installed.") from exc


def _copy_cloud(cloud):
    return deepcopy(cloud)


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
    "segment_plane": segment_plane,
}
