from copy import deepcopy

from app.examples.code_snippets import ALGORITHM_SNIPPETS


CATALOG = {
    "libraries": [
        {
            "id": "opencv",
            "name": "OpenCV",
            "enabled": True,
            "modules": [
                {
                    "id": "edge_threshold",
                    "name": "边缘与阈值",
                    "algorithms": [
                        {
                            "id": "canny",
                            "name": "Canny 边缘检测",
                            "params": [
                                {"name": "threshold1", "type": "number", "min": 0, "max": 255, "step": 1, "default": 80},
                                {"name": "threshold2", "type": "number", "min": 0, "max": 255, "step": 1, "default": 150},
                                {"name": "aperture_size", "type": "number", "min": 3, "max": 7, "step": 2, "default": 3},
                            ],
                        },
                        {
                            "id": "threshold_binary",
                            "name": "二值阈值",
                            "params": [
                                {"name": "threshold", "type": "number", "min": 0, "max": 255, "step": 1, "default": 128},
                                {"name": "max_value", "type": "number", "min": 0, "max": 255, "step": 1, "default": 255},
                            ],
                        },
                        {
                            "id": "erode",
                            "name": "腐蚀",
                            "params": [
                                {"name": "kernel_size", "type": "number", "min": 1, "max": 31, "step": 2, "default": 3},
                                {"name": "iterations", "type": "number", "min": 1, "max": 10, "step": 1, "default": 1},
                            ],
                        },
                        {
                            "id": "dilate",
                            "name": "膨胀",
                            "params": [
                                {"name": "kernel_size", "type": "number", "min": 1, "max": 31, "step": 2, "default": 3},
                                {"name": "iterations", "type": "number", "min": 1, "max": 10, "step": 1, "default": 1},
                            ],
                        },
                    ],
                },
                {
                    "id": "filter_sharpen",
                    "name": "滤波与锐化",
                    "algorithms": [
                        {
                            "id": "gaussian_blur",
                            "name": "高斯模糊",
                            "params": [
                                {"name": "kernel_size", "type": "number", "min": 1, "max": 31, "step": 2, "default": 7},
                                {"name": "sigma", "type": "number", "min": 0, "max": 20, "step": 0.1, "default": 1.5},
                            ],
                        },
                        {
                            "id": "median_blur",
                            "name": "中值滤波",
                            "params": [
                                {"name": "kernel_size", "type": "number", "min": 1, "max": 31, "step": 2, "default": 5}
                            ],
                        },
                        {
                            "id": "sharpen",
                            "name": "锐化",
                            "params": [
                                {"name": "amount", "type": "number", "min": 0, "max": 5, "step": 0.1, "default": 1.5}
                            ],
                        },
                    ],
                },
            ],
        },
        {
            "id": "open3d",
            "name": "Open3D",
            "enabled": False,
            "modules": [],
        },
    ]
}


def get_catalog() -> dict:
    payload = deepcopy(CATALOG)
    for library in payload["libraries"]:
        for module in library.get("modules", []):
            for algorithm in module.get("algorithms", []):
                algorithm["snippet_available"] = algorithm["id"] in ALGORITHM_SNIPPETS
    return payload
