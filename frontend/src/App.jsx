import { NavLink, Route, Routes } from "react-router-dom";
import PatientInput from "./pages/PatientInput.jsx";
import AnalysisResult from "./pages/AnalysisResult.jsx";
import EvidenceExplorer from "./pages/EvidenceExplorer.jsx";
import Icon from "./components/Icon.jsx";
import ScrollToTop from "./components/ScrollToTop.jsx";
import "./App.css";

const NAV_ITEMS = [
  { to: "/", end: true, label: "Patient Input" },
  { to: "/result", label: "Analysis Result" },
  { to: "/evidence", label: "Evidence Explorer" },
];

function App() {
  return (
    <div className="app-shell">
      <ScrollToTop />
      <header className="app-header">
        <div className="app-title">
          <h1>Patient-Specific Drug Safety RAG</h1>
          <p className="app-subtitle">
            Evidence-grounded, patient-context-aware medication safety assessment — research prototype
          </p>
        </div>
        <nav className="app-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end}>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<PatientInput />} />
          <Route path="/result" element={<AnalysisResult />} />
          <Route path="/evidence" element={<EvidenceExplorer />} />
        </Routes>
      </main>

      <footer className="app-footer">
        <Icon name="alertTriangle" size={14} />
        Research prototype. Information is evidence-grounded and does not replace evaluation by a
        qualified healthcare professional. This system does not diagnose, prescribe, or guarantee
        that any patient will experience a particular effect.
      </footer>
    </div>
  );
}

export default App;
