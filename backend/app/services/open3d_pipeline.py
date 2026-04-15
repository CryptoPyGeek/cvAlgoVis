from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

from app.schemas import Open3DProcessMeta, Open3DProcessRequest, Open3DProcessResponse
from app.services.open3d_algorithms import OPEN3D_ALGORITHM_HANDLERS

SUPPORTED_POINT_CLOUD_EXTENSIONS = {".ply", ".pcd"}
MAX_PREVIEW_POINTS = 5000


def _require_open3d():
    try:
        import open3d as o3d  # type: ignore

        return o3d
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Open3D dependency is not installed.") from exc


def validate_point_cloud_filename(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_POINT_CLOUD_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_POINT_CLOUD_EXTENSIONS))
        raise ValueError(f"Unsupported point-cloud file type: {suffix or '<none>'}. Supported: {supported}")
    return suffix


def _load_point_cloud(file_bytes: bytes, filename: str):
    o3d = _require_open3d()
    suffix = validate_point_cloud_filename(filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        point_cloud = o3d.io.read_point_cloud(temp_path)
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass

    if point_cloud.is_empty():
        raise ValueError("Point cloud is empty or could not be parsed.")

    return point_cloud, suffix.lstrip(".")


def process_point_cloud_file(request: Open3DProcessRequest, file_bytes: bytes) -> Open3DProcessResponse:
    handler = OPEN3D_ALGORITHM_HANDLERS.get(request.algorithm_id)
    if handler is None:
        raise ValueError(f"Unsupported Open3D algorithm: {request.algorithm_id}")

    start = time.perf_counter()
    point_cloud, file_type = _load_point_cloud(file_bytes, request.filename)
    points_before = len(point_cloud.points)

    processed_cloud, stats = handler(point_cloud, request.params)
    points_after = len(processed_cloud.points)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    if request.algorithm_id == "segment_plane":
        summary = f"平面分割完成，识别到 {stats.get('inlier_count', 0)} 个平面内点。"
    elif request.algorithm_id == "estimate_normals":
        summary = "法线估计完成，点云法线已更新。"
    elif request.algorithm_id == "remove_statistical_outlier":
        removed = max(points_before - points_after, 0)
        summary = f"离群点去除完成，移除了 {removed} 个点。"
    else:
        summary = f"点云处理完成，点数从 {points_before} 变为 {points_after}。"

    return Open3DProcessResponse(
        summary=summary,
        meta=Open3DProcessMeta(
            elapsed_ms=elapsed_ms,
            algorithm=request.algorithm_id,
            filename=request.filename,
            file_type=file_type,
            points_before=points_before,
            points_after=points_after,
        ),
        stats=stats,
        source_points=serialize_preview_points(point_cloud),
        processed_points=serialize_preview_points(processed_cloud),
    )


def serialize_preview_points(point_cloud, max_points: int = MAX_PREVIEW_POINTS) -> list[list[float]]:
    points = np.asarray(point_cloud.points, dtype=np.float32)
    if points.size == 0:
        return []

    total = len(points)
    if total > max_points:
        indices = np.linspace(0, total - 1, max_points, dtype=np.int32)
        points = points[indices]

    return [[float(x), float(y), float(z)] for x, y, z in points]
