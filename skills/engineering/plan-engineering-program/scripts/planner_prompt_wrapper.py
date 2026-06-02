#!/usr/bin/env python3
"""Wrap a user prompt with a derived planner prelude for prompt-boundary rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from planner_turn_prelude import summarize as summarize_prelude


def build_wrapped_prompt(prelude: str, user_prompt: str) -> str:
    return "\n".join(
        [
            prelude.rstrip(),
            "",
            "<user-request>",
            user_prompt.strip(),
            "</user-request>",
        ]
    )


def summarize(root: Path, user_prompt: str, strict_history: bool) -> dict[str, object]:
    prelude_summary = summarize_prelude(root, strict_history)
    wrapped = build_wrapped_prompt(str(prelude_summary["prelude"]), user_prompt)
    return {
        "root": str(root),
        "recommended_route": prelude_summary["recommended_route"],
        "program_action": prelude_summary["program_action"],
        "active_unit": prelude_summary["active_unit"],
        "prelude": prelude_summary["prelude"],
        "user_prompt": user_prompt,
        "wrapped_prompt": wrapped,
    }


def render_text(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "## Planner Prompt Wrapper",
            f"Recommended Route: {summary['recommended_route']['skill']}",  # type: ignore[index]
            f"Operating Mode: {summary['program_action']['operating_mode']}",  # type: ignore[index]
            "",
            str(summary["wrapped_prompt"]),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--prompt", required=True, help="raw user prompt to wrap")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    summary = summarize(root, args.prompt, args.strict_history)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
