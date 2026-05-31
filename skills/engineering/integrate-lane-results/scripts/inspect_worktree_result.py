#!/usr/bin/env python3
"""Inspect a worktree result for integration intake without pasted reports."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import session_tail_for_worktree as session_tail  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


STATUS_RE = re.compile(r"\b(DONE_WITH_CONCERNS|DONE|BLOCKED|NEEDS_CONTEXT)\b")
TASK_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}-\d{3,}\b")
WORKSTREAM_RE = re.compile(r"docs[\\/]+workstreams[\\/]+([A-Za-z0-9_.-]+)")


def run_git(worktree: Path, args: list[str], timeout: int = 30) -> dict[str, Any]:
    cmd = ["git", "-C", str(worktree), *args]
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "cmd": cmd, "stdout": "", "stderr": str(exc), "returncode": None}
    return {
        "ok": completed.returncode == 0,
        "cmd": cmd,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "returncode": completed.returncode,
    }


def truncate(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text.replace("\x00", "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def truncate_multiline(text: str, limit: int) -> str:
    text = session_tail.redact(text.replace("\x00", "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def extract_preserved_message(path: str | None, role: str, max_text: int) -> dict[str, Any] | None:
    if not path:
        return None
    target = Path(path)
    last: dict[str, Any] | None = None
    try:
        handle = target.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return None
    with handle:
        for line_number, line in enumerate(handle, 1):
            record = session_tail.load_json_line(line)
            if not record:
                continue
            payload = record.get("payload")
            found_role = ""
            text = ""
            if record.get("type") == "event_msg" and isinstance(payload, dict):
                if role == "assistant" and payload.get("type") == "agent_message":
                    found_role = "assistant"
                    text = str(payload.get("message") or "")
                elif role == "user" and payload.get("type") == "user_message":
                    found_role = "user"
                    text = str(payload.get("message") or "")
            elif record.get("type") == "response_item" and isinstance(payload, dict):
                if payload.get("type") == "message" and payload.get("role") == role:
                    found_role = role
                    text = session_tail.text_from_content(payload.get("content"))
            if found_role and text.strip():
                last = {
                    "role": found_role,
                    "line": line_number,
                    "timestamp": record.get("timestamp"),
                    "text": truncate_multiline(text, max_text),
                }
    return last


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def read_excerpt(path: Path, max_lines: int = 80, max_chars: int = 4000) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    selected = "\n".join(lines[:max_lines])
    return selected[:max_chars].rstrip()


def last_message_text(session_result: dict[str, Any], key: str) -> str:
    message = session_result.get(key)
    if isinstance(message, dict):
        text = message.get("text")
        if isinstance(text, str):
            return text
    return ""


def parse_worker_report(text: str) -> dict[str, Any]:
    statuses = STATUS_RE.findall(text)
    tasks = sorted(set(TASK_RE.findall(text)))
    workstreams = sorted({m.group(1) for m in WORKSTREAM_RE.finditer(text)})
    validation_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if any(token in lower for token in ("validation", "验证", "passed", "failed", "cargo ", "git diff", "json.tool")):
            validation_lines.append(truncate(line, 240))
    return {
        "status": statuses[0] if statuses else None,
        "taskIds": tasks,
        "workstreamSlugs": workstreams,
        "validationLines": validation_lines[:12],
    }


def resolve_workstream(worktree: Path, explicit: str | None, report: dict[str, Any]) -> Path | None:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            candidate = worktree / candidate
        return candidate
    for slug in report.get("workstreamSlugs") or []:
        candidate = worktree / "docs" / "workstreams" / slug
        if candidate.exists():
            return candidate
    task_ids = set(report.get("taskIds") or [])
    if not task_ids:
        return None
    root = worktree / "docs" / "workstreams"
    if not root.exists():
        return None
    matches: list[Path] = []
    for todo in root.glob("*/TODO.md"):
        try:
            text = todo.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(task_id in text for task_id in task_ids):
            matches.append(todo.parent)
    return matches[0] if len(matches) == 1 else None


def inspect_workstream(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    workstream_json_path = path / "WORKSTREAM.json"
    data = load_json(workstream_json_path)
    todo_excerpt = read_excerpt(path / "TODO.md", max_lines=60, max_chars=3000)
    handoff_excerpt = read_excerpt(path / "HANDOFF.md", max_lines=80, max_chars=4000)
    evidence_excerpt = read_excerpt(path / "EVIDENCE_AND_GATES.md", max_lines=90, max_chars=4000)
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "workstreamJson": str(workstream_json_path) if workstream_json_path.exists() else None,
        "todoExcerpt": todo_excerpt,
        "handoffExcerpt": handoff_excerpt,
        "evidenceExcerpt": evidence_excerpt,
    }
    if data:
        result.update(
            {
                "slug": data.get("slug"),
                "status": data.get("status"),
                "currentTask": data.get("current_task"),
                "completedTasks": data.get("completed_tasks"),
                "laneSlug": data.get("lane_slug"),
                "continuePolicy": data.get("continue_policy"),
            }
        )
    return result


def inspect_git(worktree: Path) -> dict[str, Any]:
    status = run_git(worktree, ["status", "--short", "--branch"])
    head = run_git(worktree, ["rev-parse", "HEAD"])
    short_head = run_git(worktree, ["rev-parse", "--short", "HEAD"])
    diff_stat = run_git(worktree, ["diff", "--stat"])
    diff_names = run_git(worktree, ["diff", "--name-status"])
    contains = run_git(worktree, ["branch", "--contains", "HEAD"])
    status_lines = status["stdout"].splitlines() if status["stdout"] else []
    return {
        "statusShortBranch": status["stdout"],
        "branchLine": status_lines[0] if status_lines else "",
        "dirty": any(line and not line.startswith("##") for line in status_lines),
        "head": head["stdout"] if head["ok"] else None,
        "shortHead": short_head["stdout"] if short_head["ok"] else None,
        "diffStat": diff_stat["stdout"],
        "diffNameStatus": diff_names["stdout"],
        "branchesContainingHead": contains["stdout"],
    }


def integration_intake(git: dict[str, Any], report: dict[str, Any], workstream: dict[str, Any] | None) -> dict[str, Any]:
    worker_status = report.get("status")
    current_task = workstream.get("currentTask") if workstream else None
    if worker_status in {"DONE", "DONE_WITH_CONCERNS", "BLOCKED", "NEEDS_CONTEXT"}:
        mode = "RESULT_INTAKE"
    elif git.get("dirty"):
        mode = "RESULT_INTAKE"
    else:
        mode = "RESULT_INTAKE"

    if worker_status == "DONE_WITH_CONCERNS":
        action = "Integrator reviews concerns, then decides whether fresh verification or a fix prompt is needed."
    elif worker_status == "DONE":
        action = "Integrator reviews the result before accepting completion or assigning verification."
    elif worker_status in {"BLOCKED", "NEEDS_CONTEXT"}:
        action = "Upper planner or integrator resolves the blocker or refines the task before any worker continues."
    elif current_task:
        action = f"Upper planner inspects current task {current_task} and decides whether it is ready to assign."
    else:
        action = "Integrator inspects repo evidence and decides the next bounded action."

    if current_task and worker_status in {"DONE", "DONE_WITH_CONCERNS"}:
        action += f" If accepted, next workstream task is {current_task}."

    return {
        "mode": mode,
        "workerStatus": worker_status,
        "currentTask": current_task,
        "nextAction": action,
    }


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    worktree = Path(args.worktree).expanduser().resolve(strict=False)
    git = inspect_git(worktree)
    session = session_tail.find_latest(
        worktree,
        Path(args.sessions_root).expanduser(),
        max_files=max(1, args.max_files),
        scan_lines=max(1, args.scan_lines),
        max_text=max(400, args.max_text),
    )
    preserved_assistant = extract_preserved_message(session.get("session"), "assistant", max(400, args.max_text))
    if preserved_assistant:
        session["lastAssistantMessage"] = preserved_assistant
    assistant_text = last_message_text(session, "lastAssistantMessage")
    report = parse_worker_report(assistant_text)
    workstream_path = resolve_workstream(worktree, args.workstream, report)
    workstream = inspect_workstream(workstream_path)
    return {
        "schemaVersion": 1,
        "worktree": str(worktree),
        "git": git,
        "session": {
            "path": session.get("session"),
            "sessionMtime": session.get("sessionMtime"),
            "matchedBy": session.get("matchedBy"),
            "matchedPath": session.get("matchedPath"),
            "lineCount": session.get("lineCount"),
            "lastTimestamp": session.get("lastTimestamp"),
            "lastAssistantMessage": session.get("lastAssistantMessage"),
        },
        "workerReport": report,
        "workstream": workstream,
        "integrationIntake": integration_intake(git, report, workstream),
    }


def print_text(result: dict[str, Any]) -> None:
    intake = result["integrationIntake"]
    git = result["git"]
    session = result["session"]
    workstream = result.get("workstream") or {}
    print(f"Mode: {intake['mode']}")
    print(f"Now: {intake['nextAction']}")
    why_parts = []
    if intake.get("workerStatus"):
        why_parts.append(f"last worker status is {intake['workerStatus']}")
    if workstream.get("currentTask"):
        why_parts.append(f"WORKSTREAM current_task is {workstream['currentTask']}")
    why_parts.append("worktree is dirty" if git.get("dirty") else "worktree is clean")
    print(f"Why: {', '.join(why_parts)}.")
    print()
    print(f"Worktree: {result['worktree']}")
    print(f"Git: {git.get('branchLine')} @ {git.get('shortHead')}")
    print(f"Dirty: {git.get('dirty')}")
    if session.get("path"):
        print(f"Session: {session['path']}")
        print(f"Session last timestamp: {session.get('lastTimestamp')}")
    else:
        print("Session: none matched")
    if workstream:
        print(f"Workstream: {workstream.get('path')}")
        print(f"Status: {workstream.get('status')} | Current task: {workstream.get('currentTask')}")
        completed = workstream.get("completedTasks")
        if completed:
            print(f"Completed tasks: {', '.join(completed)}")
    report = result["workerReport"]
    if report.get("taskIds"):
        print(f"Reported task IDs: {', '.join(report['taskIds'])}")
    if report.get("validationLines"):
        print("\nValidation lines:")
        for line in report["validationLines"]:
            print(f"- {line}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worktree", help="Worktree path to inspect.")
    parser.add_argument("--workstream", help="Optional workstream path, absolute or relative to worktree.")
    parser.add_argument("--sessions-root", default=str(session_tail.default_sessions_root()))
    parser.add_argument("--max-files", type=int, default=2000)
    parser.add_argument("--scan-lines", type=int, default=250)
    parser.add_argument("--max-text", type=int, default=4000)
    parser.add_argument("--json", action="store_true", help="Emit JSON for integration consumption.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    result = inspect(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
