import json
import shutil
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
    / "plan-engineering-program"
    / "scripts"
    / "workflow_scale.py"
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_scale(repo: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def write_workstream(root: Path, slug: str, status: str) -> None:
    ws = root / "docs" / "workstreams" / slug
    write(
        ws / "WORKSTREAM.json",
        json.dumps({"slug": slug, "status": status, "current_task": f"{slug.upper()}-010"}),
    )
    write(ws / "TODO.md", f"- [ ] {slug.upper()}-010\n")


class WorkflowScaleTests(unittest.TestCase):
    def test_direct_when_no_workstream_or_lane_substrate_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "README.md", "# Small Repo\n")

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "direct")
            self.assertEqual(payload["counts"]["workstreams"], 0)

    def test_direct_when_domain_docs_exist_without_workflow_substrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "README.md", "# Medium Repo\n")
            write(root / "AGENTS.md", "# Agent Notes\n")
            write(root / "CONTEXT.md", "# Domain Context\n")
            write(root / "docs" / "architecture" / "OVERVIEW.md", "# Architecture\n")

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "direct")
            self.assertIn("direct edit", " ".join(payload["recommended_surface"]))

    def test_workstream_when_single_workstream_substrate_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workstream(root, "alpha", "active")

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "workstream")
            self.assertEqual(payload["counts"]["active_or_draft_workstreams"], 1)

    def test_real_repo_with_middle_state_overlay_stays_workstream(self) -> None:
        source = ROOT / "repo-ref" / "skills"
        if not source.exists():
            self.skipTest("repo-ref/skills is not available")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            shutil.copytree(source, root, ignore=shutil.ignore_patterns(".git"))
            write_workstream(root, "middle-state-routing", "active")

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "workstream")
            self.assertEqual(payload["counts"]["workstreams"], 1)
            self.assertEqual(payload["counts"]["campaign_files"], 0)
            self.assertFalse(payload["signals"]["has_lanes"])
            self.assertFalse(payload["signals"]["has_workstream_links"])

    def test_program_when_lanes_and_campaigns_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "docs" / "architecture" / "LANES.md", "# Lanes\n")
            write(root / "docs" / "architecture" / "WORKSTREAM_LINKS.md", "# Links\n")
            write_workstream(root, "alpha", "active")
            write(
                root / "docs" / "workstreams" / "alpha" / "CAMPAIGNS.jsonl",
                json.dumps(
                    {
                        "campaign_id": "alpha-001",
                        "status": "approved",
                        "approved_by_user": True,
                    }
                )
                + "\n",
            )

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "program")
            self.assertTrue(payload["signals"]["has_lanes"])
            self.assertEqual(payload["counts"]["approved_or_running_campaigns"], 1)

    def test_lane_when_links_exist_without_ready_active_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "docs" / "architecture" / "LANES.md", "# Lanes\n")
            write(root / "docs" / "architecture" / "WORKSTREAM_LINKS.md", "# Links\n")
            write_workstream(root, "alpha", "active")

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "lane")
            self.assertEqual(payload["counts"]["ready_active_workstreams"], 0)

    def test_lane_when_campaign_file_is_unapproved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "docs" / "architecture" / "LANES.md", "# Lanes\n")
            write_workstream(root, "alpha", "active")
            write(
                root / "docs" / "workstreams" / "alpha" / "CAMPAIGNS.jsonl",
                json.dumps(
                    {
                        "campaign_id": "alpha-001",
                        "status": "draft",
                        "approved_by_user": False,
                    }
                )
                + "\n",
            )

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "lane")
            self.assertEqual(payload["counts"]["approved_or_running_campaigns"], 0)

    def test_audit_repair_when_only_historical_workstreams_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(20):
                write_workstream(root, f"closed-{index}", "closed")

            payload = run_scale(root)

            self.assertEqual(payload["preset"], "audit-repair")
            self.assertEqual(payload["counts"]["active_or_draft_workstreams"], 0)
            self.assertIn("direct task can still downshift", " ".join(payload["recommended_surface"]))


if __name__ == "__main__":
    unittest.main()
