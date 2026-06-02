#!/usr/bin/env python3
"""Emit a derived-only hook-like payload for planner prompt injection rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from planner_prompt_wrapper import summarize as summarize_wrapper


def summarize(root: Path, user_prompt: str, strict_history: bool, event_name: str) -> dict[str, object]:
    wrapped = summarize_wrapper(root, user_prompt, strict_history)
    return {
        "root": str(root),
        "recommended_route": wrapped["recommended_route"],
        "program_action": wrapped["program_action"],
        "active_unit": wrapped["active_unit"],
        "user_prompt": wrapped["user_prompt"],
        "wrapped_prompt": wrapped["wrapped_prompt"],
        "hook_payload": {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": wrapped["prelude"],
            }
        },
    }


def render_text(summary: dict[str, object]) -> str:
    payload = summary["hook_payload"]  # type: ignore[index]
    return "\n".join(
        [
            "## Planner Hook Adapter",
            f"Recommended Route: {summary['recommended_route']['skill']}",  # type: ignore[index]
            f"Operating Mode: {summary['program_action']['operating_mode']}",  # type: ignore[index]
            "",
            "## Hook Payload",
            json.dumps(payload, indent=2, ensure_ascii=False),
            "",
            "## Wrapped Prompt",
            str(summary["wrapped_prompt"]),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--prompt", required=True, help="raw user prompt to wrap")
    parser.add_argument("--event-name", default="UserPromptSubmit", help="hook event name to emit")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    summary = summarize(root, args.prompt, args.strict_history, args.event_name)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
