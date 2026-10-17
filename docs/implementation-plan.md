# Implementation plan

## Milestones
1. **Foundation:** configure TinyFish API credentials and confirm Research API access; agree interfaces; establish manifests and secret handling.
2. **Vertical slice:** question form, backend health, create-run API, mocked research data, structured report.
3. **Live research:** TinyFish Research API adapter and polling are implemented. Verify account access/quotas with one real run; decide whether to add the faster Search + Fetch path for live demo latency.
4. **Evidence:** normalize the provider evidence schema into stable source/claim IDs, support/contradiction relationships, and cautious gap labels. This remains outstanding.
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
