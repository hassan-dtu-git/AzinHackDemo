# API contract (proposed)

Base path: /api

## POST /research-runs
Request:
```json
{ "question": "Can AI detect river pollution using satellite imagery?" }
```
Response: 202 Accepted
```json
{ "run_id": "uuid", "status": "queued" }
```

Reject whitespace-only questions and questions exceeding the configured maximum length.

## GET /research-runs/{run_id}
Returns run ID, question, status, current stage, source counts, limitations and safe error details.

## GET /research-runs/{run_id}/report
Returns report sections after synthesis. If not ready, return an appropriate status rather than an invented report.

## GET /research-runs/{run_id}/evidence-graph
Returns claim/source nodes and labelled supports, contradicts, or contextualizes edges.

## GET /research-runs/{run_id}/sources
Returns normalized source metadata and content-access status.

## Error behavior
Use standard HTTP status codes and a stable JSON error shape. Never return API keys, raw provider secrets, or full internal exception traces. Provider-specific response fields must be normalized behind adapters before reaching the frontend.
