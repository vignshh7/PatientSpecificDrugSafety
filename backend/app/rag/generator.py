"""Answer generation: a deterministic, always-available template backend plus
an optional live-LLM backend.

Default ("template"): assembles the structured JSON answer directly from the
retrieved, cited evidence using rule-based synthesis. This guarantees the
system is fully demoable offline, with zero hallucination risk, and keeps
every claim traceable to a specific chunk id by construction.

Live LLM: if OPENROUTER_API_KEY is set (backend/.env) and `use_llm=true` is
requested, sends the structured prompt (app.rag.prompt_builder) to a model
via OpenRouter's chat-completions API (OPENROUTER_MODEL, default
anthropic/claude-haiku-4.5) and parses its JSON response, falling back to
the template path if the call fails, times out, or the response doesn't
parse. This keeps the system usable even if the API key is missing or the
network is unavailable at demo time.
"""
from __future__ import annotations

import json
import logging
import os
import re

from app import console_log as clog
from app.retrieval.query_builder import is_elderly, is_hepatic_impaired, is_renal_impaired

logger = logging.getLogger(__name__)

HIGH_RISK_KEYWORDS = ["contraindicat", "avoid", "not recommended", "should not", "severe", "fatal"]
MODERATE_RISK_KEYWORDS = ["caution", "monitor", "adjust", "reduce", "increase", "risk"]

EFFECT_SECTIONS = {"Indications and Usage", "Adverse Reactions"}
WARNING_SECTIONS = {"Contraindications", "Warnings and Precautions"}
DOSE_SECTIONS = {"Dosage Considerations"}
POPULATION_TAGS = {"renal_impairment", "hepatic_impairment", "geriatric_use", "pregnancy"}


def _cited(evidence_item: dict) -> str:
    return f"{evidence_item['text']} [{evidence_item['chunk_id']}]"


def _matched_population_chunks(patient: dict, evidence: list[dict]) -> list[dict]:
    matched = []
    for e in evidence:
        tag = e.get("population_tag")
        rel_tags = set(e.get("relevance_tags", []))
        if tag == "renal_impairment" and is_renal_impaired(patient):
            matched.append(e)
        elif tag == "hepatic_impairment" and is_hepatic_impaired(patient):
            matched.append(e)
        elif tag == "geriatric_use" and is_elderly(patient):
            matched.append(e)
        elif "renal_impairment" in rel_tags and is_renal_impaired(patient):
            matched.append(e)
        elif "hepatic_impairment" in rel_tags and is_hepatic_impaired(patient):
            matched.append(e)
        elif "elderly" in rel_tags and is_elderly(patient):
            matched.append(e)
        elif "allergy" in rel_tags and patient.get("allergies"):
            matched.append(e)
        elif "interactions" in rel_tags and patient.get("current_medications"):
            matched.append(e)
    return matched


def _classify_category(matched_chunks: list[dict], evidence_count: int) -> str:
    if evidence_count == 0:
        return "indeterminate"
    high = any(
        any(kw in m["text"].lower() for kw in HIGH_RISK_KEYWORDS) for m in matched_chunks
    )
    if high:
        return "higher_concern"
    moderate = any(
        any(kw in m["text"].lower() for kw in MODERATE_RISK_KEYWORDS) for m in matched_chunks
    )
    if moderate or matched_chunks:
        return "moderate_concern"
    return "lower_concern"


def _reasoning_summary(
    patient: dict, drug_name: str, matched_chunks: list[dict], category: str, mode: str
) -> str:
    if mode == "baseline":
        return (
            f"Drug-only baseline for {drug_name}: retrieval and synthesis used no "
            "patient-specific context (age, conditions, renal/hepatic function were not "
            "incorporated into the query or interpretation). This result reflects generic "
            "label/literature information only and is not an individualized assessment."
        )

    age = patient.get("age")
    conditions = patient.get("conditions") or []
    kidney = patient.get("kidney") or {}
    liver = patient.get("liver") or {}

    factors = []
    if age is not None:
        factors.append(f"age {age}")
    if conditions:
        factors.append(f"conditions: {', '.join(conditions)}")
    if kidney.get("egfr") is not None:
        factors.append(f"eGFR {kidney['egfr']}")
    if liver.get("ast") is not None or liver.get("alt") is not None:
        factors.append("liver function labs on file")

    factor_text = "; ".join(factors) if factors else "no structured risk factors provided"

    if matched_chunks:
        driver_sections = sorted({m["section"] for m in matched_chunks})
        match_text = (
            f"{len(matched_chunks)} retrieved passage(s) in [{', '.join(driver_sections)}] "
            "matched this patient's specific profile, which is the primary driver of the "
            "assigned context category."
        )
    else:
        match_text = (
            "No retrieved passage specifically matched this patient's structured risk "
            "factors beyond generic drug information."
        )

    return (
        f"For {drug_name}, patient profile: {factor_text}. {match_text} "
        f"Overall contextual category: {category.replace('_', ' ')}."
    )


