import type { Open3DProcessResponse } from "../types";

type Props = {
  algorithmId: string;
  result: Open3DProcessResponse;
  paramsSnapshot: Record<string, number>;
  isFresh: boolean;
  sampleDescription?: string;
  showDifferenceHint: boolean;
  errorSummary?: {
    minError: number;
    maxError: number;
    meanError: number;
    p95Error: number;
  } | null;
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

function qualityLabel(fitness: unknown, rmse: unknown): string {
  const fit = typeof fitness === "number" ? fitness : null;
  const err = typeof rmse === "number" ? rmse : null;
  if (fit !== null) {
    if (fit >= 0.95) return "优";
    if (fit >= 0.8) return "良";
    if (fit >= 0.6) return "一般";
  }
  if (err !== null) {
    if (err <= 0.02) return "优";
    if (err <= 0.05) return "良";
  }
  return "待调整";
}

export function Open3DRegistrationSummary({
  algorithmId,
  result,
  paramsSnapshot,
  isFresh,
  sampleDescription,
  showDifferenceHint,
  errorSummary
}: Props) {
  const stats = result.stats;
  const hasWorkflowMetrics = "coarse_fitness" in stats || "refined_fitness" in stats;
  const hasBasicMetrics = "fitness" in stats || "inlier_rmse" in stats;
  const quality = qualityLabel(stats.refined_fitness ?? stats.fitness, stats.refined_inlier_rmse ?? stats.inlier_rmse);

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
        <div className="registration-summary-item">
          <span className="registration-summary-label">质量等级</span>
          <strong>{quality}</strong>
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
            <div className="registration-summary-note registration-summary-item-wide">
              阶段改进：fitness {metricValue(stats.coarse_fitness)} -&gt; {metricValue(stats.refined_fitness)}，rmse{" "}
              {metricValue(stats.coarse_inlier_rmse)} -&gt; {metricValue(stats.refined_inlier_rmse)}
            </div>
          </>
        ) : null}
        {errorSummary ? (
          <>
            <div className="registration-summary-item">
              <span className="registration-summary-label">mean_error</span>
              <strong>{metricValue(errorSummary.meanError)}</strong>
            </div>
            <div className="registration-summary-item">
              <span className="registration-summary-label">p95_error</span>
              <strong>{metricValue(errorSummary.p95Error)}</strong>
            </div>
            <div className="registration-summary-item">
              <span className="registration-summary-label">min_error</span>
              <strong>{metricValue(errorSummary.minError)}</strong>
            </div>
            <div className="registration-summary-item">
              <span className="registration-summary-label">max_error</span>
              <strong>{metricValue(errorSummary.maxError)}</strong>
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
