import Icon from "./Icon.jsx";

const LABELS = {
  lower_concern: "Lower contextual concern",
  moderate_concern: "Moderate contextual concern",
  higher_concern: "Higher contextual concern",
  indeterminate: "Indeterminate / insufficient information",
};

const ICONS = {
  lower_concern: "checkCircle",
  moderate_concern: "alertTriangle",
  higher_concern: "alertOctagon",
  indeterminate: "helpCircle",
};

export default function RiskBadge({ category, probability }) {
  const key = category || "indeterminate";
  const cls = `risk-badge risk-${key}`;
  return (
    <span className={cls}>
      <Icon name={ICONS[key]} size={16} />
      {LABELS[key] || category}
      {probability !== null && probability !== undefined && (
        <span className="risk-badge-prob">· p={probability.toFixed(2)}</span>
      )}
    </span>
  );
}
