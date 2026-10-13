"""Trains and compares the three structured risk models named in the plan
(Logistic Regression baseline, Random Forest, XGBoost), on the synthetic
patient-case dataset, with a patient-level 60/20/20 train/val/test split
(each synthetic case is already one distinct patient, so a row-level split
introduces no patient leakage).

Saves:
- the best-performing model (by test AUC) to risk_model.joblib
- all three models' metrics to metrics.json (used by the research dashboard
  and by the baseline-vs-context-aware / ablation comparison)
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from app.risk_model.features import FEATURE_COLUMNS, to_feature_frame

DATA_DIR = Path(__file__).parent.parent / "data"
MODEL_PATH = Path(__file__).parent / "risk_model.joblib"
METRICS_PATH = Path(__file__).parent / "metrics.json"


def _load_cases() -> list[dict]:
    return json.loads((DATA_DIR / "patient_cases.json").read_text())


def _eval(model, X, y) -> dict:
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= 0.5).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    try:
        auc = roc_auc_score(y, proba)
    except ValueError:
        auc = float("nan")
    return {
        "accuracy": round(accuracy_score(y, pred), 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "auc": round(auc, 3) if not np.isnan(auc) else None,
    }


def main() -> None:
    cases = _load_cases()
    X = to_feature_frame(cases)
    y = np.array([c["label"] for c in cases])

    X_train, X_rest, y_train, y_rest = train_test_split(X, y, test_size=0.4, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_rest, y_rest, test_size=0.5, random_state=42, stratify=y_rest)

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, class_weight="balanced"),
        "xgboost": XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.1,
            eval_metric="logloss",
            random_state=42,
        ),
    }

    results = {}
    fitted = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        fitted[name] = model
        results[name] = {
            "train": _eval(model, X_train, y_train),
            "val": _eval(model, X_val, y_val),
            "test": _eval(model, X_test, y_test),
        }

    best_name = max(results, key=lambda n: (results[n]["test"]["auc"] or 0))
    best_model = fitted[best_name]

    joblib.dump({"model": best_model, "feature_columns": FEATURE_COLUMNS, "model_name": best_name}, MODEL_PATH)

    METRICS_PATH.write_text(
        json.dumps(
            {
                "best_model": best_name,
                "dataset_size": len(cases),
                "split": {"train": len(X_train), "val": len(X_val), "test": len(X_test)},
                "results": results,
            },
            indent=2,
        )
    )

    print(f"Best model: {best_name}")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
