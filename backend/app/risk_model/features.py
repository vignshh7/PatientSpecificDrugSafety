"""Structured feature extraction for the patient-context risk model
(plan section 10, FEATURE EXAMPLE list). Produces a fixed-order numeric
feature vector plus a one-hot drug identity block, so the same extraction
path is used for training and for live inference.
"""
from __future__ import annotations

import pandas as pd

from app.data.drugs import DRUGS

DRUG_IDS = [d["drug_id"] for d in DRUGS]

NUMERIC_FEATURES = [
    "age",
    "egfr",
    "creatinine",
    "liver_score",
    "comorbidity_count",
    "renal_disease",
    "hepatic_disease",
    "cardiovascular_disease",
    "prior_adr",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + [f"drug__{d}" for d in DRUG_IDS]


def _liver_score(liver: dict) -> float:
    ast = liver.get("ast") or 0.0
    alt = liver.get("alt") or 0.0
    bilirubin = liver.get("bilirubin") or 0.0
    # Simple composite: normalized sum of how far each marker exceeds its
    # upper-normal reference, floored at 0. Not a validated clinical score;
    # used only as a single structured-model input feature.
    return max(0.0, ast - 40) / 40 + max(0.0, alt - 40) / 40 + max(0.0, bilirubin - 1.2) / 1.2


def extract_features(patient: dict, drug_id: str) -> dict:
    conditions = [c.lower() for c in (patient.get("conditions") or [])]
    kidney = patient.get("kidney") or {}
    liver = patient.get("liver") or {}

    row = {
        "age": patient.get("age") or 0,
        "egfr": kidney.get("egfr") if kidney.get("egfr") is not None else 90.0,
        "creatinine": kidney.get("creatinine") if kidney.get("creatinine") is not None else 0.9,
        "liver_score": _liver_score(liver),
        "comorbidity_count": len(conditions),
        "renal_disease": int(any("kidney" in c or "renal" in c for c in conditions)),
        "hepatic_disease": int(any("hepatic" in c or "liver" in c or "cirrhosis" in c for c in conditions)),
        "cardiovascular_disease": int(
            any(k in c for c in conditions for k in ("coronary", "cardiac", "heart", "atrial fibrillation"))
        ),
        "prior_adr": int(bool(patient.get("prior_adr"))),
    }
    for d in DRUG_IDS:
        row[f"drug__{d}"] = 1 if d == drug_id else 0
    return row


def to_feature_frame(cases: list[dict]) -> pd.DataFrame:
    rows = [extract_features(c["patient"], c["drug_id"]) for c in cases]
    df = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    return df
