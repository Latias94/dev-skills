import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "engineering"
    / "migrate-to-trellis"
    / "scripts"
    / "audit_trellis_migration.py"
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_audit(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class MigrateToTrellisTests(unittest.TestCase):
    def test_classifies_architecture_and_workstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "AGENTS.md", "# Rules\n")
            write(root / "CONTEXT.md", "# Context\n")
            write(root / "docs" / "README.md", "Old entrypoint: use $dev-flow and WORKSTREAM.json\n")
            write(root / "docs" / "adr" / "0001-boundary.md", "# ADR\n")
            write(root / "docs" / "architecture" / "LANES.md", "# Lanes\n")
            active = root / "docs" / "workstreams" / "active-feature"
            write(active / "WORKSTREAM.json", json.dumps({"status": "active"}))
            write(active / "DESIGN.md", "# Active design\n")
            closed = root / "docs" / "workstreams" / "old-feature"
            write(closed / "WORKSTREAM.json", json.dumps({"status": "completed"}))
            write(closed / "HANDOFF.md", "# Old handoff\n")

            result = run_audit(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertFalse(payload["trellis_installed"])
            self.assertIn("keep_architecture_knowledge", payload["counts"])
            self.assertIn("distill_to_trellis_spec", payload["counts"])
            self.assertGreaterEqual(payload["legacy_reference_count"], 2)
            self.assertEqual(payload["current_workstreams"][0]["slug"], "active-feature")
            self.assertEqual(payload["stale_workstreams"][0]["slug"], "old-feature")
            rows = {row["path"]: row["category"] for row in payload["rows"]}
            self.assertEqual(rows["docs/adr/0001-boundary.md"], "keep_architecture_knowledge")
            self.assertEqual(
                rows["docs/workstreams/active-feature/WORKSTREAM.json"],
                "convert_current_workstream",
            )
            self.assertEqual(
                rows["docs/workstreams/old-feature/HANDOFF.md"],
                "retire_legacy_workstream",
            )
            references = {(row["path"], row["pattern"]) for row in payload["legacy_references"]}
            self.assertIn(("docs/README.md", "dev-flow"), references)
            self.assertIn(("docs/README.md", "WORKSTREAM.json"), references)


if __name__ == "__main__":
    unittest.main()
