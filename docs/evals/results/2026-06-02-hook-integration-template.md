# Hook Integration Template — 2026-06-02

## Purpose

This template turns the current derived runtime bridge into a host-level hook wiring pattern.

It does not centralize workflow truth.
It only injects a derived prompt block at the prompt boundary, using repository artifacts as the
authority.

## Why This Exists

Current `dev-skills` already has:

- `planner_turn_prelude.py`
- `planner_prompt_wrapper.py`
- `planner_hook_adapter.py`

What was still missing compared with `repo-ref/Trellis` was a concrete integration template that
shows how a host can call the derived bridge on each relevant event.

## Trellis Reference Shape

Observed in `repo-ref/Trellis`:

- Session bootstrap hook:
  `repo-ref/Trellis/packages/cli/src/templates/gemini/settings.json`
- Per-turn workflow-state injection hook:
  `repo-ref/Trellis/packages/cli/src/templates/gemini/settings.json`
- Hook command names:
  - `.gemini/hooks/session-start.py`
  - `.gemini/hooks/inject-workflow-state.py`

Important behavioral distinction:

- Trellis centralizes control in workflow/task state
- `dev-skills` must keep authority in ADRs, architecture docs, workstreams, tasks, campaigns, and
  evidence

Therefore the correct port is:

- borrow per-turn injection mechanics
- do not borrow workflow-file truth centralization

## Recommended Dev-Skills Hook Contract

Use a single derived payload contract:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "<planner-runtime>...</planner-runtime>"
  }
}
```

Source:

- `skills/engineering/plan-engineering-program/scripts/planner_hook_adapter.py`

## Minimal Codex/Gemini-Style Wiring

Example host hook command:

```text
python skills/engineering/plan-engineering-program/scripts/planner_hook_adapter.py <repo-root> --prompt "<raw user prompt>" --event-name <event>
```

Recommended events by intent:

- session bootstrap:
  use a separate future bootstrap adapter if needed
- prompt-boundary planner injection:
  `UserPromptSubmit` or host-equivalent
- Gemini-style compatibility:
  `BeforeAgent`

## Operational Rules

1. Inject only derived runtime guidance.
2. Never edit the injected block by hand.
3. Recompute from repo artifacts each turn.
4. Keep payload compact and route-oriented.
5. When `Operating Mode: AUDIT` and `Implementation Horizon: 0`, inject refusal guidance rather
   than a fake worker route.
6. When `Operating Mode: READINESS` and a bounded task is ready, inject route and active-unit
   guidance that keeps the model from reopening global planning.

## Current Verified Output Shapes

### `repo-ref/nako`

Verified on 2026-06-02:

- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- active workstream:
  `generated-artifact-bulk-metadata-apply`
- active task:
  `GABMA-020`
- event:
  `UserPromptSubmit`

The injected block correctly carries:

- `ASSIGN`
- bounded active-unit identity
- required context list
- route:
  `run-workstream-task`

### `repo-ref/hajimi`

Verified on 2026-06-02:

- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- event:
  `BeforeAgent`

The injected block correctly carries:

- `DISCOVERY`
- audit-only posture
- explicit no-worker-dispatch guidance

## Remaining Gaps

This template does not yet provide:

- a repository installer for host hook files
- a bootstrap hook for non-planner sessions
- platform-specific config generation
- automatic raw-prompt capture from the host runtime

Those are integration tasks, not architecture questions.

## Next Implementation Target

If we productize hook integration, the next change should be a small installer or generator that:

1. writes host hook config
2. points to `planner_hook_adapter.py`
3. selects the correct event name per platform
4. keeps all injected content derived-only
