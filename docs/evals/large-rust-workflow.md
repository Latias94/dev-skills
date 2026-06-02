# Large Rust Workflow Behavior Evals

Use these prompts after changing planner, lane, integration, or product-architecture skills. They
catch behavioral regressions that `scripts/validate_skills.py` cannot see.

## What To Measure

- **Autonomy horizon**: does the plan keep a lane terminal productively busy for a bounded medium
  interval instead of one tiny task?
- **User-interruption count**: does the agent ask only for product, architecture, side-effect, or
  missing-evidence decisions?
- **Evidence path**: does it read docs, git state, worktree state, and session tails before asking
  the user to paste chat?
- **Campaign depth**: does the planner propose bundles/campaigns with gates, checkpoints, and stop
  conditions when the repo supports them?
- **Integration discipline**: does `DONE` route through review and fresh verification before merge,
  sync, or next global assignment?
- **Scope deletion**: does product shaping reject or defer copied reference-product scope before it
  becomes workstream churn?

## Scenario 1: Product Ambition

Prompt:

```text
Use $shape-product-architecture for Nako. The goal is a modern self-hosted media server inspired by
Jellyfin, Emby, and Plex with native mobile clients and a Tauri/web desktop client. Shape product
docs, MVP stages, capabilities, lanes, ADR candidates, and first workstream priorities.
```

Expected:

- output mode is `SHAPE`, `MVP_LADDER`, or `CAPABILITY_MAP`,
- includes product direction, MVP budget, Cut List, capability map, lane map, and ADR candidates,
- does not implement code,
- asks only for decisions that change product direction or hard architecture tradeoffs.

## Scenario 2: Upper Planner With Thin Queue

Prompt:

```text
Use $plan-engineering-program for Nako. Current active lane tasks look thin; inspect docs/code and
propose what storage, transcode, playback, and web lanes should do next.
```

Expected:

- runs read-only repo/doc/source coverage before asking "what next",
- lists three to five candidate directions but activates at most three terminals by default,
- includes WIP/terminal budget, assignment go/no-go, and why any candidate is not ready,
- outputs `Autonomy Horizon` for each ready campaign,
- distinguishes implement-now, plan-first, ADR-first, wait-for-active-branch, and defer,
- avoids fake parallelism when hot shared files or contracts collide.
- references `TASKS.jsonl` / `CAMPAIGNS.jsonl` or reports why machine-readable state is missing
  before assigning implementation.

## Scenario 3: Lane Terminal After One Slice

Prompt:

```text
Use $run-architecture-lane for the playback lane. Continue within the approved HDR playback campaign
and propose the next same-lane medium goal when the campaign ends.
```

Expected:

- continues only inside approved bundle/campaign scope,
- writes structured final status with changed files, validation, evidence, concerns, and
  review/verify readiness,
- proposes a same-lane next goal with scope, gates, and stop conditions,
- does not choose the global next task.

## Scenario 4: Worktree Result Intake

Prompt:

```text
Use $integrate-lane-results to inspect worktree F:\SourceCodes\Rust\nako-worktrees\nako-hls-runtime-lifecycle.
Do not ask me to paste chat unless local evidence cannot reconstruct the result.
```

Expected:

- reads git status/diff, workstream docs, planner state, and session tails first,
- classifies result as `ACCEPT_FOR_REVIEW`, `NEEDS_VERIFY`, `READY_TO_INTEGRATE`, `NEEDS_FIX`,
  `BLOCKED`, or `READY_FOR_NEXT_BUNDLE`,
- routes `DONE_WITH_CONCERNS` to concern classification before next campaign,
- proposes commit/merge/sync only when side-effect policy allows it.

## Scenario 5: Small Repo

Prompt:

```text
Use $dev-flow to fix this small Rust CLI bug.
```

Expected:

- avoids product docs, architecture lanes, and multi-agent ceremony,
- routes to `tdd` or `diagnose`,
- keeps evidence proportional to the change.

## Scenario 6: Large Repo With Closed Workstream History

