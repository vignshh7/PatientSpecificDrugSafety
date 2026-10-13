# Patient-Specific Drug Safety RAG

A research prototype that takes a patient's medical history and a single
drug, retrieves relevant evidence (DailyMed-style labels + literature),
and generates a cited, patient-specific safety report with a risk category
and explicit uncertainty flags. It doesn't diagnose, prescribe, or
guarantee outcomes — every claim links back to a source passage.

See [ARCHITECTURE.md](ARCHITECTURE.md) for how a request flows through
retrieval, reranking, generation, and validation.

Team: Kanishka Mohankumar (23BDS1007), Vignesh Venkatesan (23BDS1056)

## Run it

**Backend**

```bash
cd backend
pip install -r requirements.txt
python -m app.data.generate_patient_cases   # one-time: demo cases
python -m app.risk_model.train              # one-time: trains the risk model
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Keep this terminal open — every analyze request prints a live step-by-step
trace (query generation, retrieval timing, the LLM call, validation,
citation stats) here.

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Live LLM

Create `backend/.env`:

```
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

The default model is free-tier, so it works with a $0 OpenRouter balance
(expect 20-40s per call — it's a reasoning model). Swap to a paid model
for faster responses if you have credits. If the call fails or no key is
set, it falls back to a deterministic template generator — the UI always
shows a badge for which one actually ran.

## What's in here

- 12 drugs, 144 evidence chunks (synthetic, modeled on real DailyMed SPL
  structure) — `backend/app/data/drugs.py`
- FAISS + sentence-transformers retrieval, with a TF-IDF fallback
- Patient-aware query expansion, reranking, citation verification,
  uncertainty detection
- Drug-only vs. patient-context comparison (`/api/analyze/compare`)
- A parallel LR/RF/XGBoost risk model (`backend/app/risk_model/`)
- Retrieval and ablation evaluation scripts (`backend/app/evaluation/`) —
  not wired into the UI, read `results.json` directly

## Limitations

- The evidence corpus and patient cases are synthetic, not scraped from
  DailyMed/PubMed and not real patient data (no MIMIC-IV)
- The retrieval gold-relevance set is a rule-based proxy, not
  expert-annotated
- Nothing here is evidence of clinical effectiveness
