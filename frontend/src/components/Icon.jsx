// Minimal hand-rolled icon set (stroke-based, 24x24, currentColor) so the UI
// doesn't depend on an external icon package or CDN at demo time.
const PATHS = {
  user: (
    <>
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c0-3.5 3-6 7-6s7 2.5 7 6" />
    </>
  ),
  pill: (
    <>
      <rect x="3.5" y="9.5" width="17" height="7" rx="3.5" transform="rotate(-35 12 13)" />
      <line x1="12" y1="9" x2="15" y2="12" />
    </>
  ),
  flask: (
    <>
      <path d="M9 3h6" />
      <path d="M10 3v6l-5.2 9A2 2 0 0 0 6.5 21h11a2 2 0 0 0 1.7-3L14 9V3" />
      <path d="M7.5 15h9" />
    </>
  ),
  chart: (
    <>
      <path d="M4 20V10" />
      <path d="M10 20V4" />
      <path d="M16 20v-7" />
      <path d="M3 20h18" />
    </>
  ),
  checkCircle: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M8.5 12.5l2.3 2.3L16 10" />
    </>
  ),
  alertTriangle: (
    <>
      <path d="M12 4 2.5 20h19L12 4z" />
      <line x1="12" y1="10" x2="12" y2="14.5" />
      <circle cx="12" cy="17.3" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  alertOctagon: (
    <>
      <path d="M7.5 3h9L21 7.5v9L16.5 21h-9L3 16.5v-9L7.5 3z" />
      <line x1="12" y1="8" x2="12" y2="12.5" />
      <circle cx="12" cy="15.3" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  helpCircle: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-1 .5-1.3 1-1.3 2.2" />
      <circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  chevronDown: <polyline points="6 9 12 15 18 9" />,
  activity: <polyline points="2.5 13 7.5 13 10 7 14.5 19 17 13 21.5 13" />,
  shield: <path d="M12 3l7 3v6c0 4.8-3 8.3-7 9.5-4-1.2-7-4.7-7-9.5V6l7-3z" />,
  database: (
    <>
      <ellipse cx="12" cy="5.5" rx="7.5" ry="2.8" />
      <path d="M4.5 5.5v6c0 1.6 3.4 2.8 7.5 2.8s7.5-1.2 7.5-2.8v-6" />
      <path d="M4.5 11.5v6c0 1.6 3.4 2.8 7.5 2.8s7.5-1.2 7.5-2.8v-6" />
    </>
  ),
  link: (
    <>
      <path d="M9.5 14.5 14.5 9.5" />
      <path d="M11 7.5l1.3-1.3a3.4 3.4 0 0 1 4.8 4.8L15.8 12.3" />
      <path d="M13 16.5l-1.3 1.3a3.4 3.4 0 0 1-4.8-4.8L8.2 11.7" />
    </>
  ),
  dna: (
    <>
      <path d="M6 3c0 6 12 12 12 18" />
      <path d="M18 3c0 6-12 12-12 18" />
      <line x1="7.5" y1="7" x2="16.5" y2="7" />
      <line x1="7.5" y1="17" x2="16.5" y2="17" />
    </>
  ),
  filter: <polygon points="4 4 20 4 14 12.5 14 19 10 21 10 12.5" />,
  kidney: (
    <>
      <path d="M9 4c-3 0-5 3-5 7.5S6 20 9.5 20c2 0 2.5-1.8 2-3.5-1-3 1-4 3-2.5 2 1.5 3.5-.5 3.5-3.5C18 6 14 4 11.5 4 10.6 4 9.8 4.1 9 4z" />
    </>
  ),
  flow: (
    <>
      <circle cx="6" cy="5" r="2.3" />
      <circle cx="18" cy="12" r="2.3" />
      <circle cx="6" cy="19" r="2.3" />
      <path d="M8 6l8 4.5" />
      <path d="M16 13.5L8 18" />
    </>
  ),
  brain: (
    <>
      <path d="M9 4.5a2.5 2.5 0 0 0-2.5 2.5v.3A2.7 2.7 0 0 0 5 9.8v1.4a2.7 2.7 0 0 0 1 2.1v.7a3 3 0 0 0 3 3h.5" />
      <path d="M15 4.5a2.5 2.5 0 0 1 2.5 2.5v.3A2.7 2.7 0 0 1 19 9.8v1.4a2.7 2.7 0 0 1-1 2.1v.7a3 3 0 0 1-3 3h-.5" />
      <path d="M9.5 4.6V18" />
      <path d="M14.5 4.6V18" />
    </>
  ),
  play: <polygon points="7 4 19 12 7 20" />,
  arrowRight: (
    <>
      <line x1="4" y1="12" x2="19" y2="12" />
      <polyline points="13 6 19 12 13 18" />
    </>
  ),
  liver: (
    <>
      <path d="M4 10c1-3 5-6 10-5s7 4 6 8-5 6-10 6-7-5-6-9z" />
    </>
  ),
};

export default function Icon({ name, size = 18, strokeWidth = 1.8, className = "" }) {
  const content = PATHS[name];
  if (!content) return null;
  return (
    <svg
      className={`icon ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {content}
    </svg>
  );
}
