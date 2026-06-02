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
    / "capability_recon_result_integrator.py"
)


PLAYBACK_RESULT = """\
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


REMOTE_ACCESS_RESULT = """\
CAPABILITY_RECON_RESULT:
capability_id: remote_access_nat_relay
classification: product_decision_required
status: NEEDS_PRODUCT_DECISION
evidence: docs/architecture/CONTROL_PLANE.md, docs/architecture/OPERATIONS_RELEASE.md
guardrail_assessment: separated cookbook, endpoint discovery, and built-in relay decisions
missing_artifacts: product/security ADR, threat model, abuse/cost model, workstream, redaction gates
owned_scope: deployment cookbook and diagnostics planning
shared_scope: Admin diagnostics, Public Client endpoint discovery, security model
product_decisions: built-in relay ownership, abuse model, cost model
implementation_allowed: false
blocked_by_active_queue: none
suggested_next_artifact: remote-access-nat-relay product ADR
"""


def run_integrator(text: str) -> subprocess.CompletedProcess[str]:
    repo = ROOT / "repo-ref" / "nako"
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--format", "json"],
        cwd=ROOT,
        input=text,
        text=True,
        capture_output=True,
        check=False,
    )


class CapabilityReconResultIntegratorTests(unittest.TestCase):
    def setUp(self) -> None:
        if not (ROOT / "repo-ref" / "nako").exists():
            self.skipTest("repo-ref/nako is not available")

    def test_merges_multiple_valid_recon_results_without_promoting_implementation(self) -> None:
        result = run_integrator(PLAYBACK_RESULT + "\n" + REMOTE_ACCESS_RESULT)
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(payload["merge_valid"])
        self.assertFalse(payload["promotion_allowed"])
        self.assertEqual(payload["accepted_result_count"], 2)
        self.assertEqual(payload["rejected_result_count"], 0)
        self.assertEqual(payload["ready_active_unit"]["task"], "GABMA-020")
        self.assertIn("playback-transcode-depth workstream draft", payload["suggested_next_artifacts"])
        self.assertIn("remote-access-nat-relay product ADR", payload["suggested_next_artifacts"])
        self.assertIn("built-in relay ownership", payload["product_decisions"])

    def test_rejects_merge_when_any_result_violates_recon_contract(self) -> None:
        invalid = PLAYBACK_RESULT.replace("implementation_allowed: false", "implementation_allowed: true")
        result = run_integrator(invalid + "\n" + REMOTE_ACCESS_RESULT)
        payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(payload["merge_valid"])
        self.assertFalse(payload["promotion_allowed"])
        self.assertEqual(payload["accepted_result_count"], 1)
        self.assertEqual(payload["rejected_result_count"], 1)
        self.assertIn("RECON result must not allow implementation directly", payload["validation"]["errors"])


if __name__ == "__main__":
    unittest.main()
