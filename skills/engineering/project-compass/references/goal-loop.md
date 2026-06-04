# Goal Loop

Use this loop for long-running projects that evolve through many goals, refactors, and planning sessions.

## Loop

```text
brainstorm -> project memory -> next goal -> loom execution -> closeout -> memory update -> next goal
```

For active multi-session work, keep the loop grounded in:

```text
state.json -> goal.md -> findings.md -> progress.md -> closeout.md -> reboot check
```

## 1. Brainstorm

Work with the user until the direction is specific enough to constrain choices:

- what the product should become
- who it serves
- what is explicitly out of scope
- which capabilities define success
- which architecture boundaries matter
- what can be deferred

If the user gives a strong metaphor such as "like Jellyfin but more modular", translate it into capabilities, non-goals, and extension points.

## 2. Project Memory

Update durable files:

- north star for direction
- capability map for product shape
- module boundaries for architecture
- roadmap for progress
- ADRs for decisions that future agents must not re-litigate

## 3. Next Goal

Shape exactly one next executable goal:

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
handoff_to:
```

Use `handoff_to: loom` when the goal is ready for lane discovery.

Before choosing a new goal, resolve active work:

- continue it if the goal, evidence, and code state still align
- close it out if the work is finished but not archived
- reconcile it if documents, task status, and current code disagree
- defer it explicitly if a higher-priority goal supersedes it

`context_manifest` names the files future implement/check/review agents must read: specs, ADRs, architecture maps, research notes, PRD, tests, or contract docs.

Create or update the scoped active plan:

```text
.codex-workflow/state.json
.codex-workflow/goals/YYYY-MM-DD-short-goal/goal.md
.codex-workflow/goals/YYYY-MM-DD-short-goal/findings.md
.codex-workflow/goals/YYYY-MM-DD-short-goal/progress.md
```

Before major decisions, re-read the active `goal.md`. After discovery, update `findings.md`. After actions, update `progress.md`.

## 4. Execution

Let `loom` discover parallel lanes, serial blockers, research lanes, architecture-first lanes, file ownership, and review gates.

## 5. Closeout

After execution, update:

- roadmap status
- capability progress
- module-boundary changes
- ADRs if decisions changed
- workstream closeout with verification and remaining risks
- spec or agent guidance when a reusable convention was learned
- active task/plan status, archive state, or session journal if the repo has those concepts

Before stopping or resuming, answer the 5-question reboot check:

| Question | Source |
|----------|--------|
| Where am I? | current phase in `state.json` and `goal.md` |
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
- the next goal or next decision is explicit

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