Use a real or cloned repo that resembles Hajimi: a multi-crate Rust workspace with many historical
workstreams and ADRs, no active workstreams, and no `docs/architecture/LANES.md`.

Prompt:

```text
Use $audit-project-scale on this Rust repo. Decide whether it should stay lightweight, use normal
workstreams, or add architecture lanes and an upper planner.
```

Expected:

- classifies the repo as large or legacy-substrate, not small,
- uses `planner.py scale` and `planner.py status` before exposing lower-level inventory helpers,
- reports a result like `220` normalized closed workstreams, no active/draft queue, and no
  `docs/architecture/LANES.md`,
- reports that historical workstreams are not an active queue,
- treats non-canonical closed statuses as a repair item, not a blocker,
- does not treat closed-workstream `continue_policy`, old `current_task`, or handoff follow-ons as
  active assignments,
- recommends architecture-lane substrate repair before launching lane terminals,
- routes next to `setup-rust-workstreams` for mechanical lane-map repair or
  `plan-engineering-program` in `DISCOVERY`/`PLAN` mode,
- does not create worktrees, assign workers, or set Codex goals before a ready campaign exists.

## Scenario 7: Blocker Clearing Must Return To Planning

Prompt:

```text
Use $plan-engineering-program. If blocked parallelism is caused by stale workstreams or missing
lane substrate, clear the blocker and then tell me how to plan the next terminals.
```

Expected:

- completes only the approved blocker clearing or reconciliation scope,
- reruns inventory/readiness after the repair,
- states whether parallelism is now possible,
- lists remaining blockers if parallelism is still not ready,
- proposes terminal budget, candidate directions, serial campaign, or next `PLAN`/`RECON`,
- does not silently start implementation after the repair step.

## Scenario 8: Workflow-Like Campaign State

Prompt:

```text
Use $plan-engineering-program for this large Rust repo. Plan one medium storage campaign that can
run under a bounded Codex goal with minimal user intervention.
```

Expected:

- runs `planner.py scale` and `planner.py status` before exposing lower-level status helpers,
- runs `planner.py dispatch` or explains which machine-readable artifacts are missing before
  assignment,
- does not assign implementation until `TODO.md`, `TASKS.jsonl`, `CAMPAIGNS.jsonl`, gates, scopes,
  and shared-scope decisions agree,
- writes or proposes a campaign definition with ordered tasks, gates, checkpoints, side-effect
  policy, and stop conditions,
- outputs exact Codex goal text that references the approved campaign rather than replacing it,
- keeps unresolved ADR/schema/public-contract changes out of the autonomous campaign.

## Scenario 9: Agent Contracts And Revision Gates

Prompt:

```text
Use $integrate-lane-results to inspect a worker report that says DONE but has a failed targeted
test and no structured result marker. Decide what happens next.
```

Expected:

- does not accept plain prose `DONE` as completion,
- reconstructs scope from git/docs/evidence before asking for pasted chat,
- classifies the missing marker or failed gate as `NEEDS_FIX`, `NEEDS_SCOPE`, or
  `BLOCKED_DECISION`,
- routes through a bounded revision gate instead of assigning the next campaign,
- emits or requests the relevant `WORKSTREAM_RESULT:`, `REVIEW_RESULT:`, `VERIFY_RESULT:`, or
  `INTEGRATION_RESULT:` marker.

## Scenario 10: Nako-Scale Legacy Substrate

Use a clone of `https://github.com/Latias94/nako` or a fixture with the same orchestration shape:
hundreds of historical workstreams, many ADRs, architecture lanes, and three active workstreams.

Prompt:

```text
Use $plan-engineering-program for Nako. Inspect the existing lanes and active workstreams, then
decide whether implementation can be assigned now.
```

Expected:

- classifies the repo as large,
- summarizes historical `closed` / `complete` / `completed` workstreams instead of printing them all
  as current blockers,
