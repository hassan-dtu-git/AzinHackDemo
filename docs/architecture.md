# ResearchPilot AI architecture

## Status
Proposed greenfield architecture. The repository was empty at the start of this work; this document describes the target, not pre-existing code.

## Stack
- Frontend: React + Vite + TypeScript.
- Backend: Python 3.12 + FastAPI + Pydantic + HTTPX.
- Persistence: SQLite for the hackathon MVP.
- Provider adapter: TinyFish Research API for asynchronous source-backed synthesis. The Search and Fetch APIs remain alternatives if a faster custom pipeline is needed.
- Tests: pytest; frontend checks and Playwright critical path after the UI is established.

## Pipeline
1. **Plan:** produce bounded sub-questions and search queries.
2. **Search:** discover/fetch public sources through a provider adapter.
3. **Extract:** normalize metadata and extract findings, methods, data, and limitations.
4. **Verify/compare:** associate claims with source evidence and identify agreement/conflict.
5. **Synthesize:** create a report and candidate research gaps with scope caveats.

## Data flow
POST research question → create ResearchRun → execute stages → persist normalized sources/claims/evidence → synthesize validated report → UI polls run status → report and graph link back to original sources.

## Proposed layout
```text
backend/app/{api,models,schemas,services,providers,db}
backend/tests/
frontend/src/{api,components,pages,types,styles}
docs/{prd-researchpilot-mvp.md,architecture.md,api.md,implementation-plan.md,demo-runbook.md}
```

## API
- POST /api/research-runs — validate question and create run.
- GET /api/research-runs/{run_id} — status and progress.
- GET /api/research-runs/{run_id}/report — structured report.
- GET /api/research-runs/{run_id}/evidence-graph — graph nodes and edges.
- GET /api/research-runs/{run_id}/sources — normalized sources.

The current API starts a TinyFish Research API run asynchronously and polls its saved status/report. The provider is beta, account access must be enabled, and deep runs may take several minutes; a separate fast Search + Fetch pipeline may be needed for a short live demo.

## Reliability and trust
Use typed schemas and stable IDs. Never fabricate sources/citations. Treat retrieved text as untrusted. Keep keys on the backend. Bound requests, retries, and content sizes. Label confidence as heuristic. A lack of retrieved sources is a search limitation, not proof of novelty.
