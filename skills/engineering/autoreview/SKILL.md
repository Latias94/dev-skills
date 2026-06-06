---
name: autoreview
description: >
  Run a structured Codex-first code review helper as a closeout check on local,
  branch, PR, or commit diffs. Use when the user asks for autoreview, Codex review,
  Claude review, second-model review, or after non-trivial code edits before final,
  commit, ship, or PR update.
---

# Auto Review

Use the bundled helper to run a structured code review before closeout. This is an advisory review
gate, not an approval router, and every accepted finding must be verified against the real code.

## Workflow

1. Format first if formatting can change line locations.
2. Pick the reviewed target:
   - dirty work: `<autoreview-helper> --mode local`
   - branch work: `<autoreview-helper> --mode branch --base origin/main`
   - committed work: `<autoreview-helper> --mode commit --commit HEAD`
3. Run focused tests separately or with `--parallel-tests "<command>"`.
4. Treat output as advisory. Verify every accepted finding by reading the relevant files and
   dependency contracts before changing code.
5. Fix accepted findings at the right ownership boundary, then rerun focused tests and autoreview.
6. Stop when the helper exits cleanly with no accepted or actionable findings.

## Guardrails

- Codex is the default review engine. Do not switch engines or models unless the user asks.
- Do not invoke nested review commands from inside the review.
- Do not push, merge, amend, or rewrite history just to review.
- Reject speculative findings, unrealistic edge cases, and broad rewrites that do not prove a scoped bug.
- If a finding exposes a repeated bug class, inspect sibling cases in the current change scope.
- Be patient with long reviews; heartbeat lines are healthy progress.

## Report

Include the review command, tests or proof run, accepted and rejected findings, follow-up fixes, and
the final clean helper result or the reason a remaining finding was consciously rejected.

## Example

```text
Use $autoreview on the current branch against origin/main. Run the focused pytest command in
parallel, verify any accepted findings before fixing them, and report the final clean review result.
```

## References

- Read `references/helper-usage.md` for target modes, panels, Windows invocation, and helper details.
- See `SOURCE.md` and `LICENSE.upstream` for upstream attribution.
