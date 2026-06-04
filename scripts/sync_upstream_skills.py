#!/usr/bin/env python3
"""Sync selected upstream skills into this repository with attribution."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "upstream-skills.json"


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def remove_tree(path: Path) -> None:
    def make_writable(func: Any, target: str, _exc_info: object) -> None:
        os.chmod(target, stat.S_IWRITE)
        func(target)

    shutil.rmtree(path, onerror=make_writable)


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("upstreams"), dict):
        raise ValueError("manifest must contain an 'upstreams' object")
    if not isinstance(data.get("skills"), list):
        raise ValueError("manifest must contain a 'skills' list")
    return data


def parse_overrides(values: list[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"source override must use upstream=path syntax: {value}")
        name, raw_path = value.split("=", 1)
        overrides[name] = Path(raw_path).expanduser().resolve()
    return overrides


def choose_entries(manifest: dict[str, Any], names: list[str], all_skills: bool) -> list[dict[str, Any]]:
    entries = manifest["skills"]
    if names:
        wanted = set(names)
        selected = [entry for entry in entries if entry.get("name") in wanted]
        missing = sorted(wanted - {entry.get("name") for entry in selected})
        if missing:
            raise ValueError("unknown skill(s): " + ", ".join(missing))
        return selected
    if all_skills:
        return list(entries)
    return [entry for entry in entries if entry.get("sync") is True]


def validate_entry(entry: dict[str, Any], upstreams: dict[str, Any]) -> None:
    for field in ("name", "category", "upstream", "upstream_path"):
        if not entry.get(field):
            raise ValueError(f"skill entry missing {field}: {entry}")
    upstream = upstreams.get(entry["upstream"])
    if upstream is None:
        raise ValueError(f"unknown upstream {entry['upstream']!r} for {entry['name']}")
    for field in ("repo_url", "license", "license_url"):
        if not upstream.get(field):
            raise ValueError(f"upstream {entry['upstream']!r} missing {field}")


def resolve_checkout(
    upstream_id: str,
    upstream: dict[str, Any],
    overrides: dict[str, Path],
    temp_dirs: list[Path],
) -> Path:
    if upstream_id in overrides:
        path = overrides[upstream_id]
        if not path.exists():
            raise FileNotFoundError(f"source override does not exist: {path}")
        return path

    hint = upstream.get("local_checkout_hint")
    if hint:
        candidate = (ROOT / str(hint)).resolve()
        if candidate.exists():
            return candidate

    repo_url = upstream["repo_url"]
    ref = upstream.get("default_ref", "main")
    temp_dir = Path(tempfile.mkdtemp(prefix=f"{upstream_id}-"))
    temp_dirs.append(temp_dir)
    run(["git", "clone", "--depth", "1", "--branch", ref, repo_url, str(temp_dir)])
    return temp_dir


def checkout_ref(source_root: Path, upstream: dict[str, Any]) -> str:
    try:
        return run(["git", "rev-parse", "HEAD"], cwd=source_root)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return str(upstream.get("default_ref", "unknown"))


def copy_skill(source: Path, target: Path, force: bool) -> None:
    if not source.exists():
        raise FileNotFoundError(f"upstream skill path does not exist: {source}")
    if not (source / "SKILL.md").exists():
        raise FileNotFoundError(f"upstream skill is missing SKILL.md: {source}")

    if target.exists():
        if not force:
            raise FileExistsError(f"target exists; use --force to replace: {target}")
        remove_tree(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )


def write_attribution(
    target: Path,
    entry: dict[str, Any],
    upstream: dict[str, Any],
    synced_ref: str,
) -> None:
    synced_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    repo_url = upstream["repo_url"]
    upstream_path = entry["upstream_path"]
    source_url = repo_url.removesuffix(".git") + f"/tree/{synced_ref}/{upstream_path}"

    source_md = f"""# Upstream Source

This skill was synchronized from an external repository.

- Skill: `{entry["name"]}`
- Upstream: `{entry["upstream"]}`
- Repository: {repo_url}
- Upstream path: `{upstream_path}`
- Source URL: {source_url}
- License: {upstream["license"]}
- License URL: {upstream["license_url"]}
- Synced ref: `{synced_ref}`
- Synced at: {synced_at}

Review upstream changes and license obligations before redistributing modified copies.
"""
    (target / "SOURCE.md").write_text(source_md, encoding="utf-8", newline="\n")


def copy_upstream_license(source_root: Path, target: Path, upstream: dict[str, Any]) -> None:
    license_file = upstream.get("license_file")
    if not license_file:
        return
    source = source_root / str(license_file)
    if source.exists():
        shutil.copy2(source, target / "LICENSE.upstream")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def print_plan(entries: list[dict[str, Any]], upstreams: dict[str, Any], dest_root: Path) -> None:
    if not entries:
        print("No skills selected. Use --skill, --all, or set sync=true in upstream-skills.json.")
        return

    print("Skill                         Target                         Upstream             License  Default")
    print("----------------------------  -----------------------------  -------------------  -------  -------")
    for entry in entries:
        upstream = upstreams[entry["upstream"]]
        target = display_path(dest_root / entry["category"] / entry["name"])
        print(
            f"{entry['name']:<28}  {target:<29}  "
            f"{entry['upstream']:<19}  {upstream['license']:<7}  {'yes' if entry.get('sync') else 'no'}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync vendored upstream Codex skills.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--skill", action="append", default=[], help="Skill name to sync; can repeat")
    parser.add_argument("--all", action="store_true", help="Select all skills in the manifest")
    parser.add_argument("--list", action="store_true", help="List upstream candidates and exit")
    parser.add_argument("--write", action="store_true", help="Write files; default is dry-run")
    parser.add_argument("--force", action="store_true", help="Replace an existing vendored skill")
    parser.add_argument(
        "--dest-root",
        type=Path,
        default=ROOT / "skills",
        help="Destination skills root; defaults to this repository's skills directory",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Override checkout path with upstream=path, for example mattpocock-skills=../skills",
    )
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    upstreams = manifest["upstreams"]
    entries = choose_entries(manifest, args.skill, args.all)
    dest_root = args.dest_root.expanduser().resolve()
    for entry in entries:
        validate_entry(entry, upstreams)

    if args.list:
        print_plan(manifest["skills"], upstreams, dest_root)
        return 0

    print_plan(entries, upstreams, dest_root)
    if not args.write:
        print("\nDry run only. Add --write to copy selected skills into this repository.")
        return 0

    overrides = parse_overrides(args.source)
    temp_dirs: list[Path] = []
    checkouts: dict[str, Path] = {}
    try:
        for entry in entries:
            upstream_id = entry["upstream"]
            upstream = upstreams[upstream_id]
            source_root = checkouts.get(upstream_id)
            if source_root is None:
                source_root = resolve_checkout(upstream_id, upstream, overrides, temp_dirs)
                checkouts[upstream_id] = source_root

            source = source_root / entry["upstream_path"]
            target = dest_root / entry["category"] / entry["name"]
            copy_skill(source, target, args.force)
            copy_upstream_license(source_root, target, upstream)
            write_attribution(target, entry, upstream, checkout_ref(source_root, upstream))
            print(f"synced {entry['name']} -> {target}")
    finally:
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                remove_tree(temp_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
