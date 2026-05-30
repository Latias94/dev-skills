# Skill Router

Use this table to choose and invoke the next skill.

| Situation | Use | Reason |
| --- | --- | --- |
| Repo scale, old docs, or lane fit is unclear | `audit-project-scale` | Classify the workflow shape before setup or planning. |
| Small repo or one bounded change | `tdd` or `diagnose` | Keep the workflow direct and avoid workstream overhead. |
| Repo lacks agent/workstream docs | `setup-rust-workstreams` | Create the project workflow substrate first. |
| User has an idea but requirements are fuzzy | `grill-with-docs` | Clarify scope, language, and risks before planning. |
| Requirement is clear and needs durable planning | `open-workstream` | Open/reuse a workstream and create a task ledger. |
| User selected an architecture direction | `plan-architecture-lane` | Choose planning depth and produce docs/code-aligned lane plans. |
| One terminal should own a large architecture area | `run-architecture-lane` | Keep a stable terminal/worktree advancing queued workstreams under one capability. |
| Multiple terminals are active on one lane | `coordinate-workstream` | Assign tasks, integrate handoffs, and resolve conflicts. |
| Existing lane needs continuation | `resume-workstream` | Reconstruct state and choose the next task. |
| Existing plan should become a PRD | `to-prd` | Produce a product/spec artifact from known context. |
| PRD/spec should become external tasks | `to-issues` | Export vertical slices to an issue tracker. |
| Execute one workstream task | `run-workstream-task` | Own one task and route to `tdd` or `diagnose`. |
| Review worker output or task diff | `review-workstream` | Check workstream compliance and code quality separately. |
| Prove a Rust task or lane is complete | `verify-rust-workstream` | Run fresh validation gates and record evidence. |
| Implement one small non-workstream slice | `tdd` | Keep code changes on a feedback loop. |
| Debug a non-workstream bug/perf issue | `diagnose` | Reproduce, hypothesize, instrument, fix, regression-test. |
| Understand unfamiliar code | `zoom-out` | Explain local code in system context. |
| Improve structure without a specific feature | `improve-codebase-architecture` | Find deepening/refactor opportunities. |
| Execute a confirmed boundary/deletion refactor | `fearless-refactor` | Convert architecture findings into the right scale of refactor execution. |
| Workstream appears done | `close-workstream` | Finalize evidence, gates, status, and follow-ons. |
| Stop or transfer work | `handoff` | Preserve resumable state without relying on chat history. |

## Decision Heuristics

- Use `plan-architecture-lane` to choose planning depth before opening workstreams or assigning bundles.
- If docs and code align, use light planning and assign ready tasks.
- If the user picked a direction but task boundaries need code evidence, inspect the relevant code
  before splitting work.
- If lane seams or docs/code alignment are unclear, `plan-architecture-lane` should delegate to
  `improve-codebase-architecture` before opening or rewriting a workstream.
- If the work will last more than one session, use a workstream.
- If one terminal can finish safely in one session, stay direct.
- If a terminal will keep owning a capability area across workstreams, use an architecture lane.
- If the repo's workflow scale is unclear, audit first and pick the smallest fitting path.
- If multiple agents are involved, use a task ledger.
- If a decision changes a hard-to-change contract, propose an ADR.
- If a task cannot be validated independently, it is probably too broad or too horizontal.
- If a journal contains durable knowledge, promote it to a workstream doc or ADR.

## Resume Rule

After any delegated skill finishes, return to `$dev-flow` routing:

```text
audit-project-scale -> dev-flow -> setup-rust-workstreams/open-workstream/run-architecture-lane
grill-with-docs -> dev-flow -> open-workstream
open-workstream -> dev-flow -> run-workstream-task
open-workstream -> dev-flow -> coordinate-workstream
run-architecture-lane -> dev-flow -> open-workstream/run-workstream-task/review-workstream
run-workstream-task -> dev-flow -> close-workstream/handoff/next task
run-workstream-task -> dev-flow -> review-workstream -> verify-rust-workstream
verify-rust-workstream -> dev-flow -> close-workstream/next task
```
