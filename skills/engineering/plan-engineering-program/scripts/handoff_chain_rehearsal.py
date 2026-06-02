#!/usr/bin/env python3
"""Build a read-only planner->worker->review->verify->integrate rehearsal chain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dispatch_rehearsal import summarize as summarize_dispatch


def runtime_preface(summary: dict[str, Any]) -> str:
    block = str(summary.get("runtime_prompt_block") or "")
    if not block:
        return ""
    return block + "\n\n"


def review_prompt(summary: dict[str, Any]) -> str:
    route = summary["recommended_route"]["skill"]
    if route in {"tdd", "diagnose"}:
        return runtime_preface(summary) + (
            f"After `{route}` completes, review the resulting diff against the user-visible behavior, "
            "test quality, and unintended scope expansion before considering follow-through complete."
        )
    active = summary["active_unit"]
    task = active.get("task")
    workstream = active.get("workstream")
    if not task or not workstream:
        return ""
    return runtime_preface(summary) + (
        f"Use $review-workstream to review task {task} in docs/workstreams/{workstream} "
        "against the workstream contract, changed file scope, and current diff. "
        "End with a REVIEW_RESULT: marker."
    )


def verify_prompt(summary: dict[str, Any]) -> str:
    route = summary["recommended_route"]["skill"]
    if route in {"tdd", "diagnose"}:
        return runtime_preface(summary) + (
            f"After `{route}` completes, rerun the targeted failing or newly added tests with fresh "
            "evidence before accepting the direct-route result."
        )
    active = summary["active_unit"]
    task = active.get("task")
    workstream = active.get("workstream")
    if not task or not workstream:
        return ""
    return runtime_preface(summary) + (
        f"Use $verify-rust-workstream to verify task {task} in docs/workstreams/{workstream} "
        "with fresh command evidence before integration. "
        "End with a VERIFY_RESULT: marker."
    )


def integrate_prompt(summary: dict[str, Any]) -> str:
    route = summary["recommended_route"]["skill"]
    if route in {"tdd", "diagnose"}:
        return runtime_preface(summary) + (
            "After direct execution, summarize changed files, validation evidence, and whether the "
            "work should remain direct or be promoted into a durable workstream follow-on."
        )
    active = summary["active_unit"]
    task = active.get("task")
    workstream = active.get("workstream")
    if not task or not workstream:
        return runtime_preface(summary) + (
            "Stay in planner/audit mode. Do not attempt result intake or integration until a real "
            "active queue exists."
        )
    return runtime_preface(summary) + (
        f"Use $integrate-lane-results after worker, review, and verify reports for task {task} "
        f"in docs/workstreams/{workstream}. Reconstruct the result from repo evidence first, then "
        "classify it with an INTEGRATION_RESULT: marker."
    )


def summarize(root: Path, strict_history: bool) -> dict[str, Any]:
    dispatch = summarize_dispatch(root, strict_history)
    action = dispatch["program_action"]
    route = dispatch["recommended_route"]["skill"]

    if route == "run-workstream-task":
        chain_state = "execution_chain_ready"
    elif route in {"tdd", "diagnose"}:
        chain_state = "direct_execution_ready"
    else:
        chain_state = "planner_only"
    refusal_reason = ""
    if chain_state == "planner_only":
        refusal_reason = (
            "current repo state does not justify entering worker/review/verify/integrate; stay in planner or audit mode"
        )

    return {
        "root": str(root),
        "program_action": action,
        "chain_state": chain_state,
        "recommended_route": dispatch["recommended_route"],
        "parallelism": dispatch["parallelism"],
        "runtime_prompt_block": dispatch["runtime_prompt_block"],
        "planner_prompt": (
            runtime_preface(dispatch)
            + "Use $plan-engineering-program with the current derived payload as the pre-dispatch baseline."
        ),
        "worker_prompt": dispatch["worker_prompt"],
        "review_prompt": review_prompt(dispatch),
        "verify_prompt": verify_prompt(dispatch),
        "integrate_prompt": integrate_prompt(dispatch),
        "refusal_reason": refusal_reason,
        "active_unit": dispatch["active_unit"],
        "audit_pressure": dispatch["audit_pressure"],
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "## Handoff Chain Rehearsal",
        f"Mode: {summary['program_action']['mode']}",
        f"Operating Mode: {summary['program_action']['operating_mode']}",
        f"Chain State: {summary['chain_state']}",
        f"Recommended Route: {summary['recommended_route']['skill']}",
    ]
    if summary["refusal_reason"]:
        lines.append(f"Refusal Reason: {summary['refusal_reason']}")
    lines.extend(
        [
            "",
            "## Planner Prompt",
            summary["planner_prompt"],
        ]
    )
    if summary["worker_prompt"]:
        lines.extend(["", "## Worker Prompt", summary["worker_prompt"]])
    if summary["review_prompt"]:
        lines.extend(["", "## Review Prompt", summary["review_prompt"]])
    if summary["verify_prompt"]:
        lines.extend(["", "## Verify Prompt", summary["verify_prompt"]])
    lines.extend(["", "## Integrate Prompt", summary["integrate_prompt"]])
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
