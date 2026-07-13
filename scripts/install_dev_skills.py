#!/usr/bin/env python3
"""Install dev-skills into Codex's skills directory."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import sys
from pathlib import Path


SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IGNORED_TREE_NAMES = {".git", ".DS_Store", "__pycache__"}


def default_dest() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "skills"
    return Path.home() / ".codex" / "skills"


def unique(names: list[str]) -> list[str]:
    return list(dict.fromkeys(name for name in names if name))


def make_writable(path: Path) -> None:
    try:
        mode = os.lstat(path).st_mode
        if stat.S_ISLNK(mode):
            return
        owner_permissions = stat.S_IWUSR
        if stat.S_ISDIR(mode):
            owner_permissions |= stat.S_IRUSR | stat.S_IXUSR
        os.chmod(path, stat.S_IMODE(mode) | owner_permissions)
    except OSError:
        pass


def validate_skill_name(name: str) -> str:
    if not SKILL_NAME.fullmatch(name):
        raise ValueError(f"skill name must be one lowercase hyphen-case path component: {name!r}")
    return name


def ensure_within_root(path: Path, root: Path) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path escapes destination root {resolved_root}: {resolved_path}") from exc
    if not relative.parts:
        raise ValueError(f"path must be below destination root {resolved_root}: {resolved_path}")
    return path


def remove_tree(path: Path, allowed_root: Path) -> None:
    ensure_within_root(path, allowed_root)
    if path.is_symlink():
        raise ValueError(f"refusing to recursively remove symlink: {path}")
    make_writable(path)
    for root, directories, files in os.walk(path):
        root_path = Path(root)
        for name in directories:
            make_writable(root_path / name)
        for name in files:
            make_writable(root_path / name)
    shutil.rmtree(path)


def files_equal(left: Path, right: Path) -> bool:
    if not right.is_file():
        return False
    left_stat = left.stat()
    right_stat = right.stat()
    if left_stat.st_size != right_stat.st_size:
        return False
    with left.open("rb") as left_file, right.open("rb") as right_file:
        while True:
            left_chunk = left_file.read(1024 * 1024)
            right_chunk = right_file.read(1024 * 1024)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def ignored_relative_path(path: Path) -> bool:
    return (
        any(part in IGNORED_TREE_NAMES for part in path.parts)
        or path.suffix in {".pyc", ".pyo"}
    )


def copy_file_if_changed(source: Path, target: Path) -> bool:
    if files_equal(source, target):
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        make_writable(target)
    shutil.copy2(source, target)
    return True


def sync_tree(source: Path, target: Path) -> tuple[int, int]:
    copied = 0
    removed = 0
    target.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source.rglob("*")):
        relative = source_path.relative_to(source)
        if ignored_relative_path(relative):
            continue
        target_path = target / relative
        ensure_within_root(target_path, target)
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue
        if copy_file_if_changed(source_path, target_path):
            copied += 1

    for target_path in sorted(target.rglob("*"), key=lambda path: len(path.parts), reverse=True):
        relative = target_path.relative_to(target)
        source_path = source / relative
        if source_path.exists() and not ignored_relative_path(relative):
            continue
        make_writable(target_path)
        if target_path.is_dir():
            remove_tree(target_path, target)
        else:
            target_path.unlink()
        removed += 1

    return copied, removed


def copy_skill(name: str, source: Path, dest_root: Path, force: bool) -> dict[str, str]:
    validate_skill_name(name)
    target = dest_root / name
    ensure_within_root(target, dest_root)
    if target.exists():
        if not force:
            return {"skill": name, "status": "skipped existing", "destination": str(target)}
        copied, removed = sync_tree(source, target)
        if copied == 0 and removed == 0:
            status = "unchanged"
        else:
            status = f"updated ({copied} copied, {removed} removed)"
        return {"skill": name, "status": status, "destination": str(target)}

    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", ".DS_Store", "__pycache__", "*.pyc", "*.pyo"),
    )
    return {"skill": name, "status": "installed", "destination": str(target)}


def remove_skill(name: str, dest_root: Path) -> dict[str, str] | None:
    validate_skill_name(name)
    target = dest_root / name
    ensure_within_root(target, dest_root)
    if not target.exists():
        return None

    remove_tree(target, dest_root)
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

    selected = unique(local_names)
    obsolete = unique(removed_names)
    for name in [*selected, *obsolete]:
        validate_skill_name(name)
    return selected, obsolete


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
