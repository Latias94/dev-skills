#!/usr/bin/env python3
"""Summarize workstream state for upper-planner program planning."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ACTIVE_STATUSES = {"active", "draft", "in_progress", "open", "blocked"}
CANONICAL_STATUSES = {"draft", "active", "blocked", "closed"}


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


def workstream_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    base = root / "docs" / "workstreams"
    if not base.exists():
        return rows

    for json_path in sorted(base.glob("*/WORKSTREAM.json")):
        data = load_json(json_path)
        if data is None:
            rows.append(
                {
                    "slug": json_path.parent.name,
                    "status": "invalid-json",
                    "current_task": "",
                    "lane_slug": "",
                    "updated": "",
                    "tags": "",
                    "path": str(json_path.relative_to(root)),
                }
            )
            continue

        rows.append(
            {
                "slug": clean(data.get("slug")) or json_path.parent.name,
                "status": clean_status(data.get("status")),
                "current_task": clean(data.get("current_task")),
                "lane_slug": clean(data.get("lane_slug")),
                "updated": clean(data.get("updated") or data.get("updated_at")),
                "tags": clean(data.get("capability_tags")),
                "path": str(json_path.relative_to(root)),
            }
        )

    return rows


def print_table(title: str, rows: list[dict[str, str]]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not rows:
        print("(none)")
        return

    headers = ["status", "slug", "lane_slug", "current_task", "updated"]
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
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rows = workstream_rows(root)
    status_counts = Counter(row["status"] for row in rows)
    active = [row for row in rows if row["status"] in ACTIVE_STATUSES]
    missing_lane = [
        row for row in rows if row["status"] in ACTIVE_STATUSES and not row["lane_slug"]
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
        "non_canonical_status_counts": non_canonical_status_counts,
        "active": active,
        "missing_lane_slug": missing_lane,
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

    print_table("Active or Draft Workstreams", active)
    print_table("Active/Draft Missing lane_slug", missing_lane)
    print_table("Invalid WORKSTREAM.json", invalid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
