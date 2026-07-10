#!/usr/bin/env python3
"""Create, validate, and render concurrency-safe engineering wiki memory bundles."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ROOT = Path("docs/knowledge/engineering")
TYPE_DIRS = {
    "work registration": "registry",
    "work progress": "progress",
    "session handoff": "sessions",
    "decision": "decisions",
    "subagent finding": "subagents",
    "verification evidence": "verification",
    "memory event": "logs",
    "repo convention": "conventions",
    "skill contract": "conventions",
    "legacy rollup snapshot": "legacy",
}
ROLLUP_BUDGETS = {
    "current-state.md": (120, 64 * 1024),
    "log.md": (360, 128 * 1024),
    "index.md": (200, 64 * 1024),
}
ROLLUP_LOG_LIMIT = 120
EXTERNAL_WORKSTREAM_STALE_DAYS = 30
LOCAL_ABSOLUTE_PATH_RE = re.compile(r"(?i)(?:[a-z]:\\|/Users/|/home/)")
CONFLICT_MARKERS = ("<<<<<<<", "=======", ">>>>>>>")
DERIVED_ROLLUP_MARKER = "<!-- engineering-wiki-memory: derived -->"
TERMINAL_REGISTRATION_STATUSES = {"cancelled", "canceled", "closed", "complete", "completed", "done"}


@dataclass(frozen=True)
class ValidationWarning:
    message: str
    suggestion: str


@dataclass(frozen=True)
class ConceptRecord:
    path: Path
    relative_path: str
    fields: dict[str, str]
    text: str

    @property
    def concept_type(self) -> str:
        return self.fields.get("type", "")

    @property
    def title(self) -> str:
        return self.fields.get("title") or self.path.stem

    @property
    def description(self) -> str:
        return self.fields.get("description", "")

    @property
    def timestamp(self) -> str:
        return self.fields.get("timestamp", "")

    @property
    def record_id(self) -> str:
        return self.fields.get("record_id", "")


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso_timestamp(value: dt.datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def timestamp_slug(value: dt.datetime) -> str:
    return value.strftime("%Y-%m-%dT%H%M%SZ")


def month_bucket(value: dt.datetime) -> str:
    return value.strftime("%Y-%m")


def new_record_id() -> str:
    return uuid.uuid4().hex


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "concept"


def yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def yaml_list(value: str | None) -> str | None:
    if not value:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        return None
    return "[" + ", ".join(yaml_string(item) for item in items) + "]"


def yaml_values(values: list[str]) -> str:
    if len(values) == 1:
        return yaml_string(values[0])
    return "[" + ", ".join(yaml_string(value) for value in values) + "]"


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + len("\n---\n") :]


def unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
        return value.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    return value


def frontmatter_fields(text: str) -> dict[str, str]:
    frontmatter, _body = split_frontmatter(text)
    fields: dict[str, str] = {}
    lines = frontmatter.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.groups()
        if value:
            fields[key] = unquote_yaml_scalar(value)
            index += 1
            continue

        items: list[str] = []
        index += 1
        while index < len(lines):
            item_match = re.match(r"^\s+-\s+(.*)$", lines[index])
            if item_match:
                items.append(unquote_yaml_scalar(item_match.group(1)))
                index += 1
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*", lines[index]):
                break
            index += 1
        fields[key] = yaml_values(items) if items else ""
    return fields


def frontmatter_value(text: str, key: str) -> str | None:
    return frontmatter_fields(text).get(key) or None


def frontmatter_values(fields: dict[str, str], key: str) -> list[str]:
    value = fields.get(key, "").strip()
    if not value:
        return []
    if not (value.startswith("[") and value.endswith("]")):
        return [value]
    inner = value[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    for character in inner:
        if quote:
            current.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
            current.append(character)
        elif character == ",":
            item = "".join(current).strip()
            if item:
                items.append(unquote_yaml_scalar(item))
            current = []
        else:
            current.append(character)
    item = "".join(current).strip()
    if item:
        items.append(unquote_yaml_scalar(item))
    return items


def is_derived_rollup(path: Path, text: str) -> bool:
    del path
    return DERIVED_ROLLUP_MARKER in text


def legacy_rollup_paths(root: Path) -> list[Path]:
    legacy: list[Path] = []
    for name in ("current-state.md", "log.md"):
        path = root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not is_derived_rollup(path, text):
            legacy.append(path)
    return legacy


def has_type_frontmatter(text: str) -> bool:
    return bool(frontmatter_fields(text).get("type"))


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
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def command_path(path: Path) -> str:
    value = str(path)
    if any(char.isspace() for char in value):
        return f'"{value}"'
    return value


def bundle_path(root: Path, raw_path: str) -> Path:
    root_resolved = root.resolve()
    path = Path(raw_path)
    candidate = path.resolve() if path.is_absolute() else (root_resolved / path).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise SystemExit(f"path must stay inside bundle root {root}: {raw_path}") from exc
    return candidate


def immutable_concept_path(root: Path, raw_path: str) -> Path:
    path = bundle_path(root, raw_path)
    if path.name in {"index.md", "log.md"} or path == (root.resolve() / "current-state.md"):
        raise SystemExit(f"reserved rollup path cannot hold an immutable concept: {raw_path}")
    return path


def write_exclusive(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except FileExistsError:
        return False
    return True


def write_if_missing(path: Path, content: str) -> bool:
    return write_exclusive(path, content)


def write_replacement(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8", errors="replace") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return True


def frontmatter_document(fields: list[tuple[str, str]], body: str) -> str:
    frontmatter = "---\n" + "\n".join(f"{key}: {value}" for key, value in fields) + "\n---\n\n"
    return frontmatter + body


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
    return "# Summary\n\n# Details\n\n# Next Action\n\n# Citations\n"


def standard_fields(
    args: argparse.Namespace,
    concept_type: str,
    title: str,
    record_id: str,
    created_at: dt.datetime,
    description: str | None = None,
) -> list[tuple[str, str]]:
    description = description if description is not None else getattr(args, "description", None)
    fields: list[tuple[str, str]] = [
        ("type", yaml_string(concept_type)),
        ("title", yaml_string(title)),
        ("description", yaml_string(description or f"{concept_type} for {title}.")),
        ("timestamp", iso_timestamp(created_at)),
        ("record_id", yaml_string(record_id)),
    ]
    tags = yaml_list(getattr(args, "tags", None))
    optional = {
        "resource": getattr(args, "resource", None),
        "tags": tags,
        "status": getattr(args, "status", None),
        "producer_id": getattr(args, "producer_id", None),
        "run_id": getattr(args, "run_id", None),
        "source_session": getattr(args, "source_session", None),
        "subagent_id": getattr(args, "subagent_id", None),
        "related_plan": getattr(args, "related_plan", None),
        "related_issue": getattr(args, "related_issue", None),
        "git_branch": getattr(args, "git_branch", None),
        "git_commit": getattr(args, "git_commit", None),
        "verified_by": getattr(args, "verified_by", None),
        "supersedes": getattr(args, "supersedes", None),
    }
    for key, value in optional.items():
        if not value:
            continue
        if key == "tags":
            fields.append((key, value))
        elif key == "supersedes":
            values = value if isinstance(value, list) else [value]
            fields.append((key, yaml_values(values)))
        else:
            fields.append((key, yaml_string(value)))
    return fields


def record_path(
    root: Path,
    concept_type: str,
    title: str,
    record_id: str,
    created_at: dt.datetime,
    explicit_path: str | None,
) -> Path:
    if explicit_path:
        return immutable_concept_path(root, explicit_path)
    dirname = TYPE_DIRS.get(concept_type.lower(), "")
    filename = f"{timestamp_slug(created_at)}-{slugify(title)}-{record_id}.md"
    base = root / dirname if dirname else root
    return base / month_bucket(created_at) / filename


def create_immutable_record(
    root: Path,
    concept_type: str,
    title: str,
    explicit_path: str | None,
    content_for: Callable[[str, dt.datetime], str],
) -> tuple[Path, str]:
    if explicit_path:
        record_id = new_record_id()
        created_at = utc_now()
        path = record_path(root, concept_type, title, record_id, created_at, explicit_path)
        if not write_exclusive(path, content_for(record_id, created_at)):
            raise SystemExit(f"refusing to overwrite immutable record: {path}")
        return path, record_id

    for _attempt in range(8):
        record_id = new_record_id()
        created_at = utc_now()
        path = record_path(root, concept_type, title, record_id, created_at, None)
        if write_exclusive(path, content_for(record_id, created_at)):
            return path, record_id
    raise SystemExit("could not allocate an unused immutable record path")


def index_content() -> str:
    return """# Engineering Memory

