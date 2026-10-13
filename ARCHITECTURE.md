# Architecture & Data Flow

This document explains **how the system actually works**, end to end: what
happens between a user clicking "Analyze" and a report appearing on screen,
which file is responsible for which step, and why each design decision was
made. `README.md` covers status and how to run it; this file covers
mechanics, for panel Q&A and for anyone picking the code up cold.

---

## 1. System at a glance

```
┌─────────────────────────────────────────────────────────────────────┐
│  REACT FRONTEND (frontend/src)                                      │
│  Patient Input → Analysis Result → Evidence Explorer                │
└───────────────────────────────┬───────────────────────────────────-─┘
                                 │ fetch() JSON over HTTP
                                 ▼
┌───────────────────────────────────────────────────────────────────-─┐
│  FASTAPI BACKEND (backend/app/main.py)                              │
│  /api/analyze · /api/analyze/baseline · /api/analyze/compare        │
│  /api/evidence/{drug_id} · /api/eval/summary · /api/feedback        │
└───────────────────────────────┬────────────────────────────────────┘
                                 ▼
                    backend/app/pipeline.py  (analyze / analyze_compare)
                                 │
        ┌────────────────────────┼─────────────────────────┐
        ▼                        ▼                          ▼
  query_builder.py          retriever.py                predict.py
  (patient → queries)   (queries → ranked chunks)   (patient → risk %)
        │                        │                          │
        └───────────┬────────────┘                          │
                     ▼                                       │
               reranker.py                                   │
         (semantic + clinical-relevance blend)                │
                     │                                       │
                     ▼                                       │
               generator.py  ◄───────────────────────────────┘
        (template, or optional live LLM via prompt_builder.py)
                     │
                     ▼
        schema_validator.py → citation.py → uncertainty.py
                     │
                     ▼
          final JSON report (see §6 for the exact shape)
                     │
                     ▼
                  db.py (SQLite: assessments, feedback)
```

Everything left of "FASTAPI BACKEND" is one HTTP round trip. Everything
inside `pipeline.py` happens synchronously, in-process, per request — there
is no job queue or async worker, because retrieval over 144 chunks and a
144-row TF-IDF/FAISS search complete in milliseconds.

---

## 2. The evidence corpus (built once, at process startup)

Source of truth: [backend/app/data/drugs.py](backend/app/data/drugs.py) (12
drugs, each with `indications`, `contraindications`,
`warnings_and_precautions`, `adverse_reactions`, `drug_interactions`,
`dosage_considerations`, and a `use_in_specific_populations` dict keyed by
`renal_impairment` / `hepatic_impairment` / `geriatric_use` / `pregnancy`)
and [backend/app/data/literature.py](backend/app/data/literature.py) (24
"PubMed-style" findings, 2 per drug, each tagged with `relevance_tags` like
`renal_impairment`, `elderly`, `interactions`).

[backend/app/ingestion/build_corpus.py](backend/app/ingestion/build_corpus.py)
flattens both into a single list of **chunks** — one chunk per label
section, one per population subsection, one per literature finding. This
is semantic chunking (one chunk = one clinically coherent unit), not
fixed-window splitting, per the plan's chunking guidance. Each chunk carries:

```python
{
  "chunk_id": "DM_metformin_pop_renal_impairment",
  "drug_id": "metformin", "drug_name": "Metformin",
  "source_name": "DailyMed", "source_type": "label",
  "section": "Use in Specific Populations - Renal Impairment",
  "text": "...",
  "url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=056072d8-...",
  "evidence_rank": 1,              # 1 = label, 3 = literature (evidence hierarchy)
  "population_tag": "renal_impairment",   # only on population chunks
  "relevance_tags": [...],                # only on literature chunks
}
```

144 chunks total (12 drugs × ~10 label sections, + 24 literature chunks).
This list is held in memory by the FastAPI process — no document database;
`build_chunks()` runs once at import time in `main.py`.

Each drug's `dailymed_setid` in `drugs.py` was resolved ahead of time
against the real DailyMed public API (`/dailymed/services/v2/spls.json`),
so every label chunk's `url` is a direct link to the exact real SPL
document, not a search page. Literature chunk URLs are a PubMed search for
the drug + clinical topic (e.g. `metformin renal impairment elderly`)
rather than the fabricated demo title, since the literature findings
themselves are synthetic and have no single real article to link to.

---

## 3. Retrieval: from patient to ranked evidence

