#!/usr/bin/env python3
"""Run a local contract smoke for capability RECON packet/result/integration flow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from capability_parallelism import RECON_RESULT_CONTRACT
from capability_recon_packet import build_packet
from capability_recon_result_integrator import integrate_text


STATUS_BY_CLASSIFICATION = {
    "recon_candidate": "RECON_DONE",
    "product_decision_required": "NEEDS_PRODUCT_DECISION",
    "needs_workstream": "NEEDS_WORKSTREAM",
}


def result_block(packet: dict[str, Any]) -> str:
    status = STATUS_BY_CLASSIFICATION.get(packet["classification"], "NEEDS_CONTEXT")
    product_decisions = "none"
    if packet["classification"] == "product_decision_required":
        product_decisions = ", ".join(packet["missing_artifacts"][:3])
    return "\n".join(
        [
            RECON_RESULT_CONTRACT["result_marker"],
            f"capability_id: {packet['capability_id']}",
            f"classification: {packet['classification']}",
            f"status: {status}",
            "evidence: synthetic contract smoke derived from runtime packet",
            "guardrail_assessment: stayed read-only and followed packet guardrail",
            "missing_artifacts: " + ", ".join(packet["missing_artifacts"]),
            "owned_scope: planning artifacts only",
            "shared_scope: active queue, public contracts, generated clients",
            f"product_decisions: {product_decisions}",
            "implementation_allowed: false",
            "blocked_by_active_queue: none",
            f"suggested_next_artifact: {packet['capability_id']} planning artifact",
        ]
    )


def run_roundtrip(root: Path, selected: list[str], strict_history: bool = False) -> dict[str, Any]:
    packet = build_packet(root, selected, strict_history)
    synthetic_results = "\n\n".join(result_block(row) for row in packet["packets"])
    integration = integrate_text(root, synthetic_results, strict_history)
    smoke_valid = (
        bool(packet["packets"])
        and integration["merge_valid"]
        and not integration["promotion_allowed"]
        and integration["accepted_result_count"] == len(packet["packets"])
    )
    return {
        "root": str(root),
        "roundtrip_valid": smoke_valid,
        "packet_count": len(packet["packets"]),
        "implementation_horizon": packet["implementation_horizon"],
        "product_recon_horizon": packet["product_recon_horizon"],
        "promotion_allowed": integration["promotion_allowed"],
        "ready_active_unit": packet["ready_active_unit"],
        "synthetic_results": synthetic_results,
        "integration": integration,
    }


def render_text(summary: dict[str, Any]) -> str:
    active = summary["ready_active_unit"]
    lines = [
        "## Capability RECON Roundtrip Smoke",
        f"Roundtrip Valid: {summary['roundtrip_valid']}",
        f"Packet Count: {summary['packet_count']}",
        f"Implementation Horizon: {summary['implementation_horizon']}",
        f"Product RECON Horizon: {summary['product_recon_horizon']}",
        f"Promotion Allowed: {summary['promotion_allowed']}",
        f"Ready Active Unit: {active.get('workstream') or '(none)'} / {active.get('task') or '(none)'}",
        "",
        "## Synthetic Results",
        summary["synthetic_results"],
    ]
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
        summary = run_roundtrip(root, selected, args.strict_history)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0 if summary["roundtrip_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
