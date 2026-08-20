from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ssi import classify_student, generate_recommendation

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "student_model.pkl"

FEATURES = [
    "Attendance Rate (%)",
    "Daily Study Hours",
    "Internal Assessment (%)",
    "Assignment Score (%)",
    "Previous Semester Score (%)",
]

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    model = None
    MODEL_LOAD_ERROR = str(exc)
else:
    MODEL_LOAD_ERROR = None


class StudentInput(BaseModel):
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    attendance: float = Field(..., ge=0, le=100)
    study_hours: float = Field(..., ge=0, le=24)
    internal_assessment: float = Field(..., ge=0, le=100)
    assignment_score: float = Field(..., ge=0, le=100)
    previous_semester_score: float = Field(..., ge=0, le=100)


class PredictionResponse(BaseModel):
    student_id: Optional[str]
    student_name: Optional[str]
    predicted_score: float
    classification: str
    risk_level: str
    recommendation: str


app = FastAPI(
    title="Smart Student Performance Prediction API",
    version="1.0.0",
    description="Prediction API for the Smart Student Performance n8n Agent.",
)


@app.get("/health")
def health():
    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "error": MODEL_LOAD_ERROR,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(student: StudentInput):
    if model is None:
        raise HTTPException(
            status_code=500,
            detail=f"Model could not be loaded: {MODEL_LOAD_ERROR}",
        )

    values = np.array([[
        student.attendance,
        student.study_hours,
        student.internal_assessment,
        student.assignment_score,
        student.previous_semester_score,
    ]], dtype=float)

    try:
        predicted = float(model.predict(values)[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    predicted = round(float(np.clip(predicted, 0, 100)), 2)
    classification, risk_level = classify_student(predicted)

    recommendation = generate_recommendation(
        risk_level=risk_level,
        study_hours=student.study_hours,
        attendance=student.attendance,
        internal_marks=student.internal_assessment,
        assignment_score=student.assignment_score,
        previous_score=student.previous_semester_score,
    )

    return PredictionResponse(
        student_id=student.student_id,
        student_name=student.student_name,
        predicted_score=predicted,
        classification=classification,
        risk_level=risk_level,
        recommendation=recommendation,
    )


@app.get("/")
def root():
    return {
        "service": "Smart Student Performance Prediction API",
        "endpoints": ["/health", "/predict"],
    }