## Core

* [Current State](current-state.md) - Derived summary of immutable memory shards.
* [Update Log](log.md) - Derived chronology of recent immutable memory shards.

## Concepts

* [Decisions](decisions/) - Durable engineering choices and rationale.
* [Progress](progress/) - Work progress tied to plans, branches, or commits.
* [Registry](registry/) - Immutable snapshots of active producers and agent lanes.
* [Sessions](sessions/) - Compaction, interruption, and handoff summaries.
* [Subagents](subagents/) - Distilled findings from spawned agents.
* [Verification](verification/) - Test, build, lint, benchmark, and manual evidence.
* [Logs](logs/) - Append-only chronological event concepts.
* [Conventions](conventions/) - Local repo rules and reusable agent contracts.
* [Legacy Snapshots](legacy/) - Preserved root views from explicit migration adoption.
"""


def record_sort_key(record: ConceptRecord) -> tuple[str, str, str]:
    return (record.timestamp, record.record_id, record.relative_path)


def markdown_link(record: ConceptRecord) -> str:
    title = record.title.replace("]", "\\]")
    return f"[{title}]({record.relative_path})"


def source_fingerprint(records: list[ConceptRecord]) -> str:
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: item.relative_path):
        digest.update(record.relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(record.text.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def collect_records(root: Path) -> list[ConceptRecord]:
    records: list[ConceptRecord] = []
    if not root.exists():
        return records
    for path in sorted(root.rglob("*.md")):
        relative_path = relative_display(path, root)
        if path.name in {"index.md", "log.md"} or relative_path == "current-state.md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fields = frontmatter_fields(text)
        if not fields.get("type"):
            continue
        records.append(ConceptRecord(path=path, relative_path=relative_path, fields=fields, text=text))
    return records


def registration_heads(records: list[ConceptRecord]) -> dict[str, list[ConceptRecord]]:
    grouped: dict[str, list[ConceptRecord]] = defaultdict(list)
    for record in records:
        if record.concept_type.lower() != "work registration":
            continue
        registration_id = record.fields.get("registration_id")
        if registration_id:
            grouped[registration_id].append(record)

    result: dict[str, list[ConceptRecord]] = {}
    for registration_id, snapshots in grouped.items():
        superseded = {
            record_id
            for snapshot in snapshots
            for record_id in frontmatter_values(snapshot.fields, "supersedes")
        }
        heads = [snapshot for snapshot in snapshots if not snapshot.record_id or snapshot.record_id not in superseded]
        result[registration_id] = sorted(heads, key=record_sort_key, reverse=True)
    return result


def render_current_state(records: list[ConceptRecord]) -> str:
    fingerprint = source_fingerprint(records)
    heads_by_registration = registration_heads(records)
    heads = [head for group in heads_by_registration.values() for head in group]
    active_heads = [head for head in heads if head.fields.get("status", "active") == "active"]
    recent = sorted(
        [record for record in records if record.concept_type.lower() != "work registration"],
        key=record_sort_key,
        reverse=True,
    )[:12]

    fields = [
        ("type", yaml_string("Current State")),
        ("title", yaml_string("Current Engineering State")),
        ("description", yaml_string("Derived summary of immutable engineering-memory shards.")),
        ("tags", '["engineering-memory", "derived"]'),
        ("source_fingerprint", yaml_string(fingerprint)),
    ]
    lines = [
        "# Current State",
        "",
        DERIVED_ROLLUP_MARKER,
        "",
        "This file is derived from immutable shards. Record new facts in shards, then render during integration.",
        "",
        f"- Source fingerprint: `{fingerprint}`",
        f"- Immutable records: {len(records)}",
        f"- Active lane heads: {len(active_heads)}",
        "",
        "# Active Registrations",
        "",
    ]
    if not heads:
        lines.append("- No registration snapshots found.")
    else:
        for registration_id in sorted(heads_by_registration):
            group = heads_by_registration[registration_id]
            for head in group:
                status = head.fields.get("status", "unknown")
                producer = head.fields.get("producer_id", "unknown")
                lines.append(f"- {markdown_link(head)}: `{status}` ({registration_id}; producer `{producer}`)")

    lines.extend(["", "# Recent Evidence", ""])
    if not recent:
        lines.append("- No non-registration records found.")
    else:
        for record in recent:
            detail = f" - {record.description}" if record.description else ""
            lines.append(f"- **{record.concept_type}**: {markdown_link(record)}{detail}")

    lines.extend(
        [
            "",
            "# Integration Notes",
            "",
            "- Registration causality follows `supersedes`; wall-clock timestamps are display and scan hints only.",
            "- Use `render --check` after integrating shards to verify this view and `log.md` are fresh.",
            "",
        ]
    )
    return frontmatter_document(fields, "\n".join(lines))


def rollup_date(record: ConceptRecord) -> str:
    if re.match(r"^\d{4}-\d{2}-\d{2}", record.timestamp):
        return record.timestamp[:10]
    return "1970-01-01"


def render_log(records: list[ConceptRecord]) -> str:
    recent = sorted(records, key=record_sort_key, reverse=True)[:ROLLUP_LOG_LIMIT]
    lines = [
        "# Engineering Memory Update Log",
        "",
        DERIVED_ROLLUP_MARKER,
        "",
        "This file is a derived view of immutable shards. It is refreshed only during integration.",
        "",
    ]
    if not recent:
        lines.append("No immutable records found.")
        lines.append("")
        return "\n".join(lines)

    current_date: str | None = None
    for record in recent:
        date = rollup_date(record)
        if date != current_date:
            if current_date is not None:
                lines.append("")
            lines.extend([f"## {date}"])
            current_date = date
        detail = f" - {record.description}" if record.description else ""
        lines.append(f"* **{record.concept_type}**: {markdown_link(record)}{detail}")
    lines.append("")
    return "\n".join(lines)


def expected_rollups(root: Path) -> dict[Path, str]:
    records = collect_records(root)
    return {
        root / "current-state.md": render_current_state(records),
        root / "log.md": render_log(records),
    }


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
        "legacy",
    ):
        (root / dirname).mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    if write_if_missing(root / "index.md", index_content()):
        created.append(root / "index.md")
    for path, content in expected_rollups(root).items():
        if write_if_missing(path, content):
            created.append(path)

    if created:
        for path in created:
            print(f"created {path}")
    else:
        print(f"bundle already initialized at {root}")


def new_concept(args: argparse.Namespace) -> None:
    if args.type.lower() == "current state":
        raise SystemExit("Current State is a derived rollup; use `render` during integration.")
    if args.type.lower() == "work registration":
        raise SystemExit("Work Registration requires a stable lane identity; use `register` instead.")
    if args.force:
        raise SystemExit("immutable concepts cannot be overwritten; create a successor record instead.")

    root = args.root
    root.mkdir(parents=True, exist_ok=True)

    def content_for(record_id: str, created_at: dt.datetime) -> str:
        return frontmatter_document(
            standard_fields(args, args.type, args.title, record_id, created_at),
            body_template(args.type),
        )

    path, record_id = create_immutable_record(root, args.type, args.title, args.path, content_for)
    print(f"created {path} (record_id: {record_id})")


def external_runtime_references(args: argparse.Namespace) -> list[str]:
    raw_values = getattr(args, "external_runtime", None) or []
    if isinstance(raw_values, str):
        raw_values = [raw_values]
    references: list[str] = []
    for raw_value in raw_values:
        reference = str(raw_value).strip().replace("\\", "/")
        while reference.startswith("./"):
            reference = reference[2:]
        if (
            not reference
            or reference.startswith("/")
            or reference.startswith("../")
            or re.match(r"^[A-Za-z]:/", reference)
        ):
            raise SystemExit("--external-runtime must be a repo-relative path")
        if reference not in references:
            references.append(reference)
    return references


def registration_content(args: argparse.Namespace, record_id: str, created_at: dt.datetime) -> str:
    fields = standard_fields(args, "Work Registration", args.title, record_id, created_at)
    fields.append(("registration_id", yaml_string(args.registration_id)))
    external_runtimes = external_runtime_references(args)
    if external_runtimes:
        fields.append(("external_runtime", yaml_values(external_runtimes)))
    optional = {
        "source_workspace": args.source_workspace,
        "latest_link": args.latest_link,
    }
    for key, value in optional.items():
        if value:
            fields.append((key, yaml_string(value)))

    latest_link_lines = [f"- {args.latest_link}"] if args.latest_link else []
    latest_link_lines.extend(f"- External runtime: `{reference}`" for reference in external_runtimes)
    latest_links = "\n".join(latest_link_lines)
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
    return frontmatter_document(fields, body)


def register_work(args: argparse.Namespace) -> None:
    if args.force:
        raise SystemExit("registrations are immutable snapshots; create a successor with --supersedes instead.")

    root = args.root
    root.mkdir(parents=True, exist_ok=True)
    records = collect_records(root)
    existing = [
        record
        for record in records
        if record.concept_type.lower() == "work registration"
        and record.fields.get("registration_id") == args.registration_id
    ]
    records_by_id = {record.record_id: record for record in records if record.record_id}
    for predecessor_id in args.supersedes or []:
        predecessor = records_by_id.get(predecessor_id)
        if not predecessor:
            continue
        if predecessor.concept_type.lower() != "work registration":
            raise SystemExit(f"{predecessor_id!r} is not a Work Registration snapshot")
        if predecessor.fields.get("registration_id") != args.registration_id:
            raise SystemExit(
                f"{predecessor_id!r} belongs to registration "
                f"{predecessor.fields.get('registration_id')!r}, not {args.registration_id!r}"
            )
    external_runtime_references(args)
    if (args.update or existing) and not args.supersedes:
        raise SystemExit(
            "a registration snapshot already exists locally; create an immutable successor with "
            "--supersedes <prior-record-id>."
        )
    title = args.title

    def content_for(record_id: str, created_at: dt.datetime) -> str:
        return registration_content(args, record_id, created_at)

    if args.path:
        path, record_id = create_immutable_record(root, "Work Registration", title, args.path, content_for)
    else:
        def registration_path_for(record_id: str, created_at: dt.datetime) -> Path:
            filename = f"{timestamp_slug(created_at)}-{slugify(args.registration_id)}-{record_id}.md"
            return root / "registry" / month_bucket(created_at) / filename

        for _attempt in range(8):
            record_id = new_record_id()
            created_at = utc_now()
            path = registration_path_for(record_id, created_at)
            if write_exclusive(path, content_for(record_id, created_at)):
                break
        else:
            raise SystemExit("could not allocate an unused immutable registration path")

    print(f"created {path} (record_id: {record_id}, registration_id: {args.registration_id})")


def add_log(args: argparse.Namespace) -> None:
    if args.rollup:
        raise SystemExit("root log.md is derived; record a Memory Event, then use `render` during integration.")

    root = args.root
    root.mkdir(parents=True, exist_ok=True)
    title = f"{args.kind}: {args.message[:80]}"

    def content_for(record_id: str, created_at: dt.datetime) -> str:
        fields = standard_fields(args, "Memory Event", title, record_id, created_at, args.message[:140])
        fields.append(("event_kind", yaml_string(args.kind)))
        body = f"# Event\n\n{args.message}\n\n# Impact\n\n# Citations\n"
        return frontmatter_document(fields, body)

    path, record_id = create_immutable_record(root, "Memory Event", title, None, content_for)
    print(f"created {path} (record_id: {record_id})")


def fenced_markdown(text: str) -> str:
    longest_tilde_run = max((len(run) for run in re.findall(r"~+", text)), default=0)
    fence = "~" * max(3, longest_tilde_run + 1)
    return f"{fence}markdown\n{text.rstrip()}\n{fence}\n"


def preserve_legacy_rollup(root: Path, path: Path, owner: str) -> Path:
    original = path.read_text(encoding="utf-8", errors="replace")
    relative_path = relative_display(path, root)
    source_digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
    title = f"Legacy rollup {relative_path} before derived adoption"

    def content_for(record_id: str, created_at: dt.datetime) -> str:
        fields = [
            ("type", yaml_string("Legacy Rollup Snapshot")),
            ("title", yaml_string(title)),
            ("description", yaml_string(f"Preserved {relative_path} before derived rollup adoption.")),
            ("timestamp", iso_timestamp(created_at)),
            ("record_id", yaml_string(record_id)),
            ("producer_id", yaml_string(owner)),
            ("source_path", yaml_string(relative_path)),
            ("source_sha256", yaml_string(source_digest)),
        ]
        body = "\n".join(
            [
                "# Legacy Rollup Snapshot",
                "",
                f"- Original path: `{relative_path}`",
                f"- Original SHA-256: `{source_digest}`",
                "",
                "# Original Content",
                "",
                fenced_markdown(original).rstrip(),
                "",
            ]
        )
        return frontmatter_document(fields, body)

    snapshot, _record_id = create_immutable_record(
        root,
        "Legacy Rollup Snapshot",
        title,
        None,
        content_for,
    )
    return snapshot


def render_bundle(root: Path, owner: str | None, check: bool, adopt_rollups: bool = False) -> int:
    if not root.exists():
        raise SystemExit(f"missing bundle root: {root}")
    if not check and not owner:
        raise SystemExit("rendering shared rollups requires --owner <integration-owner>")
    if check and adopt_rollups:
        raise SystemExit("--adopt-rollups writes preserved snapshots and cannot be used with --check")

    errors = collect_validation_errors(root)
    records = collect_records(root)
    concurrent_heads = {
        registration_id: heads
        for registration_id, heads in registration_heads(records).items()
        if len(heads) > 1
    }
    lineage_issues = registration_lineage_issues(records)
    if errors or concurrent_heads or lineage_issues:
        print("Cannot render rollups:")
        for error in errors:
            print(f"- {error}")
        for issue in lineage_issues:
            print(f"- {issue.message}")
        for registration_id, heads in concurrent_heads.items():
            paths = ", ".join(head.relative_path for head in heads)
            print(f"- registration {registration_id!r} has concurrent heads: {paths}")
        return 1

    legacy_paths = legacy_rollup_paths(root)
    if legacy_paths:
        print("Legacy rollups need explicit adoption:")
        for path in legacy_paths:
            print(f"- {path}")
        if check or not adopt_rollups:
            print(
                "Run render with --owner <integration-owner> --adopt-rollups to preserve immutable "
                "legacy snapshots before replacing root views."
            )
            return 1
        assert owner is not None
        for path in legacy_paths:
            snapshot = preserve_legacy_rollup(root, path, owner)
            print(f"preserved {path} as {snapshot}")
        records = collect_records(root)

    rollups = {
        root / "current-state.md": render_current_state(records),
        root / "log.md": render_log(records),
    }
    stale = [
        path
        for path, content in rollups.items()
        if not path.exists() or path.read_text(encoding="utf-8", errors="replace") != content
    ]
    if check:
        if stale:
            print("Stale rollups:")
            for path in stale:
                print(f"- {path}")
            return 1
        print(f"OK: derived rollups are current at {root}")
        return 0

    changed = 0
    for path, content in rollups.items():
        if write_replacement(path, content):
            changed += 1
            print(f"rendered {path}")
    if changed == 0:
        print(f"rollups already current at {root}")
    else:
        print(f"rendered {changed} rollup(s) as integration owner {owner}")
    return 0


def has_conflict_marker(text: str) -> bool:
    return any(line.startswith(CONFLICT_MARKERS) for line in text.splitlines())


def collect_validation_errors(root: Path) -> list[str]:
    errors: list[str] = []
    record_ids: dict[str, str] = {}
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if has_conflict_marker(text):
            errors.append(f"{path}: contains unresolved Git conflict markers")
        if path.name in {"index.md", "log.md"} or relative_display(path, root) == "current-state.md":
            continue
        if not has_type_frontmatter(text):
            errors.append(f"{path}: missing frontmatter with non-empty type")
            continue
        record_id = frontmatter_value(text, "record_id")
        if record_id:
            previous = record_ids.get(record_id)
            if previous:
                errors.append(f"{path}: duplicate record_id {record_id!r}; first seen in {previous}")
            else:
                record_ids[record_id] = str(path)
    return errors


def registration_lineage_issues(records: list[ConceptRecord]) -> list[ValidationWarning]:
    issues: list[ValidationWarning] = []
    registrations = [record for record in records if record.concept_type.lower() == "work registration"]
    records_by_id = {record.record_id: record for record in records if record.record_id}
    for record in registrations:
        predecessor_ids = frontmatter_values(record.fields, "supersedes")
        if predecessor_ids and not record.record_id:
            continue
        for supersedes in predecessor_ids:
            predecessor = records_by_id.get(supersedes)
            if not predecessor:
                issues.append(
                    ValidationWarning(
                        f"{record.relative_path}: supersedes {supersedes!r}, which is not present in this bundle.",
                        "Fetch or merge the predecessor before rendering shared rollups.",
                    )
                )
                continue
            if predecessor.concept_type.lower() != "work registration":
                issues.append(
                    ValidationWarning(
                        f"{record.relative_path}: supersedes {supersedes!r}, which is not a Work Registration snapshot.",
                        "Create a successor that references only a registration snapshot from the same lane.",
                    )
                )
                continue
            if predecessor.fields.get("registration_id") != record.fields.get("registration_id"):
                issues.append(
                    ValidationWarning(
                        f"{record.relative_path}: supersedes a snapshot from registration {predecessor.fields.get('registration_id')!r}.",
                        "Create a successor that supersedes only snapshots from the same registration lineage.",
                    )
                )

    return issues


def registration_warnings(records: list[ConceptRecord]) -> list[ValidationWarning]:
    warnings: list[ValidationWarning] = []
    registrations = [record for record in records if record.concept_type.lower() == "work registration"]
    for record in registrations:
        missing = [key for key in ("record_id", "registration_id", "producer_id") if not record.fields.get(key)]
        if missing:
            warnings.append(
                ValidationWarning(
                    f"{record.relative_path}: registration is missing {', '.join(missing)}; it cannot safely participate in parallel ownership.",
                    "Keep the legacy file as history; create a new immutable registration snapshot with --registration-id and --producer-id.",
                )
            )
    warnings.extend(registration_lineage_issues(records))
    for registration_id, heads in registration_heads(records).items():
        if len(heads) > 1:
            paths = ", ".join(head.relative_path for head in heads)
            warnings.append(
                ValidationWarning(
                    f"registration {registration_id!r} has {len(heads)} concurrent snapshot heads ({paths}).",
                    "During integration, create one successor registration snapshot with --supersedes pointing to the chosen predecessor, then record how the competing head was resolved.",
                )
            )
    return warnings


def related_workstreams_dir(root: Path) -> Path | None:
    for parent in (root, *root.parents):
        candidate = parent / "workstreams"
        if candidate.is_dir():
            return candidate
    return None


def workstream_display(path: Path, workstreams_dir: Path) -> str:
    try:
        return path.relative_to(workstreams_dir.parent.parent).as_posix()
    except ValueError:
        return str(path)


def workstream_updated_date(payload: dict[str, object]) -> dt.date | None:
    value = payload.get("updated")
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except ValueError:
        return None


def active_external_runtime_references(records: list[ConceptRecord]) -> set[str]:
    references: set[str] = set()
    registrations = [record for record in records if record.concept_type.lower() == "work registration"]
    heads_by_registration = registration_heads(records)
    for registration_id, heads in heads_by_registration.items():
        if all(head.fields.get("status", "active").lower() in TERMINAL_REGISTRATION_STATUSES for head in heads):
            continue
        for record in registrations:
            if record.fields.get("registration_id") != registration_id:
                continue
            references.update(frontmatter_values(record.fields, "external_runtime"))
    return references


def external_workstream_warnings(root: Path, records: list[ConceptRecord] | None = None) -> list[ValidationWarning]:
    workstreams_dir = related_workstreams_dir(root)
    if not workstreams_dir:
        return []

    active: list[tuple[Path, dict[str, object]]] = []
    malformed: list[str] = []
    for path in sorted(workstreams_dir.rglob("WORKSTREAM.json")):
        display = workstream_display(path, workstreams_dir)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            malformed.append(display)
            continue
        if not isinstance(payload, dict):
            malformed.append(display)
            continue
        if str(payload.get("status", "")).lower() == "active":
            active.append((path, payload))

    warnings: list[ValidationWarning] = []
    if malformed:
        sample = ", ".join(malformed[:4])
        suffix = "" if len(malformed) <= 4 else f", plus {len(malformed) - 4} more"
        warnings.append(
            ValidationWarning(
                f"External workstream runtime contains {len(malformed)} unreadable manifest(s): {sample}{suffix}.",
                "Repair those manifests in their own workflow; engineering memory must only reference them, never overwrite them.",
            )
        )
    if not active:
        return warnings

    referenced = active_external_runtime_references(records or collect_records(root))
    unlinked = [
        (path, payload)
        for path, payload in active
        if workstream_display(path, workstreams_dir) not in referenced
    ]
    if not unlinked:
        return warnings

    unlinked_display = [workstream_display(path, workstreams_dir) for path, _payload in unlinked]
    sample = ", ".join(unlinked_display[:6])
    suffix = "" if len(unlinked_display) <= 6 else f", plus {len(unlinked_display) - 6} more"
    warnings.append(
        ValidationWarning(
            f"Found {len(unlinked)} active external workstream runtime(s) without an open registration: {sample}{suffix}.",
            "Treat WORKSTREAM.json and its TODO/HANDOFF files as external mutable runtimes; register an immutable lane with --external-runtime instead of copying or updating them through engineering memory.",
        )
    )

    stale: list[str] = []
    today = utc_now().date()
    for path, payload in unlinked:
        updated = workstream_updated_date(payload)
        if updated and (today - updated).days > EXTERNAL_WORKSTREAM_STALE_DAYS:
            stale.append(f"{workstream_display(path, workstreams_dir)} ({updated.isoformat()})")
    if stale:
        sample = "; ".join(stale[:4])
        suffix = "" if len(stale) <= 4 else f"; plus {len(stale) - 4} more"
        warnings.append(
            ValidationWarning(
                f"Active external workstream metadata is older than {EXTERNAL_WORKSTREAM_STALE_DAYS} days: "
                + sample
                + suffix
                + ".",
                "Confirm that the external lane is still owned before resuming or duplicating its work; do not update its runtime through engineering memory.",
            )
        )
    return warnings


def collect_warnings(root: Path) -> list[ValidationWarning]:
    warnings: list[ValidationWarning] = []
    if not root.exists():
        return warnings

    root_arg = command_path(root)
    if not (root / "registry").is_dir():
        warnings.append(
            ValidationWarning(
                f"{root / 'registry'}: missing registry directory; run init before parallel work.",
                f"Run `python wiki_memory.py init --root {root_arg}`, then register active lanes with a unique registration ID.",
            )
        )

    for name, (max_lines, max_bytes) in ROLLUP_BUDGETS.items():
        path = root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = len(text.splitlines())
        size = path.stat().st_size
        if lines > max_lines or size > max_bytes:
            suggestion = (
                "Keep root rollups bounded; write detailed facts as immutable shards and rerender only during integration."
            )
            warnings.append(
                ValidationWarning(
                    f"{path}: large rollup ({lines} lines, {size // 1024} KiB).",
                    suggestion,
                )
            )

    current_state = root / "current-state.md"
    if current_state.exists():
        text = current_state.read_text(encoding="utf-8", errors="replace")
        recorded_branch = frontmatter_value(text, "git_branch")
        actual_branch = git_branch_for(root)
        if recorded_branch and actual_branch and recorded_branch != actual_branch:
            warnings.append(
                ValidationWarning(
                    f"{current_state}: git_branch is {recorded_branch!r}, but the repository is on {actual_branch!r}.",
                    "Treat this as a stale historical rollup and rerender from immutable shards during integration.",
                )
            )

    local_path_files: list[str] = []
    local_path_count = 0
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter, body = split_frontmatter(text)
        searchable_lines = [
            line for line in frontmatter.splitlines() if not line.lstrip().startswith("source_workspace:")
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
            ValidationWarning(
                f"{local_path_count} file(s) contain local absolute paths outside source_workspace hints ({sample}{suffix}).",
                "Replace absolute paths in body text and citations with repo-relative links; retain machine-local paths only in source_workspace frontmatter.",
            )
        )

    records = collect_records(root)
    for record in records:
        if not record.record_id:
            warnings.append(
                ValidationWarning(
                    f"{record.relative_path}: missing record_id; treat it as a legacy concept during parallel work.",
                    "Keep it as history and create a new immutable successor instead of rewriting it.",
                )
            )
    warnings.extend(registration_warnings(records))
    warnings.extend(external_workstream_warnings(root, records))

    large_progress_files: list[str] = []
    progress_dir = root / "progress"
    if progress_dir.is_dir():
        for path in sorted(progress_dir.rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = len(text.splitlines())
            size = path.stat().st_size
            if lines > 150 or size > 80 * 1024:
                large_progress_files.append(f"{relative_display(path, root)} ({lines} lines, {size // 1024} KiB)")
    if large_progress_files:
        sample = "; ".join(large_progress_files[:4])
        suffix = "" if len(large_progress_files) <= 4 else f"; plus {len(large_progress_files) - 4} more"
        warnings.append(
            ValidationWarning(
                "Large progress files look like mutable per-plan ledgers: " + sample + suffix + ".",
                f"Keep them as history; create successor work updates with `python wiki_memory.py new --root {root_arg} --type \"Work Progress\" --title ...`.",
            )
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
                ValidationWarning(
                    f"{plans_dir}: contains {' and '.join(parts)} artifact(s).",
                    "Leave historical plan artifacts in place; put future execution state in immutable engineering-memory shards.",
                )
            )

    legacy_paths = set(legacy_rollup_paths(root))
    if legacy_paths:
        legacy_display = ", ".join(relative_display(path, root) for path in sorted(legacy_paths))
        warnings.append(
            ValidationWarning(
                f"Legacy root rollups have not been adopted: {legacy_display}.",
                "Do not run normal render against those files. Use `python wiki_memory.py render --root ... --owner <integration-owner> --adopt-rollups` to preserve immutable snapshots before derived views take ownership.",
            )
        )

    rollups = expected_rollups(root)
    stale = [
        relative_display(path, root)
        for path, content in rollups.items()
        if path not in legacy_paths
        and (not path.exists() or path.read_text(encoding="utf-8", errors="replace") != content)
    ]
    if stale:
        warnings.append(
            ValidationWarning(
                f"Derived rollups are stale: {', '.join(stale)}.",
                "After pulling or rebasing all shards, have one integration owner run `python wiki_memory.py render --root ... --owner ...`.",
            )
        )
    return warnings


def validate_bundle(root: Path) -> int:
    errors: list[str] = []
    if not root.exists():
        errors.append(f"missing bundle root: {root}")
    else:
        errors.extend(collect_validation_errors(root))

    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"OK: {root} is a valid minimal engineering wiki memory bundle")

    if root.exists():
        warnings = collect_warnings(root)
        if warnings:
            print()
            print("Warnings:")
            for warning in warnings:
                print(f"- {warning.message}")
            suggestions = list(dict.fromkeys(warning.suggestion for warning in warnings))
            if suggestions:
                print()
                print("Suggested actions:")
                for suggestion in suggestions:
                    print(f"- {suggestion}")
    return 1 if errors else 0


def add_common_record_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--description")
    parser.add_argument("--resource")
    parser.add_argument("--tags")
    parser.add_argument("--status")
    parser.add_argument("--producer-id")
    parser.add_argument("--run-id")
    parser.add_argument("--source-session")
    parser.add_argument("--subagent-id")
    parser.add_argument("--related-plan")
    parser.add_argument("--related-issue")
    parser.add_argument("--git-branch")
    parser.add_argument("--git-commit")
    parser.add_argument("--verified-by")
    parser.add_argument("--supersedes", action="append", help="Prior record_id; repeat to merge multiple predecessors")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize a deterministic engineering wiki memory bundle")
    init.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    new = sub.add_parser("new", help="Create an immutable wiki memory concept document")
    new.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    new.add_argument("--type", required=True)
    new.add_argument("--title", required=True)
    new.add_argument("--path", help="Controlled exception: create one immutable record at this bundle-relative path")
    add_common_record_arguments(new)
    new.add_argument("--force", action="store_true", help=argparse.SUPPRESS)

    register = sub.add_parser("register", help="Create an immutable snapshot for one parallel work lane")
    register.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    register.add_argument("--title", required=True)
    register.add_argument("--registration-id", required=True, help="Stable, globally unique identity for this work lane")
    register.add_argument("--producer-id", required=True, help="Machine or agent that produced this snapshot")
    register.add_argument("--description")
    register.add_argument("--path", help="Controlled exception: create one immutable snapshot at this bundle-relative path")
    register.add_argument("--resource")
    register.add_argument("--tags")
    register.add_argument("--status", default="active")
    register.add_argument("--run-id")
    register.add_argument("--source-workspace")
    register.add_argument("--source-session")
    register.add_argument("--related-plan")
    register.add_argument("--related-issue")
    register.add_argument("--git-branch")
    register.add_argument("--git-commit")
    register.add_argument(
        "--external-runtime",
        action="append",
        help="Repo-relative WORKSTREAM.json or other external mutable runtime; repeat for more than one",
    )
    register.add_argument(
        "--supersedes",
        action="append",
        help="Prior snapshot record_id for this lane; repeat to merge multiple heads",
    )
    register.add_argument("--latest-link")
    register.add_argument("--scope")
    register.add_argument("--current-claim")
    register.add_argument("--handoff")
    register.add_argument("--update", action="store_true", help=argparse.SUPPRESS)
    register.add_argument("--force", action="store_true", help=argparse.SUPPRESS)

    log = sub.add_parser("log", help="Create an immutable chronological memory event")
    log.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    log.add_argument("--kind", default="Update")
    log.add_argument("--producer-id")
    log.add_argument("--run-id")
    log.add_argument("--source-session")
    log.add_argument("--related-plan")
    log.add_argument("--related-issue")
    log.add_argument("--git-branch")
    log.add_argument("--git-commit")
    log.add_argument("--rollup", action="store_true", help=argparse.SUPPRESS)
    log.add_argument("message")

    render = sub.add_parser("render", help="Materialize deterministic root rollups from immutable shards")
    render.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    render.add_argument("--owner", help="Required for writes; names the integration owner")
    render.add_argument("--check", action="store_true", help="Exit nonzero when rollups are stale without writing")
    render.add_argument(
        "--adopt-rollups",
        action="store_true",
        help="Preserve immutable snapshots before first replacing legacy root rollups",
    )

    validate = sub.add_parser("validate", help="Validate memory conformance and concurrency hazards")
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
        add_log(args)
        return 0
    if args.command == "render":
        return render_bundle(args.root, args.owner, args.check, args.adopt_rollups)
    if args.command == "validate":
        return validate_bundle(args.root)
    return 1


if __name__ == "__main__":
    sys.exit(main())
