#!/usr/bin/env python3
"""Create and validate small engineering wiki memory bundles."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_ROOT = Path("docs/knowledge/engineering")
TYPE_DIRS = {
    "current state": "",
    "work registration": "registry",
    "work progress": "progress",
    "session handoff": "sessions",
    "decision": "decisions",
    "subagent finding": "subagents",
    "verification evidence": "verification",
    "memory event": "logs",
    "repo convention": "conventions",
    "skill contract": "conventions",
}
ROLLUP_BUDGETS = {
    "current-state.md": (80, 64 * 1024),
    "log.md": (300, 128 * 1024),
    "index.md": (200, 64 * 1024),
}
LOCAL_ABSOLUTE_PATH_RE = re.compile(r"(?i)(?:[a-z]:\\|/Users/|/home/)")


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def timestamp_slug() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H%M%SZ")


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


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + len("\n---\n") :]


def frontmatter_value(text: str, key: str) -> str | None:
    frontmatter, _body = split_frontmatter(text)
    prefix = f"{key}:"
    for line in frontmatter.splitlines():
        if not line.startswith(prefix):
            continue
        value = line.split(":", 1)[1].strip()
        return value.strip("'\"") or None
    return None


def git_branch_for(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return None
    branch = result.stdout.strip()
    if result.returncode != 0 or not branch or branch == "HEAD":
        return None
    return branch


def related_plans_dir(root: Path) -> Path | None:
    for parent in (root, *root.parents):
        candidate = parent / "plans"
        if candidate.is_dir():
            return candidate
    return None


def relative_display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for counter in range(2, 1000):
        candidate = path.with_name(f"{stem}-{counter}{suffix}")
        if not candidate.exists():
            return candidate
    raise SystemExit(f"could not find an unused path near: {path}")


def registration_path(
    root: Path,
    title: str,
    registration_id: str | None,
    producer_id: str | None,
    source_workspace: str | None,
    explicit_path: str | None,
) -> Path:
    if explicit_path:
        path = Path(explicit_path)
        return path if path.is_absolute() else root / path

    identity = registration_id or producer_id
    if not identity and source_workspace:
        identity = Path(source_workspace).name
    filename_base = title if not identity else f"{title}-{identity}"
    return root / "registry" / f"{slugify(filename_base)}.md"


def init_bundle(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for dirname in (
        "decisions",
        "progress",
        "registry",
        "sessions",
        "subagents",
        "verification",
        "logs",
        "conventions",
    ):
        (root / dirname).mkdir(parents=True, exist_ok=True)

    index = """# Engineering Memory

## Core

* [Current State](current-state.md) - Short durable summary of the active engineering state.
* [Update Log](log.md) - Chronological history of meaningful memory updates.

## Concepts

* [Decisions](decisions/) - Durable engineering choices and rationale.
* [Progress](progress/) - Work progress tied to plans, branches, or commits.
* [Registry](registry/) - Active producers, development contexts, and agent lanes.
* [Sessions](sessions/) - Compaction, interruption, and handoff summaries.
* [Subagents](subagents/) - Distilled findings from spawned agents.
* [Verification](verification/) - Test, build, lint, benchmark, and manual evidence.
* [Logs](logs/) - Append-only chronological event concepts.
* [Conventions](conventions/) - Local repo rules and reusable agent contracts.
"""
    log = f"""# Engineering Memory Update Log

This root log is an optional rollup. Prefer append-only concepts in `logs/` during parallel work.

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
- Snapshot timestamp:
- Last verified:
- Next action:

# Active Registrations

- Add active `registry/` links here during integration.

# Integrated Summary

- Done:
- In progress:
- Blocked:

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
    filename = f"{timestamp_slug()}-{slugify(title)}.md"
    if concept_type.lower() == "current state":
        filename = "current-state.md"
    return root / dirname / filename


def body_template(concept_type: str) -> str:
    normalized = concept_type.lower()
    if normalized == "decision":
        return "# Decision\n\n# Context\n\n# Alternatives\n\n# Consequences\n\n# Citations\n"
    if normalized == "work registration":
        return "# Scope\n\n# Current Claim\n\n# Latest Links\n\n# Handoff\n\n# Citations\n"
    if normalized == "subagent finding":
        return "# Finding\n\n# Evidence\n\n# Recommendation\n\n# Disposition\n\n# Citations\n"
    if normalized == "verification evidence":
        return "# Verification\n\n# Result\n\n# Evidence\n\n# Follow-up\n\n# Citations\n"
    if normalized == "memory event":
        return "# Event\n\n# Impact\n\n# Citations\n"
    if normalized == "session handoff":
        return "# Summary\n\n# Verified State\n\n# Open Threads\n\n# Next Action\n\n# Citations\n"
    if normalized == "current state":
        return "# Current State\n\n- Goal:\n- Snapshot timestamp:\n- Last verified:\n- Next action:\n\n# Active Registrations\n\n# Integrated Summary\n\n- Done:\n- In progress:\n- Blocked:\n\n# Citations\n"
    return "# Summary\n\n# Details\n\n# Next Action\n\n# Citations\n"


