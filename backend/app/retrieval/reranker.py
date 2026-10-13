"""Lightweight lexical + clinical-relevance reranking.

The plan allows "a lightweight lexical + semantic score combination" instead
of a full cross-encoder reranker, with a suggested starting split of
60% semantic / 40% clinical-relevance (explicitly flagged in the plan as a
value to validate experimentally, not a clinical constant). We implement that
clinical-relevance term as:

1. Evidence hierarchy rank (official label > literature) -> never let a
   lower-tier source outrank the label on a near-tie.
2. Whether the chunk's population/relevance tags match patient factors that
   are actually present (renal impairment, hepatic impairment, elderly,
   interactions, allergy) -> boosts passages that are patient-relevant, not
   just topically similar.
"""
from __future__ import annotations

from app.retrieval.query_builder import is_elderly, is_hepatic_impaired, is_renal_impaired
from app.retrieval.retriever import ScoredChunk

SEMANTIC_WEIGHT = 0.6
CLINICAL_WEIGHT = 0.4

MAX_EVIDENCE_RANK = 3  # label=1, guideline-tier=2 (unused currently), literature=3


def _clinical_relevance_score(chunk: dict, patient: dict | None) -> float:
    rank_score = 1.0 - (chunk.get("evidence_rank", MAX_EVIDENCE_RANK) - 1) / MAX_EVIDENCE_RANK

    if patient is None:
        return rank_score

    tag_bonus = 0.0
    population_tag = chunk.get("population_tag")
    relevance_tags = set(chunk.get("relevance_tags", []))

    if population_tag == "renal_impairment" and is_renal_impaired(patient):
        tag_bonus += 0.5
    if population_tag == "hepatic_impairment" and is_hepatic_impaired(patient):
        tag_bonus += 0.5
    if population_tag == "geriatric_use" and is_elderly(patient):
        tag_bonus += 0.5
    if "renal_impairment" in relevance_tags and is_renal_impaired(patient):
        tag_bonus += 0.4
    if "hepatic_impairment" in relevance_tags and is_hepatic_impaired(patient):
        tag_bonus += 0.4
    if "elderly" in relevance_tags and is_elderly(patient):
        tag_bonus += 0.3
    if "allergy" in relevance_tags and patient.get("allergies"):
        tag_bonus += 0.3
    if "interactions" in relevance_tags and patient.get("current_medications"):
        tag_bonus += 0.3

    return min(1.0, rank_score * 0.6 + min(tag_bonus, 1.0) * 0.4 + 0.1)


def rerank(
    scored_chunks: list[ScoredChunk], patient: dict | None = None
) -> list[ScoredChunk]:
    reranked = []
    for sc in scored_chunks:
        clinical = _clinical_relevance_score(sc.chunk, patient)
        final_score = SEMANTIC_WEIGHT * sc.score + CLINICAL_WEIGHT * clinical
        reranked.append(ScoredChunk(chunk=sc.chunk, score=final_score))
    reranked.sort(key=lambda sc: sc.score, reverse=True)
    return reranked


def deduplicate(scored_chunks: list[ScoredChunk]) -> list[ScoredChunk]:
    seen: set[str] = set()
    unique: list[ScoredChunk] = []
    for sc in scored_chunks:
        cid = sc.chunk["chunk_id"]
        if cid in seen:
            continue
        seen.add(cid)
        unique.append(sc)
    return unique
