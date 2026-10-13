"""Builds the Review-3-style evaluation results: retrieval metrics, the
drug-only-vs-patient-context comparison table, a feature-group ablation
study, and citation/safety stats (plan sections 15-17). Writes a single
results.json consumed by the /api/eval/summary endpoint and the frontend
Research Dashboard.

GOLD RELEVANCE DEFINITION (documented, not hand-tuned per case): for a given
patient-drug case, a chunk is "gold relevant" if it is one of the drug's core
label sections (contraindications / warnings / adverse reactions) OR a
population/literature chunk whose tag matches a patient factor that is
actually present (renal impairment, hepatic impairment, elderly, allergy,
interaction). This mirrors the same clinical-matching rule used by the
generator and reranker, so the evaluation measures whether retrieval finds
the evidence the rest of the system itself treats as clinically relevant -
it is a reproducible, rule-based proxy for manual expert annotation, not a
substitute for it (see plan section 15A).
"""
from __future__ import annotations

import json
from pathlib import Path

from app.data.drugs import DRUGS
from app.ingestion.build_corpus import build_chunks
from app.pipeline import analyze
from app.rag.generator import EFFECT_SECTIONS, WARNING_SECTIONS, _matched_population_chunks
from app.retrieval.retriever import Retriever

DATA_DIR = Path(__file__).parent.parent / "data"
RESULTS_PATH = Path(__file__).parent / "results.json"
DRUG_BY_ID = {d["drug_id"]: d for d in DRUGS}


def _gold_relevant_chunk_ids(patient: dict, drug_id: str, all_chunks: list[dict]) -> set[str]:
    drug_chunks = [c for c in all_chunks if c["drug_id"] == drug_id]
    core = [c for c in drug_chunks if c["section"] in EFFECT_SECTIONS | WARNING_SECTIONS]
    matched_population = _matched_population_chunks(patient, drug_chunks)
    return {c["chunk_id"] for c in core + matched_population}


def _recall_at_k(retrieved_ids: list[str], gold_ids: set[str]) -> float:
    if not gold_ids:
        return 1.0
    hit = len(set(retrieved_ids) & gold_ids)
    return round(hit / len(gold_ids), 3)


def _precision_at_k(retrieved_ids: list[str], gold_ids: set[str]) -> float:
    if not retrieved_ids:
        return 0.0
    hit = len(set(retrieved_ids) & gold_ids)
    return round(hit / len(retrieved_ids), 3)


def _mrr(retrieved_ids: list[str], gold_ids: set[str]) -> float:
    for rank, cid in enumerate(retrieved_ids, start=1):
        if cid in gold_ids:
            return round(1 / rank, 3)
    return 0.0


def run(retriever: Retriever, demo_cases: list[dict]) -> dict:
    all_chunks = retriever.chunks

    per_case_rows = []
    for case in demo_cases:
        patient = case["patient"]
        drug_id = case["drug_id"]
        gold_ids = _gold_relevant_chunk_ids(patient, drug_id, all_chunks)

        baseline_result = analyze(retriever, patient, drug_id, case.get("dose"), mode="baseline")
        context_result = analyze(retriever, patient, drug_id, case.get("dose"), mode="context")

        baseline_ids = [e["chunk_id"] for e in baseline_result["evidence"]]
        context_ids = [e["chunk_id"] for e in context_result["evidence"]]

        row = {
            "case_id": case["case_id"],
            "drug_id": drug_id,
            "gold_count": len(gold_ids),
            "baseline": {
                "recall_at_5": _recall_at_k(baseline_ids[:5], gold_ids),
                "precision_at_5": _precision_at_k(baseline_ids[:5], gold_ids),
                "mrr": _mrr(baseline_ids, gold_ids),
                "citation_coverage": baseline_result["citation_metrics"]["coverage"],
                "unsupported_claim_rate": baseline_result["citation_metrics"]["unsupported_claim_rate"],
                "uncertainty_flags_count": len(baseline_result["uncertainty_flags"]),
            },
            "context_aware": {
                "recall_at_5": _recall_at_k(context_ids[:5], gold_ids),
                "precision_at_5": _precision_at_k(context_ids[:5], gold_ids),
                "mrr": _mrr(context_ids, gold_ids),
                "citation_coverage": context_result["citation_metrics"]["coverage"],
                "unsupported_claim_rate": context_result["citation_metrics"]["unsupported_claim_rate"],
                "uncertainty_flags_count": len(context_result["uncertainty_flags"]),
            },
        }
        per_case_rows.append(row)

    def _avg(rows, model_key, metric_key):
        vals = [r[model_key][metric_key] for r in rows]
        return round(sum(vals) / len(vals), 3) if vals else 0.0

    comparison_table = [
        {
            "metric": "Retrieval Recall@5",
            "drug_only": _avg(per_case_rows, "baseline", "recall_at_5"),
            "patient_context": _avg(per_case_rows, "context_aware", "recall_at_5"),
        },
        {
            "metric": "Retrieval Precision@5",
            "drug_only": _avg(per_case_rows, "baseline", "precision_at_5"),
            "patient_context": _avg(per_case_rows, "context_aware", "precision_at_5"),
        },
        {
            "metric": "MRR",
            "drug_only": _avg(per_case_rows, "baseline", "mrr"),
            "patient_context": _avg(per_case_rows, "context_aware", "mrr"),
        },
        {
            "metric": "Citation Coverage",
            "drug_only": _avg(per_case_rows, "baseline", "citation_coverage"),
            "patient_context": _avg(per_case_rows, "context_aware", "citation_coverage"),
        },
        {
            "metric": "Unsupported Claim Rate",
            "drug_only": _avg(per_case_rows, "baseline", "unsupported_claim_rate"),
            "patient_context": _avg(per_case_rows, "context_aware", "unsupported_claim_rate"),
        },
        {
            "metric": "Avg. Uncertainty Flags Raised",
            "drug_only": _avg(per_case_rows, "baseline", "uncertainty_flags_count"),
            "patient_context": _avg(per_case_rows, "context_aware", "uncertainty_flags_count"),
        },
    ]

    ablation = _run_ablation(retriever, demo_cases, all_chunks)

    try:
        risk_metrics = json.loads((Path(__file__).parent.parent / "risk_model" / "metrics.json").read_text())
    except FileNotFoundError:
        risk_metrics = None

    return {
        "retrieval_backend": retriever.backend,
        "n_demo_cases": len(demo_cases),
        "per_case": per_case_rows,
        "comparison_table": comparison_table,
        "ablation": ablation,
        "risk_model": risk_metrics,
    }


