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


class ErrorResponse(BaseModel):
    detail: str
    request_id: str | None = None


class CodeSnippetResponse(BaseModel):
    algorithm_id: str
    language: str = "python"
    snippet: str


class CatalogResponse(BaseModel):
    libraries: list[dict[str, Any]]
