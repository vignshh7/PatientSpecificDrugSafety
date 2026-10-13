"""FastAPI application (plan section 25: API DESIGN). Wires together the
evidence corpus, the retriever, and the analysis pipeline, and exposes the
endpoints the React frontend uses (patient input, analysis result, evidence
explorer).
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

# Must run before any app.* import that reads an env var at module import
# time (e.g. app.retrieval.retriever's EMBEDDING_MODEL default).
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.data.drugs import DRUGS
from app.ingestion.build_corpus import build_chunks
from app.pipeline import analyze, analyze_compare
from app.rag.generator import DEFAULT_OPENROUTER_MODEL
from app.retrieval.retriever import Retriever
from app.schemas import AnalyzeRequest, FeedbackRequest

DATA_DIR = Path(__file__).parent / "data"
EVAL_RESULTS_PATH = Path(__file__).parent / "evaluation" / "results.json"

app = FastAPI(title="Patient-Specific Drug Safety RAG API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_chunks = build_chunks()
_retriever = Retriever(_chunks)
db.init_db()

with open(DATA_DIR / "demo_cases.json") as f:
    _demo_cases = json.load(f)

DRUG_SUMMARY = [
    {"drug_id": d["drug_id"], "generic_name": d["generic_name"], "brand_names": d["brand_names"], "drug_class": d["drug_class"]}
    for d in DRUGS
]


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "retrieval_backend": _retriever.backend,
        "n_chunks": len(_chunks),
        "llm_configured": bool(os.environ.get("OPENROUTER_API_KEY")),
        "llm_model": os.environ.get("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
    }


@app.get("/api/drugs")
def list_drugs():
    return DRUG_SUMMARY


@app.get("/api/cases")
def list_cases():
    return _demo_cases


@app.post("/api/analyze")
def analyze_patient(req: AnalyzeRequest):
    patient = req.patient.model_dump()
    result = analyze(_retriever, patient, req.drug.drug_id, req.drug.dose, mode="context", use_llm=req.use_llm)
    result["patient_id"] = patient.get("patient_id")
    db.save_assessment(result)
    return result


@app.post("/api/analyze/baseline")
def analyze_baseline(req: AnalyzeRequest):
    patient = req.patient.model_dump()
    result = analyze(_retriever, patient, req.drug.drug_id, req.drug.dose, mode="baseline", use_llm=req.use_llm)
    result["patient_id"] = patient.get("patient_id")
    db.save_assessment(result)
    return result


@app.post("/api/analyze/compare")
def analyze_compare_endpoint(req: AnalyzeRequest):
    patient = req.patient.model_dump()
    result = analyze_compare(_retriever, patient, req.drug.drug_id, req.drug.dose, use_llm=req.use_llm)
    db.save_assessment(result["baseline"])
    db.save_assessment(result["context_aware"])
    return result


@app.get("/api/evidence/{drug_id}")
def get_evidence(drug_id: str):
    chunks = [c for c in _chunks if c["drug_id"] == drug_id]
    if not chunks:
        raise HTTPException(status_code=404, detail="No evidence found for this drug_id")
    return chunks


@app.get("/api/assessment/{assessment_id}")
def get_assessment(assessment_id: str):
    result = db.get_assessment(assessment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result


@app.post("/api/feedback")
def post_feedback(req: FeedbackRequest):
    feedback_id = f"FB_{uuid.uuid4().hex[:10]}"
    db.save_feedback(feedback_id, req.assessment_id, req.rating, req.notes)
    return {"status": "ok", "feedback_id": feedback_id}


@app.get("/api/eval/summary")
def eval_summary():
    if not EVAL_RESULTS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Evaluation results not generated yet. Run `python -m app.evaluation.run_evaluation`.",
        )
    return json.loads(EVAL_RESULTS_PATH.read_text())
