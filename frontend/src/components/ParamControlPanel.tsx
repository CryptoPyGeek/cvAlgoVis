import type { ParamDef } from "../types";
import { wheelAdjust } from "../hooks/useWheelAdjust";

type Props = {
  params: ParamDef[];
  values: Record<string, number>;
  onChange: (name: string, value: number) => void;
};

export function ParamControlPanel({ params, values, onChange }: Props) {
  return (
    <section className="panel control-panel">
      <div className="panel-title">数值调整区域（支持滚轮）</div>
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
        <div className="hint">提示：参数区支持滚轮微调。</div>
      </div>
    </section>
  );
}
