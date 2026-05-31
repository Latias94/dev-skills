#!/usr/bin/env python3
"""Summarize workstream state for upper-planner program planning."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ACTIVE_STATUSES = {"active", "draft", "in_progress", "open", "blocked"}
CANONICAL_STATUSES = {"draft", "active", "blocked", "closed"}
STATUS_ALIASES = {"complete": "closed", "completed": "closed"}
TASK_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}-\d{3,}\b")
WORKSTREAM_PATH_RE = re.compile(r"docs[\\/]+workstreams[\\/]+([A-Za-z0-9_.-]+)")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def clean_status(value: Any) -> str:
    return clean(value).strip().lower() or "unknown"


def normalized_status(value: Any) -> str:
    status = clean_status(value)
    return STATUS_ALIASES.get(status, status)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def context_manifest_path(data: dict[str, Any], workstream_dir: Path, root: Path) -> Path:
    explicit = data.get("context_manifest")
    if isinstance(explicit, str) and explicit.strip():
        path = Path(explicit.strip())
        return path if path.is_absolute() else root / path

    docs = data.get("authoritative_docs")
    if isinstance(docs, list):
        for item in docs:
            if not isinstance(item, dict):
                continue
            if item.get("role") != "context_manifest":
                continue
            path_value = item.get("path")
            if isinstance(path_value, str) and path_value.strip():
                path = Path(path_value.strip())
                return path if path.is_absolute() else root / path

    return workstream_dir / "CONTEXT.jsonl"


def summarize_continue_policy(value: Any) -> str:
    if isinstance(value, dict):
        default_action = clean(value.get("default_action"))
        next_task = clean(value.get("next_task"))
        if default_action and next_task:
            return f"{default_action}:{next_task}"
        return default_action or next_task or "present"
    return clean(value)


def todo_task_status(todo_path: Path, task_id: str) -> str:
    if not task_id:
        return "no-current-task"
    try:
        lines = todo_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "missing-todo"

    marker_re = re.compile(rf"^\s*-\s*\[(?P<mark>[ xX\-])\]\s*{re.escape(task_id)}\b")
    loose_re = re.compile(rf"\b{re.escape(task_id)}\b")
    for line in lines:
        marker = marker_re.search(line)
        if marker:
            mark = marker.group("mark")
            if mark in {"x", "X"}:
                return "done"
            if mark == "-":
                return "in-progress"
            return "open"
    return "mentioned-no-checkbox" if any(loose_re.search(line) for line in lines) else "missing"


def parse_lanes_active_queue(root: Path) -> dict[str, dict[str, str]]:
    lanes_path = root / "docs" / "architecture" / "LANES.md"
    try:
        lines = lanes_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return {}

    rows: dict[str, dict[str, str]] = {}
    headers: list[str] | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        raw_cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(raw_cells) < 2:
            continue
        if all(set(cell) <= {"-", ":", " "} and cell for cell in raw_cells):
            continue
        normalized = [normalize_header(cell) for cell in raw_cells]
        if "lane" in normalized and ("active_workstream" in normalized or "queue" in normalized):
            headers = normalized
            continue
        if not headers:
            continue
        cells = [clean_table_cell(cell) for cell in raw_cells]
        if len(cells) < len(headers):
            cells.extend("" for _ in range(len(headers) - len(cells)))
        data = dict(zip(headers, cells))
        slug = extract_workstream_slug(data.get("active_workstream", ""))
        if not slug:
            continue
        task_source = first_present(
            data.get("next_task", ""),
            data.get("queue", ""),
            data.get("current_goal_bundle", ""),
        )
        task_match = TASK_RE.search(task_source)
        rows[slug] = {
            "lane_slug": data.get("lane", ""),
            "next_task": task_match.group(0) if task_match else task_source,
            "role": first_present(data.get("recommended_terminal_role", ""), data.get("status", "")),
        }
    return rows


def normalize_header(cell: str) -> str:
    value = clean_table_cell(cell).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value


def clean_table_cell(cell: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell)
    value = value.replace("<br>", " ").replace("<br/>", " ")
    return value.strip().strip("`").strip("*").strip("_").strip()


def first_present(*values: str) -> str:
    for value in values:
        if value and value.lower() not in {"none", "n/a", "-"}:
            return value
    return ""


def extract_workstream_slug(value: str) -> str:
    value = clean_table_cell(value)
    if not value or value.lower() in {"none", "n/a", "-"}:
        return ""
    path_match = WORKSTREAM_PATH_RE.search(value)
    if path_match:
        return path_match.group(1)
    return value.split()[0].strip("`").strip()


def parse_lanes_holds(root: Path) -> set[str]:
    lanes_path = root / "docs" / "architecture" / "LANES.md"
    try:
        text = lanes_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return set(re.findall(r"Do not start `?([A-Z][A-Z0-9]{1,}-\d{3,})`?", text))


def readiness(row: dict[str, str]) -> str:
    issues: list[str] = []
    if row.get("context_manifest_exists") == "false":
        issues.append("missing-context")
    if row.get("current_task_todo_status") in {"done", "missing", "mentioned-no-checkbox", "missing-todo"}:
        issues.append(f"todo-{row['current_task_todo_status']}")
    if row.get("lane_registry_drift"):
        issues.append("lane-drift")
    return ",".join(issues) if issues else "ready"


def workstream_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    base = root / "docs" / "workstreams"
    if not base.exists():
        return rows

    lane_queue = parse_lanes_active_queue(root)
    lane_holds = parse_lanes_holds(root)

    for json_path in sorted(base.glob("*/WORKSTREAM.json")):
        data = load_json(json_path)
        if data is None:
            rows.append(
                {
                    "slug": json_path.parent.name,
                    "status": "invalid-json",
                    "normalized_status": "invalid-json",
                    "current_task": "",
                    "lane_slug": "",
                    "updated": "",
                    "tags": "",
                    "path": str(json_path.relative_to(root)),
                    "readiness": "invalid-json",
                }
            )
            continue

        slug = clean(data.get("slug")) or json_path.parent.name
        current_task = clean(data.get("current_task"))
        manifest_path = context_manifest_path(data, json_path.parent, root)
        lane_entry = lane_queue.get(slug, {})
        lanes_next_task = clean(lane_entry.get("next_task"))
        drift: list[str] = []
        if lanes_next_task and current_task and lanes_next_task != current_task:
            drift.append(f"LANES next_task={lanes_next_task} != current_task={current_task}")
        if current_task and current_task in lane_holds:
            drift.append(f"LANES says do not start {current_task}")

        row = {
            "slug": slug,
            "status": clean_status(data.get("status")),
            "normalized_status": normalized_status(data.get("status")),
            "current_task": current_task,
            "lane_slug": clean(data.get("lane_slug")),
            "updated": clean(data.get("updated") or data.get("updated_at")),
            "tags": clean(data.get("capability_tags")),
            "path": str(json_path.relative_to(root)),
            "context_manifest": display_path(manifest_path, root),
            "context_manifest_exists": str(manifest_path.exists()).lower(),
            "continue_policy": summarize_continue_policy(data.get("continue_policy")),
            "current_task_todo_status": todo_task_status(json_path.parent / "TODO.md", current_task),
            "lanes_next_task": lanes_next_task,
            "lane_registry_drift": "; ".join(drift),
        }
        row["readiness"] = readiness(row)
        rows.append(row)

    return rows


def print_table(title: str, rows: list[dict[str, str]], headers: list[str] | None = None) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not rows:
        print("(none)")
        return

    headers = headers or ["status", "slug", "lane_slug", "current_task", "updated", "readiness"]
    widths = {
        header: max(len(header), *(len(row.get(header, "")) for row in rows))
        for header in headers
    }
    print("  ".join(header.ljust(widths[header]) for header in headers))
    print("  ".join("-" * widths[header] for header in headers))
    for row in rows:
        print("  ".join(row.get(header, "").ljust(widths[header]) for header in headers))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    rows = workstream_rows(root)
    status_counts = Counter(row["status"] for row in rows)
    normalized_status_counts = Counter(row["normalized_status"] for row in rows)
    active = [row for row in rows if row["normalized_status"] in ACTIVE_STATUSES]
    missing_lane = [
        row for row in rows if row["normalized_status"] in ACTIVE_STATUSES and not row["lane_slug"]
    ]
    readiness_issues = [
        row for row in active if row.get("readiness") and row.get("readiness") != "ready"
    ]
    invalid = [row for row in rows if row["status"] == "invalid-json"]
    non_canonical_status_counts = {
        status: count
        for status, count in sorted(status_counts.items())
        if status not in CANONICAL_STATUSES
    }

    result = {
        "root": str(root),
        "total": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "normalized_status_counts": dict(sorted(normalized_status_counts.items())),
        "non_canonical_status_counts": non_canonical_status_counts,
        "active": active,
        "missing_lane_slug": missing_lane,
        "readiness_issues": readiness_issues,
        "invalid_json": invalid,
        "has_lane_registry": (root / "docs" / "architecture" / "LANES.md").exists(),
    }

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"Root: {root}")
    print(f"Workstreams: {len(rows)}")
    print(f"Has docs/architecture/LANES.md: {result['has_lane_registry']}")
    print("Status counts:")
    for status, count in sorted(status_counts.items()):
        print(f"- {status}: {count}")
    if non_canonical_status_counts:
        print("Non-canonical status counts:")
        for status, count in non_canonical_status_counts.items():
            print(f"- {status}: {count}")
    print("Normalized status counts:")
    for status, count in sorted(normalized_status_counts.items()):
        print(f"- {status}: {count}")

    print_table("Active or Draft Workstreams", active)
    print_table("Active/Draft Missing lane_slug", missing_lane)
    print_table(
        "Active/Draft Readiness Issues",
        readiness_issues,
        ["status", "slug", "current_task", "current_task_todo_status", "readiness", "lane_registry_drift"],
    )
    print_table("Invalid WORKSTREAM.json", invalid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
