import time

import numpy as np

from app.services.algorithms import ALGORITHM_HANDLERS


def process_image(library_id: str, algorithm_id: str, image: np.ndarray, params: dict):
    if library_id != "opencv":
        raise ValueError(f"Unsupported library: {library_id}")
    handler = ALGORITHM_HANDLERS.get(algorithm_id)
    if handler is None:
        raise ValueError(f"Unsupported algorithm: {algorithm_id}")
    start = time.perf_counter()
    processed = handler(image, params)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return processed, elapsed_ms
