#!/usr/bin/env python3
"""Build product-capability RECON subagent prompt packets from runtime state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from capability_parallelism import RECON_RESULT_CONTRACT, build_capability_summary


def all_candidates(summary: dict[str, Any]) -> list[dict[str, Any]]:
    parallelism = summary["capability_parallelism"]
    rows: list[dict[str, Any]] = []
    for group in ("recon_candidates", "product_decision_required", "needs_workstream"):
        rows.extend(parallelism[group])
    return rows


def build_prompt(summary: dict[str, Any], row: dict[str, Any]) -> str:
    active = summary["ready_active_unit"]
    blocked = summary["capability_parallelism"]["blocked_by_active_queue"]
    blocked_lines = "\n".join(
        f"- {item['candidate']}: {item['reason']}" for item in blocked
    ) or "- (none)"
    evidence_lines = "\n".join(f"- {path}" for path in row["evidence"][:6]) or "- (none)"
    missing_lines = "\n".join(f"- {item}" for item in row["missing_artifacts"]) or "- (none)"
    fields = "\n".join(f"{field}:" for field in RECON_RESULT_CONTRACT["required_fields"])
    return "\n".join(
        [
            "Use $plan-engineering-program as a product-capability RECON subagent.",
            "Do not edit files. Do not assign implementation. Do not create or modify workstreams.",
            "",
            f"Target repo: {summary['root']}",
            f"Operating mode: {summary['operating_mode']}",
            f"Implementation horizon: {summary['implementation_horizon']}",
            f"Product RECON horizon: {summary['product_recon_horizon']}",
            "",
            "Current ready implementation unit:",
            f"- workstream: {active.get('workstream') or '(none)'}",
            f"- task: {active.get('task') or '(none)'}",
            f"- campaign: {active.get('campaign') or '(none)'}",
            "",
            "Capability to inspect:",
            f"- id: {row['id']}",
            f"- label: {row['label']}",
            f"- classification: {row['classification']}",
            f"- guardrail: {row['guardrail']}",
            "",
            "Evidence seeds:",
            evidence_lines,
            "",
            "Missing artifacts to assess:",
            missing_lines,
            "",
            "Blocked by active queue:",
            blocked_lines,
            "",
            "Return requirements:",
            f"- end with `{RECON_RESULT_CONTRACT['result_marker']}`",
            "- set `implementation_allowed: false` unless a human-approved ADR/workstream/campaign already exists in repo truth",
            "- explain whether this remains RECON, needs product decision, needs workstream, or is blocked by the active queue",
            "- cite concrete repo docs as evidence",
            "",
            RECON_RESULT_CONTRACT["result_marker"],
            fields,
        ]
    )


def build_packet(root: Path, selected: list[str], strict_history: bool = False) -> dict[str, Any]:
    summary = build_capability_summary(root, strict_history)
    candidates = all_candidates(summary)
    by_id = {row["id"]: row for row in candidates}
    if selected:
        missing = [candidate_id for candidate_id in selected if candidate_id not in by_id]
        if missing:
            raise ValueError("unknown capability candidate(s): " + ", ".join(missing))
        candidates = [by_id[candidate_id] for candidate_id in selected]

    packets = [
        {
            "capability_id": row["id"],
            "label": row["label"],
            "classification": row["classification"],
            "guardrail": row["guardrail"],
            "missing_artifacts": row["missing_artifacts"],
            "prompt": build_prompt(summary, row),
        }
        for row in candidates
    ]
    return {
        "root": str(root),
        "implementation_horizon": summary["implementation_horizon"],
        "product_recon_horizon": summary["product_recon_horizon"],
        "ready_active_unit": summary["ready_active_unit"],
        "blocked_by_active_queue": summary["capability_parallelism"]["blocked_by_active_queue"],
        "result_contract": RECON_RESULT_CONTRACT,
        "packets": packets,
    }


def render_text(packet: dict[str, Any]) -> str:
    lines = [
        "## Capability RECON Subagent Packets",
        f"Repo: {packet['root']}",
        f"Implementation Horizon: {packet['implementation_horizon']}",
        f"Product RECON Horizon: {packet['product_recon_horizon']}",
    ]
    for row in packet["packets"]:
        lines.extend(
            [
                "",
                f"## {row['label']} [{row['capability_id']}]",
                row["prompt"],
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--candidate", action="append", default=[], help="capability id to include")
    parser.add_argument(
        "--capability-id",
        action="append",
        default=[],
        help="compatibility alias for --candidate",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    selected = [*args.candidate, *args.capability_id]
    try:
        packet = build_packet(root, selected, args.strict_history)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render_text(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
