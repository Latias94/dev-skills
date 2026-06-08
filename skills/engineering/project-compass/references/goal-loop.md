# Legacy Goal Loop

Use this only to interpret or migrate existing `.loom` goal-loop state. Do not start new projects on
this loop when Compound Engineering is available.

## Legacy Loop Shape

```text
brainstorm -> project memory -> next goal -> loom execution -> closeout -> memory update -> next goal
```

This is a historical shape to recognize in old files, not a recommended new workflow. For new work,
route to CE.

For old active multi-session work, expect state shaped like:

```text
state.local.json -> goal.md -> findings.md -> progress.md -> closeout.md -> reboot check
```

## CE Mapping

Map old loop concepts into CE like this:

| Legacy concept | CE target |
|----------------|-----------|
| north star, target users, non-goals | `ce-strategy` / `STRATEGY.md` |
| brainstormed requirements | `ce-brainstorm` / `docs/brainstorms/` |
| next executable goal | `ce-plan` input or an issue body |
| loom lane map | Loom fallback only, or local constraints passed to `ce-work` |
| closeout evidence | `ce-compound`, PR description, ADRs, or `docs/solutions/` |
| refactor pulse | `ce-plan` or `improve-codebase-architecture` when installed |

## 1. Legacy Brainstorm Fields

Work with the user until the direction is specific enough to constrain choices:

- what the product should become
- who it serves
- what is explicitly out of scope
- which capabilities define success
- which architecture boundaries matter
- what can be deferred

If the user gives a strong metaphor such as "like Jellyfin but more modular", translate it into capabilities, non-goals, and extension points.

## 2. Legacy Project Memory Fields

Old workflows may have updated durable files:

- north star for direction
- capability map for product shape
- module boundaries for architecture
- roadmap for progress
- ADRs for decisions that future agents must not re-litigate

## 3. Legacy Next Goal Fields

Old workflows may have shaped one next executable goal:

```text
goal:
active_memory:
done_when:
why_now:
depends_on:
risks:
files_or_modules_likely_involved:
verification:
context_manifest:
subagent_policy:
worktree_policy:
commit_policy:
handoff_to:
```

Use `handoff_to: ce-plan`, `ce-work`, or `loom-fallback` when translating legacy state.

Do not create native goal state or a new active `.loom/goals/<slug>/` directory unless the user
explicitly wants a Loom fallback run.

Before choosing a new goal, resolve active work:

- continue it if the goal, evidence, and code state still align
- close it out if the work is finished but not archived
- reconcile it if documents, task status, and current code disagree
- defer it explicitly if a higher-priority goal supersedes it

`context_manifest` names the files future implement/check/review agents must read: specs, ADRs, architecture maps, research notes, PRD, tests, or contract docs.

Old scoped active plans may look like:

```text
.loom/state.local.json
.loom/goals/YYYY-MM-DD-short-goal/goal.md
.loom/goals/YYYY-MM-DD-short-goal/findings.md
.loom/goals/YYYY-MM-DD-short-goal/progress.md
```

Before major migration decisions, re-read the active `goal.md`. Do not update legacy files unless the
user asked to continue or migrate that state.

## 4. Execution

Prefer CE execution. Let `loom` discover parallel lanes only in fallback mode.

## 5. Legacy Closeout Fields

Old workflows may have updated:

- roadmap status
- capability progress
- module-boundary changes
- ADRs if decisions changed
- workstream closeout with verification and remaining risks
- spec or agent guidance when a reusable convention was learned
- workflow feedback candidates: repeated corrections, missing verification steps, vague prompts, or
  rules that belong in a skill, repo instruction, test, or checklist
- active task/plan status, archive state, or session journal if the repo has those concepts

Before stopping or resuming, answer the 5-question reboot check:

| Question | Source |
|----------|--------|
| Where am I? | current phase in `state.local.json` and `goal.md` |
| Where am I going? | remaining phases in `goal.md` |
| What's the goal? | goal statement in `goal.md` |
| What have I learned? | `findings.md` |
| What have I done? | `progress.md` |

If any answer is unclear, update the planning files before continuing.

## Finish Gate

Before calling a goal complete, check:

- implementation evidence is tied to the current head or current diff
- reviewer/check findings are resolved or explicitly deferred with evidence
- the active memory says the same status as the code
- reusable lessons were promoted to specs, ADRs, or architecture docs
- missed checks and user corrections were reviewed for skill, prompt, or verification updates
- the next goal or next decision is explicit in the final answer

## 6. Refactor Pulse

Recommend a refactor pulse when any of these repeat:

- adding a feature requires touching many unrelated modules
- tests need internal knowledge instead of public contracts
- two concepts have duplicate names or responsibilities
- lane discovery keeps finding the same shared writable files
- review findings point to architectural ambiguity

Refactor pulses should clean the architecture before the next feature phase.

## Error Protocol

Never repeat the same failed action unchanged.

```text
attempt 1: diagnose and apply a targeted fix
attempt 2: use a different approach
attempt 3: question assumptions and revise the plan
after 3 failures: report the blocker with evidence
```

Log the error, attempt number, and resolution in `progress.md` or the active plan.