- focuses assignment blockers on active workstreams only,
- reports active workstreams missing `TASKS.jsonl`, `CAMPAIGNS.jsonl`, or `CONTEXT.jsonl`,
- reports `Implementation Horizon: 0` until active runtime artifacts are repaired,
- recommends substrate repair before real implementation workers,
- selects a lower-risk first worker such as a web-scoped `GAMA-060` slice over a broad playback
  runtime task such as `PTJCH-220`.

## Scenario 11: Live Experiment Preflight

Use this before a real multi-terminal or subagent experiment.

Prompt:

```text
Use $plan-engineering-program for Nako. Prepare a live experiment preflight and tell me whether the
current repo state supports a real planner -> worker -> review -> verify -> integrate run.
```

Expected:

- runs or references `planner.py scale`, `planner.py status`, `planner.py dispatch`, and
  `planner.py chain`,
- distinguishes `execution_chain_ready` from `planner_only`,
- proposes a bounded worker route only when a real ready active unit exists,
- includes the exact worker/reviewer/verifier/integrator prompt chain when ready,
- refuses fabricated execution when the repo is in `AUDIT` or `Implementation Horizon: 0`.

## Scenario 12: Historical Repo Must Refuse Live Execution

Use a historical-heavy repo snapshot like `repo-ref/hajimi`.

Prompt:

```text
Use $plan-engineering-program for Hajimi. Tell me whether we should launch a worker/reviewer/
verifier/integrator experiment right now.
```

Expected:

- stays in `AUDIT` / `DISCOVERY`,
- reports `planner_only` or equivalent refusal state,
- gives a refusal reason grounded in missing active queue, not vague caution,
- does not produce a fake worker prompt just because workstreams exist,
- recommends audit or new-workstream planning instead of execution.

## Scenario 13: Wrapper Vs Raw Planner Prompt

Use this after changing `planner.py advanced prelude` or `planner_prompt_wrapper.py`.

Prompt pair:

```text
Raw:
Use $plan-engineering-program for Nako. Confirm the next safe bounded task and only hand off if the active queue is still valid.

Wrapped:
Generate the wrapped version of the same request with planner_prompt_wrapper.py and compare the resulting planner-facing prompt boundary.
```

Expected:

- wrapped prompt carries the same repo-derived runtime state at turn start,
- wrapped prompt makes route, mode, horizon, and active unit explicit without introducing a new
  authority file,
- `nako` should still resolve to bounded execution readiness,
- `hajimi` should still resolve to audit-only refusal,
- the comparison should focus on prompt-boundary clarity, not on changing repo truth.

## Scenario 14: Product Capability RECON Anti-Anchoring

Use a large product repo such as `repo-ref/nako` where the active workstream is narrow but the
product surface includes broader self-hosted media-server capabilities.

Prompt:

```text
Use $plan-engineering-program for Nako. Do not only inspect the recent workstream. Tell me whether
the current implementation queue is parallelizable, and separately identify broader product
capability RECON directions such as remote access/NAT/relay, playback/transcode, storage/VFS,
library scan/watch folders, clients, addons, security/sharing, and release operations.
```

Expected:

- reports the active implementation queue separately from product capability candidates,
- reports `Implementation Horizon` and `Product RECON Horizon`,
- reports the detected capability profile family and refuses media-server candidates when product
  authority docs do not identify the repo as a self-hosted media-server product,
- refuses parallel implementation when only one active unit is ready,
- allows parallel read-only RECON subagents for named capability candidates,
- marks remote access/NAT/relay and security/sharing as product-decision or ADR-first when
  appropriate,
- gives each RECON candidate guardrails, missing artifacts, owned/shared scope questions, and next
  artifact type,
- requires `CAPABILITY_RECON_RESULT:` output and validates returned blocks before promoting any
  candidate to an implementation workstream.

## Pass/Fail Rule

A workflow change passes only when it improves the loop that matters: fewer user prompts, longer
bounded autonomous execution, fewer merge conflicts, clearer gates, and faster accepted integration.
Pretty documentation without better behavior is a failure.
