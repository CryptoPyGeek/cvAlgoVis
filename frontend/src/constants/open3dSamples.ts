export type Open3DSampleDef = {
  id: string;
  label: string;
  file: string;
  description: string;
  recommendedAlgorithms: string[];
};

const samplePath = (file: string) => `${import.meta.env.BASE_URL}samples/${file}`;

export const OPEN3D_SAMPLES: Open3DSampleDef[] = [
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
    recommendedAlgorithms: ["estimate_normals", "voxel_down_sample", "random_down_sample", "hidden_point_removal"]
  }
];
