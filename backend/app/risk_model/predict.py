"""Loads the trained structured risk model and scores a single patient-drug
pair at inference time, plus a lightweight feature-contribution explanation
(global feature importance x this patient's standardized feature value -
a documented proxy, not a SHAP value, used to avoid an extra heavy
dependency while still giving a feature-level explanation per plan section 19).
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.risk_model.features import FEATURE_COLUMNS, extract_features

MODEL_PATH = Path(__file__).parent / "risk_model.joblib"

_cache: dict | None = None


def _load():
    global _cache
    if _cache is None:
        if not MODEL_PATH.exists():
            return None
        _cache = joblib.load(MODEL_PATH)
    return _cache


def predict_risk(patient: dict, drug_id: str) -> dict | None:
    bundle = _load()
    if bundle is None:
        return None

    model = bundle["model"]
    feature_columns = bundle["feature_columns"]
    row = extract_features(patient, drug_id)
    X = pd.DataFrame([row], columns=feature_columns)

    probability = float(model.predict_proba(X)[0, 1])

    importances = getattr(model, "feature_importances_", None)
    top_factors = []
    if importances is not None:
        contributions = X.iloc[0].to_numpy() * importances
        order = np.argsort(-np.abs(contributions))[:5]
        for idx in order:
            col = feature_columns[idx]
            if col.startswith("drug__") and row[col] == 0:
                continue
            top_factors.append(
                {
                    "feature": col.replace("drug__", "target_drug="),
                    "value": row[col],
                    "importance_weight": round(float(importances[idx]), 4),
                }
            )

    return {
        "model_name": bundle["model_name"],
        "risk_probability": round(probability, 3),
        "top_contributing_factors": top_factors,
    }
