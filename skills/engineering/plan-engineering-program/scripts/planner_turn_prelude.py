#!/usr/bin/env python3
"""Build a derived-only planner turn prelude that simulates per-turn injection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from planner_payload import build_payload
from dispatch_rehearsal import summarize as summarize_dispatch


def summarize(root: Path, strict_history: bool) -> dict[str, Any]:
    payload = build_payload(root, strict_history)
    dispatch = summarize_dispatch(root, strict_history)
    action = payload["program_action"]
    active = payload["active_unit"]
    product = dispatch.get("product_parallelism", {})

    guidance = []
    if action["operating_mode"] == "AUDIT":
        guidance.append("Stay read-only. Do not fabricate worker dispatch or bounded execution.")
    elif action["implementation_horizon"] > 0:
        guidance.append("Prefer bounded assignment from the active queue instead of reopening global planning.")
    elif action["safe_next_move"] == "artifact repair":
        guidance.append("Repair active-queue readiness drift before assigning implementation.")
    else:
        guidance.append("Choose the smallest safe workflow scale from current repo evidence.")

    if active.get("required_context"):
        guidance.append("Load only the listed required context first; avoid broad rereads.")
    if dispatch["recommended_route"]["skill"] == "run-workstream-task":
        guidance.append("Do not choose a different global next task unless repo evidence contradicts the derived queue.")
    if product.get("product_recon_horizon"):
        guidance.append(
            "When discussing parallel work, separate ready implementation from read-only product RECON candidates."
        )

    capability_lines: list[str] = []
    if product.get("product_recon_horizon"):
        capability_lines.extend(
            [
                "<capability-parallelism>",
                f"Product RECON Horizon: {product['product_recon_horizon']}",
                f"Product RECON Candidates: {product['recon_candidate_count']}",
                f"Product Decisions Required: {product['product_decision_required_count']}",
                f"Needs Workstream: {product['needs_workstream_count']}",
                f"Blocked By Active Queue: {product['blocked_by_active_queue_count']}",
                "Top RECON Candidates:",
            ]
        )
        for row in product.get("top_recon_candidates", []):
            capability_lines.append(
                f"- {row['id']}: {row['label']} (guardrail: {row['guardrail']})"
            )
        if product.get("top_product_decisions"):
            capability_lines.append("Product Decisions Required:")
            for row in product["top_product_decisions"]:
                capability_lines.append(
                    f"- {row['id']}: {row['label']} (missing: {', '.join(row['missing_artifacts'])})"
                )
        if product.get("top_needs_workstream"):
            capability_lines.append("Needs Workstream:")
            for row in product["top_needs_workstream"]:
                capability_lines.append(
                    f"- {row['id']}: {row['label']} (missing: {', '.join(row['missing_artifacts'])})"
                )
        if product.get("blocked_by_active_queue"):
            capability_lines.append("Blocked By Active Queue:")
            for row in product["blocked_by_active_queue"]:
                capability_lines.append(f"- {row['candidate']}: {row['reason']}")
        capability_lines.extend(
            [
                f"Rule: {product['rule']}",
                "</capability-parallelism>",
            ]
        )

    prelude = "\n".join(
        [
            payload["runtime_prompt_block"],
            *capability_lines,
            "<planner-turn-guidance>",
            f"Recommended Route: {dispatch['recommended_route']['skill']}",
            f"Route Reason: {dispatch['recommended_route']['reason']}",
            f"Safe Next Move: {action['safe_next_move']}",
            "Guidance:",
            *[f"- {item}" for item in guidance],
            "Rule: This prelude is derived from repo artifacts for the current turn. It must not replace ADRs,"
            " architecture docs, workstreams, task ledgers, or evidence.",
            "</planner-turn-guidance>",
        ]
    )

    return {
        "root": str(root),
        "program_action": action,
        "active_unit": active,
        "recommended_route": dispatch["recommended_route"],
        "product_parallelism": product,
        "prelude": prelude,
    }


def render_text(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Planner Turn Prelude",
            f"Mode: {summary['program_action']['mode']}",
            f"Operating Mode: {summary['program_action']['operating_mode']}",
            f"Recommended Route: {summary['recommended_route']['skill']}",
            "",
            summary["prelude"],
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    summary = summarize(root, args.strict_history)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
