# Implementation plan

## Milestones
1. **Foundation:** verify TinyFish docs/credentials and LLM choice; agree interfaces; establish manifests and secret handling.
2. **Vertical slice:** question form, backend health, create-run API, mocked research data, structured report.
3. **Live discovery:** TinyFish adapter, source normalization, accessible public source fetching, timeouts and partial failures.
4. **Evidence:** structured extraction, claim/source IDs, support/contradiction relationships, cautious gap labels.
5. **UI:** five-stage progress, report sections, evidence graph, accessible list fallback.
6. **Hardening:** unit/integration/E2E tests, manual citation audit, backup run and demo rehearsal.

## Proposed team ownership
These are suggestions; confirm team strengths before finalizing.
- Md Hassan: integration, product flow, demo readiness.
- Navya Jain: FastAPI and TinyFish provider adapter.
- Prachi Bisht: React UI, report and progress experience.
- Misbah Javed: evidence models, comparison, graph QA and evaluation dataset.

## Evaluation
Use 5–10 questions across topics. Manually record source coverage, extraction correctness, citation validity, missed contradictions, gap scope, unsupported claims, and completion time. Audit every claim in the rehearsed demo.

## Demo runbook
1. Explain that the product returns a sourced research brief and exposes its evidence.
2. Submit: “Can AI detect river pollution using satellite imagery?”
3. Show Plan → Search → Extract → Verify/Compare → Synthesize.
4. Open a finding, follow its citation, and show source metadata/limitations.
5. Inspect a graph claim and its supporting/contradicting evidence if available.
6. Explain that candidate gaps are scoped and not proof of global novelty.
7. If live search fails, use a saved run and disclose it is backup data.

## Submission checklist
- [ ] README setup instructions tested.
- [ ] .env.example contains placeholders only.
- [ ] .gitignore excludes secrets, caches, build output, local database and virtual environments.
- [ ] No secrets committed.
- [ ] Citations and graph nodes point to real sources.
- [ ] Backup run prepared and clearly labelled.
- [ ] Presentation claims match implemented features.
