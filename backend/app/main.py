import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from app.catalog import get_catalog
from app.examples.code_snippets import ALGORITHM_SNIPPETS
from app.schemas import (
    CatalogResponse,
    CodeSnippetResponse,
    ProcessMeta,
    ProcessRequest,
    ProcessResponse,
)
from app.services.image_io import decode_image_from_base64, encode_image_to_base64
from app.services.opencv_reference import OPENCV_FUNCTION_REFERENCE
from app.services.pipeline import process_image


app = FastAPI(title="cvAlgoVis API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/catalog", response_model=CatalogResponse)
def catalog():
    return get_catalog()


@app.get("/code-snippet", response_model=CodeSnippetResponse)
def code_snippet(algorithm_id: str):
    snippet = ALGORITHM_SNIPPETS.get(algorithm_id)
    if snippet is None:
        raise HTTPException(status_code=404, detail=f"Unknown algorithm: {algorithm_id}")
    formatter = HtmlFormatter(cssclass="code-highlight", nowrap=False)
    highlighted_html = highlight(snippet, PythonLexer(), formatter)
    pygments_css = formatter.get_style_defs(".code-highlight")
    return CodeSnippetResponse(
        algorithm_id=algorithm_id,
        snippet=snippet,
        highlighted_html=highlighted_html,
        pygments_css=pygments_css,
    )


@app.get("/opencv-reference")
def opencv_reference():
    return {"functions": OPENCV_FUNCTION_REFERENCE}


@app.post("/process", response_model=ProcessResponse)
def process(payload: ProcessRequest):
    request_id = str(uuid.uuid4())
    try:
        image = decode_image_from_base64(payload.image)
        processed, elapsed_ms = process_image(
            library_id=payload.library_id,
            algorithm_id=payload.algorithm_id,
            image=image,
            params=payload.params,
        )
        encoded = encode_image_to_base64(processed)
        height, width = processed.shape[:2]
        return ProcessResponse(
            processed_image=encoded,
            meta=ProcessMeta(
                elapsed_ms=elapsed_ms,
                width=int(width),
                height=int(height),
                algorithm=payload.algorithm_id,
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{exc} [request_id={request_id}]") from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Internal error [request_id={request_id}]") from exc
