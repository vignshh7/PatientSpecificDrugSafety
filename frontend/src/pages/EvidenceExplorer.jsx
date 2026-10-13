import { useEffect, useState } from "react";
import { api } from "../api.js";
import EvidenceCard from "../components/EvidenceCard.jsx";
import Icon from "../components/Icon.jsx";

export default function EvidenceExplorer() {
  const [drugs, setDrugs] = useState([]);
  const [drugId, setDrugId] = useState("");
  const [chunks, setChunks] = useState([]);
  const [filterSource, setFilterSource] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.listDrugs().then((d) => {
      setDrugs(d);
      if (d.length) setDrugId(d[0].drug_id);
    });
  }, []);

  useEffect(() => {
    if (!drugId) return;
    setLoading(true);
    setError(null);
    api
      .getEvidence(drugId)
      .then(setChunks)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [drugId]);

  const filtered = chunks.filter((c) => filterSource === "all" || c.source_type === filterSource);
  const activeDrug = drugs.find((d) => d.drug_id === drugId);

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <Icon name="flask" />
          <h2>Evidence Explorer</h2>
        </div>
        <p className="card-subtext">
          Browse the full ingested evidence corpus (DailyMed-style labels + literature-style
          findings) for a single drug, independent of any specific patient.
        </p>
        <div className="grid-2">
          <div>
            <label>Drug</label>
            <select value={drugId} onChange={(e) => setDrugId(e.target.value)}>
              {drugs.map((d) => (
                <option key={d.drug_id} value={d.drug_id}>
                  {d.generic_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Source type</label>
            <select value={filterSource} onChange={(e) => setFilterSource(e.target.value)}>
              <option value="all">All sources</option>
              <option value="label">DailyMed label only</option>
              <option value="literature">Literature only</option>
            </select>
          </div>
        </div>
        {activeDrug && (
          <p className="card-subtext" style={{ marginTop: "0.6rem" }}>
            {activeDrug.generic_name} · {activeDrug.drug_class} · brand names:{" "}
            {activeDrug.brand_names.join(", ")}
          </p>
        )}
      </div>

      {error && (
        <div className="error-banner">
          <Icon name="alertOctagon" size={16} />
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading-banner">
          <span className="spinner" />
          Loading evidence…
        </div>
      ) : (
        <div className="card">
          <div className="card-header">
            <Icon name="database" />
            <h2>
              Evidence chunks <span className="badge-count">{filtered.length}</span>
            </h2>
          </div>
          <div style={{ marginTop: "0.8rem" }}>
            {filtered.map((chunk) => (
              <EvidenceCard key={chunk.chunk_id} chunk={chunk} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
