# Auto Review Helper Usage

Use this reference after loading the skill when command selection or helper behavior matters.

## Helper Path

From this repository:

```powershell
python skills\engineering\autoreview\scripts\autoreview --help
```

After installation into Codex skills:

```powershell
python "$HOME\.codex\skills\autoreview\scripts\autoreview" --help
```

On Windows, invoke the extensionless Python helper through `python`. Use
`--parallel-tests-shell powershell` or `--parallel-tests-shell pwsh` when the focused test command is
PowerShell-specific.

## Target Modes

Use local mode only for actual unstaged, staged, or untracked changes:

```powershell
python skills\engineering\autoreview\scripts\autoreview --mode local
```

Use branch mode for PR or branch work:

```powershell
python skills\engineering\autoreview\scripts\autoreview --mode branch --base origin/main
```

If an open PR exists and `gh` is available, prefer the real PR base:

```powershell
$base = gh pr view --json baseRefName --jq .baseRefName
python skills\engineering\autoreview\scripts\autoreview --mode branch --base "origin/$base"
```

Use commit mode for already committed changes:

```powershell
python skills\engineering\autoreview\scripts\autoreview --mode commit --commit HEAD
```

## Closeout Loop

- Run tests and review in parallel only after formatting.
- If tests or review findings cause code edits, rerun the affected tests and autoreview.
- Stop after a successful helper run with no accepted or actionable findings.
- Do not run extra review cycles solely to improve final wording.

## Options Worth Knowing

- `--engine codex|claude|droid|copilot`; default is `AUTOREVIEW_ENGINE` or `codex`.
- `--panel` or `--reviewers codex,claude` runs an opt-in multi-reviewer panel.
- `--model` and `--thinking` can set per-engine model and reasoning strength.
- `--prompt`, `--prompt-file`, and `--dataset` add context to the frozen review bundle.
- `--no-tools` and `--no-web-search` disable read-only tool/web access where supported.
- `--stream-engine-output` streams live engine output while preserving structured validation.
- `--output` and `--json-output` write structured review output to files.

## Helper Behavior

The helper builds one review bundle, calls one selected engine unless a panel is requested, validates
structured output, and exits nonzero when accepted or actionable findings are present. It resolves
bare `git`, `gh`, reviewer, and shell commands from absolute `PATH` entries only; explicit relative
binary paths are resolved from the reviewed repository root.

Treat security findings as important only when they describe concrete actionable risk or removal of
a real safety check. For rejected findings, add code comments only when they document a real
invariant or ownership decision future reviewers need to know.
