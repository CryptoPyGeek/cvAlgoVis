type Props = {
  sourceImage: string;
  resultImage: string;
  statusText: string;
  elapsedMs: number;
};

export function ImagePreviewPanel({
  sourceImage,
  resultImage,
  statusText,
  elapsedMs
}: Props) {
  return (
    <section className="panel preview-panel">
      <div className="panel-title">图像效果展示区域</div>
      <div className="preview-grid">
        <div className="image-card">
          <div className="image-title">原始图像</div>
          <div className="image-wrap">
            <img src={sourceImage} alt="source" />
          </div>
        </div>
        <div className="image-card">
          <div className="image-title">处理后图像</div>
          <div className="image-wrap">
            <img src={resultImage} alt="result" />
          </div>
        </div>
      </div>
      <div className="preview-meta">
        <span>{statusText}</span>
        <span>处理耗时：{elapsedMs} ms</span>
      </div>
    </section>
  );
}
