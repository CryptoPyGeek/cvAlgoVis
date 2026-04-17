import type { Open3DProcessResponse } from "../types";

type Props = {
  algorithmId: string;
  result: Open3DProcessResponse;
  paramsSnapshot: Record<string, number>;
  isFresh: boolean;
  sampleDescription?: string;
  showDifferenceHint: boolean;
};

function metricValue(value: unknown): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }
  return value == null ? "-" : String(value);
}

function summarizeParams(params: Record<string, number>): string {
  const entries = Object.entries(params);
  if (entries.length === 0) return "无参数";
  return entries
    .slice(0, 6)
    .map(([key, value]) => `${key}=${Number.isInteger(value) ? value : value.toFixed(4)}`)
    .join(", ");
}

export function Open3DRegistrationSummary({
  algorithmId,
  result,
  paramsSnapshot,
  isFresh,
  sampleDescription,
  showDifferenceHint
}: Props) {
  const stats = result.stats;
  const hasWorkflowMetrics = "coarse_fitness" in stats || "refined_fitness" in stats;
  const hasBasicMetrics = "fitness" in stats || "inlier_rmse" in stats;

  return (
    <section className="registration-summary panel">
      <div className="registration-summary-title">配准结果摘要</div>
      <div className="registration-summary-grid">
        <div className="registration-summary-item">
          <span className="registration-summary-label">当前算法</span>
          <strong>{algorithmId}</strong>
        </div>
        <div className="registration-summary-item">
          <span className="registration-summary-label">结果状态</span>
          <strong>{isFresh ? "已与最新参数同步" : "当前结果不是最新参数"}</strong>
        </div>
        <div className="registration-summary-item registration-summary-item-wide">
          <span className="registration-summary-label">关键参数</span>
          <strong>{summarizeParams(paramsSnapshot)}</strong>
        </div>
        {hasBasicMetrics ? (
          <>
            <div className="registration-summary-item">
              <span className="registration-summary-label">fitness</span>
              <strong>{metricValue(stats.fitness)}</strong>
            </div>
            <div className="registration-summary-item">
              <span className="registration-summary-label">inlier_rmse</span>
              <strong>{metricValue(stats.inlier_rmse)}</strong>
            </div>
          </>
        ) : null}
        {hasWorkflowMetrics ? (
          <>
            <div className="registration-summary-item">
              <span className="registration-summary-label">coarse_fitness</span>
              <strong>{metricValue(stats.coarse_fitness)}</strong>
            </div>
            <div className="registration-summary-item">
              <span className="registration-summary-label">refined_fitness</span>
              <strong>{metricValue(stats.refined_fitness)}</strong>
            </div>
            <div className="registration-summary-item">
              <span className="registration-summary-label">coarse_rmse</span>
              <strong>{metricValue(stats.coarse_inlier_rmse)}</strong>
            </div>
            <div className="registration-summary-item">
              <span className="registration-summary-label">refined_rmse</span>
              <strong>{metricValue(stats.refined_inlier_rmse)}</strong>
            </div>
          </>
        ) : null}
        {showDifferenceHint ? (
          <div className="registration-summary-note registration-summary-item-wide">
            当前样例较简单，不同配准算法可能都会得到接近结果。建议切换更复杂的配准样例观察差异。
          </div>
        ) : null}
        {sampleDescription ? (
          <div className="registration-summary-note registration-summary-item-wide">
            当前样例说明：{sampleDescription}
          </div>
        ) : null}
      </div>
    </section>
  );
}
