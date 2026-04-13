import type { AlgorithmDef, ModuleDef } from "../types";

type Props = {
  modules: ModuleDef[];
  moduleId: string;
  algorithmId: string;
  onModuleChange: (moduleId: string) => void;
  onAlgorithmChange: (algorithmId: string) => void;
};

export function AlgorithmSelector({
  modules,
  moduleId,
  algorithmId,
  onModuleChange,
  onAlgorithmChange
}: Props) {
  const activeModule =
    modules.find((m) => m.id === moduleId) ??
    modules[0] ?? { algorithms: [] as AlgorithmDef[] };

  return (
    <>
      <label>
        模块
        <select value={moduleId} onChange={(e) => onModuleChange(e.target.value)}>
          {modules.map((module) => (
            <option key={module.id} value={module.id}>
              {module.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        算法
        <select value={algorithmId} onChange={(e) => onAlgorithmChange(e.target.value)}>
          {activeModule.algorithms.map((algorithm) => (
            <option key={algorithm.id} value={algorithm.id}>
              {algorithm.name}
            </option>
          ))}
        </select>
      </label>
    </>
  );
}
