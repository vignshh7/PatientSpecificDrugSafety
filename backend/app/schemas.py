"""Pydantic request schemas for the API (plan section 25). Response bodies
are returned as plain dicts from app.pipeline.analyze(), which already
matches the documented response shape, so only request bodies are modeled
strictly here.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Kidney(BaseModel):
    egfr: float | None = None
    creatinine: float | None = None


class Liver(BaseModel):
    ast: float | None = None
    alt: float | None = None
    bilirubin: float | None = None


class CurrentMedication(BaseModel):
    name: str
    dose: str | None = None
    frequency: str | None = None


class Patient(BaseModel):
    patient_id: str | None = None
    age: int | None = None
    sex: str | None = None
    conditions: list[str] = Field(default_factory=list)
    kidney: Kidney = Field(default_factory=Kidney)
    liver: Liver = Field(default_factory=Liver)
    allergies: list[str] = Field(default_factory=list)
    current_medications: list[CurrentMedication] = Field(default_factory=list)
    pregnancy_status: str | None = None
    medical_history_text: str | None = None
    prior_adr: bool = False


class TargetDrug(BaseModel):
    drug_id: str
    dose: str | None = None


class AnalyzeRequest(BaseModel):
    patient: Patient
    drug: TargetDrug
    use_llm: bool = True


class FeedbackRequest(BaseModel):
    assessment_id: str
    rating: str  # correct | partially_correct | incorrect | unsupported_citation
    notes: str | None = None
