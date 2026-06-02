# Capability RECON Runtime Contract — 2026-06-02

## Goal

Make product-capability parallelism usable by planner and RECON subagents without letting broad
product candidates become implementation queues.

This follows the product capability RECON matrix, which showed that subagents can identify broader
self-hosted media-server directions only when the runtime makes those directions explicit.

## Change

The runtime now exposes a structured RECON contract:

- each capability candidate includes a `guardrail`
- `dispatch_rehearsal.py` preserves guardrails in top candidate summaries
- outputs include a shared `CAPABILITY_RECON_RESULT:` contract
- `capability_recon_result_validator.py` validates returned RECON blocks
- `capability_recon_result_integrator.py` merges validated RECON blocks for upper-planner intake
- `capability_recon_packet.py` generates prompt packets for RECON subagents from current runtime
- `capability_recon_roundtrip.py` runs a local packet/result/validator/integrator contract smoke
- the contract requires fields for classification, evidence, guardrail assessment, missing
  artifacts, owned/shared scope, product decisions, implementation allowance, active-queue
  blocking, and suggested next artifact

## Nako Snapshot

Verified against `repo-ref/nako`.

Current implementation remains serial:

- `generated-artifact-bulk-metadata-apply`
- `GABMA-020`
- `GABMA-20260601-01`

Product RECON remains parallel:

- `playback_transcode_depth`
- `storage_vfs_webdav`
- `library_scan_watch_folder`
- `release_ops_backup_observability`
- `remote_access_nat_relay`
- `security_access_sharing`
- `clients_surfaces`
- `addons_ecosystem`

Blocked by the active queue:

- provider mapping breadth
- generated artifact apply repair tooling
- Admin bulk apply workflow route/Web UX
- durable bulk metadata mutation

## Expected Subagent Return Shape

Every capability RECON subagent should end with:

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

Allowed status values:

- `RECON_DONE`
- `NEEDS_PRODUCT_DECISION`
- `NEEDS_WORKSTREAM`
- `BLOCKED_BY_ACTIVE_QUEUE`
- `NEEDS_CONTEXT`

## Verification

Commands run:

```powershell
python -m unittest tests.test_capability_parallelism tests.test_dispatch_rehearsal
python -m unittest tests.test_capability_recon_result_validator tests.test_capability_parallelism tests.test_dispatch_rehearsal
python -m unittest tests.test_capability_recon_result_integrator tests.test_capability_recon_result_validator tests.test_capability_parallelism tests.test_dispatch_rehearsal
python -m unittest tests.test_capability_recon_packet tests.test_capability_recon_result_integrator tests.test_capability_recon_result_validator tests.test_capability_parallelism tests.test_dispatch_rehearsal
python -m unittest tests.test_capability_recon_roundtrip tests.test_capability_recon_packet tests.test_capability_recon_result_integrator tests.test_capability_recon_result_validator tests.test_capability_parallelism tests.test_dispatch_rehearsal
python -m unittest tests.test_capability_parallelism tests.test_dispatch_rehearsal tests.test_planner_payload tests.test_handoff_chain_rehearsal tests.test_real_repo_eval_docs
python skills\engineering\plan-engineering-program\scripts\capability_recon_packet.py repo-ref\nako --candidate remote_access_nat_relay
python skills\engineering\plan-engineering-program\scripts\capability_recon_roundtrip.py repo-ref\nako --candidate playback_transcode_depth --candidate remote_access_nat_relay
python skills\engineering\plan-engineering-program\scripts\capability_parallelism.py repo-ref\nako --format json
python skills\engineering\plan-engineering-program\scripts\dispatch_rehearsal.py repo-ref\nako
```

Results:

- 4 capability/dispatch tests passed
- 8 validator/capability/dispatch tests passed
- 11 integrator/validator/capability/dispatch tests passed
- 14 packet/integrator/validator/capability/dispatch tests passed
- 18 roundtrip/packet/integrator/validator/capability/dispatch tests passed
- 15 adjacent planner/runtime/eval tests passed
- real `repo-ref/nako` output includes guardrails for all eight product capability entries
- dispatch text includes the `CAPABILITY_RECON_RESULT:` contract
- validator rejects missing required fields, unknown capability IDs, and RECON results that allow
  implementation directly
- integrator merges multiple valid RECON results while keeping `promotion_allowed = false`
- integrator rejects merges when any returned RECON result violates the contract
- packet generation preserves current active unit, blocked-by-active-queue boundaries, guardrails,
  missing artifacts, and result contract fields in subagent prompts
- roundtrip smoke proves the local packet/result/validation/integration contract is internally
  consistent and still keeps `promotion_allowed = false`

## Assessment

Result: `PASS`

This closes the immediate gap from the matrix: product-capability parallelism is now a first-class
runtime signal with subagent guardrails, prompt packets, a result contract, validation, and
upper-planner merge intake. The roundtrip smoke only proves local contract compatibility; it does
not replace live subagent behavior evidence.

The next live subagent test should ask each RECON agent to return the contract above, then run:

```powershell
python skills\engineering\plan-engineering-program\scripts\capability_recon_packet.py repo-ref\nako --candidate remote_access_nat_relay
python skills\engineering\plan-engineering-program\scripts\capability_recon_roundtrip.py repo-ref\nako --candidate playback_transcode_depth --candidate remote_access_nat_relay
python skills\engineering\plan-engineering-program\scripts\capability_recon_result_validator.py repo-ref\nako --input <agent-output.md>
python skills\engineering\plan-engineering-program\scripts\capability_recon_result_integrator.py repo-ref\nako --input <agent-output.md>
```

After validation passes, the upper planner should merge multiple `CAPABILITY_RECON_RESULT:` blocks.
The merge result must keep `promotion_allowed = false` until ADR/workstream/campaign/gate artifacts
exist and are explicitly approved.
