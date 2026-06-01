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
- uses the workstream inventory helper when available,
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

## Pass/Fail Rule

A workflow change passes only when it improves the loop that matters: fewer user prompts, longer
bounded autonomous execution, fewer merge conflicts, clearer gates, and faster accepted integration.
Pretty documentation without better behavior is a failure.
