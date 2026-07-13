#!/usr/bin/env python3
"""Sync selected upstream skills into this repository with attribution."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "upstream-skills.json"
PATH_COMPONENT = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


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


def ensure_within_root(
    path: Path,
    root: Path,
    *,
    allow_root: bool = False,
) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path escapes allowed root {resolved_root}: {resolved_path}") from exc
    if not allow_root and not relative.parts:
        raise ValueError(f"path must be below allowed root {resolved_root}: {resolved_path}")
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
    exclude = entry.get("exclude")
    if exclude is not None and (
        not isinstance(exclude, list)
        or not all(isinstance(pattern, str) and pattern for pattern in exclude)
    ):
        raise ValueError(f"exclude must be a list of non-empty patterns: {entry}")
    for field in ("name", "category"):
        if not PATH_COMPONENT.fullmatch(str(entry[field])):
            raise ValueError(f"{field} must be one lowercase hyphen-case path component: {entry[field]!r}")


def checkout_matches_remote(candidate: Path, repo_url: str, ref: str) -> bool:
    try:
        if run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=candidate):
            return False
        local_head = run(["git", "rev-parse", "HEAD"], cwd=candidate)
        remote_ref = f"refs/heads/{ref}"
        remote_output = run(
            ["git", "ls-remote", "--exit-code", repo_url, remote_ref],
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

    remote_heads = {
        parts[1]: parts[0]
        for line in remote_output.splitlines()
        if len(parts := line.split()) == 2
    }
    return remote_heads.get(remote_ref) == local_head


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

    repo_url = upstream["repo_url"]
    ref = upstream.get("default_ref", "main")
    hint = upstream.get("local_checkout_hint")
    if hint:
        candidate = (ROOT / str(hint)).resolve()
        if candidate.exists() and checkout_matches_remote(candidate, repo_url, ref):
            return candidate
        if candidate.exists():
            print(f"Ignoring stale or dirty local checkout hint: {candidate}")

    temp_dir = Path(tempfile.mkdtemp(prefix=f"{upstream_id}-"))
    temp_dirs.append(temp_dir)
    run(["git", "clone", "--depth", "1", "--branch", ref, repo_url, str(temp_dir)])
    return temp_dir


def checkout_ref(source_root: Path, upstream: dict[str, Any]) -> str:
    try:
        return run(["git", "rev-parse", "HEAD"], cwd=source_root)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return str(upstream.get("default_ref", "unknown"))


def copy_skill(
    source: Path,
    target: Path,
    force: bool,
    exclude_patterns: list[str] | None = None,
    *,
    allowed_root: Path | None = None,
) -> None:
    if not source.exists():
        raise FileNotFoundError(f"upstream skill path does not exist: {source}")
    if not (source / "SKILL.md").exists():
        raise FileNotFoundError(f"upstream skill is missing SKILL.md: {source}")

    if allowed_root is not None:
        ensure_within_root(target, allowed_root)

    if target.exists():
        if not force:
            raise FileExistsError(f"target exists; use --force to replace: {target}")
        if allowed_root is None:
            raise ValueError("allowed_root is required when replacing an existing target")
        remove_tree(target, allowed_root)

    target.parent.mkdir(parents=True, exist_ok=True)
    ignored_patterns = [
        ".git",
        ".DS_Store",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        *(exclude_patterns or []),
    ]
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(*ignored_patterns),
    )


def rewrite_frontmatter_name(target: Path, skill_name: str) -> None:
    skill_md = target / "SKILL.md"
    lines = skill_md.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"cannot rewrite skill name without frontmatter: {skill_md}")

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            newline = "\n" if line.endswith("\n") else ""
            lines[index] = f"name: {skill_name}{newline}"
            skill_md.write_text("".join(lines), encoding="utf-8", newline="\n")
            return

    raise ValueError(f"cannot rewrite skill name; frontmatter has no name field: {skill_md}")


def rewrite_invocations(target: Path, rewrite: dict[str, Any]) -> None:
    source_name = rewrite.get("from")
    target_name = rewrite.get("to")
    if not source_name or not target_name:
        raise ValueError(f"rewrite_invocations must include from and to: {rewrite}")

    skill_md = target / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    pattern = re.compile(rf"/{re.escape(str(source_name))}(?![A-Za-z0-9_-])")
    updated = pattern.sub(f"/{target_name}", text)
    if updated == text:
        raise ValueError(f"invocation rewrite did not match /{source_name} in {skill_md}")
    skill_md.write_text(updated, encoding="utf-8", newline="\n")


def rewrite_text(target: Path, rewrites: list[dict[str, Any]]) -> None:
    for rewrite in rewrites:
        if not isinstance(rewrite, dict):
            raise ValueError(f"text rewrite must be an object: {rewrite}")
        relative_path = rewrite.get("path", "SKILL.md")
        old = rewrite.get("from")
        new = rewrite.get("to")
        if not old or new is None:
            raise ValueError(f"text rewrite must include from and to: {rewrite}")

        target_root = target.resolve()
        file_path = (target_root / str(relative_path)).resolve()
        try:
            file_path.relative_to(target_root)
        except ValueError as exc:
            raise ValueError(f"text rewrite path escapes skill directory: {relative_path}") from exc

        text = file_path.read_text(encoding="utf-8")
        updated = text.replace(str(old), str(new))
        if updated == text:
            raise ValueError(f"text rewrite did not match {old!r} in {file_path}")
        file_path.write_text(updated, encoding="utf-8", newline="\n")


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

    print("Skill                         Target                         Upstream             License  Role             Auto-sync")
    print("----------------------------  -----------------------------  -------------------  -------  ---------------  -------")
    for entry in entries:
        upstream = upstreams[entry["upstream"]]
        target = display_path(dest_root / entry["category"] / entry["name"])
        role = str(entry.get("workflow_role", "candidate"))
        print(
            f"{entry['name']:<28}  {target:<29}  "
            f"{entry['upstream']:<19}  {upstream['license']:<7}  {role:<15}  {'yes' if entry.get('sync') else 'no'}"
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
    checkout_refs: dict[str, str] = {}
    try:
        for entry in entries:
            target = dest_root / entry["category"] / entry["name"]
            ensure_within_root(target, dest_root)
            if target.exists() and not args.force:
                raise FileExistsError(f"target exists; use --force to replace: {target}")

        staging_root = Path(tempfile.mkdtemp(prefix="dev-skills-sync-stage-"))
        temp_dirs.append(staging_root)
        for entry in entries:
            upstream_id = entry["upstream"]
            upstream = upstreams[upstream_id]
            source_root = checkouts.get(upstream_id)
            if source_root is None:
                source_root = resolve_checkout(upstream_id, upstream, overrides, temp_dirs)
                checkouts[upstream_id] = source_root
                checkout_refs[upstream_id] = checkout_ref(source_root, upstream)

            source = source_root / entry["upstream_path"]
            ensure_within_root(source, source_root, allow_root=True)
            target = staging_root / entry["category"] / entry["name"]
            copy_skill(
                source,
                target,
                force=False,
                exclude_patterns=entry.get("exclude"),
                allowed_root=staging_root,
            )
            if entry.get("rewrite_frontmatter_name") is True:
                rewrite_frontmatter_name(target, entry["name"])
            if isinstance(entry.get("rewrite_invocations"), dict):
                rewrite_invocations(target, entry["rewrite_invocations"])
            if isinstance(entry.get("rewrite_text"), list):
                rewrite_text(target, entry["rewrite_text"])
            copy_upstream_license(source_root, target, upstream)
            write_attribution(target, entry, upstream, checkout_refs[upstream_id])

        for entry in entries:
            staged = staging_root / entry["category"] / entry["name"]
            target = dest_root / entry["category"] / entry["name"]
            copy_skill(staged, target, args.force, allowed_root=dest_root)
            print(f"synced {entry['name']} -> {target}")
    finally:
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                remove_tree(temp_dir, Path(tempfile.gettempdir()))

    return 0


if __name__ == "__main__":
    sys.exit(main())