def _run_ablation(retriever: Retriever, demo_cases: list[dict], all_chunks: list[dict]) -> list[dict]:
    """Plan section 17: test feature groups separately by restricting which
    patient fields are visible to the query builder / reranker, then
    measuring Recall@5 against the same gold-relevance definition."""
    from app.retrieval.query_builder import build_baseline_queries, build_patient_queries
    from app.retrieval.reranker import deduplicate, rerank

    def restricted_patient(patient: dict, fields: set[str]) -> dict:
        out = {}
        if "age" in fields:
            out["age"] = patient.get("age")
        if "comorbidities" in fields:
            out["conditions"] = patient.get("conditions")
        if "kidney" in fields:
            out["kidney"] = patient.get("kidney")
        if "liver" in fields:
            out["liver"] = patient.get("liver")
        if "allergies" in fields:
            out["allergies"] = patient.get("allergies")
        if "medications" in fields:
            out["current_medications"] = patient.get("current_medications")
        return out

    experiments = [
        ("Drug only", set()),
        ("Drug + age", {"age"}),
        ("Drug + age + comorbidities", {"age", "comorbidities"}),
        ("Drug + age + comorbidities + kidney", {"age", "comorbidities", "kidney"}),
        ("Drug + age + comorbidities + kidney + liver", {"age", "comorbidities", "kidney", "liver"}),
        (
            "All patient context + RAG",
            {"age", "comorbidities", "kidney", "liver", "allergies", "medications"},
        ),
    ]

    results = []
    for name, fields in experiments:
        recalls = []
        for case in demo_cases:
            patient = case["patient"]
            drug = DRUG_BY_ID.get(case["drug_id"])
            if drug is None:
                continue
            gold_ids = _gold_relevant_chunk_ids(patient, case["drug_id"], all_chunks)

            if not fields:
                queries = build_baseline_queries(drug["generic_name"])
                rp = None
            else:
                rp = restricted_patient(patient, fields)
                queries = build_patient_queries(drug["generic_name"], rp)

            scored = []
            for q in queries:
                scored.extend(retriever.search(q.text, top_k=5, drug_id=case["drug_id"]))
            reranked = rerank(deduplicate(scored), rp)[:5]
            retrieved_ids = [sc.chunk["chunk_id"] for sc in reranked]
            recalls.append(_recall_at_k(retrieved_ids, gold_ids))

        results.append(
            {
                "experiment": name,
                "recall_at_5": round(sum(recalls) / len(recalls), 3) if recalls else 0.0,
            }
        )
    return results


def main() -> None:
    chunks = build_chunks()
    retriever = Retriever(chunks)
    demo_cases = json.loads((DATA_DIR / "demo_cases.json").read_text())

    results = run(retriever, demo_cases)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"Wrote evaluation results -> {RESULTS_PATH}")
    print(json.dumps(results["comparison_table"], indent=2))
    print(json.dumps(results["ablation"], indent=2))


if __name__ == "__main__":
    main()
