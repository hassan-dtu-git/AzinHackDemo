"""FastAPI application entry point for ResearchPilot AI."""
from __future__ import annotations

import os
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.providers.tinyfish_research import (
    TinyFishAPIError,
    TinyFishConfigurationError,
    TinyFishResearchClient,
    normalize_evidence_graph,
    normalize_research_run,
)

load_dotenv()

app = FastAPI(
    title="ResearchPilot AI API",
    description="Research question orchestration and source-backed reports.",
    version="0.2.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class RunStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class CreateResearchRunRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question must contain non-whitespace characters.")
        return value.strip()


class Citation(BaseModel):
    url: str
    title: str = ""


class ResearchRunResponse(BaseModel):
    run_id: str
    question: str
    status: str
    created_at: datetime
    stages: list[str]
    message: str
    report: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    research_plan: Any = Field(default_factory=list)
    evidence: Any = Field(default_factory=list)
    evidence_graph: dict[str, list[dict[str, Any]]] = Field(default_factory=lambda: {"nodes": [], "edges": []})
    error: Any = None
    iterations: int | None = None


STAGES = ["Plan", "Search", "Extract", "Verify and compare", "Synthesize"]


def get_tinyfish_client() -> TinyFishResearchClient:
    try:
        return TinyFishResearchClient()
    except TinyFishConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


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
    """Start a real TinyFish research run; never fabricate a report."""
    client = get_tinyfish_client()
    try:
        provider_run = client.start(payload.question)
    except TinyFishAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    run_id = str(provider_run["research_run_id"])
    return ResearchRunResponse(
        run_id=run_id,
        question=payload.question,
        status="QUEUED",
        created_at=datetime.now(UTC),
        stages=STAGES,
        message=(
            "TinyFish accepted the research request. Deep research may take several minutes; "
            "this page will check for updates."
        ),
    )


@app.get("/api/research-runs/{run_id}", response_model=ResearchRunResponse)
def get_research_run(run_id: str) -> ResearchRunResponse:
    """Poll the provider for status and its saved report/evidence."""
    client = get_tinyfish_client()
    try:
        provider_payload = client.get_run(run_id)
    except TinyFishAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    normalized = normalize_research_run(provider_payload)
    normalized_status = normalized["status"]
    if normalized_status not in {item.value for item in RunStatus}:
        normalized_status = "RUNNING"

    question = normalized["question"] or "Research question"
    return ResearchRunResponse(
        run_id=normalized["run_id"] or run_id,
        question=question,
        status=normalized_status,
        created_at=datetime.now(timezone.utc),
        stages=STAGES,
        message=normalized["message"],
        report=normalized["report"] or None,
        citations=normalized["citations"],
        research_plan=normalized["research_plan"],
        evidence=normalized["evidence"],
        evidence_graph=normalize_evidence_graph(normalized["evidence"], normalized["citations"]),
        error=normalized["error"],
        iterations=normalized["iterations"] if isinstance(normalized["iterations"], int) else None,
    )
