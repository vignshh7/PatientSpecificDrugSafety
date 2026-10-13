import { useState } from "react";

export default function TagInput({ values, onChange, placeholder }) {
  const [draft, setDraft] = useState("");

  const addTag = () => {
    const v = draft.trim();
    if (v && !values.includes(v)) {
      onChange([...values, v]);
    }
    setDraft("");
  };

  const removeTag = (tag) => onChange(values.filter((v) => v !== tag));

  return (
    <div className="pill-input">
      {values.map((v) => (
        <span className="pill" key={v}>
          {v}
          <button type="button" onClick={() => removeTag(v)}>
            ×
          </button>
        </span>
      ))}
      <input
        type="text"
        value={draft}
        placeholder={placeholder}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            addTag();
          }
        }}
        onBlur={addTag}
      />
    </div>
  );
}
