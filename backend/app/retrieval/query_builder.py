"""Patient-aware multi-query construction.

Per the project plan, a single generic query ("what are the side effects of
Drug X?") is replaced by several targeted sub-queries derived from the
patient's structured features, plus metadata filtering by drug. This module
also powers the "drug-only baseline" by building the same kind of queries
but with no patient-context subqueries at all (Model A in the plan).
"""
from __future__ import annotations

from dataclasses import dataclass

RENAL_IMPAIRED_EGFR = 60.0
HEPATIC_AST_ALT_UPPER = 40.0
HEPATIC_BILIRUBIN_UPPER = 1.2
ELDERLY_AGE = 65


@dataclass
class PatientQuery:
    text: str
    reason: str


def build_baseline_queries(drug_name: str) -> list[PatientQuery]:
    """Model A: drug-only queries, no patient context at all."""
    return [
        PatientQuery(f"{drug_name} adverse reactions", "drug-only: general safety"),
        PatientQuery(f"{drug_name} contraindications", "drug-only: general safety"),
        PatientQuery(f"{drug_name} warnings and precautions", "drug-only: general safety"),
    ]


def build_patient_queries(drug_name: str, patient: dict) -> list[PatientQuery]:
    """Model B/C: patient-context-aware query expansion."""
    queries: list[PatientQuery] = [
        PatientQuery(f"{drug_name} adverse reactions", "baseline drug safety"),
        PatientQuery(f"{drug_name} contraindications", "baseline drug safety"),
        PatientQuery(f"{drug_name} warnings and precautions", "baseline drug safety"),
    ]

    age = patient.get("age")
    if isinstance(age, (int, float)) and age >= ELDERLY_AGE:
        queries.append(
            PatientQuery(f"{drug_name} elderly patients geriatric use", f"age={age} >= {ELDERLY_AGE}")
        )

    kidney = patient.get("kidney") or {}
    egfr = kidney.get("egfr")
    if egfr is not None:
        queries.append(
            PatientQuery(
                f"{drug_name} renal impairment dosing kidney function",
                f"eGFR={egfr} provided",
            )
        )

    liver = patient.get("liver") or {}
    if any(liver.get(k) is not None for k in ("ast", "alt", "bilirubin")):
        queries.append(
            PatientQuery(
                f"{drug_name} hepatic impairment liver function",
                "liver labs provided",
            )
        )

    conditions = patient.get("conditions") or []
    for condition in conditions:
        queries.append(
            PatientQuery(
                f"{drug_name} {condition} risk considerations",
                f"condition: {condition}",
            )
        )

    allergies = patient.get("allergies") or []
    if allergies:
        queries.append(
            PatientQuery(
                f"{drug_name} allergy hypersensitivity reaction",
                f"allergies on file: {', '.join(allergies)}",
            )
        )

    current_meds = patient.get("current_medications") or []
    if current_meds:
        med_names = ", ".join(m.get("name", "") for m in current_meds if m.get("name"))
        if med_names:
            queries.append(
                PatientQuery(
                    f"{drug_name} drug interactions with {med_names}",
                    f"current medications: {med_names}",
                )
            )

    pregnancy = patient.get("pregnancy_status")
    if pregnancy and str(pregnancy).lower() not in ("none", "not_applicable", "n/a", ""):
        queries.append(
            PatientQuery(
                f"{drug_name} pregnancy use in specific populations",
                f"pregnancy_status={pregnancy}",
            )
        )

    return queries


def is_renal_impaired(patient: dict) -> bool:
    egfr = (patient.get("kidney") or {}).get("egfr")
    return egfr is not None and egfr < RENAL_IMPAIRED_EGFR


def is_hepatic_impaired(patient: dict) -> bool:
    liver = patient.get("liver") or {}
    ast, alt, bili = liver.get("ast"), liver.get("alt"), liver.get("bilirubin")
    if ast is not None and ast > HEPATIC_AST_ALT_UPPER:
        return True
    if alt is not None and alt > HEPATIC_AST_ALT_UPPER:
        return True
    if bili is not None and bili > HEPATIC_BILIRUBIN_UPPER:
        return True
    return False


def is_elderly(patient: dict) -> bool:
    age = patient.get("age")
    return isinstance(age, (int, float)) and age >= ELDERLY_AGE
