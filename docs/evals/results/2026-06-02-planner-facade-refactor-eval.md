# Planner Facade Refactor Eval — 2026-06-02

## Goal

Reduce planner runtime cognitive weight compared with a Trellis-style single workflow entrypoint.

Before this refactor, the upper planner documentation exposed many helper scripts directly:

- `planner_payload.py`
- `dispatch_rehearsal.py`
- `capability_parallelism.py`
- `capability_recon_packet.py`
- `handoff_chain_rehearsal.py`

The helpers were useful, but the operator-facing interface was too broad.

## Change

Added:

```powershell
python skills\engineering\plan-engineering-program\scripts\planner.py <subcommand> <repo>
```

Subcommands:

- `scale`
- `status`
- `dispatch`
- `capability`
- `recon-packet`
- `chain`
- `advanced`

The old helper scripts remain available for compatibility and debugging. The facade introduces no
new source of truth; it delegates to the existing helper modules.

Follow-up hardening after subagent review:

- `planner.py scale` lazy-loads only the scale helper, so help/scale no longer depends on heavier
  status, dispatch, capability, recon, or chain imports.
- `workflow_scale.py` counts approved/running campaign rows instead of campaign files, and only
  escalates to `program` from ready active workstream or approved campaign evidence.
- `workflow_scale.py` now returns `recommended_surface` as a routing hint rather than
  `allowed_artifacts`, so it does not redefine the workflow artifact contract.
- High-level docs keep `program_status.py` below the facade for debugging/repair only.
- Result validation, prompt preludes, and hook payloads are now available through
  `planner.py advanced validate-result`, `planner.py advanced prelude`, and
  `planner.py advanced hook-payload`.
- The Codex hook template and hook installer default to `planner.py advanced hook-payload` rather
  than calling the injection helper directly.

## Updated Entry Points

Updated high-level docs and skill guidance to prefer:

```powershell
python skills\engineering\plan-engineering-program\scripts\planner.py scale <repo>
python skills\engineering\plan-engineering-program\scripts\planner.py status <repo>
python skills\engineering\plan-engineering-program\scripts\planner.py dispatch <repo>
python skills\engineering\plan-engineering-program\scripts\planner.py capability <repo>
python skills\engineering\plan-engineering-program\scripts\planner.py recon-packet <repo> --candidate <id>
python skills\engineering\plan-engineering-program\scripts\planner.py chain <repo>
python skills\engineering\plan-engineering-program\scripts\planner.py advanced <prelude|hook-payload|validate-result>
```

## Verification

Command run:

```powershell
python -m unittest tests.test_workflow_scale tests.test_planner_cli tests.test_planner_payload tests.test_dispatch_rehearsal
python -m unittest tests.test_workflow_scale tests.test_planner_cli tests.test_install_codex_planner_hook tests.test_capability_recon_result_validator tests.test_planner_turn_prelude tests.test_inject_planner_runtime
python -m unittest tests.test_real_repo_eval_docs tests.test_eval_scenario
```

Result:

- 16 planner/scale tests passed
- 30 planner/advanced/hook tests passed
- 13 documentation/eval tests passed
- `scale` reports the smallest workflow preset before exposing heavier artifacts
- `scale` keeps a docs-rich repo without workstream/lane substrate on the direct surface
- `scale` preserves `repo-ref/nako` as `program` from one ready active workstream and one approved campaign
- `scale` preserves `repo-ref/hajimi` as `audit-repair` without blocking unrelated bounded direct tasks
- facade `status` preserves `GABMA-020` active unit on `repo-ref/nako`
- facade `dispatch` preserves `run-workstream-task` route and product parallelism
- facade `capability` preserves profile-family gating on `repo-ref/hajimi`
- facade `recon-packet` preserves candidate packet generation
- facade `chain` preserves the handoff state and integration prompt
- facade `advanced` preserves result validation, prelude generation, and hook payload generation

## Assessment

Result: `PASS`

This is a Trellis-aligned simplification: keep the runtime depth, but reduce the operator-facing
surface.