def new_concept(args: argparse.Namespace) -> None:
    root = args.root
    root.mkdir(parents=True, exist_ok=True)
    path = concept_path(root, args.type, args.title, args.path)
    if path.exists() and not args.force:
        if args.path or args.type.lower() == "current state":
            raise SystemExit(f"refusing to overwrite existing concept: {path}")
        path = unique_path(path)

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


def register_work(args: argparse.Namespace) -> None:
    root = args.root
    root.mkdir(parents=True, exist_ok=True)
    path = registration_path(
        root,
        args.title,
        args.registration_id,
        args.producer_id,
        args.source_workspace,
        args.path,
    )
    if path.exists() and not args.update and not args.force:
        raise SystemExit(f"refusing to overwrite existing registration; use --update: {path}")
    existed = path.exists()

    fields: list[tuple[str, str]] = [
        ("type", yaml_string("Work Registration")),
        ("title", yaml_string(args.title)),
        ("description", yaml_string(args.description or f"Registration for {args.title}.")),
        ("timestamp", now_utc()),
        ("status", yaml_string(args.status)),
        ("last_seen", now_utc()),
    ]
    tags = yaml_list(args.tags)
    optional = {
        "registration_id": args.registration_id,
        "resource": args.resource,
        "tags": tags,
        "producer_id": args.producer_id,
        "source_workspace": args.source_workspace,
        "source_session": args.source_session,
        "related_plan": args.related_plan,
        "related_issue": args.related_issue,
        "git_branch": args.git_branch,
        "git_commit": args.git_commit,
        "latest_link": args.latest_link,
    }
    for key, value in optional.items():
        if not value:
            continue
        fields.append((key, value if key == "tags" else yaml_string(value)))

    latest_links = ""
    if args.latest_link:
        latest_links = f"- {args.latest_link}\n"
    body = "\n".join(
        [
            "# Scope",
            "",
            args.scope or "",
            "",
            "# Current Claim",
            "",
            args.current_claim or "",
            "",
            "# Latest Links",
            "",
            latest_links,
            "# Handoff",
            "",
            args.handoff or "",
            "",
            "# Citations",
            "",
        ]
    )
    frontmatter = "---\n" + "\n".join(f"{key}: {value}" for key, value in fields) + "\n---\n\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + body, encoding="utf-8", newline="\n")
    print(f"{'updated' if existed else 'created'} {path}")


def add_rollup_log(root: Path, message: str, kind: str) -> None:
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


def add_log(root: Path, message: str, kind: str, rollup: bool) -> None:
    if rollup:
        add_rollup_log(root, message, kind)
        return

    root.mkdir(parents=True, exist_ok=True)
    title = f"{kind}: {message[:80]}"
    path = root / "logs" / today()[:7] / f"{timestamp_slug()}-{slugify(kind + '-' + message[:80])}.md"
    path = unique_path(path)
    frontmatter = "\n".join(
        [
            "---",
            'type: "Memory Event"',
            f"title: {yaml_string(title)}",
            f"description: {yaml_string(message[:140])}",
            f"timestamp: {now_utc()}",
            f"event_kind: {yaml_string(kind)}",
            "---",
            "",
        ]
    )
    body = f"# Event\n\n{message}\n\n# Impact\n\n# Citations\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + body, encoding="utf-8", newline="\n")
    print(f"created {path}")


def has_type_frontmatter(text: str) -> bool:
    frontmatter, _body = split_frontmatter(text)
    if not frontmatter:
        return False
    return any(line.startswith("type:") and line.split(":", 1)[1].strip() for line in frontmatter.splitlines())


