"""Uncertainty / insufficient-information detection.

Implements the subset of the plan's uncertainty checklist that can be
computed directly from the patient record, retrieved evidence, and the
structured risk model, without inventing a fake numerical "clinical
certainty" score:

1. Missing kidney function where the drug has documented renal considerations.
2. Missing liver function where the drug has documented hepatic considerations.
3. Unknown dose for the target drug.
4. Weak retrieval evidence (low top-score / few chunks retrieved).
5. Out-of-domain drug (not present in the evidence corpus at all).
6. Low structured-risk-model confidence (predicted probability near 0.5).
"""
from __future__ import annotations

WEAK_EVIDENCE_SCORE_THRESHOLD = 0.15
MIN_EXPECTED_EVIDENCE_COUNT = 3
LOW_CONFIDENCE_BAND = (0.40, 0.60)


def detect_uncertainty(
    patient: dict,
    drug_profile: dict | None,
    evidence: list[dict],
    risk_probability: float | None,
) -> tuple[list[str], list[str]]:
    """Returns (uncertainty_flags, missing_information)."""
    flags: list[str] = []
    missing: list[str] = []

    if drug_profile is None:
        flags.append(
            "Target drug is outside the supported evidence corpus; no label or "
            "literature evidence is available for this medication."
        )
        return flags, missing

    sections = drug_profile.get("sections", {})
    population = sections.get("use_in_specific_populations", {})

    kidney = patient.get("kidney") or {}
    if population.get("renal_impairment") and kidney.get("egfr") is None and kidney.get("creatinine") is None:
        flags.append(
            "Renal function (eGFR/creatinine) was not provided, but this drug has "
            "documented renal-impairment considerations."
        )
        missing.append("Kidney function (eGFR or creatinine)")

    liver = patient.get("liver") or {}
    if population.get("hepatic_impairment") and all(
        liver.get(k) is None for k in ("ast", "alt", "bilirubin")
    ):
        flags.append(
            "Liver function (AST/ALT/bilirubin) was not provided, but this drug has "
            "documented hepatic-impairment considerations."
        )
        missing.append("Liver function (AST, ALT, or bilirubin)")

    target_dose = patient.get("target_drug_dose")
    if not target_dose:
        missing.append("Dose of the target medication")

    if not patient.get("allergies"):
        missing.append("Documented allergy history (none recorded)")

    evidence_count = len(evidence)
    if evidence_count < MIN_EXPECTED_EVIDENCE_COUNT:
        flags.append(
            f"Only {evidence_count} relevant evidence passage(s) were retrieved for this "
            "patient context; evidence coverage is limited."
        )

    if evidence:
        top_score = max(e.get("score", 0.0) for e in evidence)
        if top_score < WEAK_EVIDENCE_SCORE_THRESHOLD:
            flags.append(
                "Retrieval relevance scores were low for this query; retrieved evidence "
                "may be only loosely related to the specific patient context."
            )

    if risk_probability is not None and LOW_CONFIDENCE_BAND[0] <= risk_probability <= LOW_CONFIDENCE_BAND[1]:
        flags.append(
            "The structured risk model's predicted probability is close to the decision "
            "boundary, indicating low model confidence for this patient profile."
        )

    return flags, missing
