import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "engineering"
    / "plan-engineering-program"
    / "scripts"
    / "planner.py"
)


def run_planner(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_planner_with_input(text: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        input=text,
        text=True,
        capture_output=True,
        check=False,
    )


VALID_RECON_RESULT = """\
CAPABILITY_RECON_RESULT:
capability_id: playback_transcode_depth
classification: recon_candidate
status: RECON_DONE
evidence: docs/architecture/PLAYBACK.md, docs/architecture/LANES.md
guardrail_assessment: stayed read-only and did not propose runtime or API changes
missing_artifacts: architecture map, workstream, device/profile gates, FFmpeg/hardware smoke
owned_scope: playback/transcode planning docs
shared_scope: Public Client API, generated client, Admin diagnostics
product_decisions: none
implementation_allowed: false
blocked_by_active_queue: none
suggested_next_artifact: playback-transcode-depth workstream draft
"""


class PlannerCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.nako = ROOT / "repo-ref" / "nako"
        self.hajimi = ROOT / "repo-ref" / "hajimi"
        if not self.nako.exists():
            self.skipTest("repo-ref/nako is not available")

    def test_status_subcommand_exposes_program_action(self) -> None:
        result = run_planner("status", str(self.nako), "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("program_action", payload)
        self.assertEqual(payload["active_unit"]["task"], "GABMA-020")

    def test_top_level_help_keeps_advanced_details_collapsed(self) -> None:
        result = run_planner("--help")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("advanced", result.stdout)
        self.assertNotIn("hook-payload", result.stdout)
        self.assertNotIn("validate-result", result.stdout)

    def test_advanced_help_exposes_advanced_helpers_only_on_demand(self) -> None:
        result = run_planner("advanced", "--help")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("prelude", result.stdout)
        self.assertIn("hook-payload", result.stdout)
        self.assertIn("validate-result", result.stdout)

    def test_scale_subcommand_exposes_workflow_preset(self) -> None:
        result = run_planner("scale", str(self.nako), "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(payload["preset"], {"direct", "workstream", "lane", "program", "audit-repair"})
        self.assertIn("recommended_surface", payload)

    def test_dispatch_subcommand_exposes_product_parallelism(self) -> None:
        result = run_planner("dispatch", str(self.nako), "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(payload["recommended_route"]["skill"], "run-workstream-task")
        self.assertEqual(payload["product_parallelism"]["product_recon_horizon"], 8)

    def test_capability_subcommand_respects_profile_family_gating(self) -> None:
        if not self.hajimi.exists():
            self.skipTest("repo-ref/hajimi is not available")

        result = run_planner("capability", str(self.hajimi), "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse(payload["profile_family"]["detected"])
        self.assertEqual(payload["product_recon_horizon"], 0)

    def test_recon_packet_subcommand_accepts_candidate(self) -> None:
        result = run_planner(
            "recon-packet",
            str(self.nako),
            "--candidate",
            "remote_access_nat_relay",
            "--format",
            "json",
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(len(payload["packets"]), 1)
        self.assertEqual(payload["packets"][0]["capability_id"], "remote_access_nat_relay")

    def test_chain_subcommand_exposes_handoff_state(self) -> None:
        result = run_planner("chain", str(self.nako), "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(payload["chain_state"], "execution_chain_ready")
        self.assertIn("planner_prompt", payload)
        self.assertIn("integrate_prompt", payload)

    def test_advanced_prelude_wraps_turn_prelude_helper(self) -> None:
        result = run_planner("advanced", "prelude", str(self.nako), "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(payload["recommended_route"]["skill"], "run-workstream-task")
        self.assertIn("<planner-turn-guidance>", payload["prelude"])

    def test_advanced_hook_payload_wraps_injection_helper(self) -> None:
        result = run_planner("advanced", "hook-payload", str(self.nako), "--debug")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("hookSpecificOutput", payload)
        self.assertIn("debug", payload)
        self.assertIn("<planner-runtime>", payload["hookSpecificOutput"]["additionalContext"])

    def test_advanced_validate_result_wraps_recon_validator(self) -> None:
        result = run_planner_with_input(
            VALID_RECON_RESULT,
            "advanced",
            "validate-result",
            str(self.nako),
            "--format",
            "json",
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["result_count"], 1)


if __name__ == "__main__":
    unittest.main()
