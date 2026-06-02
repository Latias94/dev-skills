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
    / "live_experiment_packet.py"
)


def run_packet(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), name, "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class LiveExperimentPacketTests(unittest.TestCase):
    def test_hajimi_refusal_packet_stays_planner_only(self) -> None:
        result = run_packet("hajimi_refusal")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["recommended_route"]["skill"], "plan-engineering-program")
        self.assertEqual(payload["program_action"]["operating_mode"], "AUDIT")
        self.assertEqual(payload["chain_state"], "planner_only")
        self.assertIn("<user-request>", payload["wrapped_prompt"])
        self.assertEqual(payload["worker_prompt"], "")

    def test_nako_chain_packet_exposes_full_chain(self) -> None:
        result = run_packet("nako_chain")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["recommended_route"]["skill"], "run-workstream-task")
        self.assertEqual(payload["program_action"]["operating_mode"], "READINESS")
        self.assertEqual(payload["chain_state"], "execution_chain_ready")
        self.assertIn("WORKSTREAM_RESULT:", payload["worker_prompt"])
        self.assertIn("REVIEW_RESULT:", payload["review_prompt"])
        self.assertIn("VERIFY_RESULT:", payload["verify_prompt"])
        self.assertIn("INTEGRATION_RESULT:", payload["integrate_prompt"])

    def test_skills_restraint_packet_stays_light(self) -> None:
        result = run_packet("skills_restraint")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertIn(payload["recommended_route"]["skill"], {"tdd", "audit-project-scale"})
        self.assertIn("<user-request>", payload["wrapped_prompt"])


if __name__ == "__main__":
    unittest.main()
