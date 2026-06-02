# Nako Product Capability Parallelism Eval — 2026-06-02

## Goal

Validate whether the workflow can identify parallel directions from the full self-hosted media
server product space, not only from recent workstreams or the current active lane.

This eval responds to a specific risk:

> If planner only reads the active workstream queue, it may become too anchored to recent work and
> miss broader product-capability parallelism.

## Current Execution Fact

Current active implementation queue remains:

- `generated-artifact-bulk-metadata-apply`
- `GABMA-020`
- `GABMA-20260601-01`

Current implementation conclusion remains:

- do not parallelize implementation now
- continue one bounded worker chain for `GABMA-020`

## Broader Product Capability Space

Nako's product space is wider than the current active metadata apply workstream.

Evidence from repository docs includes:

- media scanning and local inference
- local filesystem and WebDAV-oriented VFS
- playback source selection, remux/transcode planning, hardware acceleration policy, runtime diagnostics
- Admin API and Admin Web diagnostics
- Addon Sidecar protocol and official addon experiments
- network tunnel / remote access readiness guidance
- Docker/Compose, backup/restore, release packaging
- mobile, desktop, TV/casting client directions in historical planning docs

## Product Capability Candidates

These are valid product capability directions, but they are not ready implementation queues by
default.

| Capability | Current interpretation |
| --- | --- |
| Remote access / NAT traversal / relay | Important product surface, but built-in relay/NAT traversal requires major product, security, abuse, cost, and account-model decisions |
| Reverse proxy / VPN / tunnel cookbook | Lower-risk remote-access planning surface; can be reconned before built-in relay decisions |
| Playback/transcode next depth | Rich parallel candidate area: LL-HLS/CMAF, remote workers, admission queueing, device profiles, subtitle burn-in, hardware tone mapping |
| Storage/VFS/WebDAV | Parallel candidate area: cache repair, retry policy, source fingerprint escalation, mount hang policy, PostgreSQL runtime harness |
| Library scan/watch folder | Candidate area: watcher/debounce, copy-in-progress handling, scheduled reconciliation, per-library diagnostics |
| Clients/mobile/desktop/TV | Candidate area, but depends on client protocol, playback capability reporting, auth/session model, and SDK maturity |
| Addon manager / official addon ecosystem | Candidate area, but process lifecycle, trust/update/signing, and cross-repo gates need ADR/workstream shape |
| Jobs/automation/observability | Candidate area: job priority, retry, trace context, queue pressure, redacted incident bundles |
| Security/access/sharing | Candidate area: RBAC, per-user remote playback, session limits, share links, permission-aware cache keys |
| Release/deployment/backup | Candidate area: remote-access cookbook, hardware release matrix, backup classification, restore smoke |

## Parallelism Classification

### Ready implementation

Only:

- `GABMA-020`

### Parallel RECON candidates

Safe to explore in parallel as read-only product/architecture planning:

- remote access / NAT / relay boundary
- playback/transcode next-depth map
- storage/VFS/WebDAV hardening map
- library scan/watch-folder runtime map
- clients/mobile/desktop/TV capability map
- addon ecosystem next-depth map
- jobs/automation/observability map
- security/access/sharing model
- release/deployment/backup model

### Future parallel implementation candidates

These can become parallel implementation lanes only after:

- product direction is clear
- ADRs exist where contracts are hard to reverse
- owned/shared scopes are explicit
- workstreams and campaigns are opened
- validation gates and stop conditions are written

## Must Not Parallelize With `GABMA-020`

Do not start implementation for:

- provider mapping breadth
- generated artifact apply repair tooling
- Admin bulk apply workflow route/Web UX
- generated client contract changes for apply flows
- metadata automation result/status UI
- durable bulk metadata mutation
- anything touching the `generated-artifact-bulk-metadata-apply` public/Admin contract

These are too close to the active metadata apply boundary and must wait for `GABMA-020` review,
verification, integration, or explicit split.

## Workflow Finding

The current workflow has two separate horizons:

1. `implementation_horizon`
   - how many ready active units can safely execute now
2. `product_recon_horizon`
   - how many product capability directions can safely be explored in parallel without code changes

Current scripts expose the first much better than the second.

## Recommended Dev-Skills Change

Add a product-capability parallelism layer to planner outputs.

Candidate fields:

- `implementation_horizon`
- `product_recon_horizon`
- `capability_parallelism`
- `ready_active_units`
- `recon_candidates`
- `product_decision_required`
- `missing_artifacts`

Planner anti-anchoring rule:

> When the user asks for parallel directions, start from product capability maps, then reconcile
> those candidates against workstream readiness. Do not answer only from the current active queue.

Special handling:

- NAT traversal / built-in relay should be marked `business/security decision required`
- remote-access cookbook / endpoint discovery may be lower-risk recon
- implementation must not begin until the product boundary is decided

## Evaluation

Result: `PASS_WITH_GAP`

Why it passes:

- the workflow can distinguish active implementation from broader product capability planning
- it correctly avoids turning product ideas into fake ready queues
- it identifies broad self-hosted media server directions beyond recent workstreams

Why there is still a gap:

- current scripts do not yet emit `product_recon_horizon`
- current parallelism output is too implementation-queue-centric
- product-level parallel RECON is a planner behavior, not yet a durable runtime contract
