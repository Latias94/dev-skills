#!/usr/bin/env python3
"""Validate machine-readable orchestration artifacts for workstreams."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CANONICAL_WORKSTREAM_STATUSES = {"draft", "active", "blocked", "closed"}
ACTIVE_WORKSTREAM_STATUSES = {"draft", "active", "blocked"}
LEGACY_CLOSED_WORKSTREAM_STATUSES = {"complete", "completed", "done", "accepted"}
TASK_STATUSES = {"todo", "running", "done", "blocked", "needs_context", "verified", "accepted"}
HANDOFF_STATUSES = {"DONE", "DONE_WITH_CONCERNS", "BLOCKED", "NEEDS_CONTEXT"}
CAMPAIGN_STATUSES = {"draft", "approved", "running", "blocked", "done", "accepted"}
SIDE_EFFECT_POLICIES = {"manual", "auto-commit", "auto-commit-sync", "auto-commit-sync-merge"}


def read_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"{path}: cannot read: {exc}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: expected JSON object")
        return None
    return value


def read_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"{path}: cannot read: {exc}")
        return rows

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{index}: invalid JSONL row: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{index}: expected JSON object")
            continue
        rows.append(value)
    return rows


def require_keys(path: Path, label: str, row: dict[str, Any], keys: list[str], errors: list[str]) -> None:
    for key in keys:
        if key not in row:
            errors.append(f"{path}: {label} missing {key}")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_context(
    workstream_dir: Path,
    root: Path,
    errors: list[str],
    warnings: list[str],
    required: bool,
) -> None:
    context_path = workstream_dir / "CONTEXT.jsonl"
    if not context_path.exists():
        if required:
            errors.append(f"{context_path}: missing context manifest")
        return
    rows = read_jsonl(context_path, errors)
    for row in rows:
        file_value = row.get("path") or row.get("file")
        if not isinstance(file_value, str) or not file_value:
            errors.append(f"{context_path}: context row missing path")
            continue
        target = Path(file_value)
        target = target if target.is_absolute() else root / target
        if row.get("required") is True and not target.exists():
            warnings.append(f"{context_path}: required context target does not exist: {file_value}")


def validate_tasks(
    workstream_dir: Path,
    todo_text: str,
    errors: list[str],
    warnings: list[str],
    required: bool,
) -> set[str]:
    tasks_path = workstream_dir / "TASKS.jsonl"
    if not tasks_path.exists():
        if required:
            errors.append(f"{tasks_path}: missing TASKS.jsonl")
        return set()

    rows = read_jsonl(tasks_path, errors)
    ids: set[str] = set()
    for row in rows:
        task_id = str(row.get("task_id") or "")
        label = task_id or "task"
        require_keys(
            tasks_path,
            label,
            row,
            ["task_id", "status", "owner", "deps", "scope", "validation", "context", "evidence"],
            errors,
        )
        if not task_id:
            continue
        if task_id in ids:
            errors.append(f"{tasks_path}: duplicate task_id {task_id}")
        ids.add(task_id)
        status = str(row.get("status") or "")
        if status not in TASK_STATUSES:
            errors.append(f"{tasks_path}: {task_id} has invalid status {status!r}")
        handoff = row.get("handoff_status")
        if handoff is not None and str(handoff) not in HANDOFF_STATUSES:
            errors.append(f"{tasks_path}: {task_id} has invalid handoff_status {handoff!r}")
        for list_key in ["deps", "scope", "validation", "context", "evidence"]:
            if not isinstance(row.get(list_key), list):
                errors.append(f"{tasks_path}: {task_id} field {list_key} must be an array")
        if task_id not in todo_text:
            warnings.append(f"{tasks_path}: {task_id} is not mentioned in TODO.md")

    for row in rows:
        task_id = str(row.get("task_id") or "")
        for dep in as_list(row.get("deps")):
            if str(dep) not in ids:
                errors.append(f"{tasks_path}: {task_id} depends on unknown task {dep}")
    return ids


def validate_campaigns(
    workstream_dir: Path,
    task_ids: set[str],
    errors: list[str],
    required: bool,
) -> None:
    campaigns_path = workstream_dir / "CAMPAIGNS.jsonl"
    if not campaigns_path.exists():
        if required:
            errors.append(f"{campaigns_path}: missing CAMPAIGNS.jsonl")
        return

    rows = read_jsonl(campaigns_path, errors)
    ids: set[str] = set()
    for row in rows:
        campaign_id = str(row.get("campaign_id") or row.get("id") or "")
        label = campaign_id or "campaign"
        require_keys(
            campaigns_path,
            label,
            row,
            [
                "campaign_id",
                "status",
                "lane_slug",
                "ordered_tasks",
                "gates",
                "side_effect_policy",
                "stop_conditions",
                "approved_by_user",
            ],
            errors,
        )
        if not campaign_id:
            continue
        if campaign_id in ids:
            errors.append(f"{campaigns_path}: duplicate campaign_id {campaign_id}")
        ids.add(campaign_id)
        if str(row.get("status") or "") not in CAMPAIGN_STATUSES:
            errors.append(f"{campaigns_path}: {campaign_id} has invalid status {row.get('status')!r}")
        if str(row.get("side_effect_policy") or "") not in SIDE_EFFECT_POLICIES:
            errors.append(
                f"{campaigns_path}: {campaign_id} has invalid side_effect_policy "
                f"{row.get('side_effect_policy')!r}"
            )
        for list_key in ["ordered_tasks", "gates", "stop_conditions"]:
            if not isinstance(row.get(list_key), list):
                errors.append(f"{campaigns_path}: {campaign_id} field {list_key} must be an array")
        for task_id in as_list(row.get("ordered_tasks")):
            if str(task_id) not in task_ids:
                errors.append(f"{campaigns_path}: {campaign_id} references unknown task {task_id}")


def validate_workstream(
    workstream_dir: Path,
    root: Path,
    strict_history: bool,
) -> tuple[list[str], list[str], str]:
    errors: list[str] = []
    warnings: list[str] = []
    workstream_json = workstream_dir / "WORKSTREAM.json"
    data = read_json(workstream_json, errors)
    if data is None:
        return errors, warnings, "<invalid>"

    status = str(data.get("status") or "")
    legacy_closed = status in LEGACY_CLOSED_WORKSTREAM_STATUSES
    runtime_required = status in ACTIVE_WORKSTREAM_STATUSES or strict_history
    if status not in CANONICAL_WORKSTREAM_STATUSES and (strict_history or not legacy_closed):
        warnings.append(f"{workstream_json}: non-canonical status {status!r}")

    for name in ["TODO.md", "EVIDENCE_AND_GATES.md", "HANDOFF.md"]:
        if runtime_required and not (workstream_dir / name).exists():
            errors.append(f"{workstream_dir / name}: missing required workstream file")

    try:
        todo_text = (workstream_dir / "TODO.md").read_text(encoding="utf-8")
    except OSError:
        todo_text = ""

    if runtime_required:
        task_ids = validate_tasks(workstream_dir, todo_text, errors, warnings, required=True)
        current_task = data.get("current_task")
        if current_task and str(current_task) not in task_ids:
            errors.append(f"{workstream_json}: current_task {current_task!r} is not in TASKS.jsonl")
        validate_campaigns(workstream_dir, task_ids, errors, required=True)
        validate_context(workstream_dir, root, errors, warnings, required=True)
    return errors, warnings, status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument(
        "--strict-history",
        action="store_true",
        help="also require current machine-readable runtime artifacts for closed or legacy history",
    )
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    base = root / "docs" / "workstreams"
    all_errors: list[str] = []
    all_warnings: list[str] = []
    status_counts: dict[str, int] = {}
    workstreams = sorted(base.glob("*/WORKSTREAM.json")) if base.exists() else []

    for workstream_json in workstreams:
        errors, warnings, status = validate_workstream(workstream_json.parent, root, args.strict_history)
        status_counts[status] = status_counts.get(status, 0) + 1
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    result = {
        "root": str(root),
        "workstreams_checked": len(workstreams),
        "status_counts": status_counts,
        "strict_history": args.strict_history,
        "errors": all_errors,
        "warnings": all_warnings,
    }

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Root: {root}")
        print(f"Workstreams checked: {len(workstreams)}")
        if status_counts:
            status_summary = ", ".join(f"{key}={value}" for key, value in sorted(status_counts.items()))
            print(f"Status counts: {status_summary}")
        if not args.strict_history:
            legacy_count = sum(status_counts.get(status, 0) for status in LEGACY_CLOSED_WORKSTREAM_STATUSES)
            if legacy_count:
                print(f"Legacy closed history skipped for runtime-artifact requirements: {legacy_count}")
        if all_errors:
            print("\nErrors:")
            for error in all_errors:
                print(f"- {error}")
        if all_warnings:
            print("\nWarnings:")
            for warning in all_warnings:
                print(f"- {warning}")
        if not all_errors and not all_warnings:
            print("\nOK: orchestration artifacts are consistent.")

    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
