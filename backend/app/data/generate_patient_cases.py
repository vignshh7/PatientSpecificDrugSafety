"""Generates the synthetic patient-case datasets used by this prototype:

1. `patient_cases.json` - ~300 randomized synthetic patients x target-drug
   pairs, with an evidence-derived label used to train/compare the
   structured risk models (Logistic Regression / Random Forest / XGBoost).
   Labels are derived from a deterministic rule tied to each drug's actual
   documented renal/hepatic/elderly keywords (not assigned randomly), plus a
   small noise term so the dataset is not trivially separable.

2. `demo_cases.json` - a curated set of controlled cases (plan section 13)
   for the live demo and for the retrieval/comparison evaluation gold set,
   including contrastive pairs where only one patient factor changes.

IMPORTANT: these are synthetic cases for demonstrating the pipeline. They
are not real clinical outcomes and must not be presented as proof of
clinical effectiveness (see plan section 3 / 31).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from app.data.drugs import DRUGS

random.seed(42)

DATA_DIR = Path(__file__).parent
CONDITION_POOL = [
    "hypertension",
    "type 2 diabetes mellitus",
    "chronic kidney disease",
    "hepatic cirrhosis",
    "atrial fibrillation",
    "osteoarthritis",
    "major depressive disorder",
    "coronary artery disease",
    "asthma",
    "seizure disorder",
    "osteoporosis",
]

DRUG_BY_ID = {d["drug_id"]: d for d in DRUGS}


def _sample_patient(patient_id: str) -> dict:
    age = random.randint(18, 90)
    sex = random.choice(["M", "F"])

    # Correlate lab abnormality likelihood with age for realism.
    renal_impaired = random.random() < (0.15 + 0.35 * (age > 65))
    hepatic_impaired = random.random() < 0.15

    egfr = round(random.uniform(15, 35), 1) if renal_impaired else round(random.uniform(60, 120), 1)
    creatinine = round(random.uniform(1.5, 3.5), 2) if renal_impaired else round(random.uniform(0.6, 1.2), 2)

    if hepatic_impaired:
        ast, alt, bilirubin = (
            round(random.uniform(45, 120), 1),
            round(random.uniform(45, 130), 1),
            round(random.uniform(1.3, 3.0), 1),
        )
    else:
        ast, alt, bilirubin = (
            round(random.uniform(10, 35), 1),
            round(random.uniform(10, 35), 1),
            round(random.uniform(0.2, 1.0), 1),
        )

    n_conditions = random.randint(0, 3)
    conditions = random.sample(CONDITION_POOL, n_conditions)
    if renal_impaired and "chronic kidney disease" not in conditions:
        conditions.append("chronic kidney disease")
    if hepatic_impaired and "hepatic cirrhosis" not in conditions:
        conditions.append("hepatic cirrhosis")

    has_allergy = random.random() < 0.12
    allergies = ["penicillin"] if has_allergy else []

    n_meds = random.randint(0, 2)
    other_drug_ids = [d for d in DRUG_BY_ID if True]
    current_meds = []
    for _ in range(n_meds):
        other = random.choice(other_drug_ids)
        current_meds.append({"name": DRUG_BY_ID[other]["generic_name"], "dose": "standard", "frequency": "daily"})

    prior_adr = random.random() < 0.08

    return {
        "patient_id": patient_id,
        "age": age,
        "sex": sex,
        "conditions": conditions,
        "kidney": {"egfr": egfr, "creatinine": creatinine},
        "liver": {"ast": ast, "alt": alt, "bilirubin": bilirubin},
        "allergies": allergies,
        "current_medications": current_meds,
        "pregnancy_status": "not_applicable",
        "medical_history_text": (
            f"{age}-year-old {sex} with {', '.join(conditions) if conditions else 'no significant comorbidities'}."
        ),
        "prior_adr": prior_adr,
    }


def _label_text_has_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in keywords)


HIGH_RISK_KEYWORDS = ["contraindicat", "avoid", "not recommended", "should not", "severe"]
MODERATE_RISK_KEYWORDS = ["caution", "monitor", "adjust", "reduce", "increase"]


def _evidence_derived_concern_probability(patient: dict, drug: dict) -> float:
    """Deterministic rule tied to the drug's own documented text, not an
    arbitrary random label. Mirrors the clinical-relevance logic used by the
    retrieval reranker/generator so ML labels and RAG outputs are consistent
    with the same evidence base."""
    sections = drug["sections"]
    population = sections.get("use_in_specific_populations", {})
    score = 0.05  # small base rate

    egfr = patient["kidney"]["egfr"]
    renal_text = population.get("renal_impairment", "")
    if egfr < 45 and renal_text:
        if _label_text_has_keyword(renal_text, HIGH_RISK_KEYWORDS) and egfr < 30:
            score += 0.6
        elif _label_text_has_keyword(renal_text, MODERATE_RISK_KEYWORDS):
            score += 0.35

    liver = patient["liver"]
    hepatic_text = population.get("hepatic_impairment", "")
    if (liver["ast"] > 40 or liver["alt"] > 40 or liver["bilirubin"] > 1.2) and hepatic_text:
        if _label_text_has_keyword(hepatic_text, HIGH_RISK_KEYWORDS):
            score += 0.5
        elif _label_text_has_keyword(hepatic_text, MODERATE_RISK_KEYWORDS):
            score += 0.3

    if patient["age"] >= 65 and _label_text_has_keyword(population.get("geriatric_use", ""), MODERATE_RISK_KEYWORDS + HIGH_RISK_KEYWORDS):
        score += 0.2

    if patient["allergies"] and drug["drug_class"].lower().startswith("aminopenicillin"):
        score += 0.6

    if patient.get("prior_adr"):
        score += 0.15

    if patient["current_medications"] and _label_text_has_keyword(sections.get("drug_interactions", ""), ["increase", "risk", "potentiate"]):
        score += 0.1

    # small symmetric noise so the dataset is not perfectly rule-separable
    score += random.uniform(-0.07, 0.07)
    return max(0.0, min(1.0, score))


def build_patient_cases(n_per_drug: int = 25) -> list[dict]:
    cases = []
    case_counter = 0
    for drug in DRUGS:
        for _ in range(n_per_drug):
            case_counter += 1
            patient_id = f"SYN{case_counter:04d}"
            patient = _sample_patient(patient_id)
            prob = _evidence_derived_concern_probability(patient, drug)
            label = 1 if random.random() < prob else 0
            cases.append(
                {
                    "patient": patient,
                    "drug_id": drug["drug_id"],
                    "label_concern_probability_used": round(prob, 3),
                    "label": label,
                }
            )
    random.shuffle(cases)
    return cases


def build_demo_cases() -> list[dict]:
    """Curated, named cases for the live demo and retrieval-eval gold set.
    Includes contrastive pairs (plan section 13) that vary exactly one
    patient factor so the panel can see retrieval/output change accordingly.
    """
    base_elderly_ckd = {
        "age": 72,
        "sex": "F",
        "conditions": ["chronic kidney disease", "hypertension"],
        "kidney": {"egfr": 32, "creatinine": 1.8},
        "liver": {"ast": 22, "alt": 25, "bilirubin": 0.7},
        "allergies": [],
        "current_medications": [{"name": "Lisinopril", "dose": "10 mg", "frequency": "once daily"}],
        "pregnancy_status": "not_applicable",
        "medical_history_text": "72-year-old female with CKD stage 3b and hypertension.",
    }
    normal_renal = {
        **base_elderly_ckd,
        "age": 45,
        "conditions": ["hypertension"],
        "kidney": {"egfr": 95, "creatinine": 0.8},
        "medical_history_text": "45-year-old female with hypertension and normal renal function.",
    }

    young_healthy = {
        "age": 29,
        "sex": "M",
        "conditions": [],
        "kidney": {"egfr": 110, "creatinine": 0.9},
        "liver": {"ast": 18, "alt": 20, "bilirubin": 0.6},
        "allergies": [],
        "current_medications": [],
        "pregnancy_status": "not_applicable",
        "medical_history_text": "29-year-old male, no significant medical history.",
    }

    hepatic_impaired = {
        "age": 58,
        "sex": "M",
        "conditions": ["hepatic cirrhosis"],
        "kidney": {"egfr": 88, "creatinine": 0.9},
        "liver": {"ast": 95, "alt": 110, "bilirubin": 2.1},
        "allergies": [],
        "current_medications": [],
        "pregnancy_status": "not_applicable",
        "medical_history_text": "58-year-old male with Child-Pugh B hepatic cirrhosis.",
    }

    penicillin_allergy = {
        "age": 34,
        "sex": "F",
        "conditions": [],
        "kidney": {"egfr": 100, "creatinine": 0.7},
        "liver": {"ast": 20, "alt": 22, "bilirubin": 0.5},
        "allergies": ["penicillin"],
        "current_medications": [],
        "pregnancy_status": "not_applicable",
        "medical_history_text": "34-year-old female with documented penicillin allergy.",
    }

    polypharmacy_elderly = {
        "age": 80,
        "sex": "M",
        "conditions": ["atrial fibrillation", "coronary artery disease", "hypertension"],
        "kidney": {"egfr": 52, "creatinine": 1.3},
        "liver": {"ast": 25, "alt": 28, "bilirubin": 0.8},
        "allergies": [],
        "current_medications": [
            {"name": "Metoprolol", "dose": "50 mg", "frequency": "twice daily"},
            {"name": "Ibuprofen", "dose": "200 mg", "frequency": "as needed"},
        ],
        "pregnancy_status": "not_applicable",
        "medical_history_text": "80-year-old male with AFib, CAD, hypertension, on multiple medications.",
    }

    incomplete_history = {
        "age": 50,
        "sex": None,
        "conditions": [],
        "kidney": {"egfr": None, "creatinine": None},
        "liver": {"ast": None, "alt": None, "bilirubin": None},
        "allergies": [],
        "current_medications": [],
        "pregnancy_status": None,
        "medical_history_text": "Limited intake information available.",
    }

    cases = [
        {
            "case_id": "A1",
            "label": "Elderly CKD patient - Metformin (reduced renal function)",
            "patient": base_elderly_ckd,
            "drug_id": "metformin",
            "dose": "500 mg",
            "pair_group": "renal_function_metformin",
        },
        {
            "case_id": "A2",
            "label": "Younger patient, normal renal function - Metformin",
            "patient": normal_renal,
            "drug_id": "metformin",
            "dose": "500 mg",
            "pair_group": "renal_function_metformin",
        },
        {
            "case_id": "B1",
            "label": "Elderly CKD patient - Gabapentin (reduced renal function)",
            "patient": base_elderly_ckd,
            "drug_id": "gabapentin",
            "dose": "300 mg",
            "pair_group": "renal_function_gabapentin",
        },
        {
            "case_id": "B2",
            "label": "Young healthy patient - Gabapentin",
            "patient": young_healthy,
            "drug_id": "gabapentin",
            "dose": "300 mg",
            "pair_group": "renal_function_gabapentin",
        },
        {
            "case_id": "C1",
            "label": "Hepatic cirrhosis patient - Atorvastatin",
            "patient": hepatic_impaired,
            "drug_id": "atorvastatin",
            "dose": "20 mg",
            "pair_group": "hepatic_function_atorvastatin",
        },
        {
            "case_id": "C2",
            "label": "Young healthy patient - Atorvastatin",
            "patient": young_healthy,
            "drug_id": "atorvastatin",
            "dose": "20 mg",
            "pair_group": "hepatic_function_atorvastatin",
        },
        {
            "case_id": "D1",
            "label": "Documented penicillin allergy - Amoxicillin",
            "patient": penicillin_allergy,
            "drug_id": "amoxicillin",
            "dose": "500 mg",
            "pair_group": "allergy_amoxicillin",
        },
        {
            "case_id": "D2",
            "label": "No known allergy - Amoxicillin",
            "patient": young_healthy,
            "drug_id": "amoxicillin",
            "dose": "500 mg",
            "pair_group": "allergy_amoxicillin",
        },
        {
            "case_id": "E1",
            "label": "Elderly polypharmacy patient - Ibuprofen (interaction risk)",
            "patient": polypharmacy_elderly,
            "drug_id": "ibuprofen",
            "dose": "200 mg",
            "pair_group": "interaction_ibuprofen",
        },
        {
            "case_id": "E2",
            "label": "Young healthy patient - Ibuprofen",
            "patient": young_healthy,
            "drug_id": "ibuprofen",
            "dose": "200 mg",
            "pair_group": "interaction_ibuprofen",
        },
        {
            "case_id": "F1",
            "label": "Elderly CKD patient - Digoxin (renal toxicity risk)",
            "patient": base_elderly_ckd,
            "drug_id": "digoxin",
            "dose": "0.125 mg",
            "pair_group": "renal_function_digoxin",
        },
        {
            "case_id": "F2",
            "label": "Young healthy patient - Digoxin",
            "patient": young_healthy,
            "drug_id": "digoxin",
            "dose": "0.125 mg",
            "pair_group": "renal_function_digoxin",
        },
        {
            "case_id": "G1",
            "label": "Incomplete medical history - Warfarin (uncertainty demo)",
            "patient": incomplete_history,
            "drug_id": "warfarin",
            "dose": "5 mg",
            "pair_group": "incomplete_history_warfarin",
        },
        {
            "case_id": "H1",
            "label": "Elderly patient - Sertraline + NSAID interaction context",
            "patient": polypharmacy_elderly,
            "drug_id": "sertraline",
            "dose": "50 mg",
            "pair_group": "interaction_sertraline",
        },
    ]
    return cases


def main() -> None:
    patient_cases = build_patient_cases()
    demo_cases = build_demo_cases()

    (DATA_DIR / "patient_cases.json").write_text(json.dumps(patient_cases, indent=2))
    (DATA_DIR / "demo_cases.json").write_text(json.dumps(demo_cases, indent=2))

    print(f"Wrote {len(patient_cases)} synthetic training cases -> patient_cases.json")
    print(f"Wrote {len(demo_cases)} curated demo cases -> demo_cases.json")
    print(f"Positive label rate: {sum(c['label'] for c in patient_cases) / len(patient_cases):.2%}")


if __name__ == "__main__":
    main()
