"""FastAPI application entry point for ResearchPilot AI.

Live TinyFish/LLM orchestration is intentionally not faked. This initial
foundation validates input and returns an explicit pending-integration status.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="ResearchPilot AI API",
    description="An evidence-backed research report pipeline. Provider integration is in progress.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class RunStatus(StrEnum):
    PENDING_INTEGRATION = "pending_integration"


class CreateResearchRunRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question must contain non-whitespace characters.")
        return value.strip()


class ResearchRunResponse(BaseModel):
    run_id: str
    question: str
    status: RunStatus
    created_at: datetime
    stages: list[str]
    message: str


@app.get("/health")
def health() -> dict[str, str]:
    """Simple readiness endpoint."""
    return {"status": "ok", "service": "researchpilot-api"}


@app.post(
    "/api/research-runs",
    response_model=ResearchRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_research_run(payload: CreateResearchRunRequest) -> ResearchRunResponse:
    """Validate a question and expose the agreed run contract.

    This endpoint does not claim to perform live research yet. The next
    implementation step wires in verified TinyFish and LLM provider adapters.
    """
    return ResearchRunResponse(
        run_id=str(uuid4()),
        question=payload.question,
        status=RunStatus.PENDING_INTEGRATION,
        created_at=datetime.now(timezone.utc),
        stages=["Plan", "Search", "Extract", "Verify and compare", "Synthesize"],
        message=(
            "The API foundation is running, but live research providers are not configured yet. "
            "No sources or findings have been generated."
        ),
    )
