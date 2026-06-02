# Capability Profile Gating Eval — 2026-06-02

## Goal

Ensure product-capability parallelism does not overfit recent workstreams and does not apply a
self-hosted media-server profile to unrelated repos.

## Repos

- `repo-ref/nako`: self-hosted media server
- `repo-ref/hajimi`: host-neutral embeddable agent SDK and dogfooding CLI

## Initial Failure

The first detector used broad profile keywords across workstream history. That caused `repo-ref/hajimi`
to receive media-server-flavored candidates because old workstreams mentioned media servers as
example host applications.

This was a real false positive:

- Hajimi can be embedded by media-server hosts.
- Hajimi itself is not a media-server product.
- Product capability RECON should not launch Nako-style remote access, playback, WebDAV, client,
  addon, or media security lanes from those examples.

## Fix

`capability_parallelism.py` now gates the built-in profile pack:

- profile family: `self_hosted_media_server`
- family evidence is read only from product authority docs:
  `README.md`, `docs/GOALS.md`, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`,
  and `docs/architecture/**`
- workstream history can provide candidate evidence after the family is detected, but it cannot
  enable the family by itself

## Verification

Commands run:

```powershell
python -m unittest tests.test_capability_recon_packet tests.test_capability_recon_result_validator tests.test_capability_parallelism tests.test_dispatch_rehearsal
python skills\engineering\plan-engineering-program\scripts\capability_parallelism.py repo-ref\nako --format json
python skills\engineering\plan-engineering-program\scripts\capability_parallelism.py repo-ref\hajimi --format json
```

Observed:

- `repo-ref/nako`:
  - `profile_family.detected=true`
  - `implementation_horizon=1`
  - `product_recon_horizon=8`
  - active task remains `GABMA-020`
- `repo-ref/hajimi`:
  - `profile_family.detected=false`
  - `implementation_horizon=0`
  - `product_recon_horizon=0`
  - no media-server product candidates emitted
- 14 relevant tests passed after the follow-up parser/alias fixes.

## Assessment

Result: `PASS`

This directly addresses the anti-anchoring concern:

- Nako is no longer limited to recent generated-artifact workstream directions.
- Hajimi is no longer polluted by Nako-specific media-server capability profiles.
- Future domain support should add explicit profile packs instead of broadening this one.
