#!/usr/bin/env python3
"""Build a single read-only planner payload from orchestration artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_summary import summarize as summarize_audit
from planner_breadcrumb import render_prompt_block, summarize as summarize_breadcrumb
from program_status import workstream_summary


def derive_now_and_why(
    breadcrumb: dict[str, Any],
    audit: dict[str, Any],
    rows: list[dict[str, Any]],
) -> tuple[str, str, str]:
    mode = str(breadcrumb["phase"])
    operating_mode = str(breadcrumb["operating_mode"])
    horizon = int(breadcrumb["implementation_horizon"])
    top_patterns = audit.get("top_patterns") or []
    top_pattern = top_patterns[0]["pattern"] if top_patterns else ""
    top_count = top_patterns[0]["count"] if top_patterns else 0

    if operating_mode == "AUDIT":
        now = "inspect historical drift, then decide whether cleanup or new workstream planning is warranted"
        why = "no active queue is assignable in the current snapshot, so the safe next move is audit-oriented read-only inspection"
        safe_move = "read-only inspection"
    elif horizon > 0:
        if breadcrumb.get("active_task"):
            now = f"assign or resume `{breadcrumb['active_task']}` in `{breadcrumb['active_workstream']}`"
        else:
            now = f"assign or resume `{breadcrumb['active_workstream']}`"
        why = "the repo has a ready active queue with enough machine-readable state to support bounded execution"
        safe_move = "assignment"
    elif breadcrumb.get("blockers"):
        now = "repair active-queue readiness blockers before assigning implementation"
        why = "active work exists, but missing runtime artifacts or task-state drift make assignment unsafe"
        safe_move = "artifact repair"
    else:
        if not rows and not audit["warning_count"] and not audit["error_count"]:
            now = "downshift to a direct engineering skill such as `tdd` or `diagnose` unless the prompt proves durable workstream scope"
            why = "the repo shows no active orchestration substrate and no historical drift, so staying planner-only would add friction without improving safety"
            safe_move = "assignment"
        else:
            now = "inspect repo scale and decide whether to stay direct, open a workstream, or plan a lane"
            why = "no active assignable queue was derived from current artifacts"
            safe_move = "read-only inspection"

    if operating_mode == "READINESS" and top_count:
        why += f"; historical audit pressure exists ({top_pattern} x{top_count}) but does not currently block the active queue"

    return mode, now, why, safe_move


def build_payload(root: Path, strict_history: bool) -> dict[str, Any]:
    breadcrumb = summarize_breadcrumb(root)
    audit = summarize_audit(root, strict_history)
    rows = workstream_summary(root)
    mode, now, why, safe_move = derive_now_and_why(breadcrumb, audit, rows)
    runtime_prompt_block = render_prompt_block(breadcrumb)

    evidence_read = [
        "docs/workstreams/*/WORKSTREAM.json",
        "docs/workstreams/*/TODO.md",
        "docs/workstreams/*/TASKS.jsonl",
        "docs/workstreams/*/CAMPAIGNS.jsonl",
        "docs/workstreams/*/CONTEXT.jsonl",
    ]
    if audit["warning_count"]:
        evidence_read.append("historical warning patterns from validate_orchestration_state.py")

    return {
        "root": str(root),
        "runtime_prompt_block": runtime_prompt_block,
        "program_action": {
            "mode": mode,
            "operating_mode": breadcrumb["operating_mode"],
            "implementation_horizon": breadcrumb["implementation_horizon"],
            "now": now,
            "why": why,
            "safe_next_move": safe_move,
        },
        "active_unit": {
            "workstream": breadcrumb["active_workstream"],
            "task": breadcrumb["active_task"],
            "campaign": breadcrumb["active_campaign"],
            "blockers": breadcrumb["blockers"],
            "required_context": breadcrumb["required_context"],
        },
        "audit_pressure": {
            "warning_count": audit["warning_count"],
            "error_count": audit["error_count"],
            "top_patterns": audit["top_patterns"][:3],
            "unmatched_warning_count": audit["unmatched_warning_count"],
        },
        "repo_summary": {
            "workstreams_checked": audit["workstreams_checked"],
            "status_counts": audit["status_counts"],
            "active_workstream_count": sum(1 for row in rows if row["status"] in {"draft", "active", "blocked"}),
        },
        "evidence_read": evidence_read,
    }


def render_text(payload: dict[str, Any]) -> str:
    action = payload["program_action"]
    active = payload["active_unit"]
    audit = payload["audit_pressure"]
    lines = [
        "## Program Action",
        f"Mode: {action['mode']}",
        f"Operating Mode: {action['operating_mode']}",
        f"Implementation Horizon: {action['implementation_horizon']}",
        f"Now: {action['now']}",
        f"Why: {action['why']}",
        f"Safe Next Move: {action['safe_next_move']}",
        "",
        "## Active Unit",
        f"Workstream: {active['workstream'] or '(none)'}",
        f"Task: {active['task'] or '(none)'}",
        f"Campaign: {active['campaign'] or '(none)'}",
    ]
    if active["blockers"]:
        lines.append("Blockers: " + ", ".join(active["blockers"]))
    if active["required_context"]:
        lines.append("Required Context:")
        lines.extend(f"- {path}" for path in active["required_context"])
    lines.extend(
        [
            "",
            "## Audit Pressure",
            f"Warnings: {audit['warning_count']}",
            f"Errors: {audit['error_count']}",
        ]
    )
    for row in audit["top_patterns"]:
        lines.append(f"- {row['pattern']}: {row['count']}")
    lines.extend(["", "## Runtime Prompt Block", payload["runtime_prompt_block"]])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    payload = build_payload(root, args.strict_history)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
