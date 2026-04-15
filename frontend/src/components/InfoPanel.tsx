type Props = {
  title: string;
  lines: string[];
  metaLeft?: string;
  metaRight?: string;
};

export function InfoPanel({ title, lines, metaLeft, metaRight }: Props) {
  return (
    <section className="panel preview-panel">
      <div className="panel-title">{title}</div>
      <div className="info-card">
        {lines.map((line, index) => (
          <div className="info-line" key={`${index}-${line}`}>
            {line}
          </div>
        ))}
      </div>
      <div className="preview-meta">
        <span>{metaLeft ?? ""}</span>
        <span>{metaRight ?? ""}</span>
      </div>
    </section>
  );
}
