"""SQLite persistence (plan: "for a very small prototype: SQLite") for
stored assessments and evaluator feedback (plan section 24-25: ASSESSMENT
TABLE, CLAIM TABLE, POST /feedback)."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import JSON, Column, DateTime, String, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = Path(__file__).parent / "app.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class AssessmentRecord(Base):
    __tablename__ = "assessments"
    assessment_id = Column(String, primary_key=True)
    patient_id = Column(String, nullable=True)
    drug_id = Column(String)
    mode = Column(String)
    risk_category = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


class FeedbackRecord(Base):
    __tablename__ = "feedback"
    id = Column(String, primary_key=True)
    assessment_id = Column(String)
    rating = Column(String)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


def init_db() -> None:
    Base.metadata.create_all(engine)


def save_assessment(result: dict) -> None:
    session = SessionLocal()
    try:
        record = AssessmentRecord(
            assessment_id=result["assessment_id"],
            patient_id=(result.get("patient_id")),
            drug_id=result["drug"]["drug_id"],
            mode=result["mode"],
            risk_category=result["risk_category"],
            payload=json.loads(json.dumps(result, default=str)),
        )
        session.merge(record)
        session.commit()
    finally:
        session.close()


def get_assessment(assessment_id: str) -> dict | None:
    session = SessionLocal()
    try:
        record = session.get(AssessmentRecord, assessment_id)
        return record.payload if record else None
    finally:
        session.close()


def save_feedback(feedback_id: str, assessment_id: str, rating: str, notes: str | None) -> None:
    session = SessionLocal()
    try:
        record = FeedbackRecord(id=feedback_id, assessment_id=assessment_id, rating=rating, notes=notes)
        session.add(record)
        session.commit()
    finally:
        session.close()
