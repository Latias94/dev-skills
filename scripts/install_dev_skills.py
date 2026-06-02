#!/usr/bin/env python3
"""Install dev-skills into Codex's skills directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
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


def find_upstream_skill(root: Path, name: str) -> Path:
    skills_root = root / "skills"
    for path in skills_root.rglob("SKILL.md"):
        if path.parent.name == name:
            return path.parent
    raise FileNotFoundError(f"Could not find upstream skill {name!r} under {root}")


def find_local_skill(repo_root: Path, name: str) -> Path:
    skills_root = repo_root / "skills"
    for path in skills_root.rglob("SKILL.md"):
        if path.parent.name == name:
            return path.parent
    raise FileNotFoundError(f"Could not find local skill {name!r} under {skills_root}")


def clone_upstream() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="mattpocock-skills-"))
    subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/mattpocock/skills.git", str(tmp)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return tmp


def install_plan(
    manifest: dict[str, object],
    include_recommended: bool,
    include_optional: bool,
    include_misc: bool,
) -> tuple[list[str], list[str], list[str]]:
    local = manifest.get("local", {})
    external = manifest.get("external", {})
    upstream = manifest.get("upstream", {})
    remove = manifest.get("remove", {})

    if not isinstance(local, dict):
        raise TypeError("skills.json field 'local' must be an object")
    if not isinstance(external, dict):
        raise TypeError("skills.json field 'external' must be an object")
    if not isinstance(upstream, dict):
        raise TypeError("skills.json field 'upstream' must be an object")
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

    upstream_names: list[str] = []
    if "matt_skills" in external:
        upstream_names.extend(external.get("matt_skills", []))
    else:
        upstream_names.extend(upstream.get("required", []))
        if include_recommended:
            upstream_names.extend(upstream.get("recommended", []))
        if include_optional:
            upstream_names.extend(upstream.get("optional", []))

    removed_names: list[str] = []
    removed_names.extend(local.get("removed", []))
    removed_names.extend(remove.get("skills", []))

    desired = set(local_names + upstream_names)
    removed_names = [name for name in removed_names if name not in desired]

    return unique(local_names), unique(upstream_names), unique(removed_names)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install dev-skills for Codex.")
    parser.add_argument("--dest", type=Path, default=default_dest(), help="Destination skills dir")
    parser.add_argument(
        "--include-recommended",
        action="store_true",
        help="Also install recommended upstream mattpocock skills",
    )
    parser.add_argument(
        "--include-optional",
        action="store_true",
        help="Also install optional upstream mattpocock skills",
    )
    parser.add_argument(
        "--include-misc",
        action="store_true",
        help="Also install local miscellaneous skills",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing destination skills")
    parser.add_argument(
        "--mattpocock-skills-path",
        type=Path,
        help="Path to a local mattpocock/skills checkout",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo_root / "skills.json").read_text(encoding="utf-8"))

    args.dest.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, str]] = []

    local_names, upstream_names, removed_names = install_plan(
        manifest,
        args.include_recommended,
        args.include_optional,
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

    upstream_root = args.mattpocock_skills_path
    cleanup_root: Path | None = None
    if upstream_names and upstream_root is None:
        candidate = repo_root.parent / "skills"
        if (candidate / "skills").exists():
            upstream_root = candidate

    if upstream_names and upstream_root is None:
        cleanup_root = clone_upstream()
        upstream_root = cleanup_root

    try:
        if upstream_root is not None:
            for name in upstream_names:
                source = find_upstream_skill(upstream_root, name)
                results.append(copy_skill(name, source, args.dest, args.force))
    finally:
        if cleanup_root is not None and cleanup_root.exists():
            remove_tree(cleanup_root)

    width = max([len("Skill"), *(len(row["skill"]) for row in results)])
    print(f"{'Skill':<{width}}  Status            Destination")
    print(f"{'-' * width}  {'-' * 16}  {'-' * 11}")
    for row in sorted(results, key=lambda item: item["skill"]):
        print(f"{row['skill']:<{width}}  {row['status']:<16}  {row['destination']}")

    print("\nRestart Codex to pick up newly installed or updated skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
