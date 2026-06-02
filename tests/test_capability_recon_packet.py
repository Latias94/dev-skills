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
    / "capability_recon_packet.py"
)


def run_packet(*args: str) -> subprocess.CompletedProcess[str]:
    repo = ROOT / "repo-ref" / "nako"
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--format", "json", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class CapabilityReconPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        if not (ROOT / "repo-ref" / "nako").exists():
            self.skipTest("repo-ref/nako is not available")

    def test_builds_single_candidate_prompt_with_runtime_guardrails(self) -> None:
        result = run_packet("--candidate", "remote_access_nat_relay")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(len(payload["packets"]), 1)
        packet = payload["packets"][0]
        prompt = packet["prompt"]

        self.assertEqual(packet["capability_id"], "remote_access_nat_relay")
        self.assertIn("CAPABILITY_RECON_RESULT:", prompt)
        self.assertIn("implementation_allowed: false", prompt)
        self.assertIn("GABMA-020", prompt)
        self.assertIn("Do not edit files", prompt)
        self.assertIn("guardrail", prompt)
        self.assertIn("built-in relay", prompt)
        self.assertGreater(len(payload["blocked_by_active_queue"]), 0)

    def test_default_packet_includes_all_runtime_candidates(self) -> None:
        result = run_packet()
        payload = json.loads(result.stdout)
        candidate_ids = {row["capability_id"] for row in payload["packets"]}

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertGreaterEqual(len(candidate_ids), 6)
        self.assertIn("playback_transcode_depth", candidate_ids)
        self.assertIn("storage_vfs_webdav", candidate_ids)
        self.assertIn("clients_surfaces", candidate_ids)
        self.assertEqual(
            payload["result_contract"]["result_marker"],
            "CAPABILITY_RECON_RESULT:",
        )

    def test_rejects_unknown_candidate_id(self) -> None:
        result = run_packet("--candidate", "missing_lane")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown capability candidate", result.stderr)

    def test_capability_id_alias_is_supported(self) -> None:
        result = run_packet("--capability-id", "remote_access_nat_relay")
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(len(payload["packets"]), 1)
        self.assertEqual(payload["packets"][0]["capability_id"], "remote_access_nat_relay")


if __name__ == "__main__":
    unittest.main()
