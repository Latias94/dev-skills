#!/usr/bin/env python3
"""Emit a host-consumable hook payload for derived planner runtime injection."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from planner_turn_prelude import summarize as summarize_prelude


def resolve_root(explicit_root: str | None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    cwd = os.environ.get("CODEX_PROJECT_DIR") or os.environ.get("PWD") or "."
    return Path(cwd).resolve()


def build_payload(root: Path, event_name: str, strict_history: bool) -> dict[str, object]:
    summary = summarize_prelude(root, strict_history)
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": summary["prelude"],
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", help="repository root")
    parser.add_argument("--event-name", default="UserPromptSubmit", help="hook event name to emit")
    parser.add_argument("--strict-history", action="store_true")
    parser.add_argument("--debug", action="store_true", help="include derived debug metadata")
    args = parser.parse_args()

    root = resolve_root(args.root_arg or args.root)
    payload = build_payload(root, args.event_name, args.strict_history)
    if args.debug:
        summary = summarize_prelude(root, args.strict_history)
        payload["debug"] = {
            "root": str(root),
            "recommended_route": summary["recommended_route"],
            "program_action": summary["program_action"],
            "active_unit": summary["active_unit"],
            "product_parallelism": summary.get("product_parallelism"),
        }
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
