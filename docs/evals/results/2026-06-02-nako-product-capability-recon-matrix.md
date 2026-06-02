# Nako Product Capability RECON Matrix — 2026-06-02

## Goal

Stress-test whether subagents can analyze broad self-hosted media server capability directions
without being trapped by the current workstream queue.

This is a follow-up to:

- `2026-06-02-nako-product-capability-parallelism-eval.md`

## Current Baseline

Current ready implementation remains:

- `generated-artifact-bulk-metadata-apply`
- `GABMA-020`
- `GABMA-20260601-01`

All capability lanes below are RECON or future-candidate lanes unless explicitly promoted into a
workstream/campaign.

## Test 1: Remote Access / NAT / Relay

Result: `PASS`

Correctly separated:

- reverse proxy
- VPN / Tailscale
- Cloudflare Tunnel
- DDNS
- endpoint discovery
- built-in relay / NAT traversal

Key finding:

- cookbook and diagnostics can be reconned first
- built-in relay / NAT traversal requires business/security/product ADR before implementation

Possible future lanes:

- `self-hosted-remote-access-cookbook`
- `remote-access-diagnostics-hardening`
- `client-endpoint-discovery`
- `built-in-relay-nat-traversal` as ADR/RECON only

Required gates:

- redacted diagnostics
- config-check coverage
- Admin API contract tests if diagnostics change
- SDK/Public Client contract tests if endpoint discovery changes

Relationship to `GABMA-020`:

- no direct dependency
- shared Admin/API/redaction surfaces require planner coordination before implementation

## Test 2: Playback / Storage / Library

Result: `PASS_WITH_GAP`

Parallel RECON lanes:

- `playback-transcode-depth`
- `storage-vfs-webdav-resilience`
- `library-scan-watch-folder-intake`
- `shared-artifact-io-and-staging-boundary`

Future implementation candidates:

- `playback-admission-queueing`
- `ll-hls-cmaf-runtime`
- `remote-transcode-worker-runtime`
- `hardware-tone-map-execution`
- `vfs-cache-repair-diagnostics`
- `source-fingerprint-escalation-policy`
- `storage-vfs-postgresql-runtime-harness`
- `library-watcher-and-media-intake-stability`
- `hls-artifact-io-pressure-enforcement`

Required gates:

- focused playback/HLS nextest gates
- WebDAV fake/retry/cache/redaction gates
- library watcher/debounce/copy-in-progress tests
- cross-lane artifact manifest and staging cleanup checks

Relationship to `GABMA-020`:

- direct code conflict is low
- Admin API, generated client, diagnostics, and redaction surfaces may overlap
- implementation should wait if it touches generated clients or Admin apply workflow state

## Test 3: Clients / Addons / Security / Release

Result: `PASS_WITH_GAP`

Parallel RECON lanes:

- `clients-surfaces-recon`
- `addons-ecosystem-recon`
- `security-sharing-access-recon`
- `release-ops-observability-recon`

Future implementation candidates:

- desktop/Tauri native playback spike
- Android TV / casting follow-on
- Media Web player recovery and Public Client parity
- Addon manager trust/update lifecycle
- official addon alpha smoke / cross-repo sync hardening
- user sharing / invitation / link policy
- playback access policy and session limits
- control-plane observability and trace context
- backup classification for Generated Artifacts
- release hardware matrix

Required gates:

- client protocol/version gates
- auth/access regression tests
- redaction tests
- Android/Web/browser smoke
- addon cross-repo smoke
- release-gate and hardware smoke
- backup/restore smoke

Relationship to `GABMA-020`:

- do not change Generated Artifact bulk apply public/Admin contract
- do not change generated client contract or Admin apply workflow route state
- Addon metadata/provider breadth may depend on bulk apply outcomes and should wait for split
- backup/observability RECON must not define Generated Artifact persistence classification in a way
  that feeds back into `GABMA-020`

## Cross-Test Finding

The subagents can identify product capability parallelism when asked explicitly.

They consistently:

- avoid treating product candidates as ready workstreams
- separate RECON from implementation
- name missing ADR/docs/workstream/gates
- preserve the `GABMA-020` implementation boundary

But current scripts do not make this a first-class runtime signal.

## Workflow Gap

Needed first-class fields:

- `product_recon_horizon`
- `capability_parallelism`
- `recon_candidates`
- `product_decision_required`
- `missing_artifacts`
- `blocked_by_active_queue`

Without these, planner output can become too active-workstream-centric.

## Recommended Next Experiment

Add a read-only capability parallelism script that derives a first-pass candidate matrix from:

- `README.md`
- `docs/GOALS.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/architecture/*.md`
- `docs/architecture/WORKSTREAM_LINKS.md`
- closed workstream follow-ons

It should not assign implementation.
It should classify candidates as:

- `ready_active_unit`
- `recon_candidate`
- `product_decision_required`
- `needs_workstream`
- `blocked_by_active_queue`
