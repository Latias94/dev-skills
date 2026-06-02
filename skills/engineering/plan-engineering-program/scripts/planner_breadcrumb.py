#!/usr/bin/env python3
"""Derive a compact planner breadcrumb from repo orchestration artifacts.

This stays read-only and derived. The output is meant to be embedded into
planner-style prompts, handoffs, or future hook-style runtime injection
without becoming a new source of truth.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from program_status import ACTIVE_WORKSTREAM_STATUSES, read_jsonl, workstream_summary


def load_campaigns(workstream_dir: Path) -> list[dict[str, Any]]:
    return read_jsonl(workstream_dir / "CAMPAIGNS.jsonl")


def classify_mode(rows: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    active_rows = [row for row in rows if row["status"] in ACTIVE_WORKSTREAM_STATUSES]
    ready_rows = [row for row in active_rows if row["readiness"] == "ready"]
    historical_rows = [row for row in rows if row["status"] not in ACTIVE_WORKSTREAM_STATUSES]
    if active_rows:
        return "READINESS", active_rows, ready_rows
    if historical_rows:
        return "AUDIT", active_rows, ready_rows
    return "READINESS", active_rows, ready_rows


def determine_phase(mode: str, active_rows: list[dict[str, Any]], ready_rows: list[dict[str, Any]]) -> str:
    if mode == "AUDIT":
        return "DISCOVERY"
    if active_rows and not ready_rows:
        return "PLAN"
    if ready_rows:
        return "ASSIGN"
    return "DISCOVERY"


def first_running_campaign(workstream_dir: Path) -> str:
    for row in load_campaigns(workstream_dir):
        if str(row.get("status") or "") in {"running", "approved"}:
            return str(row.get("campaign_id") or "")
    return ""


def summarize(root: Path) -> dict[str, Any]:
    rows = workstream_summary(root)
    mode, active_rows, ready_rows = classify_mode(rows)
    phase = determine_phase(mode, active_rows, ready_rows)

    active_row = ready_rows[0] if ready_rows else active_rows[0] if active_rows else None
    active_slug = str(active_row["slug"]) if active_row else ""
    workstream_dir = root / str(active_row["path"]) if active_row else None
    current_task = str(active_row["current_task"]) if active_row else ""
    campaign_id = first_running_campaign(workstream_dir) if workstream_dir else ""
    blockers = []
    if active_row and active_row["readiness"] not in {"ready", "history"}:
        blockers = [part for part in str(active_row["readiness"]).split(",") if part]

    if mode == "AUDIT":
        next_step = "Inspect historical drift and decide whether cleanup is worth planning."
    elif ready_rows:
        next_step = "Assign the next bounded task or approved same-lane campaign."
    elif active_rows:
        next_step = "Repair active queue readiness blockers before assigning implementation."
    else:
        next_step = "Inspect repo scale and decide between direct task, workstream, or lane planning."

    context_paths: list[str] = []
    if workstream_dir and (workstream_dir / "CONTEXT.jsonl").exists():
        for row in read_jsonl(workstream_dir / "CONTEXT.jsonl"):
            path = row.get("path") or row.get("file")
            if isinstance(path, str) and path:
                context_paths.append(path)

    return {
        "root": str(root),
        "phase": phase,
        "operating_mode": mode,
        "implementation_horizon": len(ready_rows),
        "active_workstream": active_slug,
        "active_task": current_task,
        "active_campaign": campaign_id,
        "blockers": blockers,
        "required_context": context_paths[:8],
        "next_step": next_step,
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        f"Phase: {summary['phase']}",
        f"Operating Mode: {summary['operating_mode']}",
        f"Implementation Horizon: {summary['implementation_horizon']}",
        f"Active Workstream: {summary['active_workstream'] or '(none)'}",
        f"Active Task: {summary['active_task'] or '(none)'}",
        f"Active Campaign: {summary['active_campaign'] or '(none)'}",
    ]
    if summary["blockers"]:
        lines.append("Blockers: " + ", ".join(summary["blockers"]))
    if summary["required_context"]:
        lines.append("Required Context:")
        lines.extend(f"- {path}" for path in summary["required_context"])
    lines.append(f"Next Step: {summary['next_step']}")
    return "\n".join(lines)


def render_prompt_block(summary: dict[str, Any]) -> str:
    """Render a compact prompt-ready runtime block.

    The block is intentionally small enough to prepend to planner / integrator
    prompts on every turn without duplicating the full workstream inventory.
    """

    lines = [
        "<planner-runtime>",
        f"Phase: {summary['phase']}",
        f"Operating Mode: {summary['operating_mode']}",
        f"Implementation Horizon: {summary['implementation_horizon']}",
        f"Active Workstream: {summary['active_workstream'] or '(none)'}",
        f"Active Task: {summary['active_task'] or '(none)'}",
        f"Active Campaign: {summary['active_campaign'] or '(none)'}",
    ]
    if summary["blockers"]:
        lines.append("Readiness Blockers: " + ", ".join(summary["blockers"]))
    if summary["required_context"]:
        lines.append("Required Context:")
        lines.extend(f"- {path}" for path in summary["required_context"])
    lines.append(f"Next Step: {summary['next_step']}")
    lines.append(
        "Rule: Treat this as derived runtime guidance only; ADRs, architecture docs, workstreams,"
        " task ledgers, and evidence remain authoritative."
    )
    lines.append("</planner-runtime>")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json", "prompt"], default="text")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    summary = summarize(root)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif args.format == "prompt":
        print(render_prompt_block(summary))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