### 3a. Query construction — [backend/app/retrieval/query_builder.py](backend/app/retrieval/query_builder.py)

A single generic query ("side effects of Drug X") is replaced by several
targeted sub-queries, built conditionally from the patient's structured
fields:

| Patient fact present | Extra query generated |
|---|---|
| always | `"{drug} adverse reactions"`, `"{drug} contraindications"`, `"{drug} warnings and precautions"` |
| `age >= 65` | `"{drug} elderly patients geriatric use"` |
| `kidney.egfr` is not null | `"{drug} renal impairment dosing kidney function"` |
| `liver.ast/alt/bilirubin` not null | `"{drug} hepatic impairment liver function"` |
| each entry in `conditions` | `"{drug} {condition} risk considerations"` |
| `allergies` non-empty | `"{drug} allergy hypersensitivity reaction"` |
| `current_medications` non-empty | `"{drug} drug interactions with {med names}"` |
| `pregnancy_status` set and relevant | `"{drug} pregnancy use in specific populations"` |

`build_baseline_queries()` returns only the first three (drug-only, no
patient context at all) — this is **Model A**. `build_patient_queries()`
returns the full conditional set — this is **Model B/C**. Same function
family, same retriever, same reranker; the only difference between the
baseline and the patient-context run is which queries are built and whether
the patient object is passed into reranking. This symmetry is what makes
the baseline-vs-context comparison scientifically meaningful rather than
two unrelated code paths.

### 3b. Retrieval backend — [backend/app/retrieval/retriever.py](backend/app/retrieval/retriever.py)

`Retriever.__init__` tries, in order:

1. **`sentence-transformers` + FAISS** (`st_faiss` backend): encode every
   chunk with a bi-encoder — default `all-MiniLM-L6-v2`, configurable via
   `EMBEDDING_MODEL` in `backend/.env` to `BAAI/bge-m3` (the model named in
   the plan/slide) — then build a `faiss.IndexFlatIP` over the normalized
   vectors (inner product on unit vectors = cosine similarity). **BGE-M3 was
   attempted as the default and reverted**: its ~2.27GB weights file
   repeatedly stalled at 0 bytes downloading in this sandbox (small metadata
   files and a smaller model's weights downloaded fine, isolating it to
   that large-file transfer specifically, not a general network outage).
   MiniLM is fully functional and is what the running system actually uses;
   swap the env var back to `BAAI/bge-m3` on a network where that download
   completes.
2. **TF-IDF + cosine similarity** (`tfidf` backend, scikit-learn): used
   automatically if step 1's import or model download fails for any reason
   (no internet, package not installed, download interrupted).

This fallback exists because step 1 depends on a multi-hundred-MB-to-~2GB
model download the first time it runs (BGE-M3 is the larger, higher-quality
end of that range); the system must still be demoable on a machine with no
network access or an interrupted download. `GET /api/health` reports which
backend is active (`retrieval_backend`) and whether a live LLM key is
configured (`llm_configured`, `llm_model`) — always check this before a
demo.

Each sub-query is searched independently (`top_k=5`, filtered to
`drug_id == target_drug`), and results across all sub-queries are pooled.

### 3c. Deduplication + reranking — [backend/app/retrieval/reranker.py](backend/app/retrieval/reranker.py)

Pooled results are deduplicated by `chunk_id`, then rescored:

```
final_score = 0.6 × semantic_score + 0.4 × clinical_relevance_score
```

`clinical_relevance_score` combines (a) the evidence-hierarchy rank (label
chunks score higher than literature chunks) and (b) whether the chunk's
`population_tag` / `relevance_tags` actually matches something true about
*this* patient (e.g. a `renal_impairment`-tagged chunk only gets the boost
if `is_renal_impaired(patient)` — eGFR < 60 — is actually true). This is
why a chunk tagged "renal impairment" doesn't automatically outrank
everything else for a patient with normal kidneys. The 0.6/0.4 split is the
plan's suggested starting point, explicitly flagged there as something to
validate experimentally rather than treat as fixed.

Top 10 chunks after reranking become the final evidence set passed to
generation.

---

## 4. Generation — turning evidence into a structured report

[backend/app/rag/generator.py](backend/app/rag/generator.py) has two
backends behind one function, `generate(patient, drug_name, evidence, mode,
use_llm)`:

