"""Small SQLite store for reopening previously submitted research runs."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "researchpilot.sqlite3"


def _connect() -> sqlite3.Connection:
    db_path = Path(os.getenv("RESEARCHPILOT_DB_PATH", str(DEFAULT_DB_PATH)))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS research_runs (
            run_id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            response_json TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return connection


def save_run(response: dict[str, Any]) -> None:
    """Insert or update a normalized API response without storing provider secrets."""
    run_id = response.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("A non-empty run_id is required to persist a research run.")
    payload = json.dumps(response, ensure_ascii=False)
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO research_runs (run_id, question, status, created_at, response_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                question = excluded.question,
                status = excluded.status,
                created_at = excluded.created_at,
                response_json = excluded.response_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                run_id,
                str(response.get("question", "")),
                str(response.get("status", "RUNNING")),
                str(response.get("created_at", "")),
                payload,
            ),
        )


def get_run(run_id: str) -> dict[str, Any] | None:
    """Return the last stored API representation for one run."""
    with _connect() as connection:
        row = connection.execute(
            "SELECT response_json FROM research_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
    return json.loads(row["response_json"]) if row else None


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent saved runs, newest first, with a bounded result count."""
    bounded_limit = max(1, min(int(limit), 100))
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT response_json FROM research_runs
            ORDER BY created_at DESC, updated_at DESC
            LIMIT ?
            """,
            (bounded_limit,),
        ).fetchall()
    return [json.loads(row["response_json"]) for row in rows]
