type Props = {
  snippet: string;
  onCopy: () => void;
};

export function CodePanel({ snippet, onCopy }: Props) {
  return (
    <section className="panel code-panel">
      <div className="panel-title">代码区域</div>
      <div className="panel-actions">
        <button className="small" onClick={onCopy}>
          复制
        </button>
      </div>
      <pre>{snippet}</pre>
    </section>
  );
}
