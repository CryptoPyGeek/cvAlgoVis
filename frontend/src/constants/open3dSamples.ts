export type Open3DSampleDef = {
  id: string;
  label: string;
  file: string;
  targetFile?: string;
  description: string;
  recommendedAlgorithms: string[];
};

const samplePath = (file: string) => `${import.meta.env.BASE_URL}samples/${file}`;

export const OPEN3D_SAMPLES: Open3DSampleDef[] = [
  {
    id: "registration-pair",
    label: "配准点云对",
    file: samplePath("open3d-registration-source.ply"),
    targetFile: samplePath("open3d-registration-target.ply"),
    description: "成对的源点云与目标点云，差异较小，适合演示基础 ICP、刚体变换和配准质量评估。",
    recommendedAlgorithms: [
      "transform_point_cloud",
      "registration_icp_point_to_point",
      "registration_icp_point_to_plane",
      "registration_colored_icp",
      "evaluate_registration",
      "compute_point_cloud_distance"
    ]
  },
  {
    id: "registration-pair-rotated",
    label: "旋转错位配准对",
    file: samplePath("open3d-registration-rotated-source.ply"),
    targetFile: samplePath("open3d-registration-rotated-target.ply"),
    description: "带旋转和更明显错位的点云对，更适合观察 FPFH、全局粗配准与一体化工作流的差异。",
    recommendedAlgorithms: [
      "compute_fpfh_feature",
      "registration_ransac_based_on_feature_matching",
      "registration_fast_based_on_feature_matching",
      "registration_ransac_then_icp_point_to_plane",
      "registration_fast_then_icp_point_to_plane",
      "registration_icp_point_to_plane",
      "registration_colored_icp"
    ]
  },
  {
    id: "plane-outliers",
    label: "平面 + 离群点",
    file: samplePath("open3d-plane-outliers.ply"),
    description: "规则平面上带少量离群点，适合观察平面分割和统计离群点去除。",
    recommendedAlgorithms: [
      "segment_plane",
      "remove_statistical_outlier",
      "remove_radius_outlier",
      "segment_plane_outliers",
      "cluster_dbscan",
      "compute_mahalanobis_distance"
    ]
  },
  {
    id: "cube-lattice",
    label: "立方体格点",
    file: samplePath("open3d-cube-lattice.ply"),
    description: "规则体素感较强，适合直观看到体素下采样后的结构变化。",
    recommendedAlgorithms: ["voxel_down_sample", "estimate_normals", "uniform_down_sample", "compute_convex_hull"]
  },
  {
    id: "layered-ramp",
    label: "分层斜坡",
    file: samplePath("open3d-layered-ramp.ply"),
    description: "带层次和斜率变化，适合展示法线估计与下采样后的形态差异。",
    recommendedAlgorithms: [
      "estimate_normals",
      "voxel_down_sample",
      "crop_axis_aligned_bbox",
      "get_axis_aligned_bounding_box",
      "get_oriented_bounding_box"
    ]
  },
  {
    id: "sphere-shell",
    label: "球壳点云",
    file: samplePath("open3d-sphere-shell.ply"),
    description: "曲面结构更明显，适合观察法线方向和稀疏化效果。",
    recommendedAlgorithms: [
      "estimate_normals",
      "voxel_down_sample",
      "random_down_sample",
      "hidden_point_removal",
      "compute_nearest_neighbor_distance"
    ]
  }
];
