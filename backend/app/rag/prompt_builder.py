"""Structured prompt construction (plan section 7, STEP 8).

Built and shown to the user even when the deterministic template generator
is used instead of a live LLM call, so the demo can always display "this is
the prompt the patient-aware context was turned into" regardless of whether
an LLM API key is configured.
"""
from __future__ import annotations

import json

SYSTEM_PROMPT = """You are a clinical medication-information assistant operating inside a \
research prototype.
Use ONLY the supplied evidence context when making drug-specific factual claims.
Do not invent evidence.
Separate documented information from patient-context interpretation.
If the evidence is insufficient, say "Insufficient evidence".
Do not recommend starting, stopping, or changing medication.
Explicitly list missing patient information that could materially affect interpretation.
For every important claim, attach the source identifier provided in context."""

RESPONSE_SCHEMA_HINT = {
    "documented_effects": [],
    "patient_relevant_risks": [],
    "contraindications_or_warnings": [],
    "dose_context": [],
    "uncertainty_flags": [],
    "missing_information": [],
    "evidence_links": [],
    "overall_context_category": "",
    "reasoning_summary": "",
}


def build_user_prompt(patient: dict, drug_name: str, evidence: list[dict]) -> str:
    evidence_block = "\n".join(
        f"[{e['chunk_id']}] ({e['source_name']} - {e['section']}): {e['text']}"
        for e in evidence
    )
    return f"""Patient:
{json.dumps(patient, indent=2)}

Target drug:
{drug_name}

Retrieved evidence:
{evidence_block}

Return JSON with exactly these keys:
{json.dumps(RESPONSE_SCHEMA_HINT, indent=2)}

overall_context_category must be one of: "lower_concern", "moderate_concern", \
"higher_concern", "indeterminate".
Every entry in patient_relevant_risks and contraindications_or_warnings must reference \
a chunk id from the evidence above."""


def build_baseline_user_prompt(drug_name: str, evidence: list[dict]) -> str:
    """Model A (drug-only baseline): deliberately excludes the patient object
    entirely, so the LLM has no patient context to reason about, matching
    the plan's definition of the baseline (drug identity only)."""
    evidence_block = "\n".join(
        f"[{e['chunk_id']}] ({e['source_name']} - {e['section']}): {e['text']}"
        for e in evidence
    )
    return f"""Target drug:
{drug_name}

Retrieved evidence (drug-only, no patient context was used in retrieval):
{evidence_block}

Return JSON with exactly these keys:
{json.dumps(RESPONSE_SCHEMA_HINT, indent=2)}

Since no patient context was supplied, patient_relevant_risks must be an empty list and
overall_context_category must be "indeterminate".
Every entry in contraindications_or_warnings must reference a chunk id from the evidence above."""


def build_full_prompt(patient: dict, drug_name: str, evidence: list[dict]) -> dict:
    return {
        "system": SYSTEM_PROMPT,
        "user": build_user_prompt(patient, drug_name, evidence),
    }


def build_baseline_prompt(drug_name: str, evidence: list[dict]) -> dict:
    return {
        "system": SYSTEM_PROMPT,
        "user": build_baseline_user_prompt(drug_name, evidence),
    }
