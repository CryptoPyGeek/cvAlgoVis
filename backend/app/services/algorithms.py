import cv2
import numpy as np


def _odd(value: int) -> int:
    value = max(1, int(value))
    return value if value % 2 == 1 else value + 1


def _to_gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _kernel(size: int) -> np.ndarray:
    return np.ones((_odd(size), _odd(size)), dtype=np.uint8)


def _norm_to_u8(image: np.ndarray) -> np.ndarray:
    return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def bgr_to_rgb(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def bgr_to_hsv(image: np.ndarray, params: dict) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def bgr_to_yuv(image: np.ndarray, params: dict) -> np.ndarray:
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)


def bgr_to_lab(image: np.ndarray, params: dict) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def pseudo_hdr(image: np.ndarray, params: dict) -> np.ndarray:
    sigma_s = float(params.get("sigma_s", 12))
    sigma_r = float(params.get("sigma_r", 0.2))
    gamma = float(params.get("gamma", 1.2))
    enhanced = cv2.detailEnhance(image, sigma_s=max(0.1, sigma_s), sigma_r=max(0.01, sigma_r))
    lut = np.array([((i / 255.0) ** (1.0 / max(0.1, gamma))) * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(enhanced, lut)


def affine_transform(image: np.ndarray, params: dict) -> np.ndarray:
    h, w = image.shape[:2]
    tx = float(params.get("tx", 15))
    ty = float(params.get("ty", 10))
    shear = float(params.get("shear", 0.08))
    matrix = np.float32([[1, shear, tx], [shear, 1, ty]])
    return cv2.warpAffine(image, matrix, (w, h))


def perspective_transform(image: np.ndarray, params: dict) -> np.ndarray:
    h, w = image.shape[:2]
    k = float(params.get("strength", 0.08))
    src = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
    dst = np.float32([[w * k, h * k], [w * (1 - k), 0], [0, h], [w, h * (1 - k)]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(image, matrix, (w, h))


def rotate(image: np.ndarray, params: dict) -> np.ndarray:
    h, w = image.shape[:2]
    angle = float(params.get("angle", 15))
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(image, matrix, (w, h))


def scale(image: np.ndarray, params: dict) -> np.ndarray:
    factor = float(params.get("scale", 1.2))
    h, w = image.shape[:2]
    resized = cv2.resize(image, None, fx=max(0.1, factor), fy=max(0.1, factor))
    return cv2.resize(resized, (w, h))


def translate(image: np.ndarray, params: dict) -> np.ndarray:
    h, w = image.shape[:2]
    tx = float(params.get("tx", 20))
    ty = float(params.get("ty", 20))
    matrix = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(image, matrix, (w, h))


def skew(image: np.ndarray, params: dict) -> np.ndarray:
    h, w = image.shape[:2]
    sx = float(params.get("sx", 0.15))
    sy = float(params.get("sy", 0.0))
    matrix = np.float32([[1, sx, 0], [sy, 1, 0]])
    return cv2.warpAffine(image, matrix, (w, h))


def threshold_binary(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    threshold = float(params.get("threshold", 128))
    max_value = float(params.get("max_value", 255))
    _, binary = cv2.threshold(gray, threshold, max_value, cv2.THRESH_BINARY)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def adaptive_threshold(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    block_size = _odd(int(params.get("block_size", 11)))
    c = float(params.get("c", 2))
    out = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
    return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)


def global_threshold(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    threshold = float(params.get("threshold", 127))
    _, out = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)


def otsu_threshold(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    _, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)


def gaussian_blur(image: np.ndarray, params: dict) -> np.ndarray:
    kernel_size = _odd(int(params.get("kernel_size", 7)))
    sigma = float(params.get("sigma", 1.5))
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma)


def median_blur(image: np.ndarray, params: dict) -> np.ndarray:
    kernel_size = _odd(int(params.get("kernel_size", 5)))
    return cv2.medianBlur(image, kernel_size)


def mean_blur(image: np.ndarray, params: dict) -> np.ndarray:
    kernel_size = _odd(int(params.get("kernel_size", 5)))
    return cv2.blur(image, (_odd(kernel_size), _odd(kernel_size)))


def bilateral_blur(image: np.ndarray, params: dict) -> np.ndarray:
    d = int(params.get("diameter", 9))
    sigma_color = float(params.get("sigma_color", 75))
    sigma_space = float(params.get("sigma_space", 75))
    return cv2.bilateralFilter(image, d=max(1, d), sigmaColor=sigma_color, sigmaSpace=sigma_space)


def erode(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.erode(image, _kernel(int(params.get("kernel_size", 3))), iterations=int(params.get("iterations", 1)))


def dilate(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.dilate(image, _kernel(int(params.get("kernel_size", 3))), iterations=int(params.get("iterations", 1)))


def morph_open(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, _kernel(int(params.get("kernel_size", 5))))


def morph_close(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, _kernel(int(params.get("kernel_size", 5))))


def morph_gradient(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.morphologyEx(image, cv2.MORPH_GRADIENT, _kernel(int(params.get("kernel_size", 5))))


def morph_blackhat(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, _kernel(int(params.get("kernel_size", 9))))


def morph_whitehat(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.morphologyEx(image, cv2.MORPH_TOPHAT, _kernel(int(params.get("kernel_size", 9))))


def morph_tophat(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.morphologyEx(image, cv2.MORPH_TOPHAT, _kernel(int(params.get("kernel_size", 9))))


def morph_bottomhat(image: np.ndarray, params: dict) -> np.ndarray:
    k = _kernel(int(params.get("kernel_size", 9)))
    closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, k)
    return cv2.subtract(closed, image)


def canny(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    edges = cv2.Canny(
        gray,
        threshold1=float(params.get("threshold1", 80)),
        threshold2=float(params.get("threshold2", 150)),
        apertureSize=int(params.get("aperture_size", 3)),
    )
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def laplacian(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    dst = cv2.Laplacian(gray, cv2.CV_64F, ksize=_odd(int(params.get("kernel_size", 3))))
    return cv2.cvtColor(_norm_to_u8(np.abs(dst)), cv2.COLOR_GRAY2BGR)


def watershed_segmentation(image: np.ndarray, params: dict) -> np.ndarray:
    blur = cv2.GaussianBlur(image, (3, 3), 0)
    gray = _to_gray(blur)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.35 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(image.copy(), markers)
    out = image.copy()
    out[markers == -1] = [0, 0, 255]
    return out


def grabcut_segmentation(image: np.ndarray, params: dict) -> np.ndarray:
    h, w = image.shape[:2]
    rect_margin = int(params.get("margin", 10))
    rect = (rect_margin, rect_margin, max(1, w - rect_margin * 2), max(1, h - rect_margin * 2))
    mask = np.zeros(image.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    return image * mask2[:, :, np.newaxis]


def harris_corners(image: np.ndarray, params: dict) -> np.ndarray:
    gray = np.float32(_to_gray(image))
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)
    out = image.copy()
    out[dst > 0.01 * dst.max()] = [0, 0, 255]
    return out


def shi_tomasi_corners(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    max_corners = int(params.get("max_corners", 120))
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=max_corners, qualityLevel=0.01, minDistance=5)
    out = image.copy()
    if corners is not None:
        for c in corners.astype(np.int32):
            x, y = c.ravel()
            cv2.circle(out, (x, y), 3, (0, 255, 0), -1)
    return out


def fast_corners(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    threshold = int(params.get("threshold", 20))
    detector = cv2.FastFeatureDetector_create(threshold=threshold)
    kp = detector.detect(gray, None)
    return cv2.drawKeypoints(image, kp, None, color=(255, 0, 0))


def _descriptor_pair(image: np.ndarray, detector) -> tuple[list, np.ndarray, list, np.ndarray]:
    gray1 = _to_gray(image)
    h, w = gray1.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), 8, 1.0)
    transformed = cv2.warpAffine(image, matrix, (w, h))
    gray2 = _to_gray(transformed)
    kp1, des1 = detector.detectAndCompute(gray1, None)
    kp2, des2 = detector.detectAndCompute(gray2, None)
    if des1 is None or des2 is None:
        raise ValueError("Not enough features for descriptor/matching.")
    return kp1, des1, kp2, des2


def orb_features(image: np.ndarray, params: dict) -> np.ndarray:
    nfeatures = int(params.get("nfeatures", 300))
    detector = cv2.ORB_create(nfeatures=nfeatures)
    kp = detector.detect(_to_gray(image), None)
    return cv2.drawKeypoints(image, kp, None, color=(0, 255, 255))


def sift_features(image: np.ndarray, params: dict) -> np.ndarray:
    if not hasattr(cv2, "SIFT_create"):
        raise ValueError("SIFT is not available in current OpenCV build.")
    detector = cv2.SIFT_create(nfeatures=int(params.get("nfeatures", 200)))
    kp = detector.detect(_to_gray(image), None)
    return cv2.drawKeypoints(image, kp, None, color=(255, 255, 0))


def surf_features(image: np.ndarray, params: dict) -> np.ndarray:
    if not hasattr(cv2, "xfeatures2d") or not hasattr(cv2.xfeatures2d, "SURF_create"):
        raise ValueError("SURF is not available in current OpenCV build.")
    detector = cv2.xfeatures2d.SURF_create(hessianThreshold=float(params.get("hessian", 400)))
    kp = detector.detect(_to_gray(image), None)
    return cv2.drawKeypoints(image, kp, None, color=(255, 0, 255))


def lbp_features(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    c = gray[1:-1, 1:-1]
    lbp = np.zeros_like(c, dtype=np.uint8)
    lbp |= ((gray[:-2, :-2] >= c) << 7).astype(np.uint8)
    lbp |= ((gray[:-2, 1:-1] >= c) << 6).astype(np.uint8)
    lbp |= ((gray[:-2, 2:] >= c) << 5).astype(np.uint8)
    lbp |= ((gray[1:-1, 2:] >= c) << 4).astype(np.uint8)
    lbp |= ((gray[2:, 2:] >= c) << 3).astype(np.uint8)
    lbp |= ((gray[2:, 1:-1] >= c) << 2).astype(np.uint8)
    lbp |= ((gray[2:, :-2] >= c) << 1).astype(np.uint8)
    lbp |= ((gray[1:-1, :-2] >= c) << 0).astype(np.uint8)
    return cv2.applyColorMap(cv2.resize(lbp, (image.shape[1], image.shape[0])), cv2.COLORMAP_JET)


def hog_features(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    hog = cv2.HOGDescriptor()
    feats = hog.compute(cv2.resize(gray, (64, 128)))
    vec = feats.flatten()
    side = int(np.ceil(np.sqrt(vec.shape[0])))
    padded = np.zeros(side * side, dtype=np.float32)
    padded[: vec.shape[0]] = vec
    heat = _norm_to_u8(padded.reshape(side, side))
    heat = cv2.resize(heat, (image.shape[1], image.shape[0]))
    return cv2.applyColorMap(heat, cv2.COLORMAP_TURBO)


def knn_match(image: np.ndarray, params: dict) -> np.ndarray:
    detector = cv2.ORB_create(nfeatures=int(params.get("nfeatures", 400)))
    kp1, des1, kp2, des2 = _descriptor_pair(image, detector)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    pairs = bf.knnMatch(des1, des2, k=2)
    good = []
    for pair in pairs:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < 0.75 * n.distance:
            good.append([m])
    return cv2.drawMatchesKnn(image, kp1, cv2.warpAffine(image, cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), 8, 1.0), (image.shape[1], image.shape[0])), kp2, good[:50], None, flags=2)


def bf_match(image: np.ndarray, params: dict) -> np.ndarray:
    detector = cv2.ORB_create(nfeatures=int(params.get("nfeatures", 400)))
    kp1, des1, kp2, des2 = _descriptor_pair(image, detector)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(matcher.match(des1, des2), key=lambda x: x.distance)[:60]
    transformed = cv2.warpAffine(image, cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), 8, 1.0), (image.shape[1], image.shape[0]))
    return cv2.drawMatches(image, kp1, transformed, kp2, matches, None, flags=2)


def flann_match(image: np.ndarray, params: dict) -> np.ndarray:
    detector = cv2.SIFT_create() if hasattr(cv2, "SIFT_create") else cv2.ORB_create()
    kp1, des1, kp2, des2 = _descriptor_pair(image, detector)
    if des1.dtype != np.float32:
        des1 = des1.astype(np.float32)
        des2 = des2.astype(np.float32)
    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    pairs = flann.knnMatch(des1, des2, k=2)
    good = []
    for pair in pairs:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < 0.75 * n.distance:
            good.append([m])
    transformed = cv2.warpAffine(image, cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), 8, 1.0), (image.shape[1], image.shape[0]))
    return cv2.drawMatchesKnn(image, kp1, transformed, kp2, good[:50], None, flags=2)


def template_match(image: np.ndarray, params: dict) -> np.ndarray:
    gray = _to_gray(image)
    h, w = gray.shape
    ratio = float(params.get("template_ratio", 0.2))
    tw = max(12, int(w * ratio))
    th = max(12, int(h * ratio))
    template = gray[:th, :tw]
    response = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(response)
    out = image.copy()
    cv2.rectangle(out, max_loc, (max_loc[0] + tw, max_loc[1] + th), (0, 255, 255), 2)
    return out


def template_match_homology(image: np.ndarray, params: dict) -> np.ndarray:
    orb = cv2.ORB_create(nfeatures=500)
    gray = _to_gray(image)
    h, w = gray.shape
    matrix = cv2.getPerspectiveTransform(
        np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]]),
        np.float32([[w * 0.1, h * 0.05], [w * 0.9, 0], [w * 0.05, h], [w, h * 0.95]]),
    )
    warped = cv2.warpPerspective(image, matrix, (w, h))
    kp1, des1 = orb.detectAndCompute(gray, None)
    kp2, des2 = orb.detectAndCompute(_to_gray(warped), None)
    if des1 is None or des2 is None:
        return image
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(bf.match(des1, des2), key=lambda x: x.distance)[:80]
    if len(matches) < 4:
        return cv2.drawMatches(image, kp1, warped, kp2, matches, None, flags=2)
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    hmat, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    out = warped.copy()
    if hmat is not None:
        corners = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]]).reshape(-1, 1, 2)
        proj = cv2.perspectiveTransform(corners, hmat)
        cv2.polylines(out, [np.int32(proj)], True, (0, 255, 0), 3)
    return out


