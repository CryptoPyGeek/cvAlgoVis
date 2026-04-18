from typing import Any

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    library_id: str = Field(default="opencv", description="Algorithm library id.")
    algorithm_id: str = Field(description="Algorithm id, such as 'canny'.")
    params: dict[str, float | int] = Field(default_factory=dict)
    image: str = Field(description="Input image as data URL or raw base64.")


class ProcessMeta(BaseModel):
    elapsed_ms: int
    width: int
    height: int
    algorithm: str


class ProcessResponse(BaseModel):
    processed_image: str
    meta: ProcessMeta


class Open3DProcessRequest(BaseModel):
    algorithm_id: str = Field(description="Open3D algorithm id.")
    params: dict[str, float | int] = Field(default_factory=dict)
    filename: str = Field(description="Original uploaded point-cloud filename.")
    target_filename: str | None = Field(default=None, description="Optional target point-cloud filename.")


class Open3DProcessMeta(BaseModel):
    elapsed_ms: int
    algorithm: str
    filename: str
    target_filename: str | None = None
    file_type: str
    points_before: int
    points_after: int


class Open3DProcessResponse(BaseModel):
    result_kind: str = "point_cloud_summary"
    summary: str
    meta: Open3DProcessMeta
    stats: dict[str, Any] = Field(default_factory=dict)
    source_points: list[list[float]] = Field(default_factory=list)
    target_points: list[list[float]] = Field(default_factory=list)
    processed_points: list[list[float]] = Field(default_factory=list)
    processed_normals: list[list[float]] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str
    request_id: str | None = None


class CodeSnippetResponse(BaseModel):
    algorithm_id: str
    language: str = "python"
    snippet: str
    highlighted_html: str
    pygments_css: str


class CatalogResponse(BaseModel):
    libraries: list[dict[str, Any]]
