import numpy as np

from app.services.algorithms import (
    ALGORITHM_HANDLERS,
    canny,
    gaussian_blur,
    sharpen,
)


def fake_image():
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    image[16:48, 16:48] = (255, 255, 255)
    return image


def test_canny_returns_bgr_shape():
    out = canny(fake_image(), {"threshold1": 50, "threshold2": 120, "aperture_size": 3})
    assert out.shape == (64, 64, 3)


def test_gaussian_blur_preserves_shape():
    out = gaussian_blur(fake_image(), {"kernel_size": 5, "sigma": 1.0})
    assert out.shape == (64, 64, 3)


def test_sharpen_changes_pixels():
    inp = fake_image()
    out = sharpen(inp, {"amount": 2.0})
    assert out.shape == inp.shape
    assert np.any(out != inp)


def test_all_handlers_callable():
    for name, handler in ALGORITHM_HANDLERS.items():
        out = handler(fake_image(), {})
        assert out.shape == (64, 64, 3), f"{name} output shape mismatch"