def generate_template(patient: dict, drug_name: str, evidence: list[dict], mode: str) -> dict:
    documented_effects = [_cited(e) for e in evidence if e["section"] in EFFECT_SECTIONS]
    warnings = [_cited(e) for e in evidence if e["section"] in WARNING_SECTIONS]
    dose_context = [_cited(e) for e in evidence if e["section"] in DOSE_SECTIONS]

    matched_chunks = _matched_population_chunks(patient, evidence) if mode != "baseline" else []
    patient_relevant_risks = [_cited(e) for e in matched_chunks]
    dose_context += [
        _cited(e) for e in matched_chunks if e.get("population_tag") in {"renal_impairment", "hepatic_impairment"}
    ]

    category = _classify_category(matched_chunks, len(evidence)) if mode != "baseline" else "indeterminate"
    reasoning = _reasoning_summary(patient, drug_name, matched_chunks, category, mode)

    evidence_links = sorted({e["chunk_id"] for e in evidence})

    return {
        "documented_effects": documented_effects,
        "patient_relevant_risks": patient_relevant_risks,
        "contraindications_or_warnings": warnings,
        "dose_context": list(dict.fromkeys(dose_context)),
        "uncertainty_flags": [],
        "missing_information": [],
        "evidence_links": evidence_links,
        "overall_context_category": category,
        "reasoning_summary": reasoning,
    }


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# A free-tier reasoning model as the default: it works with a $0-balance
# OpenRouter key (no payment method required), unlike most paid models. It
# spends part of its own output-token budget on internal reasoning before
# writing the final JSON answer, so it needs a larger max_tokens/timeout
# than a non-reasoning model would.
DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


def _call_openrouter(system_prompt: str, user_prompt: str) -> dict | None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        clog.sub("OpenRouter: no OPENROUTER_API_KEY set -> falling back to template")
        logger.warning("OPENROUTER_API_KEY not set; falling back to template.")
        return None
    try:
        import requests
    except ImportError:
        return None

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
    clog.sub(f"OpenRouter: POST chat/completions model={model} ...")
    try:
        with clog.Timer() as t:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": 8000,
                    "temperature": 0.2,
                },
                timeout=90,
            )
        clog.sub(f"OpenRouter: HTTP {response.status_code} in {t.elapsed:.2f}s")
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            clog.sub("OpenRouter: response had no JSON object -> falling back to template")
            logger.warning("OpenRouter response had no JSON object; falling back to template.")
            return None
        clog.sub(f"OpenRouter: parsed JSON answer ({len(text)} chars)")
        return json.loads(match.group(0))
    except Exception as exc:
        clog.sub(f"OpenRouter: call failed ({exc}) -> falling back to template")
        logger.warning("OpenRouter call failed; falling back to template.", exc_info=True)
        return None


def _try_generate_llm(patient: dict, drug_name: str, evidence: list[dict], mode: str) -> dict | None:
    from app.rag.prompt_builder import build_baseline_prompt, build_full_prompt

    if mode == "baseline":
        prompt = build_baseline_prompt(drug_name, evidence)
    else:
        prompt = build_full_prompt(patient, drug_name, evidence)

    return _call_openrouter(prompt["system"], prompt["user"])


def generate(
    patient: dict, drug_name: str, evidence: list[dict], mode: str = "context", use_llm: bool = False
) -> tuple[dict, str]:
    if use_llm:
        llm_result = _try_generate_llm(patient, drug_name, evidence, mode)
        if llm_result is not None:
            model_name = os.environ.get("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
            return llm_result, f"llm:{model_name}"

    return generate_template(patient, drug_name, evidence, mode), "template"
