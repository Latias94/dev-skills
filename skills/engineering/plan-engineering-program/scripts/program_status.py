#!/usr/bin/env python3
"""Summarize orchestration state for an upper planner."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


TASK_STATUSES = ["todo", "running", "done", "blocked", "needs_context", "verified", "accepted"]
CAMPAIGN_STATUSES = ["draft", "approved", "running", "blocked", "done", "accepted"]
ACTIVE_WORKSTREAM_STATUSES = {"draft", "active", "blocked"}
LEGACY_CLOSED_WORKSTREAM_STATUSES = {"complete", "completed", "done", "accepted"}


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return rows

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return ""
    return result.stdout.strip()


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def count_by(rows: list[dict[str, Any]], field: str, statuses: list[str]) -> dict[str, int]:
    counts = Counter(str(row.get(field, "unknown")).strip() or "unknown" for row in rows)
    result = {status: counts.get(status, 0) for status in statuses}
    for status, count in sorted(counts.items()):
        if status not in result:
            result[status] = count
    return result


def first_task(tasks: list[dict[str, Any]], *statuses: str) -> str:
    wanted = set(statuses)
    for task in tasks:
        if task.get("status") in wanted:
            return str(task.get("task_id", ""))
    return ""


def workstream_summary(root: Path) -> list[dict[str, Any]]:
    base = root / "docs" / "workstreams"
    if not base.exists():
        return []

    rows: list[dict[str, Any]] = []
    for json_path in sorted(base.glob("*/WORKSTREAM.json")):
        data = read_json(json_path) or {}
        workstream_dir = json_path.parent
        tasks_path = workstream_dir / "TASKS.jsonl"
        campaigns_path = workstream_dir / "CAMPAIGNS.jsonl"
        tasks = read_jsonl(tasks_path)
        campaigns = read_jsonl(campaigns_path)
        workstream_status = str(data.get("status") or "unknown")
        runtime_required = workstream_status in ACTIVE_WORKSTREAM_STATUSES
        current_task = str(data.get("current_task") or "")
        if not current_task:
            current_task = first_task(tasks, "running") or first_task(tasks, "todo", "needs_context")

        blockers: list[str] = []
        if runtime_required:
            for required in ["TODO.md", "CONTEXT.jsonl", "EVIDENCE_AND_GATES.md", "HANDOFF.md"]:
                if not (workstream_dir / required).exists():
                    blockers.append(f"missing-{required}")
            if not tasks_path.exists():
                blockers.append("missing-TASKS.jsonl")
            if not campaigns_path.exists():
                blockers.append("missing-CAMPAIGNS.jsonl")
            if current_task and tasks and current_task not in {str(task.get("task_id")) for task in tasks}:
                blockers.append("current-task-not-in-TASKS")

        rows.append(
            {
                "slug": str(data.get("slug") or workstream_dir.name),
                "path": rel(workstream_dir, root),
                "status": workstream_status,
                "lane_slug": str(data.get("lane_slug") or ""),
                "current_task": current_task,
                "task_counts": count_by(tasks, "status", TASK_STATUSES),
                "campaign_counts": count_by(campaigns, "status", CAMPAIGN_STATUSES),
                "readiness": "ready" if runtime_required and not blockers else ",".join(blockers) if blockers else "history",
            }
        )
    return rows


def table(rows: list[dict[str, Any]]) -> str:
    headers = ["status", "slug", "lane_slug", "current_task", "readiness"]
    if not rows:
        return "(none)"
    widths = {
        header: max(len(header), *(len(str(row.get(header, ""))) for row in rows))
        for header in headers
    }
    lines = [
        "  ".join(header.ljust(widths[header]) for header in headers),
        "  ".join("-" * widths[header] for header in headers),
    ]
    for row in rows:
        lines.append("  ".join(str(row.get(header, "")).ljust(widths[header]) for header in headers))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--all", action="store_true", help="print all historical workstream rows in text output")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    rows = workstream_summary(root)
    branch = git(root, "branch", "--show-current")
    head = git(root, "rev-parse", "--short", "HEAD")
    status = git(root, "status", "--short", "--branch")
    worktrees = git(root, "worktree", "list", "--porcelain")
    status_counts = Counter(row["status"] for row in rows)
    active_rows = [row for row in rows if row["status"] in ACTIVE_WORKSTREAM_STATUSES]
    ready_active = [row for row in active_rows if row["readiness"] == "ready"]
    blocked_active = [row for row in active_rows if row["readiness"] not in {"ready", "history"}]
    historical_rows = [row for row in rows if row["status"] not in ACTIVE_WORKSTREAM_STATUSES]
    result = {
        "root": str(root),
        "branch": branch,
        "head": head,
        "git_status": status.splitlines(),
        "worktree_count": sum(1 for line in worktrees.splitlines() if line.startswith("worktree ")),
        "status_counts": dict(sorted(status_counts.items())),
        "workstreams": rows,
        "active_workstreams": active_rows,
        "ready_workstreams": ready_active,
        "blocked_workstreams": blocked_active,
        "historical_workstreams": historical_rows,
        "implementation_horizon": len(ready_active),
    }

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"Root: {root}")
    print(f"Branch: {branch or '(unknown)'}")
    print(f"Head: {head or '(unknown)'}")
    print(f"Worktrees: {result['worktree_count']}")
    if status_counts:
        counts = ", ".join(f"{key}={value}" for key, value in sorted(status_counts.items()))
        print(f"Status counts: {counts}")
    legacy_count = sum(status_counts.get(status, 0) for status in LEGACY_CLOSED_WORKSTREAM_STATUSES)
    if legacy_count:
        print(f"Legacy closed history skipped by default: {legacy_count}")

    print("\nActive Workstreams")
    print("------------------")
    print(table(active_rows))
    if not args.all and historical_rows:
        print(f"\nHistorical rows hidden: {len(historical_rows)}. Use --all to print them.")
    if args.all:
        print("\nAll Workstreams")
        print("---------------")
        print(table(rows))
    if blocked_active:
        print(
            f"\nImplementation Horizon: {len(ready_active)} ready active rows; "
            f"{len(blocked_active)} active rows blocked until readiness issues are repaired."
        )
    elif active_rows:
        print(f"\nImplementation Horizon: {len(ready_active)} ready active rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