def collect_warnings(root: Path) -> list[str]:
    warnings: list[str] = []
    if not root.exists():
        return warnings

    if not (root / "registry").is_dir():
        warnings.append(f"{root / 'registry'}: missing registry directory; run init before parallel work.")

    for name, (max_lines, max_bytes) in ROLLUP_BUDGETS.items():
        path = root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = len(text.splitlines())
        size = path.stat().st_size
        if lines > max_lines or size > max_bytes:
            warnings.append(
                f"{path}: large rollup ({lines} lines, {size // 1024} KiB). "
                "Keep future facts in sharded concepts and refresh this view during integration."
            )

    current_state = root / "current-state.md"
    if current_state.exists():
        text = current_state.read_text(encoding="utf-8", errors="replace")
        recorded_branch = frontmatter_value(text, "git_branch")
        actual_branch = git_branch_for(root)
        if recorded_branch and actual_branch and recorded_branch != actual_branch:
            warnings.append(
                f"{current_state}: git_branch is {recorded_branch!r}, but the repository is on "
                f"{actual_branch!r}. Treat this file as a stale rollup until refreshed."
            )

    local_path_files: list[str] = []
    local_path_count = 0
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter, body = split_frontmatter(text)
        searchable_lines = [
            line
            for line in frontmatter.splitlines()
            if not line.lstrip().startswith("source_workspace:")
        ]
        searchable_lines.extend(body.splitlines())
        if any(LOCAL_ABSOLUTE_PATH_RE.search(line) for line in searchable_lines):
            local_path_count += 1
            if len(local_path_files) < 6:
                local_path_files.append(relative_display(path, root))
    if local_path_count:
        sample = ", ".join(local_path_files)
        suffix = "" if local_path_count <= len(local_path_files) else f", plus {local_path_count - len(local_path_files)} more"
        warnings.append(
            f"{local_path_count} file(s) contain local absolute paths outside source_workspace hints "
            f"({sample}{suffix}). Prefer repo-relative citations for portable memory."
        )

    large_progress_files: list[str] = []
    progress_dir = root / "progress"
    if progress_dir.is_dir():
        for path in sorted(progress_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = len(text.splitlines())
            size = path.stat().st_size
            if lines > 150 or size > 80 * 1024:
                large_progress_files.append(f"{relative_display(path, root)} ({lines} lines, {size // 1024} KiB)")
    if large_progress_files:
        sample = "; ".join(large_progress_files[:4])
        suffix = "" if len(large_progress_files) <= 4 else f"; plus {len(large_progress_files) - 4} more"
        warnings.append(
            "Large progress files look like mutable per-plan ledgers: "
            f"{sample}{suffix}. Treat them as historical rollups and write successor progress concepts."
        )

    plans_dir = related_plans_dir(root)
    if plans_dir:
        plan_progress = sorted(plans_dir.glob("*progress*.md"))
        plan_audits = sorted(plans_dir.glob("*audit*.md"))
        if plan_progress or plan_audits:
            parts = []
            if plan_progress:
                parts.append(f"{len(plan_progress)} progress")
            if plan_audits:
                parts.append(f"{len(plan_audits)} audit")
            warnings.append(
                f"{plans_dir}: contains {' and '.join(parts)} artifact(s). Keep existing files as history; "
                "write future execution state to the engineering memory bundle, not docs/plans."
            )

    return warnings


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
    warnings = collect_warnings(root)
    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
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

    register = sub.add_parser("register", help="Create or update a parallel work registration")
    register.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    register.add_argument("--title", required=True)
    register.add_argument("--description")
    register.add_argument("--path")
    register.add_argument("--registration-id")
    register.add_argument("--resource")
    register.add_argument("--tags")
    register.add_argument("--status", default="active")
    register.add_argument("--producer-id")
    register.add_argument("--source-workspace")
    register.add_argument("--source-session")
    register.add_argument("--related-plan")
    register.add_argument("--related-issue")
    register.add_argument("--git-branch")
    register.add_argument("--git-commit")
    register.add_argument("--latest-link")
    register.add_argument("--scope")
    register.add_argument("--current-claim")
    register.add_argument("--handoff")
    register.add_argument("--update", action="store_true")
    register.add_argument("--force", action="store_true")

    log = sub.add_parser("log", help="Append a chronological log entry")
    log.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    log.add_argument("--kind", default="Update")
    log.add_argument("--rollup", action="store_true", help="Append root log.md instead of creating a sharded event")
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
    if args.command == "register":
        register_work(args)
        return 0
    if args.command == "log":
        add_log(args.root, args.message, args.kind, args.rollup)
        return 0
    if args.command == "validate":
        return validate_bundle(args.root)
    return 1


if __name__ == "__main__":
    sys.exit(main())
