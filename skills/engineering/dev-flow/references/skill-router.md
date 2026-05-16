# Skill Router

Use this table to choose and invoke the next skill.

| Situation | Use | Reason |
| --- | --- | --- |
| Repo lacks agent/workstream docs | `bootstrap-rust-project` | Create the project workflow substrate first. |
| User has an idea but requirements are fuzzy | `grill-with-docs` | Clarify scope, language, and risks before planning. |
| Requirement is clear and needs durable planning | `rust-workstream` | Open/reuse a workstream and create a task ledger. |
| Existing plan should become a PRD | `to-prd` | Produce a product/spec artifact from known context. |
| PRD/spec should become external tasks | `to-issues` | Export vertical slices to an issue tracker. |
| Implement one behavior slice | `tdd` | Keep code changes on a feedback loop. |
| Debug a bug/perf issue | `diagnose` | Reproduce, hypothesize, instrument, fix, regression-test. |
| Understand unfamiliar code | `zoom-out` | Explain local code in system context. |
| Improve structure without a specific feature | `improve-codebase-architecture` | Find deepening/refactor opportunities. |
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
grill-with-docs -> dev-flow -> rust-workstream
rust-workstream -> dev-flow -> tdd/diagnose
tdd/diagnose -> dev-flow -> evidence/handoff/closeout
```
