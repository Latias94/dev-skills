# Discovery Rules

Use these rules before deciding whether a broad repo goal can run in parallel.

## Authority Order

Read project-local authority before inventing lanes:

1. repo instructions: `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.github/`, tool config
2. durable decisions: `docs/adr/`, `CONTEXT.md`, architecture docs, product docs, repo-local specs
3. current task state: `.loom/`, `.planning/`, issue/PR text, workstream docs, journals, recent closeouts
4. code structure: workspace manifests, package boundaries, module ownership, generated code
5. verification surface: tests, fixtures, benchmarks, CI commands, scripts, snapshots
6. live risk: current branch, dirty files, recent diffs, untracked files, local-only changes

Read legacy `.trellis/` state only when the repo already has it. Do not require it, create it, or use it as the default workflow state.

Do not overwrite or normalize user changes discovered in dirty state.

## Discovery Depth

Loom does not cap tokens, model choice, or reasoning depth. Subagents should inherit the current agent's model and thinking strength unless the user requests otherwise.

Explore until lane ownership, dependencies, and verification are defensible. If an unknown can be investigated independently, record it in `discovery_evidence` and create a `research-only` or `architecture-first` lane instead of blocking the whole workflow in one thread.

## Lane Discovery Heuristics

Prefer parallel lanes when all of these are true:

- writable files are disjoint
- public contracts are already stable or each lane only reads them
- each lane has an independent verification command
- ordering does not affect observable behavior
- each lane can stop cleanly when it encounters unassigned files

Prefer serial-first lanes when any of these are true:

- a migration, schema, generated API, lockfile, workspace manifest, or global config must change
- two lanes need the same public type, trait, interface, route, or persistence contract
- one lane changes behavior that another lane must consume
- test fixtures or snapshots are shared and likely to churn
- the repo has dirty user edits in the target area

Prefer research-only lanes when:

- the dependency graph is unclear
- the requested outcome crosses unfamiliar modules
- the verification strategy is unknown
- external behavior, protocol rules, or production constraints need evidence

Prefer architecture-first lanes when:

- safe parallelism is blocked by tightly coupled modules
- adding the requested behavior would scatter knowledge across many callers
- tests can only be written through brittle internals
- a small interface decision would unlock multiple implementation lanes

## Evidence To Capture

For every proposed lane, record at least one concrete source of evidence:

- file path and what it proves
- ADR/spec/workstream decision and how it constrains the lane
- dependency edge or call path
- command/test that verifies the lane
- dirty file that blocks or narrows the lane

Avoid confidence based on directory names alone. Confirm with imports, call sites, manifests, tests, or recent diffs.

## Unsafe Dispatch Signals

Do not dispatch implementation workers until the lane map is revised if:

- two workers would write the same file
- ownership depends on a generated artifact that has not been regenerated
- the lane requires touching high-context instructions or install scripts
- a worker must infer an API contract that another worker is also changing
- verification would only be possible after all lanes merge

In these cases, create a serial planning, research, or architecture lane first.
