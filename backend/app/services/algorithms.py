import cv2
import numpy as np


def _odd(value: int) -> int:
    value = max(1, int(value))
    return value if value % 2 == 1 else value + 1


def canny(image: np.ndarray, params: dict) -> np.ndarray:
    # cv2.cvtColor: convert BGR input to grayscale for edge extraction.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.Canny(image, threshold1, threshold2, apertureSize) -> edge map.
    edges = cv2.Canny(
        gray,
        threshold1=float(params.get("threshold1", 80)),
        threshold2=float(params.get("threshold2", 150)),
        apertureSize=int(params.get("aperture_size", 3)),
    )
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def threshold_binary(image: np.ndarray, params: dict) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold = float(params.get("threshold", 128))
    max_value = float(params.get("max_value", 255))
    _, binary = cv2.threshold(gray, threshold, max_value, cv2.THRESH_BINARY)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def erode(image: np.ndarray, params: dict) -> np.ndarray:
    kernel_size = _odd(int(params.get("kernel_size", 3)))
    iterations = int(params.get("iterations", 1))
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    return cv2.erode(image, kernel, iterations=iterations)


def dilate(image: np.ndarray, params: dict) -> np.ndarray:
    kernel_size = _odd(int(params.get("kernel_size", 3)))
    iterations = int(params.get("iterations", 1))
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    return cv2.dilate(image, kernel, iterations=iterations)


def gaussian_blur(image: np.ndarray, params: dict) -> np.ndarray:
    kernel_size = _odd(int(params.get("kernel_size", 7)))
    sigma = float(params.get("sigma", 1.5))
    # cv2.GaussianBlur(src, ksize, sigmaX) -> smoothed image.
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma)


def median_blur(image: np.ndarray, params: dict) -> np.ndarray:
    kernel_size = _odd(int(params.get("kernel_size", 5)))
    return cv2.medianBlur(image, kernel_size)


def sharpen(image: np.ndarray, params: dict) -> np.ndarray:
    amount = float(params.get("amount", 1.5))
    kernel = np.array(
        [[0, -1, 0], [-1, 5 + amount, -1], [0, -1, 0]],
        dtype=np.float32,
    )
    return cv2.filter2D(image, ddepth=-1, kernel=kernel)


def find_contours_overlay(image: np.ndarray) -> np.ndarray:
    """Reference for cv2.findContours usage."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # cv2.findContours(image, mode, method) -> (contours, hierarchy).
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    canvas = image.copy()
    cv2.drawContours(canvas, contours, -1, (0, 255, 0), 2)
    return canvas


def warp_perspective_demo(image: np.ndarray) -> np.ndarray:
    """Reference for cv2.warpPerspective usage."""
    h, w = image.shape[:2]
    src = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
    dst = np.float32([[w * 0.05, h * 0.1], [w * 0.95, 0], [0, h], [w, h * 0.9]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    # cv2.warpPerspective(src, M, dsize) -> perspective corrected image.
    return cv2.warpPerspective(image, matrix, (w, h))


def match_template_demo(image: np.ndarray) -> np.ndarray:
    """Reference for cv2.matchTemplate usage."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    tw, th = max(10, w // 5), max(10, h // 5)
    template = gray[:th, :tw]
    # cv2.matchTemplate(image, templ, method) -> response map.
    response = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(response)
    canvas = image.copy()
    cv2.rectangle(canvas, max_loc, (max_loc[0] + tw, max_loc[1] + th), (0, 255, 255), 2)
    return canvas


def face_detect_demo(image: np.ndarray) -> np.ndarray:
    """Reference for CascadeClassifier.detectMultiScale usage."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    # detectMultiScale(image, scaleFactor, minNeighbors, minSize) -> face boxes.
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    canvas = image.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(canvas, (x, y), (x + w, y + h), (255, 200, 0), 2)
    return canvas


ALGORITHM_HANDLERS = {
    "canny": canny,
    "threshold_binary": threshold_binary,
    "erode": erode,
    "dilate": dilate,
    "gaussian_blur": gaussian_blur,
    "median_blur": median_blur,
    "sharpen": sharpen,
}
