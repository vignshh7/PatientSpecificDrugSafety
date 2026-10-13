import { useState } from "react";
import Icon from "./Icon.jsx";

export default function EvidenceCard({ chunk }) {
  const [open, setOpen] = useState(false);
  const isLabel = chunk.source_type === "label";
  return (
    <div className="evidence-card">
      <button className="evidence-card-header" onClick={() => setOpen(!open)}>
        <span className={`source-pill source-${isLabel ? "label" : "literature"}`}>
          {chunk.source_name}
        </span>
        <span className="evidence-section">{chunk.section}</span>
        <span className="evidence-drug">{chunk.drug_name}</span>
        {chunk.score !== undefined && (
          <span className="evidence-score">score {chunk.score.toFixed(2)}</span>
        )}
        <span className="evidence-toggle" style={{ transform: open ? "rotate(180deg)" : "none" }}>
          <Icon name="chevronDown" size={16} />
        </span>
      </button>
      {open && (
        <div className="evidence-card-body">
          <p>{chunk.text}</p>
          <div className="evidence-meta">
            <span className="mono">{chunk.chunk_id}</span>
            <span>published: {chunk.publication_date}</span>
          </div>
          <a href={chunk.url} target="_blank" rel="noreferrer" className="source-link">
            <Icon name="link" size={14} /> Open on {chunk.source_name}
          </a>
        </div>
      )}
    </div>
  );
}
