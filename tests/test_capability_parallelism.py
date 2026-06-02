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
    / "plan-engineering-program"
    / "scripts"
    / "capability_parallelism.py"
)


def run_script(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--format", "json", *extra],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_repo() -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "docs" / "workstreams").mkdir(parents=True)
    write(root / "CONTEXT.md", "# Context\n")
    return tmp


class CapabilityParallelismTests(unittest.TestCase):
    def test_detects_product_recon_candidates_separate_from_ready_unit(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            write(
                root / "README.md",
                "\n".join(
                    [
                        "# Example",
                        "Network tunnel support, reverse proxy, NAT traversal, and relay are future remote access concerns.",
                        "Playback, transcode, WebDAV, library scan, Android, Addon, sharing, backup, and observability are future product areas.",
                    ]
                ),
            )
            ws = root / "docs" / "workstreams" / "generated-artifact-bulk-metadata-apply"
            write(
                ws / "WORKSTREAM.json",
                json.dumps(
                    {
                        "slug": "generated-artifact-bulk-metadata-apply",
                        "status": "active",
                        "current_task": "GABMA-020",
                    },
                    indent=2,
                ),
            )
            write(ws / "TODO.md", "- [ ] GABMA-020\n")
            write(ws / "EVIDENCE_AND_GATES.md", "# Gates\n")
            write(ws / "HANDOFF.md", "# Handoff\n")
            write(
                ws / "TASKS.jsonl",
                json.dumps(
                    {
                        "task_id": "GABMA-020",
                        "status": "todo",
                        "owner": "codex",
                        "deps": [],
                        "scope": ["crates/example"],
                        "validation": ["cargo nextest run -p example"],
                        "context": ["CONTEXT.md"],
                        "evidence": [],
                    }
                )
                + "\n",
            )
            write(
                ws / "CAMPAIGNS.jsonl",
                json.dumps(
                    {
                        "campaign_id": "GABMA-20260601-01",
                        "status": "approved",
                        "lane_slug": "metadata",
                        "ordered_tasks": ["GABMA-020"],
                        "gates": ["cargo nextest run -p example"],
                        "side_effect_policy": "manual",
                        "stop_conditions": ["failed gate"],
                        "approved_by_user": True,
                    }
                )
                + "\n",
            )
            write(ws / "CONTEXT.jsonl", json.dumps({"path": "CONTEXT.md", "required": True}) + "\n")

            result = run_script(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(payload["implementation_horizon"], 1)
            self.assertTrue(payload["profile_family"]["detected"])
            self.assertGreaterEqual(payload["product_recon_horizon"], 5)
            self.assertEqual(payload["ready_active_unit"]["task"], "GABMA-020")
            self.assertGreater(len(payload["capability_parallelism"]["blocked_by_active_queue"]), 0)
            self.assertEqual(
                payload["recon_result_contract"]["result_marker"],
                "CAPABILITY_RECON_RESULT:",
            )
            self.assertIn(
                "implementation_allowed",
                payload["recon_result_contract"]["required_fields"],
            )
            decision_ids = {
                row["id"] for row in payload["capability_parallelism"]["product_decision_required"]
            }
            self.assertIn("remote_access_nat_relay", decision_ids)
            for group in (
                "recon_candidates",
                "product_decision_required",
                "needs_workstream",
            ):
                for row in payload["capability_parallelism"][group]:
                    self.assertTrue(row["guardrail"])
                    self.assertTrue(row["missing_artifacts"])

    def test_real_nako_detects_multiple_product_candidates(self) -> None:
        repo = ROOT / "repo-ref" / "nako"
        if not repo.exists():
            self.skipTest("repo-ref/nako is not available")

        result = run_script(repo)
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(payload["ready_active_unit"]["task"], "GABMA-020")
        self.assertTrue(payload["profile_family"]["detected"])
        self.assertGreaterEqual(payload["product_recon_horizon"], 6)
        candidate_ids = {
            row["id"]
            for group in (
                "recon_candidates",
                "product_decision_required",
                "needs_workstream",
            )
            for row in payload["capability_parallelism"][group]
        }
        self.assertIn("remote_access_nat_relay", candidate_ids)
        self.assertIn("playback_transcode_depth", candidate_ids)
        self.assertIn("addons_ecosystem", candidate_ids)
        self.assertIn(
            "guardrail_assessment",
            payload["recon_result_contract"]["required_fields"],
        )
        for group in (
            "recon_candidates",
            "product_decision_required",
            "needs_workstream",
        ):
            for row in payload["capability_parallelism"][group]:
                self.assertIn("guardrail", row)
                self.assertGreater(len(row["guardrail"]), 20)

    def test_generic_sdk_language_does_not_trigger_capability_profiles(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            write(
                root / "README.md",
                "\n".join(
                    [
                        "# Generic SDK",
                        "The client SDK uses auth sessions, redaction, diagnostics, and storage for agent transcripts.",
                        "These words are not enough to infer media-server product capabilities.",
                    ]
                ),
            )

            result = run_script(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertFalse(payload["profile_family"]["detected"])
            self.assertEqual(payload["product_recon_horizon"], 0)


if __name__ == "__main__":
    unittest.main()
