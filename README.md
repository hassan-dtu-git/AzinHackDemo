# ResearchPilot AI

**Ask a research question. Get an evidence-backed report.**

ResearchPilot AI is a hackathon MVP by Team ByteForge for AzinHack. The target product plans research queries, discovers public sources, extracts structured evidence, compares claims, assesses candidate research gaps, and presents a cited report with an evidence graph.

> **Current status:** the frontend and API are wired to TinyFish Research API. Live runs require a valid `TINYFISH_API_KEY` and Research API access on the account. The provider can take several minutes; the UI polls for status and displays the returned report/citations. Evidence graph and deeper local analysis are still in progress.

## Planned stack

- Frontend: React + Vite + TypeScript
- Backend: Python 3.12 + FastAPI + Pydantic
- Storage: SQLite planned for the MVP
- Discovery and cited synthesis: TinyFish Research API (beta; account access/quota may apply)

## Run locally

### Backend

Python 3.12 is recommended. From the repository root, copy `.env.example` to `backend/.env` and set `TINYFISH_API_KEY` from your TinyFish dashboard. For PowerShell run `Copy-Item .env.example backend/.env`; for macOS/Linux run `cp .env.example backend/.env`. Never commit the real key.

~~~bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
~~~

Health check: http://127.0.0.1:8000/health  
API schema: http://127.0.0.1:8000/docs

### Frontend

In a second terminal:

~~~bash
cd frontend
npm install
npm run dev
~~~

Open http://localhost:5173. Vite proxies `/api` and `/health` requests to the backend on port 8000.

### Tests

With the backend virtual environment activated:

~~~bash
cd backend
pytest
ruff check .
~~~

These commands are documented from the configured manifests but have not been executed in this hosted editing session.

## Project documents

- [MVP PRD](docs/prd-researchpilot-mvp.md)
- [Architecture](docs/architecture.md)
- [API contract](docs/api.md)
- [Implementation plan and demo runbook](docs/implementation-plan.md)
- [AI coding assistant instructions](CLAUDE.md)

## Evidence integrity rules

- Never invent sources, citations, findings, dates, datasets, or source content.
- Link report claims to validated evidence or label them as inference.
- Lack of search results is not proof of global novelty.
- Respect public access; do not bypass logins or paywalls.
- Keep provider credentials on the backend and out of version control.
