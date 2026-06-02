#!/usr/bin/env python3
"""Generate a read-only dispatch rehearsal from the unified planner payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capability_parallelism import build_capability_summary
from planner_payload import build_payload


def derive_route(payload: dict[str, Any]) -> tuple[str, str, bool]:
    action = payload["program_action"]
    active = payload["active_unit"]

    if action["operating_mode"] == "AUDIT":
        return "plan-engineering-program", "historical audit baseline; do not dispatch workers", False
    if action["mode"] == "ASSIGN" and active.get("task"):
        return "run-workstream-task", "ready bounded task exists", False
    if action["mode"] == "PLAN":
        return "resume-workstream", "active queue exists but readiness blockers require repair first", False
    if action["safe_next_move"] == "assignment" and action["implementation_horizon"] == 0:
        return "tdd", "light-substrate bounded engineering work should downshift to a direct execution skill", False
    return "audit-project-scale", "no active assignable queue; stay read-only until workflow scale is clear", False


def build_worker_prompt(payload: dict[str, Any]) -> str:
    action = payload["program_action"]
    active = payload["active_unit"]
    if action["operating_mode"] == "AUDIT" or not active.get("task"):
        return ""

    context_lines = "\n".join(f"- {item}" for item in active.get("required_context", [])) or "- (none listed)"
    blockers = active.get("blockers") or []
    blocker_text = ", ".join(blockers) if blockers else "none"

    return "\n".join(
        [
            f"Use $run-workstream-task to execute task {active['task']}.",
            "You are not alone in the codebase.",
            f"Role: worker",
            f"Program state: {action['mode']}",
            f"Task or campaign: {active['task']} / {active.get('campaign') or '(none)'}",
            "Owned scope: infer from TASKS.jsonl and workstream ledger before editing",
            "Forbidden/shared scope: any scope not explicitly owned by the assigned task",
            "Required context:",
            context_lines,
            "Validation: use the task-local validation command from TASKS.jsonl",
            "Stop conditions: shared-scope drift, ADR/schema/public-contract change, failed gates, missing context",
            "Side-effect policy: do not infer beyond current campaign/workstream approval",
            "Result marker: WORKSTREAM_RESULT:",
            "Return path: upper planner or integrator for review/verify and next approved task",
            f"Known blockers before dispatch: {blocker_text}",
            "Do not choose the global next task.",
        ]
    )


def slim_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "label": row["label"],
        "classification": row["classification"],
        "guardrail": row["guardrail"],
        "missing_artifacts": row["missing_artifacts"],
        "evidence": row["evidence"][:3],
        "notes": row["notes"],
    }


def summarize(root: Path, strict_history: bool) -> dict[str, Any]:
    payload = build_payload(root, strict_history)
    capability = build_capability_summary(root, strict_history)
    route, reason, parallel_safe = derive_route(payload)
    action = payload["program_action"]
    active = payload["active_unit"]

    if action["operating_mode"] == "AUDIT":
        parallel_reason = "no active queue exists, so worker parallelism would be fabricated"
    elif action["implementation_horizon"] <= 1:
        parallel_reason = "only one ready active unit is derived from current artifacts"
    else:
        parallel_reason = "multiple ready active units exist and still need explicit scope checks"

    return {
        "root": str(root),
        "program_action": payload["program_action"],
        "runtime_prompt_block": payload["runtime_prompt_block"],
        "recommended_route": {
            "skill": route,
            "reason": reason,
        },
        "parallelism": {
            "parallel_safe_now": parallel_safe,
            "reason": parallel_reason,
        },
        "product_parallelism": {
            "profile_family": capability["profile_family"],
            "product_recon_horizon": capability["product_recon_horizon"],
            "recon_candidate_count": len(
                capability["capability_parallelism"]["recon_candidates"]
            ),
            "product_decision_required_count": len(
                capability["capability_parallelism"]["product_decision_required"]
            ),
            "needs_workstream_count": len(
                capability["capability_parallelism"]["needs_workstream"]
            ),
            "blocked_by_active_queue_count": len(
                capability["capability_parallelism"]["blocked_by_active_queue"]
            ),
            "top_recon_candidates": [
                slim_candidate(row)
                for row in capability["capability_parallelism"]["recon_candidates"][:4]
            ],
            "top_product_decisions": [
                slim_candidate(row)
                for row in capability["capability_parallelism"]["product_decision_required"][:3]
            ],
            "top_needs_workstream": [
                slim_candidate(row)
                for row in capability["capability_parallelism"]["needs_workstream"][:3]
            ],
            "blocked_by_active_queue": capability["capability_parallelism"][
                "blocked_by_active_queue"
            ][:5],
            "recon_result_contract": capability["recon_result_contract"],
            "rule": capability["rule"],
        },
        "active_unit": active,
        "worker_prompt": build_worker_prompt(payload),
        "audit_pressure": payload["audit_pressure"],
    }


def render_text(summary: dict[str, Any]) -> str:
    action = summary["program_action"]
    route = summary["recommended_route"]
    parallel = summary["parallelism"]
    product = summary["product_parallelism"]
    lines = [
        "## Dispatch Rehearsal",
        f"Mode: {action['mode']}",
        f"Operating Mode: {action['operating_mode']}",
        f"Implementation Horizon: {action['implementation_horizon']}",
        f"Recommended Route: {route['skill']}",
        f"Reason: {route['reason']}",
        f"Parallel Safe Now: {parallel['parallel_safe_now']}",
        f"Parallelism Reason: {parallel['reason']}",
        f"Profile Family: {product['profile_family']['label']} (detected={product['profile_family']['detected']})",
        f"Product RECON Horizon: {product['product_recon_horizon']}",
        f"Product RECON Candidates: {product['recon_candidate_count']}",
        f"Product Decisions Required: {product['product_decision_required_count']}",
        f"Needs Workstream: {product['needs_workstream_count']}",
        f"Blocked By Active Queue: {product['blocked_by_active_queue_count']}",
    ]
    if product["top_recon_candidates"]:
        lines.append("")
        lines.append("## Top Product RECON Candidates")
        for row in product["top_recon_candidates"]:
            lines.append(f"- {row['label']} [{row['id']}]")
            lines.append(f"  Guardrail: {row['guardrail']}")
            lines.append(f"  Missing: {', '.join(row['missing_artifacts'])}")
    if product["top_product_decisions"]:
        lines.append("")
        lines.append("## Product Decisions Required")
        for row in product["top_product_decisions"]:
            lines.append(f"- {row['label']} [{row['id']}]")
            lines.append(f"  Guardrail: {row['guardrail']}")
            lines.append(f"  Missing: {', '.join(row['missing_artifacts'])}")
    if product["top_needs_workstream"]:
        lines.append("")
        lines.append("## Needs Workstream")
        for row in product["top_needs_workstream"]:
            lines.append(f"- {row['label']} [{row['id']}]")
            lines.append(f"  Guardrail: {row['guardrail']}")
            lines.append(f"  Missing: {', '.join(row['missing_artifacts'])}")
    if product["blocked_by_active_queue"]:
        lines.append("")
        lines.append("## Blocked By Active Queue")
        for row in product["blocked_by_active_queue"]:
            lines.append(f"- {row['candidate']}: {row['reason']}")
    contract = product["recon_result_contract"]
    lines.extend(
        [
            "",
            "## RECON Result Contract",
            f"Marker: {contract['result_marker']}",
            "Required Fields: " + ", ".join(contract["required_fields"]),
        ]
    )
    if summary["worker_prompt"]:
        lines.extend(["", "## Worker Prompt", summary["worker_prompt"]])
    lines.extend(["", "## Runtime Prompt Block", summary["runtime_prompt_block"]])
    return "\n".join(lines)


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
