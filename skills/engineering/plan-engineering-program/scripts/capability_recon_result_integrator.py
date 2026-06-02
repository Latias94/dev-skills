#!/usr/bin/env python3
"""Merge validated product-capability RECON subagent results for the upper planner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from capability_parallelism import build_capability_summary
from capability_recon_result_validator import parse_blocks, validate_text


def split_value(value: str | None) -> list[str]:
    if value is None:
        return []
    normalized = value.strip()
    if normalized.lower() in {"", "none", "(none)", "n/a", "na", "not applicable"}:
        return []
    parts = normalized.replace(";", ",").split(",")
    return [part.strip() for part in parts if part.strip()]


def integrate_text(root: Path, text: str, strict_history: bool = False) -> dict[str, Any]:
    capability = build_capability_summary(root, strict_history)
    validation = validate_text(root, text, strict_history)
    blocks = parse_blocks(text)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for result, block in zip(validation["results"], blocks):
        if not result["valid"]:
            rejected.append(result)
            continue
        accepted.append(
            {
                "capability_id": result["capability_id"],
                "classification": result["classification"],
                "status": result["status"],
                "evidence": split_value(block.get("evidence")),
                "missing_artifacts": split_value(block.get("missing_artifacts")),
                "owned_scope": split_value(block.get("owned_scope")),
                "shared_scope": split_value(block.get("shared_scope")),
                "product_decisions": split_value(block.get("product_decisions")),
                "blocked_by_active_queue": split_value(block.get("blocked_by_active_queue")),
                "suggested_next_artifact": block.get("suggested_next_artifact", "").strip(),
            }
        )

    suggested_next_artifacts = [
        row["suggested_next_artifact"] for row in accepted if row["suggested_next_artifact"]
    ]
    product_decisions = sorted(
        {decision for row in accepted for decision in row["product_decisions"]}
    )
    blocked_by_results = sorted(
        {blocked for row in accepted for blocked in row["blocked_by_active_queue"]}
    )
    runtime_blocked = [
        row["candidate"]
        for row in capability["capability_parallelism"]["blocked_by_active_queue"]
    ]

    merge_valid = validation["valid"] and bool(accepted)
    return {
        "root": str(root),
        "merge_valid": merge_valid,
        "promotion_allowed": False,
        "promotion_rule": "Validated RECON results are planning inputs only; implementation still requires explicit ADR/workstream/campaign/gates approval.",
        "ready_active_unit": capability["ready_active_unit"],
        "implementation_horizon": capability["implementation_horizon"],
        "product_recon_horizon": capability["product_recon_horizon"],
        "accepted_result_count": len(accepted),
        "rejected_result_count": len(rejected),
        "accepted_results": accepted,
        "rejected_results": rejected,
        "suggested_next_artifacts": suggested_next_artifacts,
        "product_decisions": product_decisions,
        "blocked_by_results": blocked_by_results,
        "runtime_blocked_by_active_queue": runtime_blocked,
        "validation": validation,
    }


def render_text(summary: dict[str, Any]) -> str:
    active = summary["ready_active_unit"]
    lines = [
        "## Capability RECON Result Integration",
        f"Merge Valid: {summary['merge_valid']}",
        f"Promotion Allowed: {summary['promotion_allowed']}",
        f"Implementation Horizon: {summary['implementation_horizon']}",
        f"Product RECON Horizon: {summary['product_recon_horizon']}",
        f"Ready Active Unit: {active.get('workstream') or '(none)'} / {active.get('task') or '(none)'}",
        f"Accepted Results: {summary['accepted_result_count']}",
        f"Rejected Results: {summary['rejected_result_count']}",
        "",
        "## Suggested Next Artifacts",
    ]
    if not summary["suggested_next_artifacts"]:
        lines.append("(none)")
    else:
        lines.extend(f"- {artifact}" for artifact in summary["suggested_next_artifacts"])

    lines.append("")
    lines.append("## Product Decisions")
    if not summary["product_decisions"]:
        lines.append("(none)")
    else:
        lines.extend(f"- {decision}" for decision in summary["product_decisions"])

    lines.append("")
    lines.append("## Runtime Blocked By Active Queue")
    if not summary["runtime_blocked_by_active_queue"]:
        lines.append("(none)")
    else:
        lines.extend(f"- {blocked}" for blocked in summary["runtime_blocked_by_active_queue"])

    lines.extend(["", "## Rule", summary["promotion_rule"]])
    if summary["validation"]["errors"]:
        lines.append("")
        lines.append("## Validation Errors")
        lines.extend(f"- {error}" for error in summary["validation"]["errors"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--input", help="file containing CAPABILITY_RECON_RESULT blocks")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    summary = integrate_text(root, text, args.strict_history)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0 if summary["merge_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
