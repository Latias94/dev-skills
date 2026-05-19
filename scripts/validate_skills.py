#!/usr/bin/env python3
"""Validate local skills against the repository skill authoring rules."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"


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


def validate_skill(skill_dir: Path) -> tuple[dict[str, str | int], list[str]]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    category = skill_dir.parent.name

    if not skill_md.exists():
        return {"skill": name, "lines": 0, "description": 0, "refs": 0}, ["missing SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    meta = frontmatter(text)

    description = ""
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
        if "Use when" not in description:
            errors.append('description missing "Use when" trigger')

    if category != "misc" and len(lines) > 100:
        errors.append(f"SKILL.md over 100 lines: {len(lines)}")

    if not re.search(r"(?mi)^## (Full )?Example\b|```text", text):
        errors.append("missing concrete example")

    refs_dir = skill_dir / "references"
    ref_files = [path for path in refs_dir.glob("**/*") if path.is_file()] if refs_dir.exists() else []
    deep_refs = [path for path in ref_files if len(path.relative_to(refs_dir).parts) > 1]
    if deep_refs:
        errors.append("references deeper than one level: " + ", ".join(str(path) for path in deep_refs))

    agent_file = skill_dir / "agents" / "openai.yaml"
    if not agent_file.exists():
        errors.append("missing agents/openai.yaml")

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

    skill_dirs = sorted(path.parent for path in SKILLS_ROOT.rglob("SKILL.md"))
    for skill_dir in skill_dirs:
        row, errors = validate_skill(skill_dir)
        rows.append(row)
        all_errors.extend((skill_dir.name, error) for error in errors)

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

    print("\nOK: local skills follow the repository write-a-skill checklist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
