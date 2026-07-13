from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import install_dev_skills, sync_upstream_skills, validate_skills


class ScriptModuleEntryPointTests(unittest.TestCase):
    def test_installer_module_entry_point_is_available(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-m", "scripts.install_dev_skills", "--help"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Install dev-skills for Codex.", result.stdout)


class UpstreamCheckoutResolutionTests(unittest.TestCase):
    def test_current_clean_local_hint_is_reused(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp = Path(raw_temp)
            local_checkout = temp / "local"
            local_checkout.mkdir()
            upstream = {
                "repo_url": "https://example.com/upstream.git",
                "default_ref": "main",
                "local_checkout_hint": str(local_checkout),
            }

            with mock.patch.object(
                sync_upstream_skills,
                "run",
                side_effect=["", "abc123", "abc123\trefs/heads/main"],
            ) as run_mock:
                resolved = sync_upstream_skills.resolve_checkout("example", upstream, {}, [])

            self.assertEqual(resolved, local_checkout.resolve())
            self.assertEqual(run_mock.call_count, 3)

    def test_stale_local_hint_falls_back_to_a_fresh_clone(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp = Path(raw_temp)
            local_checkout = temp / "local"
            clone_checkout = temp / "fresh"
            local_checkout.mkdir()
            upstream = {
                "repo_url": "https://example.com/upstream.git",
                "default_ref": "main",
                "local_checkout_hint": str(local_checkout),
            }
            temp_dirs: list[Path] = []

            with (
                mock.patch.object(
                    sync_upstream_skills,
                    "run",
                    side_effect=["", "old123", "new456\trefs/heads/main", ""],
                ) as run_mock,
                mock.patch.object(
                    sync_upstream_skills.tempfile,
                    "mkdtemp",
                    return_value=str(clone_checkout),
                ),
            ):
                resolved = sync_upstream_skills.resolve_checkout(
                    "example",
                    upstream,
                    {},
                    temp_dirs,
                )

            self.assertEqual(resolved, clone_checkout)
            self.assertEqual(temp_dirs, [clone_checkout])
            self.assertEqual(run_mock.call_args_list[-1].args[0][0:2], ["git", "clone"])


class UpstreamSkillCopyTests(unittest.TestCase):
    def test_manifest_exclusions_are_not_copied(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp = Path(raw_temp)
            source = temp / "source"
            target = temp / "target"
            source.mkdir()
            (source / "SKILL.md").write_text("skill\n", encoding="utf-8")
            (source / "README.md").write_text("upstream docs\n", encoding="utf-8")
            (source / ".DS_Store").write_bytes(b"metadata")

            sync_upstream_skills.copy_skill(
                source,
                target,
                force=False,
                exclude_patterns=["README.md", ".DS_Store"],
            )

            self.assertTrue((target / "SKILL.md").exists())
            self.assertFalse((target / "README.md").exists())
            self.assertFalse((target / ".DS_Store").exists())


class ManifestPathSafetyTests(unittest.TestCase):
    def test_upstream_entry_rejects_path_segments(self) -> None:
        entry = {
            "name": "../outside",
            "category": "engineering",
            "upstream": "example",
            "upstream_path": "skills/example",
        }
        upstreams = {
            "example": {
                "repo_url": "https://example.com/upstream.git",
                "license": "MIT",
                "license_url": "https://example.com/license",
            }
        }

        with self.assertRaisesRegex(ValueError, "name"):
            sync_upstream_skills.validate_entry(entry, upstreams)

    def test_install_plan_rejects_path_segments(self) -> None:
        manifest = {
            "local": {"core": ["safe-skill"]},
            "remove": {"skills": ["../outside"]},
        }

        with self.assertRaisesRegex(ValueError, "skill name"):
            install_dev_skills.install_plan(manifest, False, False)


class InstallerPlanTests(unittest.TestCase):
    def test_unbundled_skills_are_not_scheduled_for_removal(self) -> None:
        manifest = {"local": {"core": ["bundled-skill"]}}

        selected, obsolete = install_dev_skills.install_plan(manifest, False, False)

        self.assertEqual(selected, ["bundled-skill"])
        self.assertEqual(obsolete, [])


class TransactionalUpstreamSyncTests(unittest.TestCase):
    def test_failed_rewrite_does_not_replace_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp = Path(raw_temp)
            source_root = temp / "source"
            source_skill = source_root / "skill"
            destination_root = temp / "destination"
            destination_skill = destination_root / "engineering" / "demo"
            source_skill.mkdir(parents=True)
            destination_skill.mkdir(parents=True)
            (source_skill / "SKILL.md").write_text("new\n", encoding="utf-8")
            (destination_skill / "SKILL.md").write_text("old\n", encoding="utf-8")
            manifest_path = temp / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "upstreams": {
                            "example": {
                                "repo_url": "https://example.com/upstream.git",
                                "default_ref": "main",
                                "license": "MIT",
                                "license_url": "https://example.com/license",
                            }
                        },
                        "skills": [
                            {
                                "name": "demo",
                                "category": "engineering",
                                "upstream": "example",
                                "upstream_path": "skill",
                                "rewrite_text": [
                                    {
                                        "path": "SKILL.md",
                                        "from": "missing upstream text",
                                        "to": "replacement",
                                    }
                                ],
                                "sync": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            arguments = [
                "sync_upstream_skills.py",
                "--manifest",
                str(manifest_path),
                "--skill",
                "demo",
                "--write",
                "--force",
                "--dest-root",
                str(destination_root),
                "--source",
                f"example={source_root}",
            ]

            with (
                mock.patch.object(sys, "argv", arguments),
                self.assertRaisesRegex(ValueError, "rewrite did not match"),
            ):
                sync_upstream_skills.main()

            self.assertEqual(
                (destination_skill / "SKILL.md").read_text(encoding="utf-8"),
                "old\n",
            )


class SkillValidationTests(unittest.TestCase):
    def test_unmanaged_source_file_does_not_bypass_local_rules(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            skill_dir = Path(raw_temp) / "misc" / "adapted-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: adapted-skill\n"
                "description: Use when adapted prose must be checked.\n"
                "---\n"
                "\n# Adapted Skill\n",
                encoding="utf-8",
            )
            (skill_dir / "SOURCE.md").write_text("adapted upstream\n", encoding="utf-8")

            _row, errors = validate_skills.validate_skill(skill_dir, {})

            self.assertIn("missing concrete example", errors)
            self.assertIn("missing agents/openai.yaml", errors)


class InstallerFilteringTests(unittest.TestCase):
    def test_install_does_not_copy_python_caches(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp = Path(raw_temp)
            source = temp / "source"
            cache = source / "scripts" / "__pycache__"
            destination_root = temp / "destination"
            cache.mkdir(parents=True)
            (source / "SKILL.md").write_text("skill\n", encoding="utf-8")
            (cache / "helper.pyc").write_bytes(b"cache")

            install_dev_skills.copy_skill("demo", source, destination_root, force=False)

            self.assertTrue((destination_root / "demo" / "SKILL.md").exists())
            self.assertFalse((destination_root / "demo" / "scripts" / "__pycache__").exists())


@unittest.skipIf(os.name == "nt", "POSIX permission semantics are required")
class ReadOnlyTreeRemovalTests(unittest.TestCase):
    def test_installer_removes_inaccessible_extra_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp = Path(raw_temp)
            source = temp / "source"
            target = temp / "target"
            stale = target / "__pycache__"
            source.mkdir()
            stale.mkdir(parents=True)
            (source / "SKILL.md").write_text("source\n", encoding="utf-8")
            (target / "SKILL.md").write_text("source\n", encoding="utf-8")
            (stale / "cache.pyc").write_bytes(b"stale")
            stale.chmod(stat.S_IWUSR)

            try:
                copied, removed = install_dev_skills.sync_tree(source, target)
            finally:
                if stale.exists():
                    stale.chmod(stat.S_IRWXU)

            self.assertEqual(copied, 0)
            self.assertGreaterEqual(removed, 1)
            self.assertFalse(stale.exists())

    def test_upstream_sync_replaces_inaccessible_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            temp = Path(raw_temp)
            source = temp / "source"
            target = temp / "target"
            source.mkdir()
            target.mkdir()
            (source / "SKILL.md").write_text("new\n", encoding="utf-8")
            (target / "SKILL.md").write_text("old\n", encoding="utf-8")
            target.chmod(stat.S_IWUSR)

            try:
                sync_upstream_skills.copy_skill(
                    source,
                    target,
                    force=True,
                    allowed_root=temp,
                )
            finally:
                if target.exists():
                    target.chmod(stat.S_IRWXU)

            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "new\n")


if __name__ == "__main__":
    unittest.main()
