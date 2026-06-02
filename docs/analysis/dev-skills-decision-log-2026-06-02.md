# Dev Skills Decision Log — 2026-06-02

## Purpose

This log records the main decisions reached during the current refactor pass so future iterations do
not re-litigate settled points without new evidence.

## Decisions

### D1. Keep project-owned truth outside workflow control files

Decision:

- keep ADRs, architecture docs, and workstreams as the project source of truth

Reason:

- large Rust repos need durable engineering truth that survives sessions and tooling changes

Rejected alternative:

- centralize workflow truth into a Trellis-style task/workflow control file

### D2. Borrow runtime hardening from Trellis selectively

Decision:

- adopt clearer runtime semantics and planner-style output,
- do not adopt Trellis task truth as the universal top-level abstraction

Reason:

- Trellis is stronger at per-turn control,
- but `dev-skills` is solving a different large-program governance problem

### D3. Keep composing with Matt skills

Decision:

- keep using Matt-style narrow skills as lower-level building blocks

Reason:

- they provide strong local engineering behavior without over-owning the program layer

Rejected alternative:

- re-implement or replace those lower-level skills inside `dev-skills`

### D4. Separate `READINESS` from `AUDIT`

Decision:

- readiness and historical audit are now first-class distinct modes

Reason:

- `nako` and `hajimi` proved that historical evidence drift is common and must not automatically be
  treated as an assignment blocker

### D5. Use `nako` and `hajimi` for different kinds of proof

Decision:

- use `nako` primarily as a route-choice/readiness benchmark
- use `hajimi` primarily as a historical-audit benchmark

Reason:

- the current snapshots expose different strengths and therefore test different failure modes

### D6. Prefer layered validation over one red/green gate

Decision:

- keep strict active-queue readiness checks separate from softer historical-quality checks

Reason:

- real repos frequently contain good historical work that is not normalized enough for strict
  machine checks

Rejected alternative:

- fail the whole repo on any historical evidence inconsistency

### D7. Keep runtime breadcrumb derived, not authoritative

Decision:

- add a compact planner breadcrumb as a derived read-only script output
- do not promote the breadcrumb into a new committed control artifact

Reason:

- large-repo orchestration needs a tighter artifact-to-turn bridge
- but committed truth must remain in ADRs, architecture docs, and workstreams

Rejected alternative:

- introduce a Trellis-style top-level workflow state file as a competing authority

### D8. Runtime hardening must be consumed, not only generated

Decision:

- propagate the derived runtime block through planner payloads and dispatch rehearsals

Reason:

- a runtime artifact that is only inspectable but not consumed will not materially change live
  routing behavior

Rejected alternative:

- stop after generating breadcrumb summaries and assume operators will manually translate them into
  each prompt

## What Would Reopen These Decisions

Only reopen a decision if new evidence shows:

- users are confused by the readiness/audit split,
- current artifact authority is insufficient in practice,
- Matt-skill composition becomes a real constraint,
- or a real repo proves that the current layering still causes wrong routing.
