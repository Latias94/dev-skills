#!/usr/bin/env python3
"""Validate CAPABILITY_RECON_RESULT blocks from product-capability RECON subagents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from capability_parallelism import RECON_RESULT_CONTRACT, build_capability_summary


MARKER = RECON_RESULT_CONTRACT["result_marker"]
KNOWN_FIELDS = set(RECON_RESULT_CONTRACT["required_fields"])


def parse_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    last_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == MARKER:
            if current is not None:
                blocks.append(current)
            current = {}
            last_key = None
            continue
        if current is None or not line:
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            normalized = key.strip().lower()
            if normalized in KNOWN_FIELDS:
                current[normalized] = value.strip()
                last_key = normalized
            elif last_key:
                current[last_key] = (current[last_key] + " " + line).strip()
        elif last_key:
            current[last_key] = (current[last_key] + " " + line).strip()
    if current is not None:
        blocks.append(current)
    return blocks


def is_empty(value: str | None, *, allow_none: bool = False) -> bool:
    if value is None:
        return True
    normalized = value.strip().lower()
    if not normalized:
        return True
    if allow_none:
        return False
    return normalized in {"none", "(none)", "n/a", "na", "not applicable"}


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1", "y"}:
        return True
    if normalized in {"false", "no", "0", "n"}:
        return False
    return None


def known_capabilities(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    known: dict[str, dict[str, Any]] = {}
    parallelism = summary["capability_parallelism"]
    for group in ("recon_candidates", "product_decision_required", "needs_workstream"):
        for row in parallelism[group]:
            known[row["id"]] = row
    return known


def validate_block(
    block: dict[str, str],
    index: int,
    known: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    required = RECON_RESULT_CONTRACT["required_fields"]

    for field in required:
        allow_none = field in {"product_decisions", "blocked_by_active_queue"}
        if is_empty(block.get(field), allow_none=allow_none):
            errors.append(f"missing required field `{field}`")

    capability_id = block.get("capability_id", "")
    known_row = known.get(capability_id)
    if not known_row:
        errors.append(f"unknown capability_id `{capability_id}`")
    else:
        expected = known_row["classification"]
        observed = block.get("classification", "")
        if observed != expected:
            errors.append(
                f"classification mismatch for `{capability_id}`: expected `{expected}`, got `{observed}`"
            )

    status = block.get("status", "")
    allowed_status = set(RECON_RESULT_CONTRACT["allowed_status"])
    if status not in allowed_status:
        errors.append(f"status `{status}` is not in allowed status set")

    implementation_allowed = parse_bool(block.get("implementation_allowed"))
    if implementation_allowed is None:
        errors.append("implementation_allowed must be true/false")
    elif implementation_allowed:
        errors.append("RECON result must not allow implementation directly")

    if known_row:
        classification = known_row["classification"]
        if classification == "product_decision_required" and status not in {
            "NEEDS_PRODUCT_DECISION",
            "NEEDS_CONTEXT",
            "RECON_DONE",
        }:
            warnings.append("product decision candidate should normally return NEEDS_PRODUCT_DECISION")
        if classification == "needs_workstream" and status not in {
            "NEEDS_WORKSTREAM",
            "NEEDS_CONTEXT",
            "RECON_DONE",
        }:
            warnings.append("needs-workstream candidate should normally return NEEDS_WORKSTREAM")
        if classification == "recon_candidate" and status not in {
            "RECON_DONE",
            "NEEDS_WORKSTREAM",
            "NEEDS_CONTEXT",
        }:
            warnings.append("recon candidate returned an unusual status for its classification")

    return {
        "index": index,
        "capability_id": capability_id,
        "classification": block.get("classification", ""),
        "status": status,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def validate_text(root: Path, text: str, strict_history: bool = False) -> dict[str, Any]:
    summary = build_capability_summary(root, strict_history)
    known = known_capabilities(summary)
    blocks = parse_blocks(text)
    results = [validate_block(block, index, known) for index, block in enumerate(blocks, start=1)]
    errors = [error for result in results for error in result["errors"]]
    warnings = [warning for result in results for warning in result["warnings"]]
    if not blocks:
        errors.append(f"no `{MARKER}` blocks found")
    return {
        "root": str(root),
        "valid": not errors,
        "result_count": len(blocks),
        "errors": errors,
        "warnings": warnings,
        "results": results,
        "contract": RECON_RESULT_CONTRACT,
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "## Capability RECON Result Validation",
        f"Valid: {summary['valid']}",
        f"Result Count: {summary['result_count']}",
    ]
    if summary["errors"]:
        lines.append("Errors:")
        lines.extend(f"- {error}" for error in summary["errors"])
    if summary["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in summary["warnings"])
    lines.append("Results:")
    for result in summary["results"]:
        lines.append(
            f"- #{result['index']} {result['capability_id']} "
            f"[{result['classification']}] status={result['status']} valid={result['valid']}"
        )
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
    summary = validate_text(root, text, args.strict_history)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
