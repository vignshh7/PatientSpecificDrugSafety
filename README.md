# Patient-Specific Drug Safety RAG

Evidence-grounded, patient-context-aware clinical decision-support **research
prototype** that assesses a single medication against a patient's medical
history, retrieves drug-specific evidence, generates a structured
evidence-linked safety report, and explicitly flags uncertainty. Built to
cover all three review phases of the project plan: research foundation +
data, RAG prototype implementation, and evaluation.

**Research prototype positioning**: this system does not diagnose, prescribe,
or guarantee that any patient will experience a particular effect. Every
factual claim it produces is linked to a specific evidence passage, and it
explicitly reports what it does not know.

Team: Kanishka Mohankumar (23BDS1007), Vignesh Venkatesan (23BDS1056).

For a step-by-step technical walkthrough of how a request actually flows
through the system (query building → retrieval → reranking → generation →
citation/uncertainty checks → risk model), see [ARCHITECTURE.md](ARCHITECTURE.md).

## What's actually implemented

| Plan component | Status | Notes |
|---|---|---|
| Evidence corpus (DailyMed-style labels + PubMed-style literature) | ✅ | 12 drugs, 144 chunks, synthetic/demo content modeled on real SPL section structure — see `backend/app/data/drugs.py` |
| Chunking + metadata | ✅ | Semantic sections, not fixed-window splitting |
| Embeddings + FAISS | ✅ (MiniLM) / ⚠️ (BGE-M3) | `sentence-transformers` + FAISS `IndexFlatIP`, real and active (`retrieval_backend: "st_faiss"`). Defaults to `all-MiniLM-L6-v2`, configurable to `BAAI/bge-m3` (the slide's named model) via `EMBEDDING_MODEL` in `backend/.env` — **BGE-M3's ~2.27GB weights file could not download in this sandbox** (large-file/LFS CDN connectivity stalled at 0 bytes on repeated attempts, while small metadata files and the smaller model downloaded fine); it should work on a machine/network without that restriction. Falls back to TF-IDF automatically if the embedding model can't load at all. |
| Patient-aware multi-query expansion | ✅ | `backend/app/retrieval/query_builder.py` |
| Reranking (lexical + clinical relevance) | ✅ | 0.6 semantic / 0.4 clinical-relevance blend, evidence-hierarchy aware |
| Structured LLM prompt | ✅ | Always built and viewable; see "Live LLM generation" below |
| Generation | ✅ live LLM (default) + ✅ template fallback | Live LLM generation via OpenRouter (`nvidia/nemotron-3-super-120b-a12b:free` by default — a free model, so the demo works with a $0-balance OpenRouter key) is the default path; falls back to the deterministic, fully-cited template generator if the API call fails, times out, or no key is configured. The UI shows a badge stating which one actually ran on every result. |
| Citation verification | ✅ | Every claim must reference a retrieved chunk id; precision/coverage computed |
| Uncertainty detection | ✅ | Missing renal/hepatic data, weak evidence, out-of-domain drug, low ML confidence |
| Structured risk model (LR / RF / XGBoost) | ✅ | Trained on 300 synthetic patient-drug cases; comparison metrics in `backend/app/risk_model/metrics.json` (not currently surfaced in the UI) |
| Drug-only vs. patient-context comparison | ✅ | `/api/analyze/compare`, side-by-side UI |
| Ablation study | ✅ | `backend/app/evaluation/run_evaluation.py` |
| Retrieval evaluation (Recall@k, Precision@k, MRR) | ✅ | Rule-based gold-relevance definition (documented, reproducible — not a substitute for manual expert annotation); written to `evaluation/results.json`, not currently surfaced in the UI |
| Frontend (3 pages) | ✅ | Patient Input, Analysis Result (Conclusion summary, source-linked citations to the exact DailyMed/PubMed document, live-LLM-vs-fallback badge), Evidence Explorer |
| Real clinical validation / MIMIC-IV | ❌ not attempted | Out of scope for a student prototype; see Limitations |

## Architecture

```
Patient input (React)
        |
        v
FastAPI /api/analyze
        |
        v
Patient-aware query builder  ---->  multi-query expansion
        |
        v
Retriever (sentence-transformers + FAISS, or TF-IDF fallback)
        |
        v
Reranker (semantic 0.6 + clinical-relevance 0.4, evidence hierarchy)
        |
        v
Evidence selection (label > literature)
        |
   +----+----------------------+
   |                           |
   v                           v
XGBoost/RF/LR risk signal   Structured generator (live LLM via OpenRouter, template fallback)
   |                           |
   +----+----------------------+
        |
        v
Schema validation (pydantic) -> citation verification -> uncertainty checks
        |
        v
Evidence-linked JSON report -> React UI (report, evidence explorer, dashboard)
```

## Repository layout

```
patient-drug-rag/
  backend/
    app/
      data/            drug label corpus, literature, synthetic patient cases
      ingestion/       build_corpus.py — chunking + metadata
      retrieval/       retriever (FAISS/TF-IDF), query builder, reranker
      risk_model/      features, train, predict (LR / RF / XGBoost)
      rag/             prompt builder, generator, uncertainty, citation, schema
      evaluation/      retrieval/comparison/ablation evaluation -> results.json
      pipeline.py      end-to-end orchestrator (analyze / analyze_compare)
      main.py          FastAPI app + routes
      db.py            SQLite persistence (assessments, feedback)
    requirements.txt
  frontend/
    src/
      pages/           PatientInput, AnalysisResult, EvidenceExplorer
      components/      RiskBadge, EvidenceCard, TagInput, Icon
      api.js           backend client
```

## Running it

### Backend

```bash
cd backend
pip install -r requirements.txt          # torch/sentence-transformers are large; TF-IDF fallback works without them
python -m app.data.generate_patient_cases # one-time: generates patient_cases.json + demo_cases.json
python -m app.risk_model.train            # one-time: trains LR/RF/XGBoost, writes risk_model.joblib + metrics.json
python -m app.evaluation.run_evaluation   # one-time: writes evaluation/results.json (retrieval/ablation metrics)
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Keep this terminal window visible during a demo: every `/api/analyze*`
request prints a live, step-by-step trace (query generation, retrieval
timing, the OpenRouter call and its duration, schema validation, citation
coverage, risk model output) straight to this console — see
`backend/app/console_log.py`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (or whatever port Vite prints).

### Live LLM generation (default)

Create `backend/.env` (already gitignored — never commit it):

```
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2   # or BAAI/bge-m3 if that download succeeds on your network
```

`backend/app/main.py` loads this file at startup (`python-dotenv`). With the
key set, every `/api/analyze*` request (`use_llm: true` by default, also a
checkbox in the Patient Input page) sends the structured prompt
(`app/rag/prompt_builder.py`) to the configured model via OpenRouter's
chat-completions API and parses its JSON response — this is a real network
call to a real model, not a simulation. The response's `generated_by` field
reports exactly what ran, e.g. `"llm:nvidia/nemotron-3-super-120b-a12b:free"`,
and the frontend shows this as a badge on every report ("Live LLM" vs.
"Template fallback") so it's never silently hidden which one actually ran.

The default model is a **free** OpenRouter model specifically so the demo
works with a $0-balance key — it's a reasoning model, so expect ~20-40s per
call (it spends part of its output budget on hidden reasoning tokens before
writing the JSON answer). If you have OpenRouter credits, swap
`OPENROUTER_MODEL` to a paid model (e.g. `anthropic/claude-haiku-4.5`) for a
much faster response.

If the call fails, times out, or no key is configured, the system
**falls back to the deterministic template generator** — the demo never
breaks from a missing key, a network blip, or an exhausted free-tier rate
limit. The frontend checkbox lets you force template-only mode (e.g. for an
instant, zero-cost demo pass).

## Demo script (plan section 35)

1. Patient Input page → "Load a demo case" → pick **A1: Elderly CKD patient
   - Metformin**.
2. Click **Analyze**.
3. On the Analysis Result page, click **Show generated retrieval queries** —
   shows the patient-aware sub-queries (age, eGFR, conditions, current meds).
4. Click **Show drug-only baseline comparison** — side-by-side Model A
   (drug-only) vs. Model C (patient-context + RAG). For this case, baseline
   reports `indeterminate` with no patient-specific risks; patient-context
   reports `higher_concern` with 3 renal-impairment-linked findings citing
   `DM_metformin_pop_renal_impairment` and a literature chunk.
5. Expand an evidence card, or a source chip next to any claim, to show the
   exact cited passage and a link straight to the real DailyMed/PubMed
   document it came from.
6. Switch to **Evidence Explorer** to show the full corpus for a drug,
   independent of any patient.
7. Repeat steps 1-4 with demo case **A2** (same drug, normal renal function)
   to show the output changes only because the clinical evidence supports it
   (plan success criterion #1).

Retrieval Recall@5 / citation coverage / ablation / LR-RF-XGBoost comparison
numbers are not shown in the UI — run `python -m app.evaluation.run_evaluation`
and read `backend/app/evaluation/results.json` directly for those.

## Honest research findings

- On the 14-case controlled demo set, **Random Forest generalized better
  than XGBoost** (higher test AUC) despite XGBoost's higher plan ranking —
  consistent with XGBoost overfitting on a small (300-row) synthetic
  dataset. This is a legitimate, presentable finding, not a bug.
- Patient-context retrieval **did not uniformly beat the drug-only baseline
  on Recall@5** in this small sample, but it raised roughly 2x as many
  uncertainty flags and surfaced patient-specific considerations absent from
  the baseline. The plan explicitly allows this outcome (section 16): "the
  goal is NOT to force Model B to win."
- Citation coverage was 100% in both modes by construction (the template
  generator only emits statements with an attached chunk id); this measures
  the generator's citation discipline, not an independent fact-check, and
  should be described that way in the report.

## Limitations 

- The evidence corpus (12 drugs, 144 chunks) and all patient cases are
  **synthetic**, modeled on public DailyMed-style section structure and
  well-established pharmacology facts — not scraped from DailyMed/PubMed and
  not real patient records (MIMIC-IV was not used; see plan section 3).
- The retrieval gold-relevance set used for Recall@k/ablation is a
  **rule-based proxy**, not manual expert annotation.
- Live LLM generation is the default, but it automatically falls back to a
  deterministic, template-based generator (no hallucination risk, works
  fully offline) if the API call fails, times out, or no key is configured
  — this trades some natural-language fluency for guaranteed faithfulness
  on that fallback path.
- None of this should be presented as proof of clinical effectiveness.
