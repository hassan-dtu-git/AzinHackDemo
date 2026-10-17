"""Conservative candidate-gap extraction from explicit provider evidence."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def _valid_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def extract_gap_candidates(evidence: Any, citations: list[dict[str, str]]) -> list[dict[str, str]]:
    """Extract only explicitly labelled limitations; never infer novelty from silence.

    A candidate is emitted only when a provider evidence item explicitly names a limitation,
    gap, or future-work item. Each candidate needs an associated valid source URL, either on
    the item or in a nested source object. Citation presence alone is not enough.
    """
    if isinstance(evidence, dict):
        items = evidence.get("items") if isinstance(evidence.get("items"), list) else [evidence]
    elif isinstance(evidence, list):
        items = evidence
    else:
        items = []

    candidates: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    text_keys = ("limitation", "limitations", "research_gap", "gap", "future_work", "future_research")
    for item in items:
        if not isinstance(item, dict):
            continue
        description = ""
        for key in text_keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                description = value.strip()
                break
            if isinstance(value, list):
                description = "; ".join(
                    entry.strip() for entry in value
                    if isinstance(entry, str) and entry.strip()
                )
                if description:
                    break
        if not description:
            continue

        source = item.get("source")
        if isinstance(source, dict):
            url = source.get("url") or source.get("source_url") or ""
            title = source.get("title") or source.get("name") or ""
        else:
            url = item.get("source_url") or item.get("url") or ""
            title = item.get("source_title") or item.get("title") or ""

        if not _valid_http_url(url):
            continue
        title = title.strip() if isinstance(title, str) else ""
        key = (description.casefold(), url)
        if key in seen:
            continue
        seen.add(key)
        candidates.append({
            "description": description,
            "source_url": url,
            "source_title": title or url,
            "basis": "Explicit limitation or future-work statement returned by the source/provider.",
        })
        if len(candidates) >= 20:
            break

    return candidates