**Template backend (default, always available).** Deterministic, rule-based
assembly:
- `documented_effects` ← chunks in sections `Indications and Usage` /
  `Adverse Reactions`
- `contraindications_or_warnings` ← chunks in `Contraindications` /
  `Warnings and Precautions`
- `dose_context` ← `Dosage Considerations` chunk + any matched renal/hepatic
  population chunk
- `patient_relevant_risks` ← chunks whose population/relevance tag matches
  a patient factor that is actually present (same matching logic as the
  reranker, in `_matched_population_chunks`) — **empty by construction in
  baseline mode**, since Model A never checks patient factors
- every statement is emitted as `"{evidence text} [{chunk_id}]"` — the
  citation tag is part of the generation step, not bolted on afterward
- `overall_context_category` is derived by scanning matched chunks for
  high-risk keywords (`contraindicat`, `avoid`, `not recommended`, `should
  not`, `severe`, `fatal`) → `higher_concern`; moderate keywords (`caution`,
  `monitor`, `adjust`, `reduce`) → `moderate_concern`; no matches →
  `lower_concern`; no evidence at all → `indeterminate`
- `reasoning_summary` is a templated paragraph naming which patient factors
  were present and which retrieved sections drove the category

This backend can never hallucinate a fact not present in the retrieved
evidence, because it only ever emits evidence text verbatim plus its own
citation tag — the tradeoff is narrative fluency (it reads like assembled
bullet points, not prose). It is kept as the automatic fallback, not removed,
specifically so a missing key or a network blip never breaks the demo.

