import { useState } from "react";

type Props = {
  snippet: string;
  highlightedHtml: string;
  pygmentsCss: string;
  highlightAvailable: boolean;
  highlightMessage: string;
  onCopy: () => void;
};

function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

export function CodePanel({
  snippet,
  highlightedHtml,
  pygmentsCss,
  highlightAvailable,
  highlightMessage,
  onCopy
}: Props) {
  const [fontSize, setFontSize] = useState(14);
  const html = highlightedHtml || `<span>${escapeHtml(snippet)}</span>`;
  const statusText = highlightAvailable
    ? `高亮状态：已启用（Pygments）${highlightMessage ? `｜${highlightMessage}` : ""}`
    : `高亮状态：降级模式${highlightMessage ? `｜${highlightMessage}` : ""}`;

  return (
    <section className="panel code-panel">
      <div className="panel-title">代码区</div>
      <div className="panel-actions">
        <div className="font-size-tools">
          <span className="font-size-label">字号</span>
          <button
            className="small ghost font-size-btn"
            onClick={() => setFontSize((v) => Math.max(11, v - 1))}
          >
            A-
          </button>
          <button
            className="small ghost font-size-btn"
            onClick={() => setFontSize((v) => Math.min(22, v + 1))}
          >
            A+
          </button>
          <span className="font-size-value">{fontSize}px</span>
        </div>
        <button className="small" onClick={onCopy}>
          复制
        </button>
      </div>
      <div className={`hint ${highlightAvailable ? "highlight-ok" : "highlight-off"}`}>
        {statusText}
      </div>
      <div
        className="code-highlight code-block"
        style={{ fontSize }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
      {pygmentsCss ? <style>{pygmentsCss}</style> : null}
    </section>
  );
}
