function SourceCard({ source }) {
  return (
    <div className="source-card">
      <div className="source-icon">📄</div>

      <div>
        <strong>{source.title}</strong>
        <p>{source.description}</p>
      </div>

      <span className="source-arrow">↗</span>
    </div>
  );
}

export default SourceCard;