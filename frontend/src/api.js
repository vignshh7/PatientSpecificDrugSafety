const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  listDrugs: () => request("/drugs"),
  listCases: () => request("/cases"),
  analyze: (patient, drug, useLlm = false) =>
    request("/analyze", { method: "POST", body: JSON.stringify({ patient, drug, use_llm: useLlm }) }),
  analyzeBaseline: (patient, drug, useLlm = false) =>
    request("/analyze/baseline", { method: "POST", body: JSON.stringify({ patient, drug, use_llm: useLlm }) }),
  analyzeCompare: (patient, drug, useLlm = false) =>
    request("/analyze/compare", { method: "POST", body: JSON.stringify({ patient, drug, use_llm: useLlm }) }),
  getEvidence: (drugId) => request(`/evidence/${drugId}`),
  getAssessment: (id) => request(`/assessment/${id}`),
  sendFeedback: (assessmentId, rating, notes) =>
    request("/feedback", { method: "POST", body: JSON.stringify({ assessment_id: assessmentId, rating, notes }) }),
};
