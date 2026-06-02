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
    / "capability_recon_result_validator.py"
)


VALID_RESULT = """\
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

MULTILINE_RESULT = """\
CAPABILITY_RECON_RESULT:
capability_id: playback_transcode_depth
classification: recon_candidate
status: NEEDS_WORKSTREAM
evidence:
  - docs/architecture/PLAYBACK.md: playback/transcode is a dedicated capability map.
  - docs/architecture/LANES.md: current active queue is unrelated.
guardrail_assessment: stayed read-only and did not propose runtime or API changes
missing_artifacts:
  - architecture map
  - workstream
owned_scope: playback/transcode planning docs
shared_scope: Public Client API, generated client, Admin diagnostics
product_decisions: choose the first next-depth slice
implementation_allowed: false
blocked_by_active_queue: none
suggested_next_artifact: playback-transcode-depth workstream draft
"""


def run_validator(text: str) -> subprocess.CompletedProcess[str]:
    repo = ROOT / "repo-ref" / "nako"
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--format", "json"],
        cwd=ROOT,
        input=text,
        text=True,
        capture_output=True,
        check=False,
    )


class CapabilityReconResultValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        if not (ROOT / "repo-ref" / "nako").exists():
            self.skipTest("repo-ref/nako is not available")

    def test_accepts_valid_recon_result(self) -> None:
        result = run_validator(VALID_RESULT)
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["result_count"], 1)
        self.assertEqual(payload["results"][0]["capability_id"], "playback_transcode_depth")

    def test_accepts_multiline_fields_with_colons(self) -> None:
        result = run_validator(MULTILINE_RESULT)
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["results"][0]["status"], "NEEDS_WORKSTREAM")

    def test_rejects_missing_required_field(self) -> None:
        invalid = VALID_RESULT.replace("suggested_next_artifact: playback-transcode-depth workstream draft\n", "")
        result = run_validator(invalid)
        payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(payload["valid"])
        self.assertIn("missing required field `suggested_next_artifact`", payload["errors"])

    def test_rejects_recon_result_that_allows_implementation(self) -> None:
        invalid = VALID_RESULT.replace("implementation_allowed: false", "implementation_allowed: true")
        result = run_validator(invalid)
        payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(payload["valid"])
        self.assertIn("RECON result must not allow implementation directly", payload["errors"])

    def test_rejects_unknown_capability_id(self) -> None:
        invalid = VALID_RESULT.replace("capability_id: playback_transcode_depth", "capability_id: magic_lane")
        result = run_validator(invalid)
        payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(payload["valid"])
        self.assertIn("unknown capability_id `magic_lane`", payload["errors"])


if __name__ == "__main__":
    unittest.main()
