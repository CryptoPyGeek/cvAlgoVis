import { useMemo, useState } from "react";

type Props = {
  snippet: string;
  onCopy: () => void;
};

const KEYWORDS = [
  "def",
  "return",
  "for",
  "in",
  "if",
  "else",
  "import",
  "from",
  "class",
  "while",
  "try",
  "except",
  "True",
  "False",
  "None"
];

function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function highlightPython(code: string): string {
  const escaped = escapeHtml(code);
  const withComments = escaped.replace(/(#.*)$/gm, '<span class="tok-comment">$1</span>');
  const withStrings = withComments.replace(
    /(".*?"|'.*?')/g,
    '<span class="tok-string">$1</span>'
  );
  return KEYWORDS.reduce((acc, kw) => {
    const re = new RegExp(`\\b${kw}\\b`, "g");
    return acc.replace(re, `<span class="tok-keyword">${kw}</span>`);
  }, withStrings);
}

export function CodePanel({ snippet, onCopy }: Props) {
  const [fontSize, setFontSize] = useState(13);
  const highlighted = useMemo(() => highlightPython(snippet), [snippet]);

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
        dangerouslySetInnerHTML={{ __html: highlighted }}
      />
    </section>
  );
}
