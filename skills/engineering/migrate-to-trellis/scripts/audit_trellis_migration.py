#!/usr/bin/env python3
"""Read-only audit for migrating dev-skills workflow artifacts to Trellis."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


WORKSTREAM_STATUSES_CURRENT = {"active", "draft", "ready", "in_progress", "planned"}
WORKSTREAM_STATUSES_STALE = {"closed", "complete", "completed", "done", "archived", "abandoned"}
REFERENCE_SCAN_EXTENSIONS = {".md", ".json", ".jsonl", ".toml", ".yaml", ".yml", ".txt"}
REFERENCE_SCAN_SKIP_DIRS = {
    ".git",
    ".trellis/tasks/archive",
    "docs/workstreams",
    "node_modules",
    "target",
    "repo-ref",
    "skills/engineering/migrate-to-trellis",
}
REFERENCE_SCAN_SKIP_PATHS = {"docs/migration-to-trellis.md"}
RETIRED_REFERENCE_PATTERNS = (
    "dev-flow",
    "audit-project-scale",
    "setup-rust-workstreams",
    "shape-product-architecture",
    "open-workstream",
    "plan-architecture-lane",
    "run-architecture-lane",
    "plan-engineering-program",
    "integrate-lane-results",
    "run-workstream-task",
    "review-workstream",
    "verify-rust-workstream",
    "resume-workstream",
    "close-workstream",
    "docs/workstreams",
    "WORKSTREAM.json",
    "TASKS.jsonl",
    "CAMPAIGNS.jsonl",
)


def normalize(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def workstream_status(workstream_dir: Path) -> str:
    data = read_json(workstream_dir / "WORKSTREAM.json")
    return str(data.get("status") or "").strip().lower()


def classify_workstream_file(root: Path, path: Path) -> dict[str, Any]:
    rel = normalize(path, root)
    parts = Path(rel).parts
    slug = parts[2] if len(parts) >= 3 else ""
    workstream_dir = root / "docs" / "workstreams" / slug
    status = workstream_status(workstream_dir)
    filename = path.name

    if status in WORKSTREAM_STATUSES_CURRENT:
        category = "convert_current_workstream"
        action = "Convert still-current work into a Trellis task or parent task."
    elif status in WORKSTREAM_STATUSES_STALE:
        category = "retire_legacy_workstream"
        action = "Extract durable lessons, then remove from active docs unless an audit archive is required."
    else:
        category = "review_workstream_history"
        action = "Review status before deciding whether to convert or archive."

    if filename in {"WORKSTREAM.json", "TASKS.jsonl", "CAMPAIGNS.jsonl"}:
        action += " Drop this file as workflow authority after migration."
    elif filename in {"EVIDENCE_AND_GATES.md"}:
        action += " Mine validation commands for Trellis quality checks."
    elif filename in {"HANDOFF.md", "CLOSEOUT.md"}:
        action += " Mine only durable context; otherwise archive."
    elif filename in {"DESIGN.md", "README.md", "TODO.md"}:
        action += " Use as PRD or research seed if work is still current."

    return {
        "path": rel,
        "category": category,
        "action": action,
        "workstream": slug,
        "status": status or "unknown",
    }


def classify_file(root: Path, path: Path) -> dict[str, Any] | None:
    rel = normalize(path, root)
    lower = rel.lower()

    if lower.startswith(".trellis/"):
        return {"path": rel, "category": "existing_trellis", "action": "Preserve Trellis runtime state."}
    if lower in {"agents.md", "claude.md"}:
        return {
            "path": rel,
            "category": "reconcile_agent_rules",
            "action": "Preserve repo rules outside managed Trellis blocks; remove duplicate workflow authority.",
        }
    if lower == "context.md":
        return {
            "path": rel,
            "category": "distill_to_trellis_spec",
            "action": "Distill stable domain language into .trellis/spec/guides/project-context.md.",
        }
    if lower.startswith("docs/adr/"):
        return {
            "path": rel,
            "category": "keep_architecture_knowledge",
            "action": "Keep in place and link from Trellis specs/tasks.",
        }
    if lower.startswith("docs/architecture/"):
        return {
            "path": rel,
            "category": "keep_architecture_knowledge",
            "action": "Keep in place or summarize into .trellis/spec/guides/architecture.md.",
        }
    if lower.startswith("docs/workstreams/"):
        return classify_workstream_file(root, path)
    return None


def iter_candidate_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for rel in ("AGENTS.md", "CLAUDE.md", "CONTEXT.md"):
        path = root / rel
        if path.exists():
            candidates.append(path)
    for rel in ("docs/adr", "docs/architecture", "docs/workstreams", ".trellis"):
        path = root / rel
        if path.is_dir():
            candidates.extend(item for item in path.rglob("*") if item.is_file())
    return sorted(set(candidates))


def should_skip_reference_scan(root: Path, path: Path) -> bool:
    rel = normalize(path, root)
    normalized = rel.lower()
    if normalized in {item.lower() for item in REFERENCE_SCAN_SKIP_PATHS}:
        return True
    return any(
        normalized == skip_dir.lower() or normalized.startswith(skip_dir.lower() + "/")
        for skip_dir in REFERENCE_SCAN_SKIP_DIRS
    )


def iter_reference_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_reference_scan(root, path):
            continue
        if path.suffix.lower() in REFERENCE_SCAN_EXTENSIONS:
            files.append(path)
    return sorted(files)


def scan_legacy_references(root: Path, max_rows: int = 500) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    count = 0
    lowered_patterns = tuple((pattern, pattern.lower()) for pattern in RETIRED_REFERENCE_PATTERNS)
    for path in iter_reference_files(root):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            lowered = line.lower()
            for pattern, lowered_pattern in lowered_patterns:
                if lowered_pattern in lowered:
                    count += 1
                    if len(rows) < max_rows:
                        rows.append(
                            {
                                "path": normalize(path, root),
                                "line": line_no,
                                "pattern": pattern,
                                "category": "legacy_reference",
                                "action": "Update or remove this reference during Trellis migration.",
                            }
                        )
    return rows, count


def build_audit(root: Path) -> dict[str, Any]:
    rows = [row for path in iter_candidate_files(root) if (row := classify_file(root, path))]
    legacy_references, legacy_reference_count = scan_legacy_references(root)
    counts: dict[str, int] = defaultdict(int)
    workstreams: dict[str, dict[str, Any]] = {}
    for row in rows:
        counts[row["category"]] += 1
        if row.get("workstream"):
            workstreams.setdefault(
                row["workstream"],
                {
                    "status": row["status"],
                    "category": row["category"],
                    "files": 0,
                },
            )
            workstreams[row["workstream"]]["files"] += 1

    current_workstreams = [
        {"slug": slug, **data}
        for slug, data in sorted(workstreams.items())
        if data["category"] == "convert_current_workstream"
    ]
    stale_workstreams = [
        {"slug": slug, **data}
        for slug, data in sorted(workstreams.items())
        if data["category"] == "retire_legacy_workstream"
    ]
    return {
        "root": str(root),
        "trellis_installed": (root / ".trellis" / "workflow.md").exists(),
        "counts": dict(sorted(counts.items())),
        "current_workstreams": current_workstreams,
        "stale_workstreams": stale_workstreams,
        "legacy_reference_count": legacy_reference_count,
        "legacy_references": legacy_references,
        "rows": rows,
        "recommendations": recommendations(
            root,
            current_workstreams,
            stale_workstreams,
            legacy_reference_count,
        ),
    }


def recommendations(
    root: Path,
    current_workstreams: list[dict[str, Any]],
    stale_workstreams: list[dict[str, Any]],
    legacy_reference_count: int,
) -> list[str]:
    notes: list[str] = []
    if not (root / ".trellis" / "workflow.md").exists():
        notes.append("Trellis is not installed; confirm beta init before writing .trellis files.")
    notes.append("Keep ADR and architecture docs as durable repo knowledge.")
    notes.append("Move stable CONTEXT.md language into .trellis/spec/guides/project-context.md.")
    if current_workstreams:
        notes.append("Convert current workstreams into Trellis tasks; do not keep old ledgers active.")
    if stale_workstreams:
        notes.append("Retire stale workstreams after extraction; keep a legacy archive only if needed.")
    if legacy_reference_count:
        notes.append("Clean legacy skill/workstream references from active docs after deleting old workflow files.")
    notes.append("Curate implement.jsonl and check.jsonl explicitly for every migrated task.")
    return notes


def render_text(audit: dict[str, Any], limit: int) -> str:
    lines = [
        "## Trellis Migration Audit",
        f"Repo: {audit['root']}",
        f"Trellis Installed: {audit['trellis_installed']}",
        "",
        "## Counts",
    ]
    for category, count in audit["counts"].items():
        lines.append(f"- {category}: {count}")

    lines.extend(["", "## Current Workstreams To Convert"])
    if not audit["current_workstreams"]:
        lines.append("(none)")
    for row in audit["current_workstreams"][:limit]:
        lines.append(f"- {row['slug']} ({row['status']}, files={row['files']})")

    lines.extend(["", "## Stale Workstreams To Retire"])
    if not audit["stale_workstreams"]:
        lines.append("(none)")
    for row in audit["stale_workstreams"][:limit]:
        lines.append(f"- {row['slug']} ({row['status']}, files={row['files']})")

    lines.extend(["", "## Recommendations"])
    lines.extend(f"- {item}" for item in audit["recommendations"])

    lines.extend(["", "## Legacy References To Clean"])
    lines.append(f"Total: {audit['legacy_reference_count']}")
    if not audit["legacy_references"]:
        lines.append("(none)")
    for row in audit["legacy_references"][:limit]:
        lines.append(f"- {row['path']}:{row['line']} [{row['pattern']}]")

    lines.extend(["", "## Sample Files"])
    for row in audit["rows"][:limit]:
        lines.append(f"- {row['path']} -> {row['category']}: {row['action']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--limit", type=int, default=20, help="sample row limit for text output")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    audit = build_audit(root)
    if args.format == "json":
        print(json.dumps(audit, indent=2, sort_keys=True))
    else:
        print(render_text(audit, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
