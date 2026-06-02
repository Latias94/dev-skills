#!/usr/bin/env python3
"""Install the minimal dev-skills Codex hook template into a target repo."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def template_path() -> Path:
    return (
        repo_root()
        / "skills"
        / "engineering"
        / "plan-engineering-program"
        / "assets"
        / "codex-hook-template"
        / "hooks.json"
    )


def render_template(event_name: str, command: str, timeout: int) -> dict[str, object]:
    return {
        "hooks": {
            event_name: [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": command,
                            "timeout": timeout,
                        }
                    ]
                }
            ]
        }
    }


def install(
    target_repo: Path,
    force: bool,
    event_name: str,
    command: str,
    timeout: int,
    merge: bool,
) -> Path:
    dest_dir = target_repo / ".codex"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "hooks.json"
    payload = render_template(event_name, command, timeout)
    if dest.exists():
        if merge:
            existing = json.loads(dest.read_text(encoding="utf-8"))
            hooks = existing.setdefault("hooks", {})
            hooks[event_name] = payload["hooks"][event_name]  # type: ignore[index]
            dest.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return dest
        if not force:
            raise FileExistsError(f"{dest} already exists; rerun with --force to replace it")
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_repo", type=Path, help="Repository root to receive .codex/hooks.json")
    parser.add_argument("--force", action="store_true", help="Replace an existing hooks.json")
    parser.add_argument("--event-name", default="UserPromptSubmit", help="Hook event name to install")
    parser.add_argument(
        "--command",
        default="python -X utf8 skills/engineering/plan-engineering-program/scripts/planner.py advanced hook-payload",
        help="Command to install in hooks.json",
    )
    parser.add_argument("--timeout", type=int, default=15, help="Hook timeout in seconds")
    parser.add_argument("--merge", action="store_true", help="Merge this event into an existing hooks.json")
    args = parser.parse_args()

    target_repo = args.target_repo.resolve()
    if not target_repo.exists():
        raise FileNotFoundError(f"Target repo does not exist: {target_repo}")

    dest = install(
        target_repo,
        args.force,
        args.event_name,
        args.command,
        args.timeout,
        args.merge,
    )
    payload = {
        "status": "installed",
        "target_repo": str(target_repo),
        "destination": str(dest),
        "source_template": str(template_path()),
        "event_name": args.event_name,
        "command": args.command,
        "timeout": args.timeout,
        "merge": args.merge,
    }
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
