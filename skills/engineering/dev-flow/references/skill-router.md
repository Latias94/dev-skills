# Skill Router

Use this table to choose and invoke the next skill.

| Situation | Use | Reason |
| --- | --- | --- |
| Repo lacks agent/workstream docs | `setup-rust-workstreams` | Create the project workflow substrate first. |
| User has an idea but requirements are fuzzy | `grill-with-docs` | Clarify scope, language, and risks before planning. |
| Requirement is clear and needs durable planning | `open-workstream` | Open/reuse a workstream and create a task ledger. |
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
| Workstream appears done | `close-workstream` | Finalize evidence, gates, status, and follow-ons. |
| Stop or transfer work | `handoff` | Preserve resumable state without relying on chat history. |

## Decision Heuristics

- If the work will last more than one session, use a workstream.
- If multiple agents are involved, use a task ledger.
- If a decision changes a hard-to-change contract, propose an ADR.
- If a task cannot be validated independently, it is probably too broad or too horizontal.
- If a journal contains durable knowledge, promote it to a workstream doc or ADR.

## Resume Rule

After any delegated skill finishes, return to `$dev-flow` routing:

```text
grill-with-docs -> dev-flow -> open-workstream
open-workstream -> dev-flow -> run-workstream-task
open-workstream -> dev-flow -> coordinate-workstream
run-workstream-task -> dev-flow -> close-workstream/handoff/next task
run-workstream-task -> dev-flow -> review-workstream -> verify-rust-workstream
verify-rust-workstream -> dev-flow -> close-workstream/next task
```
