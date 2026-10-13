"""End-to-end orchestrator implementing the plan's pseudocode
(section 23: analyze_patient) for both the patient-context pipeline (Model C)
and the drug-only baseline (Model A), plus the comparison helper used by the
"compare" endpoint and the final demo script (section 35, steps 11-12).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app import console_log as clog
from app.data.drugs import DRUGS
from app.rag import uncertainty
from app.rag.citation import citation_metrics, extract_claims
from app.rag.generator import generate
from app.rag.schema_validator import validate_answer
from app.retrieval.query_builder import build_baseline_queries, build_patient_queries
from app.retrieval.reranker import deduplicate, rerank
from app.risk_model.predict import predict_risk

DRUG_BY_ID = {d["drug_id"]: d for d in DRUGS}

DISCLAIMER = (
    "Research prototype. Information is evidence-grounded and does not replace "
    "evaluation by a qualified healthcare professional. This system does not "
    "diagnose, prescribe, or guarantee that any patient will experience a "
    "particular effect."
)

TOP_K_PER_QUERY = 5
MAX_FINAL_EVIDENCE = 10


def _retrieve_evidence(retriever, queries, drug_id: str, patient: dict | None):
    all_scored = []
    for q in queries:
        all_scored.extend(retriever.search(q.text, top_k=TOP_K_PER_QUERY, drug_id=drug_id))
    deduped = deduplicate(all_scored)
    reranked = rerank(deduped, patient)
    return reranked[:MAX_FINAL_EVIDENCE]


def _evidence_dicts(scored_chunks) -> list[dict]:
    out = []
    for sc in scored_chunks:
        item = dict(sc.chunk)
        item["score"] = round(sc.score, 4)
        out.append(item)
    return out


def analyze(
    retriever,
    patient: dict,
    drug_id: str,
    dose: str | None = None,
    mode: str = "context",
    use_llm: bool = False,
) -> dict:
    """mode: "context" (Model C, patient-context + RAG) or "baseline" (Model A, drug-only)."""
    mode_label = "Model C - patient-context + RAG" if mode != "baseline" else "Model A - drug-only baseline"
    clog.banner(f"ANALYZE  drug_id={drug_id}  {mode_label}  use_llm={use_llm}")
    clog.step(
        "Patient",
        f"age={patient.get('age')} sex={patient.get('sex')} conditions={patient.get('conditions')} "
        f"eGFR={(patient.get('kidney') or {}).get('egfr')}",
    )

    drug = DRUG_BY_ID.get(drug_id)
    drug_name = drug["generic_name"] if drug else drug_id
    clog.step("Drug normalization", f"{drug_id} -> {drug_name}" if drug else f"{drug_id} NOT FOUND in corpus")

    if mode == "baseline":
        queries = build_baseline_queries(drug_name)
        retrieval_patient = None
    else:
        queries = build_patient_queries(drug_name, patient)
        retrieval_patient = patient
    clog.step("Query generation", f"{len(queries)} retrieval queries built")
    for q in queries:
        clog.sub(f"- {q.text}")

    if drug is None:
        evidence_dicts: list[dict] = []
    else:
        with clog.Timer() as t:
            scored = _retrieve_evidence(retriever, queries, drug_id, retrieval_patient)
        evidence_dicts = _evidence_dicts(scored)
        clog.step(
            "Retrieval + reranking",
            f"{len(evidence_dicts)} evidence chunks kept (FAISS search + dedup + rerank, {t.elapsed:.2f}s)",
        )

    clog.step("Generation", f"requesting answer (use_llm={use_llm})...")
    with clog.Timer() as t:
        raw_answer, generated_by = generate(patient, drug_name, evidence_dicts, mode=mode, use_llm=use_llm)
    clog.step("Generation", f"generated_by={generated_by} ({t.elapsed:.2f}s)")

    answer = validate_answer(raw_answer)
    if "failed schema validation" in answer.reasoning_summary:
        clog.step("Schema validation", "FAILED - falling back to safe empty answer")
    else:
        clog.step("Schema validation", "OK")

    if mode == "baseline":
        # Model A is drug-only by definition: enforce this regardless of
        # whether the template or a live LLM produced the raw answer, since
        # an LLM call isn't guaranteed to follow the "no patient context"
        # instruction perfectly every time.
        answer.patient_relevant_risks = []
        answer.overall_context_category = "indeterminate"

    valid_chunk_ids = {e["chunk_id"] for e in evidence_dicts}
    claims = []
    for field_name, prefix in [
        ("documented_effects", "effect"),
        ("patient_relevant_risks", "risk"),
        ("contraindications_or_warnings", "warning"),
        ("dose_context", "dose"),
    ]:
        claims.extend(extract_claims(getattr(answer, field_name), valid_chunk_ids, prefix))
    citation_stats = citation_metrics(claims)
    clog.step(
        "Citation check",
        f"{len(claims)} claims, coverage={citation_stats['coverage']:.0%}, "
        f"unsupported={citation_stats['unsupported_claim_rate']:.0%}",
    )

    risk_probability = None
    risk_explanation = None
    if mode != "baseline" and drug is not None:
        risk_result = predict_risk(patient, drug_id)
        if risk_result is not None:
            risk_probability = risk_result["risk_probability"]
            risk_explanation = risk_result
    clog.step("Risk model", f"probability={risk_probability}" if risk_probability is not None else "not available")

    uncertainty_flags, missing_info = uncertainty.detect_uncertainty(
        {**patient, "target_drug_dose": dose}, drug, evidence_dicts, risk_probability
    )
    uncertainty_flags = list(dict.fromkeys(answer.uncertainty_flags + uncertainty_flags))
    missing_info = list(dict.fromkeys(answer.missing_information + missing_info))
    clog.step("Uncertainty detection", f"{len(uncertainty_flags)} flag(s) raised")

    assessment_id = f"AS_{uuid.uuid4().hex[:10]}"
    clog.step("DONE", f"risk_category={answer.overall_context_category} assessment_id={assessment_id}")

    return {
        "assessment_id": assessment_id,
        "mode": mode,
        "drug": {"drug_id": drug_id, "generic_name": drug_name, "dose": dose},
        "queries_used": [{"text": q.text, "reason": q.reason} for q in queries],
        "documented_effects": answer.documented_effects,
        "patient_relevant_risks": answer.patient_relevant_risks,
        "contraindications_or_warnings": answer.contraindications_or_warnings,
        "dose_context": answer.dose_context,
        "risk_category": answer.overall_context_category,
        "risk_probability": risk_probability,
        "risk_model_explanation": risk_explanation,
        "uncertainty_flags": uncertainty_flags,
        "missing_information": missing_info,
        "reasoning_summary": answer.reasoning_summary,
        "evidence": evidence_dicts,
        "claims": [c.__dict__ for c in claims],
        "citation_metrics": citation_stats,
        "model_version": "v1.0",
        "generated_by": generated_by,
        "disclaimer": DISCLAIMER,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def analyze_compare(retriever, patient: dict, drug_id: str, dose: str | None = None, use_llm: bool = False) -> dict:
    clog.banner(f"COMPARE REQUEST  drug_id={drug_id}  running Model A then Model C")
    baseline = analyze(retriever, patient, drug_id, dose, mode="baseline", use_llm=use_llm)
    context_aware = analyze(retriever, patient, drug_id, dose, mode="context", use_llm=use_llm)

    diff_highlights = []
    baseline_risks = set(baseline["documented_effects"] + baseline["contraindications_or_warnings"])
    context_risks = set(context_aware["patient_relevant_risks"])
    new_in_context = [r for r in context_risks if r not in baseline_risks]
    if new_in_context:
        diff_highlights.append(
            f"Patient-context retrieval surfaced {len(new_in_context)} additional patient-specific "
            "consideration(s) not present in the drug-only baseline."
        )
    if baseline["risk_category"] != context_aware["risk_category"]:
        diff_highlights.append(
            f"Risk category differs: baseline='{baseline['risk_category']}' vs "
            f"patient-context='{context_aware['risk_category']}'."
        )
    if not diff_highlights:
        diff_highlights.append("No material difference detected for this particular case.")

    return {
        "baseline": baseline,
        "context_aware": context_aware,
        "diff_highlights": diff_highlights,
    }
