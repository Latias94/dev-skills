#!/usr/bin/env python3
"""Summarize historical orchestration drift patterns for audit-mode inspection."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


VALIDATOR = Path(__file__).with_name("validate_orchestration_state.py")

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "missing_terminal_task_evidence",
        re.compile(r"closed/completed workstream TODO tasks missing terminal evidence"),
    ),
    (
        "gate_command_not_listed",
        re.compile(r"evidence gate command not listed in gates"),
    ),
    (
        "non_terminal_task_result",
        re.compile(r"closed/completed workstream has non-terminal evidence result"),
    ),
    (
        "non_pass_gate_result",
        re.compile(r"closed/completed workstream has non-pass gate evidence"),
    ),
    (
        "task_not_in_todo",
        re.compile(r"evidence task .* is not present in TODO\.md task ledger"),
    ),
    (
        "non_canonical_status",
        re.compile(r"non-canonical status"),
    ),
]


def run_validator(root: Path, strict_history: bool) -> dict[str, Any]:
    args = [sys.executable, str(VALIDATOR), str(root), "--format", "json"]
    if strict_history:
        args.append("--strict-history")
    result = subprocess.run(
        args,
        cwd=root.parent,
        text=True,
        capture_output=True,
        check=False,
    )
    if not result.stdout.strip():
        raise RuntimeError(result.stderr.strip() or "validator produced no output")
    return json.loads(result.stdout)


def workstream_name(message: str) -> str:
    marker = "\\docs\\workstreams\\"
    if marker in message:
        tail = message.split(marker, 1)[1]
        return tail.split("\\", 1)[0]
    marker = "/docs/workstreams/"
    if marker in message:
        tail = message.split(marker, 1)[1]
        return tail.split("/", 1)[0]
    return "<unknown>"


def classify(warnings: list[str]) -> tuple[dict[str, int], dict[str, list[str]], list[str]]:
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = defaultdict(list)
    unmatched: list[str] = []
    for warning in warnings:
        matched = False
        for key, pattern in PATTERNS:
            if pattern.search(warning):
                counts[key] += 1
                if len(examples[key]) < 5:
                    examples[key].append(workstream_name(warning))
                matched = True
                break
        if not matched:
            unmatched.append(warning)
    return dict(counts), dict(examples), unmatched


def summarize(root: Path, strict_history: bool) -> dict[str, Any]:
    payload = run_validator(root, strict_history)
    warnings = [str(item) for item in payload.get("warnings", [])]
    counts, examples, unmatched = classify(warnings)
    top_patterns = [
        {
            "pattern": key,
            "count": count,
            "example_workstreams": examples.get(key, []),
        }
        for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        "root": str(root),
        "strict_history": strict_history,
        "workstreams_checked": payload.get("workstreams_checked", 0),
        "status_counts": payload.get("status_counts", {}),
        "error_count": len(payload.get("errors", [])),
        "warning_count": len(warnings),
        "top_patterns": top_patterns,
        "unmatched_warning_count": len(unmatched),
        "unmatched_warning_examples": unmatched[:5],
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        f"Root: {summary['root']}",
        f"Workstreams checked: {summary['workstreams_checked']}",
        f"Strict history: {summary['strict_history']}",
        f"Warnings: {summary['warning_count']}",
        f"Errors: {summary['error_count']}",
    ]
    status_counts = summary.get("status_counts") or {}
    if status_counts:
        lines.append(
            "Status counts: " + ", ".join(f"{key}={value}" for key, value in sorted(status_counts.items()))
        )
    lines.append("")
    lines.append("Top Drift Patterns")
    lines.append("------------------")
    if not summary["top_patterns"]:
        lines.append("(none)")
    else:
        for row in summary["top_patterns"]:
            lines.append(f"- {row['pattern']}: {row['count']}")
            if row["example_workstreams"]:
                lines.append(f"  examples: {', '.join(row['example_workstreams'])}")
    if summary["unmatched_warning_count"]:
        lines.append("")
        lines.append(
            f"Unmatched warnings: {summary['unmatched_warning_count']} "
            "(extend classifier if these patterns matter)"
        )
        for warning in summary["unmatched_warning_examples"]:
            lines.append(f"  - {warning}")
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
