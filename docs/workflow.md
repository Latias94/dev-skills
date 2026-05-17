# Dev Workflow

中文文档: [zh-CN/workflow.md](./zh-CN/workflow.md)

This workflow gives a Trellis-like development experience while keeping ADRs and workstreams as the
project source of truth. Skill structure follows the small, composable style used by
`mattpocock/skills`: an entrypoint skill routes the phase, while narrower skills own bootstrap,
planning, implementation, diagnosis, and handoff.

`$dev-flow` is an orchestrator: after a delegated skill finishes, return to `$dev-flow` and route the
next phase.

## Skill Router

```mermaid
flowchart TD
  Start([New request]) --> Init{Repo has AGENTS/CONTEXT/workstreams?}
  Init -- No --> Bootstrap[$setup-rust-workstreams]
  Init -- Yes --> Existing{Resume existing workstream?}
  Bootstrap --> Clear
  Existing -- Yes --> Resume[$resume-workstream]
  Existing -- No --> Clear{Goal and risk clear?}

  Clear -- No --> Grill[$grill-with-docs]
  Grill --> Durable{Durable multi-slice change?}
  Clear -- Yes --> Durable

  Durable -- Yes --> WS[$open-workstream]
  Durable -- No --> Kind{What kind of work?}

  WS --> Split[Planner writes task ledger]
  Split --> Parallel{Parallelizable?}
  Parallel -- Yes --> Multi[$coordinate-workstream assigns worker tasks]
  Parallel -- No --> Single[Run one slice locally]

  Kind -- Feature --> TDD[$tdd]
  Kind -- Bug/perf --> Diagnose[$diagnose]
  Kind -- Architecture --> Arch[$improve-codebase-architecture]
  Kind -- Unknown code --> Zoom[$zoom-out]
  Kind -- Spec export --> PRD[$to-prd]

  Multi --> Validate[Task validation gates]
  Single --> Validate
  TDD --> Validate
  Diagnose --> Validate
  Arch --> WS
  Zoom --> Kind
  PRD --> Issues{Need external issue tracker?}
  Issues -- Yes --> ToIssues[$to-issues]
  Issues -- No --> WS

  ToIssues --> Validate
  Validate --> Record[Record evidence and journal]
  Record --> Handoff{Need handoff?}
  Handoff -- Yes --> Hand[$handoff]
  Handoff -- No --> Close{Lane complete?}
  Hand --> Close
  Close -- No --> Split
  Close -- Yes --> Closeout[$close-workstream updates gates, milestones, WORKSTREAM.json]
  Resume --> Kind
```

## Artifact Authority

```mermaid
flowchart TD
  ADR[Accepted ADRs and architecture contracts] --> Design[Workstream DESIGN / MILESTONES / EVIDENCE]
  Design --> Ledger[Task ledger: TODO.md]
  Ledger --> Journal[Session JOURNAL and HANDOFF]
  Journal --> Chat[Chat history]

  ADR -. overrides .-> Design
  Design -. overrides .-> Ledger
  Ledger -. overrides .-> Journal
  Journal -. summarizes .-> Chat
```

Rules:

- ADRs are durable contracts.
- Workstreams are durable execution lanes.
- `TODO.md` is the multi-agent task ledger.
- `JOURNAL/` and `HANDOFF.md` are resume aids, not sources of truth.

## Multi-Agent Execution

```mermaid
sequenceDiagram
  participant User
  participant Planner
  participant WorkerA
  participant WorkerB
  participant Reviewer
  participant Docs as Workstream Docs

  User->>Planner: clarified goal or existing workstream
  Planner->>Docs: update DESIGN, TODO, gates
  Planner->>WorkerA: assign TASK-A with file scope and validation
  Planner->>WorkerB: assign TASK-B with disjoint scope and validation
  WorkerA->>Docs: update task status, evidence, journal
  WorkerB->>Docs: update task status, evidence, journal
  WorkerA-->>Planner: changed files, validation, blockers
  WorkerB-->>Planner: changed files, validation, blockers
  Planner->>Reviewer: request standards + spec review
  Reviewer-->>Planner: findings or approval
  Planner->>Docs: integrate evidence, update milestones, close or split follow-on
```

## Standard Development Loop

1. Start with `$dev-flow`.
2. Use `$setup-rust-workstreams` only when the repo lacks workflow docs.
3. Let `$dev-flow` delegate to `$grill-with-docs` before durable or risky work.
4. Let `$dev-flow` delegate to `$open-workstream` for large features and refactors.
5. Use `$coordinate-workstream` from the planner terminal when multiple terminals are active.
6. Let `$run-workstream-task` delegate executable slices to `$tdd` or `$diagnose`.
7. Use `$handoff` before stopping or transferring a session.
8. Close work by updating evidence, gates, milestones, and `WORKSTREAM.json`.

## Workstream Split Rule

Do not create a workstream per task. Create a new workstream only when the work has its own durable
goal, scope boundary, validation gates, and closeout path.

Inside one workstream, split tasks by independently validatable vertical slices.
