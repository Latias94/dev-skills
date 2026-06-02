# Capability RECON Subagent Contract Eval — 2026-06-02

## Goal

Validate product-capability RECON with real subagents against `repo-ref/nako`, then machine-validate
their returned `CAPABILITY_RECON_RESULT:` blocks.

This eval covers three classifications:

- `remote_access_nat_relay`: `product_decision_required`
- `clients_surfaces`: `needs_workstream`
- `playback_transcode_depth`: `recon_candidate`

## Runtime Findings

The subagents correctly separated implementation readiness from product RECON:

- current implementation queue remains serial:
  `generated-artifact-bulk-metadata-apply / GABMA-020 / GABMA-20260601-01`
- product capability RECON can run in parallel
- none of the three candidates allowed implementation
- remote access was classified as product/security ADR-first
- clients and playback/transcode were classified as needing focused planning/workstream artifacts

The live run also exposed two runtime issues that were fixed:

- packet CLI drift: docs expected `--capability-id`, while the current script used `--candidate`
- validator parsing: multi-line fields with bullet lines such as `- docs/foo.md: note` were
  incorrectly parsed as unknown fields

## Fixes

- `capability_recon_packet.py` now accepts `--candidate` and compatibility alias `--capability-id`.
- `capability_recon_result_validator.py` now treats only known contract fields as fields; other
  colon-containing lines are folded into the current field.
- `tests/test_capability_recon_packet.py` covers the compatibility alias.
- `tests/test_capability_recon_result_validator.py` covers multi-line fields with colon-containing
  bullet lines.

## Validation

Commands run:

```powershell
python -m unittest tests.test_capability_recon_result_validator tests.test_capability_recon_packet tests.test_capability_parallelism tests.test_dispatch_rehearsal
python -m unittest tests.test_capability_recon_result_integrator tests.test_capability_recon_roundtrip
python skills\engineering\plan-engineering-program\scripts\capability_recon_packet.py --help
python skills\engineering\plan-engineering-program\scripts\capability_recon_packet.py repo-ref\nako --candidate remote_access_nat_relay --format json
python skills\engineering\plan-engineering-program\scripts\capability_recon_packet.py repo-ref\nako --capability-id remote_access_nat_relay --format json
python skills\engineering\plan-engineering-program\scripts\capability_recon_result_validator.py repo-ref\nako --format json
```

Results:

- 14 capability/dispatch/validator tests passed
- 4 roundtrip/integrator tests passed
- `--candidate` and `--capability-id` both produced the same packet
- validator accepted all three real subagent result blocks
- validator result: `valid=true`, `result_count=3`, `errors=[]`, `warnings=[]`

## Assessment

Result: `PASS`

The workflow now supports real parallel product RECON subagents without promoting broad product
directions into implementation queues. The next improvement should be profile-pack generalization:
the current built-in pack is intentionally gated to self-hosted media-server product docs.
