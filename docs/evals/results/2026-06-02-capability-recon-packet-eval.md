# Capability RECON Packet Eval — 2026-06-02

## Goal

Validate whether a product-capability RECON candidate can be packaged into a bounded subagent prompt
with a stable result schema.

This is the next step after adding:

- `capability_parallelism.py`
- named `product_parallelism` entries in `dispatch_rehearsal.py`
- `capability_recon_packet.py`

## Target

Repo:

- `repo-ref/nako`

Capability:

- `remote_access_nat_relay`

Command:

```powershell
python skills\engineering\plan-engineering-program\scripts\capability_recon_packet.py repo-ref\nako --candidate remote_access_nat_relay --format json
```

## Expected Behavior

The generated packet must:

- name the current ready active unit:
  `generated-artifact-bulk-metadata-apply / GABMA-020 / GABMA-20260601-01`
- forbid file edits and implementation
- include evidence paths
- include missing artifacts
- include active-queue blockers
- require the shared `CAPABILITY_RECON_RESULT:` schema

## Observed Subagent Result

The first subagent returned structured JSON with:

- `capability_id: remote_access_nat_relay`
- `classification: product_decision_required`
- `implementation_allowed_now: false`
- guardrails separating:
  - reverse proxy
  - VPN / Tailscale
  - Cloudflare Tunnel
  - DDNS
  - endpoint discovery
  - built-in relay / NAT traversal
- missing artifacts:
  - product/security ADR
  - threat model
  - abuse/cost model
  - account/identity model
  - privacy/logging model
  - operations/support model
  - dedicated workstream
  - owned/shared scope
  - redaction gates
- blocked-by entries tied to:
  - current `GABMA-020` active unit
  - generated artifact apply repair/tooling boundaries
  - Admin/generated client contract risk
  - durable mutation being forbidden before the read-only plan contract is reviewed

## Evaluation

Result: `PASS`

Why it passes:

- subagent did not implement code
- subagent did not open or claim a ready workstream
- output followed the requested schema
- implementation was explicitly forbidden
- next artifact was correctly classified as `ADR`

## Contract Hardening

After the first packet run, the packet schema was aligned with the shared runtime contract from
`capability_parallelism.py`.

Expected final block:

```text
CAPABILITY_RECON_RESULT:
capability_id:
classification:
status:
evidence:
guardrail_assessment:
missing_artifacts:
owned_scope:
shared_scope:
product_decisions:
implementation_allowed:
blocked_by_active_queue:
suggested_next_artifact:
```

Follow-up verification:

```powershell
python -m unittest tests.test_capability_recon_packet tests.test_capability_recon_result_validator tests.test_capability_parallelism tests.test_dispatch_rehearsal
```

Result:

- 11 tests passed
- `capability_recon_packet.py` now exposes the same contract as `capability_recon_result_validator.py`
- future subagent outputs can be machine-validated before the planner promotes a candidate

## Meaning

This closes the loop from:

1. product capability detection
2. named runtime candidate
3. bounded RECON subagent packet
4. structured RECON result

The workflow can now support parallel product RECON without pretending those directions are ready
implementation lanes.
