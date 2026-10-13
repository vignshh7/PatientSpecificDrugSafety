import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { useAppContext } from "../AppContext.jsx";
import TagInput from "../components/TagInput.jsx";
import Icon from "../components/Icon.jsx";

const EMPTY_PATIENT = {
  patient_id: "",
  age: "",
  sex: "",
  conditions: [],
  kidney: { egfr: "", creatinine: "" },
  liver: { ast: "", alt: "", bilirubin: "" },
  allergies: [],
  current_medications: [],
  pregnancy_status: "not_applicable",
  medical_history_text: "",
};

export default function PatientInput() {
  const navigate = useNavigate();
  const { setCompareResult } = useAppContext();

  const [drugs, setDrugs] = useState([]);
  const [cases, setCases] = useState([]);
  const [patient, setPatient] = useState(EMPTY_PATIENT);
  const [drugId, setDrugId] = useState("");
  const [dose, setDose] = useState("");
  const [medDraft, setMedDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useLlm, setUseLlm] = useState(true);
  const [activeCaseId, setActiveCaseId] = useState("");
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.listDrugs().then(setDrugs).catch((e) => setError(e.message));
    api.listCases().then(setCases).catch((e) => setError(e.message));
    api.health().then(setHealth).catch(() => {});
  }, []);

  const loadCase = (caseId) => {
    const c = cases.find((x) => x.case_id === caseId);
    if (!c) return;
    setPatient({
      ...EMPTY_PATIENT,
      ...c.patient,
      kidney: { egfr: "", creatinine: "", ...c.patient.kidney },
      liver: { ast: "", alt: "", bilirubin: "", ...c.patient.liver },
      conditions: c.patient.conditions || [],
      allergies: c.patient.allergies || [],
      current_medications: c.patient.current_medications || [],
    });
    setDrugId(c.drug_id);
    setDose(c.dose || "");
    setActiveCaseId(caseId);
  };

  const addMedication = () => {
    const v = medDraft.trim();
    if (v) {
      setPatient((p) => ({ ...p, current_medications: [...p.current_medications, { name: v }] }));
      setMedDraft("");
    }
  };

  const removeMedication = (name) => {
    setPatient((p) => ({
      ...p,
      current_medications: p.current_medications.filter((m) => m.name !== name),
    }));
  };

  const buildPayloadPatient = () => ({
    patient_id: patient.patient_id || null,
    age: patient.age === "" ? null : Number(patient.age),
    sex: patient.sex || null,
    conditions: patient.conditions,
    kidney: {
      egfr: patient.kidney.egfr === "" ? null : Number(patient.kidney.egfr),
      creatinine: patient.kidney.creatinine === "" ? null : Number(patient.kidney.creatinine),
    },
    liver: {
      ast: patient.liver.ast === "" ? null : Number(patient.liver.ast),
      alt: patient.liver.alt === "" ? null : Number(patient.liver.alt),
      bilirubin: patient.liver.bilirubin === "" ? null : Number(patient.liver.bilirubin),
    },
    allergies: patient.allergies,
    current_medications: patient.current_medications,
    pregnancy_status: patient.pregnancy_status || null,
    medical_history_text: patient.medical_history_text || null,
  });

  const handleAnalyze = async () => {
    if (!drugId) {
      setError("Please select a target drug.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const payloadPatient = buildPayloadPatient();
      const result = await api.analyzeCompare(payloadPatient, { drug_id: drugId, dose: dose || null }, useLlm);
      setCompareResult(result);
      navigate("/result");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const activeCase = cases.find((c) => c.case_id === activeCaseId);

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <Icon name="database" />
          <h2>Start from a curated demo case</h2>
        </div>
        <p className="card-subtext">
          {cases.length ? `${cases.length} controlled cases` : "Loading cases…"} across{" "}
          {drugs.length ? `${drugs.length} drugs` : "…"} — contrastive pairs that vary exactly one
          patient factor (renal function, hepatic function, allergy, interactions) so you can show
          the output change only where the evidence supports it.
        </p>
        <select value={activeCaseId} onChange={(e) => e.target.value && loadCase(e.target.value)}>
          <option value="">— select a curated demo case —</option>
          {cases.map((c) => (
            <option key={c.case_id} value={c.case_id}>
              {c.case_id}: {c.label}
            </option>
          ))}
        </select>
        {activeCase && (
          <p className="card-subtext" style={{ marginTop: "0.6rem" }}>
            <Icon name="checkCircle" size={13} /> Loaded <strong>{activeCase.case_id}</strong> —
            pair group: <code>{activeCase.pair_group}</code>
          </p>
        )}
      </div>

      {error && (
        <div className="error-banner">
          <Icon name="alertOctagon" size={16} />
          {error}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <Icon name="user" />
          <h2>Demographics</h2>
        </div>
        <div className="grid-3">
          <div>
            <label>Age</label>
            <input
              type="number"
              value={patient.age}
              onChange={(e) => setPatient({ ...patient, age: e.target.value })}
            />
          </div>
          <div>
            <label>Sex</label>
            <select value={patient.sex || ""} onChange={(e) => setPatient({ ...patient, sex: e.target.value })}>
              <option value="">Unspecified</option>
              <option value="F">Female</option>
              <option value="M">Male</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label>Pregnancy status</label>
            <select
              value={patient.pregnancy_status || "not_applicable"}
              onChange={(e) => setPatient({ ...patient, pregnancy_status: e.target.value })}
            >
              <option value="not_applicable">Not applicable</option>
              <option value="pregnant">Pregnant</option>
              <option value="not_pregnant">Not pregnant</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>
        </div>

        <label>Medical conditions / comorbidities</label>
        <TagInput
          values={patient.conditions}
          onChange={(v) => setPatient({ ...patient, conditions: v })}
          placeholder="type a condition and press Enter"
        />

        <label>Known allergies</label>
        <TagInput
          values={patient.allergies}
          onChange={(v) => setPatient({ ...patient, allergies: v })}
          placeholder="e.g. penicillin"
        />
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <Icon name="kidney" />
            <h2>Kidney function</h2>
          </div>
          <label>eGFR (mL/min/1.73m²)</label>
          <input
            type="number"
            value={patient.kidney.egfr}
            onChange={(e) => setPatient({ ...patient, kidney: { ...patient.kidney, egfr: e.target.value } })}
          />
          <label>Creatinine (mg/dL)</label>
          <input
            type="number"
            value={patient.kidney.creatinine}
            onChange={(e) =>
              setPatient({ ...patient, kidney: { ...patient.kidney, creatinine: e.target.value } })
            }
          />
        </div>
        <div className="card">
          <div className="card-header">
            <Icon name="liver" />
            <h2>Liver function</h2>
          </div>
          <label>AST (U/L)</label>
          <input
            type="number"
            value={patient.liver.ast}
            onChange={(e) => setPatient({ ...patient, liver: { ...patient.liver, ast: e.target.value } })}
          />
          <label>ALT (U/L)</label>
          <input
            type="number"
            value={patient.liver.alt}
            onChange={(e) => setPatient({ ...patient, liver: { ...patient.liver, alt: e.target.value } })}
          />
          <label>Bilirubin (mg/dL)</label>
          <input
            type="number"
            value={patient.liver.bilirubin}
            onChange={(e) =>
              setPatient({ ...patient, liver: { ...patient.liver, bilirubin: e.target.value } })
            }
          />
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <Icon name="pill" />
          <h2>Current medication list</h2>
        </div>
        <div className="pill-input">
          {patient.current_medications.map((m) => (
            <span className="pill" key={m.name}>
              {m.name}
              <button type="button" onClick={() => removeMedication(m.name)}>
                ×
              </button>
            </span>
          ))}
          <input
            type="text"
            value={medDraft}
            placeholder="type a medication name and press Enter"
            onChange={(e) => setMedDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === ",") {
                e.preventDefault();
                addMedication();
              }
            }}
            onBlur={addMedication}
          />
        </div>

        <label>Relevant medical history / clinical notes</label>
        <textarea
          value={patient.medical_history_text || ""}
          onChange={(e) => setPatient({ ...patient, medical_history_text: e.target.value })}
        />
      </div>

      <div className="card">
        <div className="card-header">
          <Icon name="flask" />
          <h2>Target medication</h2>
        </div>
        <div className="grid-2">
          <div>
            <label>Drug</label>
            <select value={drugId} onChange={(e) => setDrugId(e.target.value)}>
              <option value="">— select a drug —</option>
              {drugs.map((d) => (
                <option key={d.drug_id} value={d.drug_id}>
                  {d.generic_name} ({d.drug_class})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Dose (optional)</label>
            <input type="text" value={dose} onChange={(e) => setDose(e.target.value)} placeholder="e.g. 500 mg" />
          </div>
        </div>

        <div className="llm-toggle-row">
          <label className="checkbox-row">
            <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} />
            Use live LLM generation
          </label>
          {health && (
            <span className={`llm-status ${health.llm_configured ? "is-ready" : "is-missing"}`}>
              <Icon name={health.llm_configured ? "checkCircle" : "alertTriangle"} size={12} />
              {health.llm_configured
                ? `OpenRouter key configured — will call ${health.llm_model}`
                : "No OPENROUTER_API_KEY configured — will always use the template generator"}
            </span>
          )}
        </div>
        <p className="card-subtext" style={{ marginTop: "0.3rem" }}>
          If unchecked, or if the live call fails or times out, the deterministic template
          generator is used instead — every claim is still evidence-cited either way. The analysis
          result page always shows which one actually ran.
        </p>

        <div style={{ marginTop: "1rem" }}>
          <button className="btn-primary" onClick={handleAnalyze} disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                Analyzing…
              </>
            ) : (
              <>
                <Icon name="activity" size={16} /> Analyze
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
