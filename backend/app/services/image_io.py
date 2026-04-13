import base64
import re

import cv2
import numpy as np


DATA_URL_RE = re.compile(r"^data:image\/[a-zA-Z0-9.+-]+;base64,(?P<data>.+)$")


def decode_image_from_base64(image_payload: str) -> np.ndarray:
    match = DATA_URL_RE.match(image_payload.strip())
    raw_base64 = match.group("data") if match else image_payload.strip()
    raw = base64.b64decode(raw_base64)
    arr = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Image decode failed.")
    return image


def encode_image_to_base64(image: np.ndarray) -> str:
    ok, buffer = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("Image encode failed.")
    encoded = base64.b64encode(buffer.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"
