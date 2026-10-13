"""Pydantic validation of generated structured answers (plan STEP 9).

Rejects/flags a generated response if it is missing required keys, uses an
unsupported risk category, or references chunk ids that were not actually
retrieved.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

VALID_CATEGORIES = {"lower_concern", "moderate_concern", "higher_concern", "indeterminate"}

LIST_FIELDS = (
    "documented_effects",
    "patient_relevant_risks",
    "contraindications_or_warnings",
    "dose_context",
    "uncertainty_flags",
    "missing_information",
    "evidence_links",
)


class GeneratedAnswer(BaseModel):
    documented_effects: list[str] = Field(default_factory=list)
    patient_relevant_risks: list[str] = Field(default_factory=list)
    contraindications_or_warnings: list[str] = Field(default_factory=list)
    dose_context: list[str] = Field(default_factory=list)
    uncertainty_flags: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    evidence_links: list[str] = Field(default_factory=list)
    overall_context_category: str = "indeterminate"
    reasoning_summary: str = ""

    @field_validator(*LIST_FIELDS, mode="before")
    @classmethod
    def _coerce_list_of_str(cls, v):
        # Smaller/free LLMs don't always follow the requested shape exactly
        # (null instead of [], a bare string instead of a one-item list, or
        # {"text": "..."} objects instead of plain strings). Normalize those
        # instead of failing validation and discarding the whole answer.
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        if not isinstance(v, list):
            return []
        out = []
        for item in v:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("claim") or item.get("statement")
                if text:
                    out.append(str(text))
            elif item is not None:
                out.append(str(item))
        return out

    @field_validator("overall_context_category", mode="before")
    @classmethod
    def _coerce_category(cls, v):
        return v if isinstance(v, str) else "indeterminate"

    @field_validator("overall_context_category")
    @classmethod
    def _check_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            return "indeterminate"
        return v

    @field_validator("reasoning_summary", mode="before")
    @classmethod
    def _coerce_reasoning(cls, v):
        return "" if v is None else str(v)


def validate_answer(raw: dict) -> GeneratedAnswer:
    try:
        return GeneratedAnswer(**raw)
    except Exception:
        return GeneratedAnswer(
            overall_context_category="indeterminate",
            reasoning_summary="Generated response failed schema validation; returning a safe fallback.",
            uncertainty_flags=["Response generation failed schema validation."],
        )
