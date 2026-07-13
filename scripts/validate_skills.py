#!/usr/bin/env python3
"""Validate local skills against the repository skill authoring rules."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def frontmatter(text: str) -> str | None:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return match.group(1) if match else None


def field(frontmatter_text: str, name: str) -> str | None:
    lines = frontmatter_text.splitlines()
    prefix = f"{name}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue

        rest = line[len(prefix) :].strip()
        if rest != ">":
            return rest.strip().strip("\"'")

        value_lines: list[str] = []
        for next_line in lines[index + 1 :]:
            if re.match(r"^[A-Za-z0-9_-]+:", next_line):
                break
            value_lines.append(next_line.strip())
        return " ".join(value_lines).strip()

    return None


def yaml_scalar(text: str, name: str) -> str | None:
    match = re.search(rf"(?m)^\s+{re.escape(name)}:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip("\"'") if match else None


def validate_skill(
    skill_dir: Path,
    vendored_entries: dict[tuple[str, str], dict[str, Any]],
) -> tuple[dict[str, str | int], list[str]]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    category = skill_dir.parent.name
    vendored_entry = vendored_entries.get((category, name))
    is_vendored = vendored_entry is not None

    if not skill_md.exists():
        return {"skill": name, "lines": 0, "description": 0, "refs": 0}, ["missing SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    meta = frontmatter(text)

    description = ""
    if not SKILL_NAME.fullmatch(name):
        errors.append("directory name is not lowercase hyphen-case")
    if (skill_dir / "README.md").exists():
        errors.append("individual skill directories must not contain README.md")
    if meta is None:
        errors.append("missing frontmatter")
    else:
        declared_name = field(meta, "name")
        description = field(meta, "description") or ""
        if declared_name != name:
            errors.append(f"name {declared_name!r} does not match directory {name!r}")
        if not description:
            errors.append("missing description")
        if len(description) > 1024:
            errors.append(f"description too long: {len(description)} chars")
        if not is_vendored and "Use when" not in description:
            errors.append('description missing "Use when" trigger')

    if not is_vendored and category != "misc" and len(lines) > 100:
        errors.append(f"SKILL.md over 100 lines: {len(lines)}")

    if not is_vendored and not re.search(r"(?mi)^## (Full )?Example\b|```text", text):
        errors.append("missing concrete example")

    refs_dir = skill_dir / "references"
    ref_files = [path for path in refs_dir.glob("**/*") if path.is_file()] if refs_dir.exists() else []
    deep_refs = [path for path in ref_files if len(path.relative_to(refs_dir).parts) > 1]
    if deep_refs:
        errors.append("references deeper than one level: " + ", ".join(str(path) for path in deep_refs))

    agent_file = skill_dir / "agents" / "openai.yaml"
    if not is_vendored and not agent_file.exists():
        errors.append("missing agents/openai.yaml")
    if agent_file.exists():
        agent_text = agent_file.read_text(encoding="utf-8")
        short_description = yaml_scalar(agent_text, "short_description") or ""
        default_prompt = yaml_scalar(agent_text, "default_prompt") or ""
        if not 25 <= len(short_description) <= 64:
            errors.append(
                "agents/openai.yaml short_description must be 25-64 characters: "
                f"{len(short_description)}"
            )
        if f"${name}" not in default_prompt:
            errors.append(f"agents/openai.yaml default_prompt must mention ${name}")

    source_file = skill_dir / "SOURCE.md"
    if is_vendored:
        if not source_file.exists():
            errors.append("vendored skill is missing SOURCE.md")
        else:
            source_text = source_file.read_text(encoding="utf-8")
            expected_source_fields = (
                f'- Upstream: `{vendored_entry["upstream"]}`',
                f'- Upstream path: `{vendored_entry["upstream_path"]}`',
                "- Repository:",
                "- License:",
                "- Synced ref:",
                "- Synced at:",
            )
            for expected in expected_source_fields:
                if expected not in source_text:
                    errors.append(f"SOURCE.md missing or mismatched field: {expected}")

    row: dict[str, str | int] = {
        "category": category,
        "skill": name,
        "lines": len(lines),
        "description": len(description),
        "refs": len(ref_files),
    }
    return row, errors


def main() -> int:
    all_errors: list[tuple[str, str]] = []
    rows: list[dict[str, str | int]] = []

    upstream_manifest = json.loads((ROOT / "upstream-skills.json").read_text(encoding="utf-8"))
    vendored_entries = {
        (str(entry["category"]), str(entry["name"])): entry
        for entry in upstream_manifest["skills"]
        if entry.get("sync") is True
    }
    install_manifest = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
    installed_names = install_manifest.get("local", {}).get("core", [])

    skill_dirs = sorted(path.parent for path in SKILLS_ROOT.rglob("SKILL.md"))
    directories_by_name: dict[str, list[Path]] = {}
    for skill_dir in skill_dirs:
        directories_by_name.setdefault(skill_dir.name, []).append(skill_dir)
        row, errors = validate_skill(skill_dir, vendored_entries)
        rows.append(row)
        all_errors.extend((skill_dir.name, error) for error in errors)

    for name, directories in directories_by_name.items():
        if len(directories) > 1:
            all_errors.append(
                (name, "duplicate skill name: " + ", ".join(str(path) for path in directories))
            )

    for (category, name), _entry in vendored_entries.items():
        expected = SKILLS_ROOT / category / name / "SKILL.md"
        if not expected.exists():
            all_errors.append((name, f"manifest target is missing: {expected}"))

    for name in installed_names:
        matches = directories_by_name.get(str(name), [])
        if len(matches) != 1:
            all_errors.append(
                (str(name), f"skills.json requires exactly one matching skill directory; found {len(matches)}")
            )

    print("Category     Skill                         Lines  Desc  Refs")
    print("-----------  ----------------------------  -----  ----  ----")
    for row in rows:
        print(
            f"{row['category']:<11}  {row['skill']:<28}  "
            f"{row['lines']:>5}  {row['description']:>4}  {row['refs']:>4}"
        )

    if all_errors:
        print("\nErrors:")
        for skill_name, error in all_errors:
            print(f"- {skill_name}: {error}")
        return 1

    print("\nOK: managed skills match the manifests and repository authoring rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
