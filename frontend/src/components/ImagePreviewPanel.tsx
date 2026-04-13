type Props = {
  title: string;
  image: string;
  metaLeft?: string;
  metaRight?: string;
};

export function ImagePreviewPanel({
  title,
  image,
  metaLeft,
  metaRight
}: Props) {
  return (
    <section className="panel preview-panel">
      <div className="panel-title">{title}</div>
      <div className="image-card">
        <div className="image-wrap">
          <img src={image} alt={title} />
        </div>
      </div>
      <div className="preview-meta">
        <span>{metaLeft ?? ""}</span>
        <span>{metaRight ?? ""}</span>
      </div>
    </section>
  );
}