**Live LLM backend (default).** `use_llm: true` is the default on every
`/api/analyze*` request (and a checkbox on the Patient Input page, default
checked). `_call_openrouter()` sends the request through
[backend/app/rag/prompt_builder.py](backend/app/rag/prompt_builder.py)'s
structured system/user prompt (explicit instructions: use only supplied
evidence, say "insufficient evidence" rather than invent, attach a source id
to every claim, never recommend starting/stopping medication) to
**OpenRouter's chat-completions API** (`https://openrouter.ai/api/v1/chat/
completions`, `OPENROUTER_API_KEY` + `OPENROUTER_MODEL` from
`backend/.env`, default model `nvidia/nemotron-3-super-120b-a12b:free` — a
free model chosen so the demo works with a $0-balance OpenRouter account;
swap to a paid model like `anthropic/claude-haiku-4.5` for a much faster
response if credits are available) and parses the JSON response. This is a
genuine outbound HTTPS call to a hosted model, not a simulation. Model A
(baseline) and Model C (context) use two different prompts —
`build_baseline_prompt()` deliberately omits the patient object entirely, so
the LLM has no patient context to reason about for the baseline, matching
Model A's drug-only definition; `pipeline.analyze()` additionally
force-clears `patient_relevant_risks` and the risk category for baseline
responses regardless of backend, so this invariant holds even if the model
doesn't follow the instruction perfectly.

**Any failure at any step — no key, package missing, network error, bad
status code, malformed JSON — falls through to the template backend**,
inside `_call_openrouter()`'s broad `except Exception: return None`. The
response's `generated_by` field tells you which path actually ran
(`"llm:nvidia/nemotron-3-super-120b-a12b:free"` or `"template"`); the
frontend renders this as a badge on every report, and `backend/app/
console_log.py` prints the OpenRouter call, its HTTP status, and its
duration live to the terminal running `uvicorn`, so this is always visible,
never hidden. `schema_validator.py`'s `GeneratedAnswer` also tolerates
common shape deviations from smaller/free models (e.g. `null` instead of
`[]`, a bare string instead of a one-item list, `{"text": ...}` objects
instead of plain strings) by coercing them, rather than discarding the
whole answer and falling back to the empty "indeterminate" template.

---

## 5. Validation, citation, and uncertainty — the safety layer

Three checks run on every generated answer, in order, inside
[backend/app/pipeline.py](backend/app/pipeline.py)`.analyze()`:

1. **Schema validation** — [schema_validator.py](backend/app/rag/schema_validator.py):
   a pydantic model with a fixed field set; `overall_context_category` is
   coerced to `"indeterminate"` if it's not one of the four allowed values.
   A malformed LLM response can never crash the pipeline or leak a free-form
   category into the UI.
2. **Citation extraction + verification** — [citation.py](backend/app/rag/citation.py):
   every generated statement is scanned with a regex for `[chunk_id]` tags;
   a claim is `supported` only if the referenced id is among the chunks that
   were *actually retrieved for this request* (not just any valid id in the
   corpus). `citation_metrics()` turns this into `precision` / `coverage` /
   `unsupported_claim_rate`, shown on the Analysis Result page as "Citation
   faithfulness" under each report.
3. **Uncertainty detection** — [uncertainty.py](backend/app/rag/uncertainty.py):
   independent of what the generator said about itself, this checks:
   missing renal labs when the drug has documented renal guidance; missing
   hepatic labs when the drug has documented hepatic guidance; missing dose;
   fewer than 3 evidence chunks retrieved; top retrieval score below 0.15;
   drug not in corpus at all; risk-model probability within 0.40–0.60 of the
   decision boundary. These flags are computed from hard numbers, not
   language-model self-assessment.

---

## 6. The response shape

Every `/api/analyze*` call returns one JSON object with this shape
(see [backend/app/pipeline.py](backend/app/pipeline.py)`.analyze()` for the
authoritative source):

```
assessment_id, mode ("context"|"baseline"), drug {drug_id, generic_name, dose},
queries_used [{text, reason}],
documented_effects[], patient_relevant_risks[], contraindications_or_warnings[],
dose_context[], risk_category, risk_probability, risk_model_explanation,
uncertainty_flags[], missing_information[], reasoning_summary,
evidence[] (full chunk objects + retrieval score),
claims[] (claim_id, claim_text, source_chunk_ids, supported),
citation_metrics {precision, coverage, unsupported_claim_rate},
model_version, generated_by, disclaimer, created_at
```

`POST /api/analyze/compare` runs `analyze()` twice (`mode="baseline"` then
`mode="context"`) and wraps both plus a `diff_highlights[]` list (computed
by diffing the two `patient_relevant_risks` sets and comparing
`risk_category`) — this is what powers the side-by-side view.

---

## 7. The structured risk model (parallel, independent signal)

This is a **separate, parallel signal**, not part of the RAG chain — the
generator never sees or is constrained by the risk model's output; it's
attached to the final response alongside the evidence-based report, exactly
as the plan specifies ("do not let the ML model invent clinical evidence").

- **Features** — [features.py](backend/app/risk_model/features.py): `age`,
  `egfr`, `creatinine`, a composite `liver_score` (normalized excess over
  AST/ALT/bilirubin upper-normal), `comorbidity_count`, three comorbidity
  flags derived from condition-name keyword matching, `prior_adr`, plus a
  12-wide one-hot block for drug identity.
- **Labels** — [generate_patient_cases.py](backend/app/data/generate_patient_cases.py):
  300 synthetic patients (25 per drug), label derived from a deterministic
  function of the *same drug text* the reranker and generator use (does the
  patient's egfr/liver values cross a threshold that the drug's own
  `use_in_specific_populations` text flags as high/moderate risk?), plus
  ±0.07 random noise so the dataset isn't perfectly separable. This keeps
  the ML labels evidence-grounded rather than arbitrary, per the plan's
  explicit prohibition on random labels.
- **Training** — [train.py](backend/app/risk_model/train.py): patient-level
  60/20/20 train/val/test split (each synthetic case is already one
  distinct patient, so no leakage), trains Logistic Regression / Random
  Forest / XGBoost, picks the best by test AUC, saves it + a feature-column
  manifest to `risk_model.joblib`.
- **Inference** — [predict.py](backend/app/risk_model/predict.py): loads the
  saved model once, scores a single patient-drug pair, and returns a
  lightweight explanation (`feature_importances_ × this patient's feature
  value`, top 5 by magnitude) — a documented proxy, not a SHAP value (SHAP
  was deliberately not added, to avoid another heavy dependency for a
  feature-importance view that serves the same demo purpose).

On this project's 300-row synthetic dataset, **Random Forest generalized
better than XGBoost** (see `backend/app/risk_model/metrics.json`) — XGBoost
fit the training set almost perfectly (train AUC ≈ 1.0) but dropped on
held-out data, a textbook small-dataset overfitting signature. This is
reported as a finding, not hidden.

---

## 8. Evaluation — how the retrieval/ablation numbers are produced

[backend/app/evaluation/run_evaluation.py](backend/app/evaluation/run_evaluation.py)
is a standalone script (run once, writes `results.json`, served statically
by `/api/eval/summary` — not currently rendered anywhere in the UI, read the
JSON directly or via that endpoint) that:

1. **Defines "gold relevant" chunks per case** without manual annotation:
   for a given patient + drug, gold = the drug's core label sections
   (contraindications / warnings / adverse reactions) **plus** any
   population/literature chunk whose tag matches a patient factor that is
   actually true — i.e., the exact same matching rule the generator and
   reranker already use internally. This makes the evaluation measure
   "does retrieval find what the rest of the system itself treats as
   relevant," which is reproducible and documented, but explicitly **not**
   a substitute for manual expert annotation (stated plainly so it isn't
   oversold to the panel).
2. **Runs both Model A and Model C** over all 14 curated demo cases
   ([demo_cases.json](backend/app/data/demo_cases.json)), computes
   Recall@5 / Precision@5 / MRR against the gold set, plus citation
   coverage and uncertainty-flag counts from the real pipeline output —
   these are not separately mocked, they come from calling `analyze()`.
3. **Runs the ablation study**: six experiments that progressively reveal
   more patient fields to the query builder/reranker (`Drug only` → `+age`
   → `+comorbidities` → `+kidney` → `+liver` → `+all patient context`),
   measuring Recall@5 at each step, to see which information actually
   moves retrieval quality (plan section 17).
4. **Bundles the risk model's `metrics.json`** (already written by
   `train.py`) into the same results file so the dashboard has one source.

---

## 9. Frontend architecture

```
src/
  main.jsx            BrowserRouter + AppProvider wrapping App
  App.jsx             Header, 3-tab nav, footer disclaimer, <Routes>
  AppContext.jsx       React Context holding the last compareResult
                       (this is how PatientInput hands its result to AnalysisResult
                       without prop drilling or URL state)
  api.js               Thin fetch wrapper, one function per endpoint
  pages/
    PatientInput.jsx    Form + "load demo case" dropdown; also calls api.health()
                         on mount to show whether an OpenRouter key is configured
                         before the user even clicks Analyze; Analyze calls
                         api.analyzeCompare() → navigate("/result")
    AnalysisResult.jsx  Reads compareResult from context; renders the report via a
                         shared <ReportBody> used for both the single view and the
                         two-column compare view — each with its own Conclusion
                         block (verdict + documented advantages vs. the specific
                         concern driving it) and a live-LLM-vs-template-fallback
                         badge; feedback buttons call api.sendFeedback
    EvidenceExplorer.jsx Independent of any analysis — drug dropdown → api.getEvidence()
  components/
    RiskBadge, EvidenceCard, TagInput, Icon   presentational only, no fetching
