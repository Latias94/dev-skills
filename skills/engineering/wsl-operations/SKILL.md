---
name: wsl-operations
description: Run WSL commands through a non-interactive, output-sanitizing wrapper and apply guarded distribution lifecycle operations. Use when Codex needs to inspect WSL distributions, execute commands inside WSL from PowerShell, avoid ANSI focus-sequence or UTF-16 output corruption, or stop, shut down, or unregister a WSL distribution.
---

# WSL Operations

Keep the Windows-to-WSL boundary quiet: run without a TTY, capture before display, and identify a
distribution by both name and registered base path before destructive work.

## Clean Execution

1. Resolve `scripts/wsl_run.py` relative to this skill directory. Use it instead of direct
   `wsl.exe` calls when output will be shown to the user.
2. Inspect registered distributions before choosing one:

```powershell
python "$skillRoot\scripts\wsl_run.py" list
python "$skillRoot\scripts\wsl_run.py" registry
```

3. Pass routine commands as argv, not as an interpolated shell string:

```powershell
python "$skillRoot\scripts\wsl_run.py" run --distro Ubuntu-26.04 -- uname -a
python "$skillRoot\scripts\wsl_run.py" run --distro Ubuntu-26.04 --user root -- apt-get update
```

Use repeated `--env NAME=VALUE` options when a command needs non-secret environment values. For a
complex shell program, create a temporary script with `apply_patch`, execute that file with `bash`
through the wrapper, then remove only that known temporary file with `apply_patch`.

The execution step is complete when the child exit code is preserved and displayed output contains
no NUL, DEL, ANSI, OSC, or xterm focus-reporting sequences.

## Lifecycle Operations

Use the wrapper for non-destructive lifecycle commands:

```powershell
python "$skillRoot\scripts\wsl_run.py" terminate --distro Ubuntu-26.04
python "$skillRoot\scripts\wsl_run.py" shutdown
```

Before unregistering, require explicit user authorization to destroy the distribution, then compare
the exact `registry` name and base path against the intended target. Supply both values again so the
wrapper can reject stale or ambiguous state:

```powershell
python "$skillRoot\scripts\wsl_run.py" unregister --distro Ubuntu --expected-base-path 'H:\WSL\Ubuntu' --confirm-destroy Ubuntu
```

The unregister step is complete only when the command succeeds and the distribution no longer
exists in the WSL registry. Never substitute a similar name or infer a target from the default marker.

## Terminal Artifacts

Treat literal `[I` and `[O` after an escape byte as xterm focus-in/focus-out reports. Treat embedded
NUL characters in `wsl.exe --list` output as UTF-16LE. The wrapper handles both by detaching stdin,
capturing pipes, decoding before display, and stripping terminal controls. If focus text still enters
the prompt after the wrapper exits, report a host terminal or Codex UI state leak; restarting that UI
may be required because a skill can mitigate but cannot reset another process's terminal mode.

## Example

```text
Use $wsl-operations to list my WSL distributions cleanly, run `uname -a` in Ubuntu-26.04, and report
the exact exit status without allowing terminal control sequences into the conversation UI.
```
