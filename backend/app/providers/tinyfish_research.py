"""Adapter for TinyFish's asynchronous source-backed Research API."""
from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = "https://agent.tinyfish.ai"


class TinyFishConfigurationError(RuntimeError):
    """Raised when the TinyFish API key is not configured."""


class TinyFishAPIError(RuntimeError):
    """Raised when TinyFish rejects or cannot process a request."""


class TinyFishResearchClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = (api_key or os.getenv("TINYFISH_API_KEY", "")).strip()
        if not self.api_key:
            raise TinyFishConfigurationError(
                "TINYFISH_API_KEY is missing. Add it to backend/.env before starting live research."
            )

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def start(self, query: str) -> dict[str, Any]:
        """Enqueue a deep research run; do not retry this POST automatically."""
        try:
            response = httpx.post(
                f"{BASE_URL}/v1/automation/run-research-async",
                headers=self.headers,
                json={"query": query, "mode": "deep", "output_language": "en"},
                timeout=20.0,
            )
        except httpx.HTTPError as exc:
            raise TinyFishAPIError("Could not connect to TinyFish. Check network connectivity.") from exc

        if response.is_error:
            raise self._to_error(response)
        payload = self._json_object(response)
        if not payload.get("research_run_id"):
            raise TinyFishAPIError("TinyFish accepted no research run ID; check the provider response.")
        return payload

    def get_run(self, research_run_id: str) -> dict[str, Any]:
        try:
            response = httpx.get(
                f"{BASE_URL}/v1/research-run/{research_run_id}",
                headers=self.headers,
                timeout=20.0,
            )
        except httpx.HTTPError as exc:
            raise TinyFishAPIError("Could not retrieve the TinyFish research status.") from exc

        if response.is_error:
            raise self._to_error(response)
        return self._json_object(response)

    @staticmethod
    def _json_object(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise TinyFishAPIError("TinyFish returned an invalid JSON response.") from exc
        if not isinstance(payload, dict):
            raise TinyFishAPIError("TinyFish returned an unexpected response shape.")
        return payload

    @staticmethod
    def _to_error(response: httpx.Response) -> TinyFishAPIError:
        message = "TinyFish request failed."
        try:
            payload = response.json()
            error = payload.get("error", {}) if isinstance(payload, dict) else {}
            if isinstance(error, dict) and isinstance(error.get("message"), str):
                message = error["message"]
            elif isinstance(payload, dict) and isinstance(payload.get("detail"), str):
                message = payload["detail"]
        except ValueError:
            pass

        if response.status_code == 401:
            message = "TinyFish rejected the API key. Check TINYFISH_API_KEY."
        elif response.status_code == 403:
            message = (
                "TinyFish denied access. Check that the key is valid and Research API access "
                "is enabled for the account."
            )
        elif response.status_code == 429:
            message = "TinyFish rate limit or research quota reached. Check the account limits before retrying."
        return TinyFishAPIError(message)


def normalize_research_run(payload: dict[str, Any], fallback_question: str = "") -> dict[str, Any]:
    """Convert the provider response to the stable API contract used by the UI."""
    status = str(payload.get("status") or "RUNNING").upper()
    deep_result = payload.get("deep_result")
    if not isinstance(deep_result, dict):
        deep_result = {}
    result_value = deep_result.get("result") or payload.get("result") or ""
    report = result_value if isinstance(result_value, str) else ""

    raw_citations = deep_result.get("citations") or payload.get("citations") or []
    citations: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    if isinstance(raw_citations, list):
        for item in raw_citations:
            if isinstance(item, str):
                url, title = item, ""
            elif isinstance(item, dict):
                url = item.get("url") or item.get("source_url") or ""
                title = item.get("title") or item.get("name") or ""
            else:
                continue
            if isinstance(url, str) and url.startswith(("https://", "http://")) and url not in seen_urls:
                citations.append({"url": url, "title": title if isinstance(title, str) else ""})
                seen_urls.add(url)

    plan = payload.get("research_plan")
    evidence = payload.get("evidence")
    safe_evidence = evidence if isinstance(evidence, (list, dict)) else []

    return {
        "run_id": str(payload.get("research_run_id") or payload.get("id") or ""),
        "question": str(payload.get("query") or fallback_question),
        "status": status,
        "report": report,
        "citations": citations,
        "research_plan": plan if isinstance(plan, (list, dict)) else [],
        "evidence": safe_evidence,
        "error": payload.get("error"),
        "iterations": payload.get("iterations"),
        "message": (
            "Research completed." if status == "COMPLETED"
            else "Research failed; inspect the provider error and any partial results."
            if status in {"FAILED", "CANCELLED", "TIMED_OUT"}
            else "TinyFish research is running. Deep research may take several minutes."
        ),
    }


def normalize_evidence_graph(
    evidence: Any, citations: list[dict[str, str]]
) -> dict[str, list[dict[str, Any]]]:
    """Build a conservative graph from explicit provider evidence only.

    Citation-only sources become source nodes. Claim nodes and source-to-claim edges are
    created only when an evidence item explicitly contains claim text and a source URL.
    Unknown relationships are labelled "associated"; contradiction/support labels are
    retained only when the provider explicitly supplies them.
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    source_ids: dict[str, str] = {}
    claim_ids: dict[str, str] = {}

    def add_source(url: str, title: str = "") -> str:
        if url not in source_ids:
            source_id = f"source-{len(source_ids) + 1}"
            source_ids[url] = source_id
            nodes.append({
                "id": source_id,
                "type": "source",
                "label": title.strip() or url,
                "url": url,
            })
        elif title.strip():
            for node in nodes:
                if node["id"] == source_ids[url] and node["label"] == url:
                    node["label"] = title.strip()
                    break
        return source_ids[url]

    for citation in citations:
        url = citation.get("url", "")
        if isinstance(url, str) and url.startswith(("https://", "http://")):
            add_source(url, str(citation.get("title") or ""))

    if isinstance(evidence, dict):
        items = evidence.get("items") if isinstance(evidence.get("items"), list) else [evidence]
    elif isinstance(evidence, list):
        items = evidence
    else:
        items = []

    allowed_relations = {
        "supports", "contradicts", "mentions", "associated", "qualifies"
    }
    for item in items:
        if not isinstance(item, dict):
            continue
        claim = next(
            (
                item.get(key).strip()
                for key in ("claim", "statement", "finding", "text")
                if isinstance(item.get(key), str) and item.get(key).strip()
            ),
            "",
        )
        if not claim:
            continue

        source_value = item.get("source")
        if isinstance(source_value, dict):
            url = source_value.get("url") or source_value.get("source_url") or ""
            title = source_value.get("title") or source_value.get("name") or ""
        else:
            url = item.get("source_url") or item.get("url") or ""
            title = item.get("source_title") or item.get("title") or ""
        if not isinstance(url, str) or not url.startswith(("https://", "http://")):
            continue

        source_id = add_source(url, title if isinstance(title, str) else "")
        if claim not in claim_ids:
            claim_id = f"claim-{len(claim_ids) + 1}"
            claim_ids[claim] = claim_id
            nodes.append({"id": claim_id, "type": "claim", "label": claim})
        else:
            claim_id = claim_ids[claim]

        relation_value = item.get("relation") or item.get("relationship") or item.get("stance")
        relation = (
            relation_value.strip().lower()
            if isinstance(relation_value, str) and relation_value.strip().lower() in allowed_relations
            else "associated"
        )
        edge = {"source": source_id, "target": claim_id, "relation": relation}
        if edge not in edges:
            edges.append(edge)

    return {"nodes": nodes, "edges": edges}
