#!/usr/bin/env python3
"""Classify the smallest dev-skills workflow scale that fits a repository."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from program_status import read_jsonl, workstream_summary


ACTIVE_STATUSES = {"active", "blocked", "draft"}
APPROVED_CAMPAIGN_STATUSES = {"approved", "running"}


PRESET_SURFACES = {
    "direct": [
        "use tdd, diagnose, prototype, or a direct edit",
        "keep workstream, lane, and campaign docs hidden unless the task itself needs durable planning",
    ],
    "workstream": [
        "use one workstream surface and task ledger",
        "hide lane maps, campaign queues, and program dispatch until the workstream is ready",
    ],
    "lane": [
        "use lane-level planning and one owned capability surface",
        "hide campaign queues and worker dispatch until a ready queue or approved campaign exists",
    ],
    "program": [
        "use planner.py status, dispatch, and chain before assigning terminals",
        "keep implementation scoped to ready active workstreams or approved campaigns",
    ],
    "audit-repair": [
        "repair or summarize historical workflow substrate before assigning from it",
        "a new bounded direct task can still downshift through dev-flow if it does not depend on historical queue authority",
    ],
}


def has_file(root: Path, rel: str) -> bool:
    return (root / rel).is_file()


def count_machine_artifacts(root: Path, filename: str) -> int:
    base = root / "docs" / "workstreams"
    if not base.is_dir():
        return 0
    return sum(1 for _ in base.rglob(filename))


def count_approved_campaigns(root: Path) -> int:
    base = root / "docs" / "workstreams"
    if not base.is_dir():
        return 0
    count = 0
    for path in base.rglob("CAMPAIGNS.jsonl"):
        for row in read_jsonl(path):
            status = str(row.get("status") or "").strip().lower()
            if status in APPROVED_CAMPAIGN_STATUSES and row.get("approved_by_user") is True:
                count += 1
    return count


def classify(root: Path) -> dict[str, Any]:
    rows = workstream_summary(root)
    active_rows = [row for row in rows if str(row.get("status", "")).lower() in ACTIVE_STATUSES]
    ready_active_rows = [row for row in active_rows if row.get("readiness") == "ready"]
    blocked_active_rows = [row for row in active_rows if row.get("readiness") not in {"ready", "history"}]
    active_count = len(active_rows)
    ready_active_count = len(ready_active_rows)
    workstream_count = len(rows)
    has_lanes = has_file(root, "docs/architecture/LANES.md")
    has_workstream_links = has_file(root, "docs/architecture/WORKSTREAM_LINKS.md")
    task_jsonl_count = count_machine_artifacts(root, "TASKS.jsonl")
    campaign_file_count = count_machine_artifacts(root, "CAMPAIGNS.jsonl")
    approved_campaign_count = count_approved_campaigns(root)

    if workstream_count == 0 and not has_lanes:
        preset = "direct"
        reason = "no durable workstream or lane substrate was detected"
    elif active_count == 0 and workstream_count >= 20:
        preset = "audit-repair"
        reason = "historical workstream substrate exists but no active queue is assignable from that history"
    elif has_lanes and (
        approved_campaign_count > 0
        or ready_active_count > 1
        or (has_workstream_links and ready_active_count > 0)
    ):
        preset = "program"
        reason = "lane substrate plus approved campaigns, ready workstream links, or multiple ready active units require upper-planner coordination"
    elif has_lanes:
        preset = "lane"
        reason = "architecture lane substrate exists, but program-level campaign coordination is not yet required"
    else:
        preset = "workstream"
        reason = "durable workstream substrate exists without architecture-lane coordination"

    return {
        "root": str(root),
        "preset": preset,
        "reason": reason,
        "counts": {
            "workstreams": workstream_count,
            "active_or_draft_workstreams": active_count,
            "ready_active_workstreams": ready_active_count,
            "blocked_active_workstreams": len(blocked_active_rows),
            "task_jsonl": task_jsonl_count,
            "campaign_files": campaign_file_count,
            "approved_or_running_campaigns": approved_campaign_count,
        },
        "signals": {
            "has_lanes": has_lanes,
            "has_workstream_links": has_workstream_links,
        },
        "recommended_surface": PRESET_SURFACES[preset],
        "rule": "Use the smallest preset that protects the work; this is a routing hint, not a new source of workflow artifact truth.",
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "## Workflow Scale",
        f"Preset: {summary['preset']}",
        f"Reason: {summary['reason']}",
        "",
        "## Counts",
    ]
    for key, value in summary["counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Signals"])
    for key, value in summary["signals"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Recommended Surface"])
    lines.extend(f"- {item}" for item in summary["recommended_surface"])
    lines.extend(["", "## Rule", summary["rule"]])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    summary = classify(root)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
