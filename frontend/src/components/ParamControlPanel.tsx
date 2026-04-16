import type { ParamDef } from "../types";
import { wheelAdjust } from "../hooks/useWheelAdjust";

type Props = {
  params: ParamDef[];
  values: Record<string, number>;
  onChange: (name: string, value: number) => void;
};

const PARAM_HINTS: Record<string, string> = {
  threshold1: "低阈值：越低越容易检测到弱边缘。",
  threshold2: "高阈值：越高越偏向保留强边缘。",
  aperture_size: "Sobel 核大小：影响边缘提取细节。",
  kernel_size: "卷积核大小：控制平滑/形态学作用范围。",
  sigma: "高斯标准差：控制模糊强度。",
  sigma_s: "HDR 空间平滑参数。",
  sigma_r: "HDR 色彩范围参数。",
  amount: "锐化强度。",
  angle: "旋转角度（度）。",
  scale: "缩放倍数（1 为原始尺寸）。",
  tx: "X 方向平移量。",
  ty: "Y 方向平移量。",
  block_size: "自适应阈值窗口大小。",
  c: "自适应阈值偏置常量。",
  nfeatures: "目标特征点数量上限。",
  template_ratio: "模板大小占原图比例。",
  voxel_size: "体素边长：越大，下采样越明显。",
  radius: "法线估计的邻域搜索半径。",
  max_nn: "法线估计使用的最近邻点数量上限。",
  nb_neighbors: "统计离群点分析时的邻域点数。",
  std_ratio: "离群点判定的标准差比例阈值。",
  distance_threshold: "点到平面的最大允许距离。",
  num_iterations: "RANSAC 最大迭代次数。",
  every_k_points: "均匀下采样保留步长，越大保留的点越少。",
  sampling_ratio: "随机保留点比例，越小采样越稀疏。",
  nb_points: "半径离群点去除要求的最少邻居点数。",
  min_x: "包围盒最小 X 边界。",
  min_y: "包围盒最小 Y 边界。",
  min_z: "包围盒最小 Z 边界。",
  max_x: "包围盒最大 X 边界。",
  max_y: "包围盒最大 Y 边界。",
  max_z: "包围盒最大 Z 边界。",
  eps: "DBSCAN 聚类半径，越大越容易合并邻近点簇。",
  min_points: "形成有效聚类所需的最少点数。",
  camera_x: "隐藏点移除观察点的 X 坐标。",
  camera_y: "隐藏点移除观察点的 Y 坐标。",
  camera_z: "隐藏点移除观察点的 Z 坐标。",
  robust: "是否启用鲁棒有向包围盒估计。",
  joggle_inputs: "是否对输入点做微扰以避免凸包退化。",
  tz: "Z 方向平移量。",
  roll_deg: "绕 X 轴旋转角度。",
  pitch_deg: "绕 Y 轴旋转角度。",
  yaw_deg: "绕 Z 轴旋转角度。",
  max_correspondence_distance: "源点与目标点建立对应关系的最大距离。",
  max_iteration: "ICP 迭代次数上限。",
  normal_radius: "点到面 ICP 中法线估计的邻域半径。",
  normal_max_nn: "点到面 ICP 中法线估计的最大邻居数量。",
  feature_radius: "FPFH 特征搜索半径。",
  feature_max_nn: "FPFH 特征搜索的最大邻居数。",
  ransac_n: "RANSAC 每次采样用于估计变换的点数。",
  iteration_number: "快速全局配准的迭代次数。",
  lambda_geometric: "彩色 ICP 中几何一致性相对颜色一致性的权重。",
  coarse_max_iteration: "粗配准阶段的最大迭代次数。",
  icp_max_iteration: "精配准阶段 ICP 的最大迭代次数。"
};

function paramHint(param: ParamDef): string {
  if (param.description) return param.description;
  return PARAM_HINTS[param.name] ?? "用于控制算法处理强度或范围。";
}

export function ParamControlPanel({ params, values, onChange }: Props) {
  return (
    <section className="panel control-panel">
      <div className="panel-title">参数设置区</div>
      <div>
        {params.map((param) => (
          <div className="control-item" key={param.name}>
            <div className="row">
              <strong>{param.name}</strong>
              <input
                type="number"
                value={values[param.name] ?? param.default}
                min={param.min}
                max={param.max}
                step={param.step}
                onChange={(e) => onChange(param.name, Number(e.target.value))}
                onWheel={(e) => {
                  e.preventDefault();
                  const next = wheelAdjust(
                    values[param.name] ?? param.default,
                    param.step,
                    param.min,
                    param.max,
                    e.deltaY
                  );
                  onChange(param.name, next);
                }}
              />
            </div>
            <div className="param-hint">{paramHint(param)}</div>
            <input
              type="range"
              value={values[param.name] ?? param.default}
              min={param.min}
              max={param.max}
              step={param.step}
              onChange={(e) => onChange(param.name, Number(e.target.value))}
              onWheel={(e) => {
                e.preventDefault();
                const next = wheelAdjust(
                  values[param.name] ?? param.default,
                  param.step,
                  param.min,
                  param.max,
                  e.deltaY
                );
                onChange(param.name, next);
              }}
            />
          </div>
        ))}
        <div className="hint">提示：滑块、输入框、鼠标滚轮都可调参。</div>
      </div>
    </section>
  );
}