```

There is no global state library — `AppContext` is a single `useState`
holding the last `compareResult`. Navigating to `/result` without having
analyzed anything first renders an explicit empty state rather than
crashing on `null`.

**Why the Patient Input page calls `/api/analyze/compare` (not plain
`/api/analyze`)**: the single most important demo moment (plan section 35,
step 12) is the baseline-vs-context side-by-side, so the app always has
both results on hand the moment the report page loads, instead of making
the user trigger a second network call to see the comparison.

---

## 10. Key design decisions (and why)

| Decision | Why |
|---|---|
| TF-IDF fallback behind the FAISS/embeddings path | The demo must never fail because of a network hiccup or a machine without the model cached. |
| Live LLM (OpenRouter) as the default, template as automatic fallback | Matches the slide's "LLM Generation" step with a real model call. The template path is kept, not removed, so a missing key / network failure / bad response degrades gracefully instead of crashing the demo — every statement it emits is retrieved text + a citation tag, so the fallback is still zero-hallucination. |
| SQLite, not Postgres | Plan explicitly allows this for a prototype of this size; no setup step required to run the demo. |
| Evidence corpus is synthetic, not scraped | DailyMed/PubMed scraping was out of scope for the timeline; content is modeled on real SPL section structure and well-established pharmacology facts, and is labeled as synthetic everywhere it's surfaced (README, dashboard, this doc). |
| Gold-relevance for evaluation is rule-based, not hand-annotated | Reproducible and consistent with the rest of the system's own relevance logic, at the cost of not being independent expert ground truth — stated as a limitation, not hidden. |
| ML risk model is a parallel signal, never a gate on the RAG output | Matches the plan's explicit rule: "do not let the ML model invent clinical evidence." |
| One in-process FastAPI app, no task queue | Corpus is 144 chunks; full retrieval + generation completes in well under a second, so there's nothing to queue. |
