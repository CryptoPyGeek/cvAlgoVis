ALGORITHM_SNIPPETS = {
    "bgr_to_rgb": """result = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)""",
    "bgr_to_hsv": """hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)""",
    "bgr_to_yuv": """yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
result = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)""",
    "bgr_to_lab": """lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)""",
    "pseudo_hdr": """enhanced = cv2.detailEnhance(image, sigma_s=sigma_s, sigma_r=sigma_r)
result = gamma_correct(enhanced, gamma)""",
    "affine_transform": """M = np.float32([[1, shear, tx], [shear, 1, ty]])
result = cv2.warpAffine(image, M, (w, h))""",
    "perspective_transform": """M = cv2.getPerspectiveTransform(src_pts, dst_pts)
result = cv2.warpPerspective(image, M, (w, h))""",
    "rotate": """M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
result = cv2.warpAffine(image, M, (w, h))""",
    "scale": """resized = cv2.resize(image, None, fx=scale, fy=scale)
result = cv2.resize(resized, (w, h))""",
    "translate": """M = np.float32([[1,0,tx],[0,1,ty]])
result = cv2.warpAffine(image, M, (w, h))""",
    "skew": """M = np.float32([[1,sx,0],[sy,1,0]])
result = cv2.warpAffine(image, M, (w, h))""",
    "canny": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, threshold1, threshold2, apertureSize=aperture_size)
result = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)""",
    "threshold_binary": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, threshold, max_value, cv2.THRESH_BINARY)
result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)""",
    "adaptive_threshold": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)""",
    "global_threshold": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)""",
    "otsu_threshold": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)""",
    "erode": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.erode(image, kernel, iterations=iterations)""",
    "dilate": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.dilate(image, kernel, iterations=iterations)""",
    "morph_open": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)""",
    "morph_close": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)""",
    "morph_gradient": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)""",
    "morph_blackhat": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, kernel)""",
    "morph_whitehat": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, kernel)""",
    "morph_tophat": """kernel = np.ones((kernel_size, kernel_size), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, kernel)""",
    "morph_bottomhat": """closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
result = cv2.subtract(closed, image)""",
    "gaussian_blur": """result = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma)""",
    "median_blur": """result = cv2.medianBlur(image, kernel_size)""",
    "mean_blur": """result = cv2.blur(image, (kernel_size, kernel_size))""",
    "bilateral_blur": """result = cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)""",
    "laplacian": """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=kernel_size)
result = cv2.cvtColor(normalize(np.abs(lap)), cv2.COLOR_GRAY2BGR)""",
    "watershed_segmentation": """markers = build_markers(image)
markers = cv2.watershed(image, markers)
result[markers == -1] = (0, 0, 255)""",
    "grabcut_segmentation": """mask = np.zeros(image.shape[:2], np.uint8)
cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
result = image * np.where((mask==2)|(mask==0),0,1)[:, :, None]""",
    "harris_corners": """dst = cv2.cornerHarris(np.float32(gray), 2, 3, 0.04)
result[dst > 0.01 * dst.max()] = (0, 0, 255)""",
    "shi_tomasi_corners": """corners = cv2.goodFeaturesToTrack(gray, maxCorners=max_corners, qualityLevel=0.01, minDistance=5)
for c in corners: cv2.circle(result, tuple(c), 3, (0,255,0), -1)""",
    "fast_corners": """detector = cv2.FastFeatureDetector_create(threshold=threshold)
kp = detector.detect(gray, None)
result = cv2.drawKeypoints(image, kp, None)""",
    "sift_features": """detector = cv2.SIFT_create(nfeatures=nfeatures)
kp = detector.detect(gray, None)
result = cv2.drawKeypoints(image, kp, None)""",
    "surf_features": """detector = cv2.xfeatures2d.SURF_create(hessianThreshold=hessian)
kp = detector.detect(gray, None)
result = cv2.drawKeypoints(image, kp, None)""",
    "orb_features": """detector = cv2.ORB_create(nfeatures=nfeatures)
kp = detector.detect(gray, None)
result = cv2.drawKeypoints(image, kp, None)""",
    "lbp_features": """lbp = local_binary_pattern(gray)
result = cv2.applyColorMap(lbp, cv2.COLORMAP_JET)""",
    "hog_features": """hog = cv2.HOGDescriptor()
features = hog.compute(cv2.resize(gray, (64, 128)))
result = visualize_hog(features)""",
    "knn_match": """matches = bf.knnMatch(des1, des2, k=2)
good = [m for m,n in matches if m.distance < 0.75 * n.distance]
result = cv2.drawMatchesKnn(img1, kp1, img2, kp2, [[m] for m in good], None)""",
    "bf_match": """matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = sorted(matcher.match(des1, des2), key=lambda x: x.distance)
result = cv2.drawMatches(img1, kp1, img2, kp2, matches[:60], None)""",
    "flann_match": """flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1, des2, k=2)
result = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good_matches, None)""",
    "template_match": """response = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
_, _, _, max_loc = cv2.minMaxLoc(response)
cv2.rectangle(result, max_loc, (max_loc[0]+tw, max_loc[1]+th), (0,255,255), 2)""",
    "template_match_homology": """matches = bf.match(des1, des2)
H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
proj = cv2.perspectiveTransform(corners, H)""",
    "sharpen": """kernel = np.array([[0, -1, 0], [-1, 5 + amount, -1], [0, -1, 0]], dtype=np.float32)
result = cv2.filter2D(image, ddepth=-1, kernel=kernel)""",
    "voxel_down_sample": """pcd = o3d.io.read_point_cloud(path)
down = pcd.voxel_down_sample(voxel_size=voxel_size)""",
    "estimate_normals": """pcd = o3d.io.read_point_cloud(path)
pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn)
)""",
    "remove_statistical_outlier": """pcd = o3d.io.read_point_cloud(path)
filtered, ind = pcd.remove_statistical_outlier(
    nb_neighbors=nb_neighbors, std_ratio=std_ratio
)""",
    "uniform_down_sample": """pcd = o3d.io.read_point_cloud(path)
down = pcd.uniform_down_sample(every_k_points=every_k_points)""",
    "random_down_sample": """pcd = o3d.io.read_point_cloud(path)
down = pcd.random_down_sample(sampling_ratio=sampling_ratio)""",
    "remove_radius_outlier": """pcd = o3d.io.read_point_cloud(path)
filtered, ind = pcd.remove_radius_outlier(
    nb_points=nb_points, radius=radius
)""",
    "crop_axis_aligned_bbox": """pcd = o3d.io.read_point_cloud(path)
bbox = o3d.geometry.AxisAlignedBoundingBox(
    min_bound=[min_x, min_y, min_z],
    max_bound=[max_x, max_y, max_z],
)
cropped = pcd.crop(bbox)""",
    "segment_plane": """pcd = o3d.io.read_point_cloud(path)
plane_model, inliers = pcd.segment_plane(
    distance_threshold=distance_threshold,
    ransac_n=ransac_n,
    num_iterations=num_iterations,
)""",
}
