# ResearchPilot AI

**Ask a research question. Get an evidence-backed report.**

ResearchPilot AI is a hackathon MVP by Team ByteForge for AzinHack. The target product plans research queries, discovers public sources, extracts structured evidence, compares claims, assesses candidate research gaps, and presents a cited report with an evidence graph.

> **Current status:** the frontend and API are wired to TinyFish Research API. Live runs require a valid `TINYFISH_API_KEY` and Research API access on the account. The provider can take several minutes; the UI polls for status and displays the returned report/citations. The API stores run snapshots in SQLite and the UI lists recent runs for reopening. Evidence graph links are conservative and depend on explicit provider evidence. Candidate research gaps are surfaced only when provider evidence explicitly labels a limitation, gap, or future-work statement and links it to a valid source URL; they are not novelty claims.

## Planned stack

- Frontend: React + Vite + TypeScript
- Backend: Python 3.12 + FastAPI + Pydantic
- Storage: SQLite stores recent research runs locally so they can be reopened
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


### TinyFish account notes

The app uses the TinyFish Research API (currently documented as beta). Create a key at https://agent.tinyfish.ai/api-keys and confirm Research API access is enabled for that account. TinyFish documents deep runs as typically taking 5–20 minutes and Research beta limits as five runs per account per Pacific calendar day by default, so keep a known-good completed run ready for the live demo. Search/Fetch are faster alternatives if the team later adds its own extraction/synthesis layer.

### Frontend

In a second terminal:

~~~bash
cd frontend
npm install
npm run dev
~~~

Open http://localhost:5173. Vite proxies `/api` and `/health` requests to the backend on port 8000.

### Run history storage

Research run snapshots are stored in `backend/researchpilot.sqlite3` by default. Override the location with `RESEARCHPILOT_DB_PATH` if needed. The database is local and should not be committed. The history endpoint returns the latest 20 saved runs by default.

## Tests

With the backend virtual environment activated:

~~~bash
cd backend
pytest
ruff check .
~~~

GitHub Actions runs the backend tests, Ruff, and frontend production build on each push. The code-editing session itself cannot execute the app locally, so use the CI results as the current validation record.

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
