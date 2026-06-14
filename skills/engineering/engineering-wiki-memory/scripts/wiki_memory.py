#!/usr/bin/env python3
"""Create and validate small engineering wiki memory bundles."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


DEFAULT_ROOT = Path("docs/knowledge/engineering")
TYPE_DIRS = {
    "current state": "",
    "work progress": "progress",
    "session handoff": "sessions",
    "decision": "decisions",
    "subagent finding": "subagents",
    "verification evidence": "verification",
    "repo convention": "conventions",
    "skill contract": "conventions",
}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "concept"


def yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_list(value: str | None) -> str | None:
    if not value:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        return None
    return "[" + ", ".join(yaml_string(item) for item in items) + "]"


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def init_bundle(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for dirname in ("decisions", "progress", "sessions", "subagents", "verification", "conventions"):
        (root / dirname).mkdir(parents=True, exist_ok=True)

    index = """# Engineering Memory

## Core

* [Current State](current-state.md) - Short durable summary of the active engineering state.
* [Update Log](log.md) - Chronological history of meaningful memory updates.

## Concepts

* [Decisions](decisions/) - Durable engineering choices and rationale.
* [Progress](progress/) - Work progress tied to plans, branches, or commits.
* [Sessions](sessions/) - Compaction, interruption, and handoff summaries.
* [Subagents](subagents/) - Distilled findings from spawned agents.
* [Verification](verification/) - Test, build, lint, benchmark, and manual evidence.
* [Conventions](conventions/) - Local repo rules and reusable agent contracts.
"""
    log = f"""# Engineering Memory Update Log

## {today()}
* **Initialization**: Created engineering wiki memory bundle.
"""
    current = f"""---
type: "Current State"
title: "Current Engineering State"
description: "Short durable summary of the active engineering state."
tags: ["engineering-memory"]
timestamp: {now_utc()}
status: "active"
---

# Current State

- Goal:
- Branch:
- Last verified:
- Done:
- In progress:
- Blocked:
- Next action:

# Citations
"""

    created = []
    if write_if_missing(root / "index.md", index):
        created.append(root / "index.md")
    if write_if_missing(root / "log.md", log):
        created.append(root / "log.md")
    if write_if_missing(root / "current-state.md", current):
        created.append(root / "current-state.md")

    if created:
        for path in created:
            print(f"created {path}")
    else:
        print(f"bundle already initialized at {root}")


def concept_path(root: Path, concept_type: str, title: str, explicit_path: str | None) -> Path:
    if explicit_path:
        path = Path(explicit_path)
        return path if path.is_absolute() else root / path
    dirname = TYPE_DIRS.get(concept_type.lower(), "")
    filename = f"{today()}-{slugify(title)}.md"
    if concept_type.lower() == "current state":
        filename = "current-state.md"
    return root / dirname / filename


def body_template(concept_type: str) -> str:
    normalized = concept_type.lower()
    if normalized == "decision":
        return "# Decision\n\n# Context\n\n# Alternatives\n\n# Consequences\n\n# Citations\n"
    if normalized == "subagent finding":
        return "# Finding\n\n# Evidence\n\n# Recommendation\n\n# Disposition\n\n# Citations\n"
    if normalized == "verification evidence":
        return "# Verification\n\n# Result\n\n# Evidence\n\n# Follow-up\n\n# Citations\n"
    if normalized == "session handoff":
        return "# Summary\n\n# Verified State\n\n# Open Threads\n\n# Next Action\n\n# Citations\n"
    if normalized == "current state":
        return "# Current State\n\n- Goal:\n- Branch:\n- Last verified:\n- Done:\n- In progress:\n- Blocked:\n- Next action:\n\n# Citations\n"
    return "# Summary\n\n# Details\n\n# Next Action\n\n# Citations\n"


def new_concept(args: argparse.Namespace) -> None:
    root = args.root
    root.mkdir(parents=True, exist_ok=True)
    path = concept_path(root, args.type, args.title, args.path)
    if path.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite existing concept: {path}")

    fields: list[tuple[str, str]] = [
        ("type", yaml_string(args.type)),
        ("title", yaml_string(args.title)),
        ("description", yaml_string(args.description or f"{args.type} for {args.title}.")),
        ("timestamp", now_utc()),
    ]
    tags = yaml_list(args.tags)
    optional = {
        "resource": args.resource,
        "tags": tags,
        "status": args.status,
        "source_session": args.source_session,
        "subagent_id": args.subagent_id,
        "related_plan": args.related_plan,
        "git_branch": args.git_branch,
        "git_commit": args.git_commit,
        "verified_by": args.verified_by,
    }
    for key, value in optional.items():
        if not value:
            continue
        fields.append((key, value if key == "tags" else yaml_string(value)))

    frontmatter = "---\n" + "\n".join(f"{key}: {value}" for key, value in fields) + "\n---\n\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + body_template(args.type), encoding="utf-8", newline="\n")
    print(f"created {path}")


def add_log(root: Path, message: str, kind: str) -> None:
    path = root / "log.md"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Engineering Memory Update Log\n", encoding="utf-8", newline="\n")

    text = path.read_text(encoding="utf-8")
    date_heading = f"## {today()}"
    entry = f"* **{kind}**: {message}\n"
    if date_heading in text:
        text = text.replace(date_heading + "\n", date_heading + "\n" + entry, 1)
    else:
        lines = text.splitlines(keepends=True)
        insert_at = 1 if lines and lines[0].startswith("# ") else 0
        lines[insert_at:insert_at] = ["\n", date_heading + "\n", entry]
        text = "".join(lines)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"updated {path}")


def has_type_frontmatter(text: str) -> bool:
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---\n", 4)
    if end == -1:
        return False
    frontmatter = text[4:end]
    return any(line.startswith("type:") and line.split(":", 1)[1].strip() for line in frontmatter.splitlines())


def validate_bundle(root: Path) -> int:
    errors: list[str] = []
    if not root.exists():
        errors.append(f"missing bundle root: {root}")
    else:
        for path in sorted(root.rglob("*.md")):
            if path.name in {"index.md", "log.md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if not has_type_frontmatter(text):
                errors.append(f"{path}: missing frontmatter with non-empty type")

    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"OK: {root} is a valid minimal engineering wiki memory bundle")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize an engineering wiki memory bundle")
    init.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    new = sub.add_parser("new", help="Create a new wiki memory concept document")
    new.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    new.add_argument("--type", required=True)
    new.add_argument("--title", required=True)
    new.add_argument("--description")
    new.add_argument("--path")
    new.add_argument("--resource")
    new.add_argument("--tags")
    new.add_argument("--status")
    new.add_argument("--source-session")
    new.add_argument("--subagent-id")
    new.add_argument("--related-plan")
    new.add_argument("--git-branch")
    new.add_argument("--git-commit")
    new.add_argument("--verified-by")
    new.add_argument("--force", action="store_true")

    log = sub.add_parser("log", help="Append a chronological log entry")
    log.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    log.add_argument("--kind", default="Update")
    log.add_argument("message")

    validate = sub.add_parser("validate", help="Validate minimal wiki memory conformance")
    validate.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    args = parser.parse_args()
    if args.command == "init":
        init_bundle(args.root)
        return 0
    if args.command == "new":
        new_concept(args)
        return 0
    if args.command == "log":
        add_log(args.root, args.message, args.kind)
        return 0
    if args.command == "validate":
        return validate_bundle(args.root)
    return 1


if __name__ == "__main__":
    sys.exit(main())
