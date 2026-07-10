from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path

from scripts import install_dev_skills, sync_upstream_skills


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
                sync_upstream_skills.copy_skill(source, target, force=True)
            finally:
                if target.exists():
                    target.chmod(stat.S_IRWXU)

            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "new\n")


if __name__ == "__main__":
    unittest.main()
