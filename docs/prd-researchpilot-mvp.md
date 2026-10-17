# PRD: ResearchPilot AI MVP

**Status:** Draft for implementation · **Date:** 17 October 2026

## Problem and goal
Students and researchers spend time discovering papers/datasets, comparing methods and results, checking claims against original sources, and identifying unanswered questions. ResearchPilot turns one question into a structured, evidence-backed report where claims link to sources and uncertainty is visible.

Demo question: “Can AI detect river pollution using satellite imagery?”

## Target users
- Students exploring scientific/technical topics.
- Researchers conducting an initial literature scan.
- Hackathon judges evaluating a transparent multi-stage agent.

## MVP scope
1. Research question input and validation.
2. Visible stages: Plan, Search, Extract, Verify/Compare, Synthesize.
3. Live discovery/fetch of public sources through TinyFish after its current API contract and credentials are verified.
4. Structured extraction of findings, methods, datasets, dates, and limitations when present.
5. Basic claim grouping and support/contradiction relationships.
6. Cited report with scope, findings, methods/data, conflicts, candidate gaps, and source list.
7. Evidence graph for major claims.
8. Loading, partial-result, empty-result, inaccessible-source, timeout, and provider-error states.
9. Clearly labelled backup demo run if live search fails.

Out of scope: global novelty claims, exhaustive literature coverage, custom model training, accounts/billing, paywall/login bypass, paper-to-prototype mode, cross-field idea links, and report export unless the core loop is stable.

## User stories and acceptance criteria
- **Submit:** empty questions are rejected; a run visibly progresses through all five stages; failures are not presented as success.
- **Discover:** sources include URL/title when available, retrieval time, and access status; duplicates are removed; no sources are invented.
- **Extract:** missing metadata is marked unknown/not reported; claims link to source IDs and evidence excerpts where available; one failed source does not abort the run.
- **Compare:** relationships are labelled supports/contradicts/contextualizes with rationale; confidence is an explained heuristic, not a scientific probability.
- **Assess gaps:** explicit future work, methodological limitations, conflicting results, coverage gaps, and search-coverage gaps are distinguished. No results do not prove global novelty.
- **Report:** every factual claim is linked to a source or labelled inference; citations open original URLs; search scope and limitations are shown.
- **Graph:** claim/source nodes and labelled edges are selectable; a readable list alternative remains available.

## Success metrics
- Rehearsed demo completes in under 2 minutes when provider latency permits.
- Aim for at least five usable sources when available; disclose lower coverage.
- Every factual demo claim is traceable or labelled inference.
- Manual audit finds no fabricated source/citation/finding.
- All five stages and useful failure states are visible.

## Data objects
ResearchRun, Source, Claim, EvidenceExcerpt, EvidenceEdge, CandidateGap, Report. Use stable IDs and validate all references.

## Reliability, security and privacy
Bound request sizes, timeouts, retries, query counts, and source counts. Keep keys server-side. Treat source text as untrusted input. Reject private/loopback/link-local fetch targets and revalidate redirects. Do not bypass logins/paywalls or render raw HTML. Clearly label static fallback data.

## Open questions
1. Verify TinyFish endpoints, authentication, response schema, quotas and rate limits.
2. Choose LLM provider/model and budget.
3. Confirm local/Codespaces/deployed demo environment.
4. Confirm team comfort with React/Vite/TypeScript and FastAPI/Python.
5. Confirm internet reliability at judging.

## Definition of done
Clean setup works; mocked vertical slice runs; live source discovery is integrated; report and graph render; citations resolve; critical failure paths are tested; secrets are absent from version control; README and demo claims match actual behavior.
