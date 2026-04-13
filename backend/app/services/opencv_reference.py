"""Centralized OpenCV function reference used in code comments and docs.

The project keeps this dictionary so new contributors can quickly understand
common APIs, parameter meaning, and return values.
"""

OPENCV_FUNCTION_REFERENCE = {
    "cv2.imread": {
        "purpose": "从磁盘读取图像文件。",
        "params": {"filename": "图像路径", "flags": "读取模式，如 cv2.IMREAD_COLOR"},
        "returns": "numpy.ndarray | None，读取失败返回 None。",
    },
    "cv2.cvtColor": {
        "purpose": "执行色彩空间转换，例如 BGR->GRAY。",
        "params": {"src": "输入图像", "code": "转换代码，如 cv2.COLOR_BGR2GRAY"},
        "returns": "转换后的图像 ndarray。",
    },
    "cv2.GaussianBlur": {
        "purpose": "高斯滤波，常用于降噪。",
        "params": {"src": "输入图像", "ksize": "卷积核大小(奇数)", "sigmaX": "X 方向标准差"},
        "returns": "模糊后的图像 ndarray。",
    },
    "cv2.Canny": {
        "purpose": "Canny 边缘检测。",
        "params": {
            "image": "通常为灰度图",
            "threshold1": "低阈值",
            "threshold2": "高阈值",
            "apertureSize": "Sobel 核大小(3/5/7)",
        },
        "returns": "单通道边缘图 ndarray。",
    },
    "cv2.findContours": {
        "purpose": "在二值图中查找轮廓。",
        "params": {"image": "二值图", "mode": "轮廓检索模式", "method": "轮廓近似方法"},
        "returns": "(contours, hierarchy) 元组。",
    },
    "cv2.warpPerspective": {
        "purpose": "执行透视变换，常用于矫正视角。",
        "params": {"src": "输入图像", "M": "3x3 透视矩阵", "dsize": "输出图尺寸"},
        "returns": "透视变换后的图像 ndarray。",
    },
    "cv2.matchTemplate": {
        "purpose": "模板匹配，定位局部图案。",
        "params": {"image": "搜索图像", "templ": "模板图像", "method": "匹配方法常量"},
        "returns": "响应图 ndarray，峰值位置表示最佳匹配。",
    },
    "cv2.CascadeClassifier.detectMultiScale": {
        "purpose": "Haar/LBP 级联检测，常用于人脸检测。",
        "params": {
            "image": "灰度图",
            "scaleFactor": "图像金字塔缩放比例",
            "minNeighbors": "相邻候选框阈值",
            "minSize": "最小检测窗口",
        },
        "returns": "检测框列表 ndarray，形如 (x, y, w, h)。",
    },
}
