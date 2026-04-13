ALGORITHM_SNIPPETS = {
    "canny": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, threshold1, threshold2, apertureSize=aperture_size)
result = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)""",
    "threshold_binary": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, threshold, max_value, cv2.THRESH_BINARY)
result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)""",
    "erode": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.erode(image, kernel, iterations=iterations)""",
    "dilate": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.dilate(image, kernel, iterations=iterations)""",
    "gaussian_blur": """result = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma)""",
    "median_blur": """result = cv2.medianBlur(image, kernel_size)""",
    "sharpen": """kernel = np.array([[0, -1, 0], [-1, 5 + amount, -1], [0, -1, 0]], dtype=np.float32)
result = cv2.filter2D(image, ddepth=-1, kernel=kernel)""",
}
