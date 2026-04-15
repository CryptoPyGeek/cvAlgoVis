from copy import deepcopy

from app.examples.code_snippets import ALGORITHM_SNIPPETS


def p(name: str, min_v: float, max_v: float, step: float, default: float, description: str | None = None):
    payload = {"name": name, "type": "number", "min": min_v, "max": max_v, "step": step, "default": default}
    if description:
        payload["description"] = description
    return payload


CATALOG = {
    "libraries": [
        {
            "id": "opencv",
            "name": "OpenCV",
            "enabled": True,
            "input_kind": "image",
            "modules": [
                {
                    "id": "color_intensity",
                    "name": "颜色与强度处理",
                    "algorithms": [
                        {"id": "bgr_to_rgb", "name": "RGB 转换", "params": []},
                        {"id": "bgr_to_hsv", "name": "HSV 转换", "params": []},
                        {"id": "bgr_to_yuv", "name": "YUV 转换", "params": []},
                        {"id": "bgr_to_lab", "name": "Lab 转换", "params": []},
                        {"id": "pseudo_hdr", "name": "HDR 增强", "params": [p("sigma_s", 1, 80, 1, 12), p("sigma_r", 0.01, 1, 0.01, 0.2), p("gamma", 0.5, 2.5, 0.1, 1.2)]},
                    ],
                },
                {
                    "id": "geometric_transform",
                    "name": "几何变换",
                    "algorithms": [
                        {"id": "affine_transform", "name": "仿射变换", "params": [p("tx", -100, 100, 1, 15), p("ty", -100, 100, 1, 10), p("shear", -0.5, 0.5, 0.01, 0.08)]},
                        {"id": "perspective_transform", "name": "透视变换", "params": [p("strength", 0.01, 0.3, 0.01, 0.08)]},
                        {"id": "rotate", "name": "旋转", "params": [p("angle", -180, 180, 1, 15)]},
                        {"id": "scale", "name": "缩放", "params": [p("scale", 0.2, 3, 0.05, 1.2)]},
                        {"id": "translate", "name": "平移", "params": [p("tx", -200, 200, 1, 20), p("ty", -200, 200, 1, 20)]},
                        {"id": "skew", "name": "倾斜", "params": [p("sx", -0.5, 0.5, 0.01, 0.15), p("sy", -0.5, 0.5, 0.01, 0.0)]},
                    ],
                },
                {
                    "id": "threshold_binarization",
                    "name": "阈值与二值化",
                    "algorithms": [
                        {
                            "id": "canny",
                            "name": "Canny 边缘检测",
                            "params": [
                                p("threshold1", 0, 255, 1, 80),
                                p("threshold2", 0, 255, 1, 150),
                                p("aperture_size", 3, 7, 2, 3),
                            ],
                        },
                        {
                            "id": "threshold_binary",
                            "name": "二值化",
                            "params": [
                                p("threshold", 0, 255, 1, 128),
                                p("max_value", 0, 255, 1, 255),
                            ],
                        },
                        {"id": "adaptive_threshold", "name": "自适应阈值", "params": [p("block_size", 3, 51, 2, 11), p("c", -20, 20, 1, 2)]},
                        {"id": "global_threshold", "name": "全局阈值", "params": [p("threshold", 0, 255, 1, 127)]},
                        {"id": "otsu_threshold", "name": "Otsu 阈值", "params": []},
                    ],
                },
                {
                    "id": "denoise_smooth",
                    "name": "去噪与平滑",
                    "algorithms": [
                        {
                            "id": "gaussian_blur",
                            "name": "高斯去噪",
                            "params": [
                                p("kernel_size", 1, 31, 2, 7),
                                p("sigma", 0, 20, 0.1, 1.5),
                            ],
                        },
                        {
                            "id": "median_blur",
                            "name": "中值去噪",
                            "params": [p("kernel_size", 1, 31, 2, 5)],
                        },
                        {
                            "id": "mean_blur",
                            "name": "均值去噪",
                            "params": [p("kernel_size", 1, 31, 2, 5)],
                        },
                        {
                            "id": "bilateral_blur",
                            "name": "双边去噪",
                            "params": [
                                p("diameter", 1, 31, 1, 9),
                                p("sigma_color", 1, 200, 1, 75),
                                p("sigma_space", 1, 200, 1, 75),
                            ],
                        },
                    ],
                },
                {
                    "id": "morphology",
                    "name": "形态学处理",
                    "algorithms": [
                        {"id": "erode", "name": "腐蚀", "params": [p("kernel_size", 1, 31, 2, 3), p("iterations", 1, 10, 1, 1)]},
                        {"id": "dilate", "name": "膨胀", "params": [p("kernel_size", 1, 31, 2, 3), p("iterations", 1, 10, 1, 1)]},
                        {"id": "morph_open", "name": "开运算", "params": [p("kernel_size", 1, 31, 2, 5)]},
                        {"id": "morph_close", "name": "闭运算", "params": [p("kernel_size", 1, 31, 2, 5)]},
                        {"id": "morph_gradient", "name": "形态学梯度", "params": [p("kernel_size", 1, 31, 2, 5)]},
                        {"id": "morph_blackhat", "name": "黑帽", "params": [p("kernel_size", 1, 31, 2, 9)]},
                        {"id": "morph_whitehat", "name": "白帽", "params": [p("kernel_size", 1, 31, 2, 9)]},
                        {"id": "morph_tophat", "name": "顶帽", "params": [p("kernel_size", 1, 31, 2, 9)]},
                        {"id": "morph_bottomhat", "name": "底帽", "params": [p("kernel_size", 1, 31, 2, 9)]},
                    ],
                },
                {
                    "id": "gradient_edge",
                    "name": "梯度与边缘检测",
                    "algorithms": [
                        {"id": "canny", "name": "Canny 边缘检测", "params": [p("threshold1", 0, 255, 1, 80), p("threshold2", 0, 255, 1, 150), p("aperture_size", 3, 7, 2, 3)]},
                        {"id": "laplacian", "name": "Laplacian（拉普拉斯）", "params": [p("kernel_size", 1, 31, 2, 3)]},
                    ],
                },
                {
                    "id": "segmentation",
                    "name": "图像分割",
                    "algorithms": [
                        {"id": "watershed_segmentation", "name": "分水岭算法", "params": []},
                        {"id": "grabcut_segmentation", "name": "GrabCut 算法", "params": [p("margin", 1, 120, 1, 10)]},
                    ],
                },
                {
                    "id": "feature_detection_description",
                    "name": "特征检测与描述",
                    "algorithms": [
                        {"id": "harris_corners", "name": "Harris 角点检测", "params": []},
                        {"id": "shi_tomasi_corners", "name": "Shi-Tomasi 角点检测", "params": [p("max_corners", 10, 500, 1, 120)]},
                        {"id": "fast_corners", "name": "FAST 角点检测", "params": [p("threshold", 1, 100, 1, 20)]},
                        {"id": "sift_features", "name": "SIFT 特征", "params": [p("nfeatures", 50, 1000, 10, 200)]},
                        {"id": "surf_features", "name": "SURF 特征", "params": [p("hessian", 100, 1000, 10, 400)]},
                        {"id": "orb_features", "name": "ORB 特征", "params": [p("nfeatures", 50, 1500, 10, 300)]},
                        {"id": "lbp_features", "name": "LBP 描述子", "params": []},
                        {"id": "hog_features", "name": "HOG 描述子", "params": []},
                    ],
                },
                {
                    "id": "matching_retrieval",
                    "name": "匹配与检索",
                    "algorithms": [
                        {"id": "knn_match", "name": "KNN 匹配策略", "params": [p("nfeatures", 100, 2000, 10, 400)]},
                        {"id": "bf_match", "name": "BF 匹配器", "params": [p("nfeatures", 100, 2000, 10, 400)]},
                        {"id": "flann_match", "name": "FLANN 匹配器", "params": []},
                        {"id": "template_match", "name": "模板匹配", "params": [p("template_ratio", 0.05, 0.5, 0.01, 0.2)]},
                        {"id": "template_match_homology", "name": "模板匹配 + 同源", "params": []},
                    ],
                },
                {
                    "id": "enhancement",
                    "name": "增强处理",
                    "algorithms": [
                        {"id": "sharpen", "name": "锐化", "params": [p("amount", 0, 5, 0.1, 1.5)]}
                    ],
                },
            ],
        },
        {
            "id": "open3d",
            "name": "Open3D",
            "enabled": True,
            "input_kind": "point_cloud",
            "status_note": "首版支持 ply / pcd 点云文件，结果以处理摘要与统计信息展示。",
            "modules": [
                {
                    "id": "point_cloud_basic",
                    "name": "点云基础处理",
                    "algorithms": [
                        {
                            "id": "voxel_down_sample",
                            "name": "体素下采样",
                            "params": [p("voxel_size", 0.001, 1.0, 0.001, 0.05, "体素边长，越大采样越粗。")],
                        },
                        {
                            "id": "estimate_normals",
                            "name": "法线估计",
                            "params": [
                                p("radius", 0.01, 5.0, 0.01, 0.2, "邻域搜索半径。"),
                                p("max_nn", 5, 200, 1, 30, "参与估计的最近邻点上限。"),
                            ],
                        },
                        {
                            "id": "remove_statistical_outlier",
                            "name": "统计离群点去除",
                            "params": [
                                p("nb_neighbors", 5, 200, 1, 20, "统计分析时的邻居数量。"),
                                p("std_ratio", 0.1, 5.0, 0.1, 2.0, "标准差阈值比例。"),
                            ],
                        },
                        {
                            "id": "segment_plane",
                            "name": "平面分割",
                            "params": [
                                p("distance_threshold", 0.001, 1.0, 0.001, 0.02, "点到平面的最大内点距离。"),
                                p("ransac_n", 3, 10, 1, 3, "拟合平面所需采样点数。"),
                                p("num_iterations", 10, 5000, 10, 1000, "RANSAC 迭代次数。"),
                            ],
                        },
                    ],
                }
            ],
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
