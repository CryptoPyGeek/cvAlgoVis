import { useState } from "react";

type Props = {
  snippet: string;
  highlightedHtml: string;
  pygmentsCss: string;
  onCopy: () => void;
};

export function CodePanel({ snippet, highlightedHtml, pygmentsCss, onCopy }: Props) {
  const [fontSize, setFontSize] = useState(14);

  return (
    <section className="panel code-panel">
      <div className="panel-title">代码区</div>
      <div className="panel-actions">
        <button className="small ghost" onClick={() => setFontSize((v) => Math.max(11, v - 1))}>
          A-
        </button>
        <button className="small ghost" onClick={() => setFontSize((v) => Math.min(22, v + 1))}>
          A+
        </button>
        <button className="small" onClick={onCopy}>
          复制
        </button>
      </div>
      <pre
        className="code-highlight"
        style={{ fontSize }}
        dangerouslySetInnerHTML={{ __html: highlightedHtml || `<code>${snippet}</code>` }}
      />
      {pygmentsCss ? <style>{pygmentsCss}</style> : null}
    </section>
  );
}
