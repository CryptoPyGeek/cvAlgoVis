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
  ransac_n: "RANSAC 每次拟合平面抽样的点数。",
  num_iterations: "RANSAC 最大迭代次数。"
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
