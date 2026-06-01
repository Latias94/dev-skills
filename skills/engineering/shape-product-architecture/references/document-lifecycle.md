# Product Architecture Document Lifecycle

Use this when deciding which document to create or update while shaping a large product.

## Phase To Artifact

| Phase | Create/update | Purpose |
| --- | --- | --- |
| Bounded grill | `CONTEXT.md`, `docs/product/VISION.md` | Durable product language, users, non-goals, reference-product pressure |
| MVP shaping | `docs/product/MVP_LADDER.md` | MVP stages, exit criteria, deferred scope, validation expectations |
| Capability mapping | `docs/architecture/CAPABILITY_MAP.md` | Product workflows mapped to capabilities and module/lane candidates |
| Lane mapping | `docs/architecture/LANES.md`, `docs/architecture/<CAPABILITY>.md` | Owned scopes, shared scopes, maturity gaps, validation ladder, lane backlog |
| Hard decision | `docs/adr/<NNNN>-<slug>.md` | Accepted long-term contract or explicit rejected alternative |
| Durable execution | `docs/workstreams/<slug>/` | Target state, task ledger, gates, evidence, context, closeout |
| Implementation | `EVIDENCE_AND_GATES.md`, `JOURNAL/`, `HANDOFF.md` | Fresh proof and resumable session state |
| Closeout | Workstream closeout, architecture docs, ADRs if needed | Promote durable knowledge out of journals |

## ADR Triggers

Create or update an ADR when the decision changes a hard-to-change contract:

- public API, wire protocol, generated client contract, or plugin/addon interface,
- database schema, storage format, migration policy, or data authority,
- playback/transcode compatibility rule, device profile policy, or media artifact identity,
- runtime ownership for sessions, jobs, admission, cancellation, retries, or supervisors,
- security, permission, auth, deployment, release, or cross-repo versioning policy,
- cross-lane seam where future work would branch differently depending on the decision.

Do not create an ADR for a local implementation tactic, temporary task split, test-only change,
or internal refactor that leaves contracts and ownership unchanged. Record those in workstream docs
or architecture maps.

## MVP Ladder Rules

Each MVP stage should state:

- user-visible scenario,
- required capabilities,
- non-goals and deferred scope,
- architecture lanes involved,
- validation gates,
- acceptance evidence,
- next stage unlocked by completing it.

An MVP stage is satisfied when the key scenario works end to end, the required contracts are stable
enough for the next stage, known blockers are either fixed or explicitly deferred, and validation is
recorded in evidence docs.

## Priority Classes

- `mvp-blocker`: needed for the current MVP scenario to work.
- `parallelism-unlocker`: clarifies a seam so several lanes can proceed.
- `architecture-risk`: prevents likely rework or contract churn.
- `user-visible`: improves a user-facing workflow but is not a blocker.
- `ops-safety`: improves diagnostics, repair, migration, or failure handling.
- `maturity-deepening`: moves toward the reference-product upper bound after MVP needs are covered.

## Handoff To Execution

After shaping, route to:

- `plan-engineering-program` when several lanes or worktrees need sequencing,
- `plan-architecture-lane` when one lane needs code-aware boundary planning,
- `open-workstream` when one durable slice is ready,
- `grill-with-docs` when a product decision remains genuinely unresolved.
