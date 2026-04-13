import numpy as np

from app.services.algorithms import (
    ALGORITHM_HANDLERS,
    adaptive_threshold,
    bgr_to_hsv,
    bf_match,
    canny,
    gaussian_blur,
    grabcut_segmentation,
    laplacian,
    template_match,
    sharpen,
    watershed_segmentation,
)


def fake_image():
    image = np.zeros((96, 96, 3), dtype=np.uint8)
    image[20:76, 20:76] = (180, 180, 180)
    image[28:68, 28:68] = (255, 255, 255)
    image[::6, :] = (40, 40, 40)
    image[:, ::8] = (70, 70, 70)
    return image


def test_canny_returns_bgr_shape():
    out = canny(fake_image(), {"threshold1": 50, "threshold2": 120, "aperture_size": 3})
    assert out.shape == (96, 96, 3)


def test_gaussian_blur_preserves_shape():
    out = gaussian_blur(fake_image(), {"kernel_size": 5, "sigma": 1.0})
    assert out.shape == (96, 96, 3)


def test_color_conversion_shape():
    out = bgr_to_hsv(fake_image(), {})
    assert out.shape == (96, 96, 3)


def test_adaptive_threshold_shape():
    out = adaptive_threshold(fake_image(), {"block_size": 11, "c": 2})
    assert out.shape == (96, 96, 3)


def test_laplacian_shape():
    out = laplacian(fake_image(), {"kernel_size": 3})
    assert out.shape == (96, 96, 3)


def test_segmentation_shapes():
    out1 = watershed_segmentation(fake_image(), {})
    out2 = grabcut_segmentation(fake_image(), {"margin": 2})
    assert out1.shape == (96, 96, 3)
    assert out2.shape == (96, 96, 3)


def test_matching_shapes():
    out1 = template_match(fake_image(), {"template_ratio": 0.25})
    out2 = bf_match(fake_image(), {"nfeatures": 100})
    assert out1.shape[2] == 3
    assert out2.shape[2] == 3


def test_sharpen_changes_pixels():
    inp = fake_image()
    out = sharpen(inp, {"amount": 2.0})
    assert out.shape == inp.shape
    assert np.any(out != inp)


def test_all_handlers_callable():
    for name, handler in ALGORITHM_HANDLERS.items():
        try:
            out = handler(fake_image(), {})
        except ValueError as exc:
            assert "not available" in str(exc).lower() or "not enough features" in str(exc).lower()
            continue
        assert len(out.shape) == 3 and out.shape[2] == 3, f"{name} output channels mismatch"
        assert out.shape[0] > 0 and out.shape[1] > 0, f"{name} output size mismatch"
