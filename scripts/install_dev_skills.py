#!/usr/bin/env python3
"""Install dev-skills into Codex's skills directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
from pathlib import Path


def default_dest() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "skills"
    return Path.home() / ".codex" / "skills"


def unique(names: list[str]) -> list[str]:
    return list(dict.fromkeys(name for name in names if name))


def remove_tree(path: Path) -> None:
    def make_writable(func, target: str, _exc_info: object) -> None:
        os.chmod(target, stat.S_IWRITE)
        func(target)

    shutil.rmtree(path, onerror=make_writable)


def copy_skill(name: str, source: Path, dest_root: Path, force: bool) -> dict[str, str]:
    target = dest_root / name
    if target.exists():
        if not force:
            return {"skill": name, "status": "skipped existing", "destination": str(target)}
        remove_tree(target)

    shutil.copytree(source, target)
    return {"skill": name, "status": "installed", "destination": str(target)}


def remove_skill(name: str, dest_root: Path) -> dict[str, str] | None:
    target = dest_root / name
    if not target.exists():
        return None

    remove_tree(target)
    return {"skill": name, "status": "removed obsolete", "destination": str(target)}


def find_local_skill(repo_root: Path, name: str) -> Path:
    skills_root = repo_root / "skills"
    for path in skills_root.rglob("SKILL.md"):
        if path.parent.name == name:
            return path.parent
    raise FileNotFoundError(f"Could not find local skill {name!r} under {skills_root}")


def install_plan(
    manifest: dict[str, object],
    include_recommended: bool,
    include_misc: bool,
) -> tuple[list[str], list[str]]:
    local = manifest.get("local", {})
    remove = manifest.get("remove", {})

    if not isinstance(local, dict):
        raise TypeError("skills.json field 'local' must be an object")
    if not isinstance(remove, dict):
        raise TypeError("skills.json field 'remove' must be an object")

    local_names: list[str] = []
    if "core" in local:
        local_names.extend(local.get("core", []))
    else:
        local_names.extend(local.get("required", []))
        if include_recommended:
            local_names.extend(local.get("recommended", []))
        if include_misc:
            local_names.extend(local.get("misc", []))

    removed_names: list[str] = []
    removed_names.extend(local.get("removed", []))
    removed_names.extend(remove.get("skills", []))

    desired = set(local_names)
    removed_names = [name for name in removed_names if name not in desired]

    return unique(local_names), unique(removed_names)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install dev-skills for Codex.")
    parser.add_argument("--dest", type=Path, default=default_dest(), help="Destination skills dir")
    parser.add_argument(
        "--include-recommended",
        action="store_true",
        help="Also install local recommended skills when skills.json defines them",
    )
    parser.add_argument(
        "--include-misc",
        action="store_true",
        help="Also install local miscellaneous skills",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing destination skills")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo_root / "skills.json").read_text(encoding="utf-8"))

    results: list[dict[str, str]] = []

    args.dest.mkdir(parents=True, exist_ok=True)

    local_names, removed_names = install_plan(
        manifest,
        args.include_recommended,
        args.include_misc,
    )

    for name in removed_names:
        row = remove_skill(name, args.dest)
        if row is not None:
            results.append(row)

    for name in local_names:
        source = find_local_skill(repo_root, name)
        if not (source / "SKILL.md").exists():
            raise FileNotFoundError(f"Local skill {name!r} is missing at {source}")
        results.append(copy_skill(name, source, args.dest, args.force))

    width = max([len("Skill"), *(len(row["skill"]) for row in results)])
    print(f"{'Skill':<{width}}  Status            Destination")
    print(f"{'-' * width}  {'-' * 16}  {'-' * 11}")
    for row in sorted(results, key=lambda item: item["skill"]):
        print(f"{row['skill']:<{width}}  {row['status']:<16}  {row['destination']}")

    print("\nRestart Codex to pick up newly installed or updated skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
