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
    / "capability_recon_roundtrip.py"
)


def run_roundtrip(*args: str) -> subprocess.CompletedProcess[str]:
    repo = ROOT / "repo-ref" / "nako"
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--format", "json", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class CapabilityReconRoundtripTests(unittest.TestCase):
    def setUp(self) -> None:
        if not (ROOT / "repo-ref" / "nako").exists():
            self.skipTest("repo-ref/nako is not available")

    def test_roundtrip_keeps_recon_results_from_promoting_implementation(self) -> None:
        result = run_roundtrip(
            "--candidate",
            "playback_transcode_depth",
            "--candidate",
            "remote_access_nat_relay",
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(payload["roundtrip_valid"])
        self.assertEqual(payload["packet_count"], 2)
        self.assertFalse(payload["promotion_allowed"])
        self.assertEqual(payload["ready_active_unit"]["task"], "GABMA-020")
        self.assertEqual(payload["integration"]["accepted_result_count"], 2)
        self.assertEqual(payload["integration"]["rejected_result_count"], 0)
        self.assertIn("CAPABILITY_RECON_RESULT:", payload["synthetic_results"])

    def test_roundtrip_rejects_unknown_candidate(self) -> None:
        result = run_roundtrip("--candidate", "missing_lane")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown capability candidate", result.stderr)


if __name__ == "__main__":
    unittest.main()
