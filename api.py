"""
Module 3/4 - FastAPI backend.

Exposes the multi-agent pipeline as HTTP endpoints so the Streamlit
frontend (or anything else) can call it over the network instead of
running graph.py as a script each time.

Run with:
    uvicorn src.api:app --reload --port 8000
"""
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src import graph
from src.agents import qa_agent, schedule_agent

app = FastAPI(
    title="EduPath AI API",
    description="Multi-agent RAG-based career & education advisor for Tamil Nadu students",
    version="0.3.0",
)


class AdviseRequest(BaseModel):
    student_text: str


class AdviseResponse(BaseModel):
    profile: dict
    recommendation: str
    pathway: str
    retrieved: Optional[dict] = None
    scholarships: Optional[List[dict]] = None
    practice_plan: Optional[dict] = None


class QARequest(BaseModel):
    question: str
    category: Optional[str] = None  # optional: "career" | "course" | "scholarship" | "scheme"


class QAResponse(BaseModel):
    answer: str


class ScheduleRequest(BaseModel):
    pathway: str
    target_date: str  # ISO format, e.g. "2027-08-15"


class ScheduleResponse(BaseModel):
    schedule: str


@app.get("/")
def health_check():
    """Simple endpoint to confirm the API is running."""
    return {"status": "ok", "service": "EduPath AI", "version": "0.3.0"}


@app.post("/advise", response_model=AdviseResponse)
def advise(request: AdviseRequest):
    """
    Runs the full multi-agent pipeline:
    Profile -> Retrieval -> Scholarship Evaluation -> Recommendation -> Practice Plan -> Pathway.
    """
    try:
        result = graph.run_advisor(request.student_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AdviseResponse(
        profile=result["profile"],
        recommendation=result["recommendation"],
        pathway=result["pathway"],
        retrieved=result.get("retrieved"),
        scholarships=result.get("scholarships"),
        practice_plan=result.get("practice_plan"),
    )


@app.post("/qa", response_model=QAResponse)
def qa(request: QARequest):
    """
    Standalone Q&A endpoint - for quick questions that don't need full
    profiling, e.g. "What's the income limit for PRAGATI scholarship?"
    """
    try:
        answer = qa_agent.answer_question(request.question, category=request.category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QAResponse(answer=answer)


@app.post("/schedule", response_model=ScheduleResponse)
def schedule(request: ScheduleRequest):
    """
    Converts an already-generated pathway roadmap into a concrete,
    dated month-by-month schedule based on the student's target goal date.
    """
    try:
        result = schedule_agent.generate_schedule(request.pathway, request.target_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ScheduleResponse(schedule=result)
