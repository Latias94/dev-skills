#!/usr/bin/env python3
"""Install dev-skills into Codex's skills directory."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
import shutil
import stat
import subprocess
import sys
from pathlib import Path


CE_MARKETPLACE = "compound-engineering-plugin"
CE_MARKETPLACE_SOURCE = "EveryInc/compound-engineering-plugin"
CE_PLUGIN = "compound-engineering"
CE_PLUGIN_SELECTOR = f"{CE_PLUGIN}@{CE_MARKETPLACE}"
CE_UPSTREAM_PLUGIN_JSON = (
    "https://raw.githubusercontent.com/EveryInc/compound-engineering-plugin/"
    "main/plugins/compound-engineering/.codex-plugin/plugin.json"
)
PROTECTED_REMOVE_NAMES = {CE_PLUGIN, CE_MARKETPLACE}


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
    if name in PROTECTED_REMOVE_NAMES:
        return {"skill": name, "status": "protected", "destination": str(dest_root / name)}

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


def run_checked(command: list[str]) -> None:
    executable = shutil.which(command[0])
    if executable is None:
        raise FileNotFoundError(
            f"Required command not found: {command[0]}. "
            "Install it first or run the Compound Engineering install manually."
        )

    subprocess.run([executable, *command[1:]], check=True)


def run_capture(command: list[str]) -> str:
    executable = shutil.which(command[0])
    if executable is None:
        raise FileNotFoundError(f"Required command not found: {command[0]}")

    result = subprocess.run(
        [executable, *command[1:]],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def load_upstream_ce_version() -> str | None:
    try:
        with urllib.request.urlopen(CE_UPSTREAM_PLUGIN_JSON, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None

    version = data.get("version")
    return str(version) if version else None


def load_installed_ce_info() -> dict[str, object] | None:
    try:
        data = json.loads(run_capture(["codex", "plugin", "list", "--json"]))
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        data = {}

    installed = data.get("installed") if isinstance(data, dict) else None
    if isinstance(installed, list):
        for plugin in installed:
            if not isinstance(plugin, dict):
                continue
            if plugin.get("name") == CE_PLUGIN or plugin.get("pluginId") == CE_PLUGIN_SELECTOR:
                return plugin

    cache_root = Path.home() / ".codex" / "plugins" / "cache" / CE_MARKETPLACE / CE_PLUGIN
    if not cache_root.exists():
        return None

    versions = sorted(cache_root.iterdir(), key=lambda path: path.name, reverse=True)
    for version_dir in versions:
        plugin_json = version_dir / ".codex-plugin" / "plugin.json"
        if not plugin_json.exists():
            continue
        try:
            data = json.loads(plugin_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        return {
            "pluginId": CE_PLUGIN_SELECTOR,
            "name": CE_PLUGIN,
            "marketplaceName": CE_MARKETPLACE,
            "version": data.get("version", version_dir.name),
            "enabled": None,
            "source": {"source": "cache", "path": str(version_dir)},
        }

    return None


def print_compound_engineering_status() -> None:
    installed = load_installed_ce_info()
    upstream = load_upstream_ce_version()

    print("\nCompound Engineering status:")
    if installed is None:
        print("- Installed: no")
    else:
        print("- Installed: yes")
        print(f"- Plugin: {installed.get('pluginId', CE_PLUGIN_SELECTOR)}")
        print(f"- Version: {installed.get('version', 'unknown')}")
        print(f"- Enabled: {installed.get('enabled', 'unknown')}")

    print(f"- Upstream version: {upstream or 'unknown'}")

    current = str(installed.get("version")) if installed and installed.get("version") else None
    if current and upstream:
        status = "up to date" if current == upstream else "update available"
        print(f"- Status: {status}")
    elif upstream is None:
        print("- Status: could not fetch upstream version")


def install_or_update_compound_engineering(update: bool) -> None:
    action = "Updating" if update else "Installing"
    print(f"\n{action} Compound Engineering external workflow:")

    if update:
        try:
            run_checked(["codex", "plugin", "marketplace", "upgrade", CE_MARKETPLACE])
        except subprocess.CalledProcessError:
            print("Marketplace upgrade failed; continuing with marketplace add/install.")

    run_checked(["codex", "plugin", "marketplace", "add", CE_MARKETPLACE_SOURCE])
    run_checked(["codex", "plugin", "add", CE_PLUGIN_SELECTOR])
    run_checked([
        "bunx",
        "-p",
        "@every-env/compound-plugin",
        "compound-plugin",
        "install",
        "compound-engineering",
        "--to",
        "codex",
    ])
    print_compound_engineering_status()
    print(
        "\nCompound Engineering marketplace, Codex plugin, and companion agents are installed. "
        "Restart Codex to apply plugin changes."
    )


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
    parser.add_argument(
        "--install-compound-engineering",
        "--install-ce",
        action="store_true",
        help="Also install the external Compound Engineering Codex marketplace and agent set",
    )
    parser.add_argument(
        "--update-compound-engineering",
        "--update-ce",
        action="store_true",
        help="Refresh the Compound Engineering marketplace snapshot, Codex plugin, and agent set",
    )
    parser.add_argument(
        "--check-compound-engineering",
        "--check-ce",
        action="store_true",
        help="Print installed and upstream Compound Engineering versions",
    )
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="Install managed skills only and skip Compound Engineering actions",
    )
    parser.add_argument(
        "--ce-only",
        action="store_true",
        help="Run Compound Engineering actions only and skip managed skill installation/removal",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing destination skills")
    args = parser.parse_args()

    ce_requested = (
        args.install_compound_engineering
        or args.update_compound_engineering
        or args.check_compound_engineering
    )
    if args.skills_only and args.ce_only:
        parser.error("--skills-only and --ce-only cannot be used together")
    if args.skills_only and ce_requested:
        parser.error("--skills-only cannot be combined with Compound Engineering actions")

    install_skills = not args.ce_only
    if ce_requested and not args.force:
        install_skills = False

    repo_root = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo_root / "skills.json").read_text(encoding="utf-8"))

    results: list[dict[str, str]] = []

    if install_skills:
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

    if args.check_compound_engineering:
        print_compound_engineering_status()
    if args.update_compound_engineering:
        install_or_update_compound_engineering(update=True)
    if args.install_compound_engineering:
        install_or_update_compound_engineering(update=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