def sharpen(image: np.ndarray, params: dict) -> np.ndarray:
    amount = float(params.get("amount", 1.5))
    kernel = np.array([[0, -1, 0], [-1, 5 + amount, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(image, ddepth=-1, kernel=kernel)


ALGORITHM_HANDLERS = {
    "bgr_to_rgb": bgr_to_rgb,
    "bgr_to_hsv": bgr_to_hsv,
    "bgr_to_yuv": bgr_to_yuv,
    "bgr_to_lab": bgr_to_lab,
    "pseudo_hdr": pseudo_hdr,
    "affine_transform": affine_transform,
    "perspective_transform": perspective_transform,
    "rotate": rotate,
    "scale": scale,
    "translate": translate,
    "skew": skew,
    "threshold_binary": threshold_binary,
    "adaptive_threshold": adaptive_threshold,
    "global_threshold": global_threshold,
    "otsu_threshold": otsu_threshold,
    "gaussian_blur": gaussian_blur,
    "median_blur": median_blur,
    "mean_blur": mean_blur,
    "bilateral_blur": bilateral_blur,
    "erode": erode,
    "dilate": dilate,
    "morph_open": morph_open,
    "morph_close": morph_close,
    "morph_gradient": morph_gradient,
    "morph_blackhat": morph_blackhat,
    "morph_whitehat": morph_whitehat,
    "morph_tophat": morph_tophat,
    "morph_bottomhat": morph_bottomhat,
    "canny": canny,
    "laplacian": laplacian,
    "watershed_segmentation": watershed_segmentation,
    "grabcut_segmentation": grabcut_segmentation,
    "harris_corners": harris_corners,
    "shi_tomasi_corners": shi_tomasi_corners,
    "fast_corners": fast_corners,
    "orb_features": orb_features,
    "sift_features": sift_features,
    "surf_features": surf_features,
    "lbp_features": lbp_features,
    "hog_features": hog_features,
    "knn_match": knn_match,
    "bf_match": bf_match,
    "flann_match": flann_match,
    "template_match": template_match,
    "template_match_homology": template_match_homology,
    "sharpen": sharpen,
}
