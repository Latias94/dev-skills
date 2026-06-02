import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "engineering" / "plan-engineering-program" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from eval_scenario import evaluate, load_scenario  # type: ignore  # noqa: E402


class EvalScenarioTests(unittest.TestCase):
    def test_nako_readiness_scores_assignable_program_case(self) -> None:
        scenario = load_scenario(ROOT / "docs" / "evals" / "scenarios" / "2026-06-02-nako-readiness-eval.json")
        result = evaluate(ROOT / "repo-ref" / "nako", scenario, False)

        self.assertEqual(result["scores"]["routing"]["score"], 2)
        self.assertEqual(result["program_action"]["operating_mode"], "READINESS")
        self.assertEqual(result["chain_state"], "execution_chain_ready")
        self.assertEqual(result["recommended_route"]["skill"], "run-workstream-task")
        self.assertEqual(result["comparison"]["trellis_like"]["runtime_enforcement"]["score"], 2)
        self.assertEqual(result["comparison"]["matt_skills_like"]["design_pressure"]["score"], 2)
        self.assertTrue(result["expectation_checks"]["trellis"]["must_resolve_active_task"]["passed"])
        self.assertTrue(result["expectation_checks"]["trellis"]["must_emit_execution_handoff"]["passed"])
        self.assertTrue(result["expectation_checks"]["matt"]["must_preserve_design_pressure"]["passed"])

    def test_hajimi_audit_scores_planner_only_case(self) -> None:
        scenario = load_scenario(ROOT / "docs" / "evals" / "scenarios" / "2026-06-02-hajimi-audit-eval.json")
        result = evaluate(ROOT / "repo-ref" / "hajimi", scenario, False)

        self.assertEqual(result["scores"]["routing"]["score"], 2)
        self.assertEqual(result["program_action"]["operating_mode"], "AUDIT")
        self.assertEqual(result["chain_state"], "planner_only")
        self.assertEqual(result["recommended_route"]["skill"], "plan-engineering-program")
        self.assertEqual(result["comparison"]["trellis_like"]["runtime_enforcement"]["score"], 2)
        self.assertEqual(result["comparison"]["matt_skills_like"]["skill_sharpness"]["score"], 0)
        self.assertTrue(result["expectation_checks"]["trellis"]["must_refuse_fabricated_execution"]["passed"])
        self.assertTrue(result["expectation_checks"]["trellis"]["must_minimize_unnecessary_context"]["passed"])
        self.assertTrue(result["expectation_checks"]["matt"]["must_preserve_design_pressure"]["passed"])

    def test_hajimi_adversarial_live_execution_fails_expected_route_and_checks(self) -> None:
        scenario = load_scenario(
            ROOT / "docs" / "evals" / "scenarios" / "2026-06-02-hajimi-live-execution-adversarial.json"
        )
        result = evaluate(ROOT / "repo-ref" / "hajimi", scenario, False)

        self.assertEqual(result["scores"]["routing"]["score"], 0)
        self.assertEqual(result["program_action"]["operating_mode"], "AUDIT")
        self.assertEqual(result["chain_state"], "planner_only")
        self.assertFalse(result["expectation_checks"]["trellis"]["must_emit_execution_handoff"]["passed"])
        self.assertFalse(result["expectation_checks"]["matt"]["should_prefer_sharp_skill"]["passed"])
        self.assertFalse(result["expectation_checks"]["matt"]["should_avoid_heavy_orchestration"]["passed"])

    def test_nako_adversarial_planner_only_fails_route_but_keeps_good_runtime_traits(self) -> None:
        scenario = load_scenario(
            ROOT / "docs" / "evals" / "scenarios" / "2026-06-02-nako-planner-only-adversarial.json"
        )
        result = evaluate(ROOT / "repo-ref" / "nako", scenario, False)

        self.assertEqual(result["scores"]["routing"]["score"], 0)
        self.assertEqual(result["recommended_route"]["skill"], "run-workstream-task")
        self.assertEqual(result["chain_state"], "execution_chain_ready")
        self.assertTrue(result["expectation_checks"]["trellis"]["should_not_remain_planner_only"]["passed"])
        self.assertTrue(result["expectation_checks"]["matt"]["should_not_miss_ready_execution"]["passed"])

    def test_skills_medium_direct_now_downshifts_to_tdd(self) -> None:
        scenario = load_scenario(
            ROOT / "docs" / "evals" / "scenarios" / "2026-06-02-skills-medium-direct-eval.json"
        )
        result = evaluate(ROOT / "repo-ref" / "skills", scenario, False)

        self.assertEqual(result["scores"]["routing"]["score"], 2)
        self.assertEqual(result["recommended_route"]["skill"], "tdd")
        self.assertEqual(result["chain_state"], "direct_execution_ready")
        self.assertTrue(result["expectation_checks"]["trellis"]["should_not_remain_planner_only"]["passed"])
        self.assertTrue(result["expectation_checks"]["matt"]["must_preserve_design_pressure"]["passed"])
        self.assertTrue(result["expectation_checks"]["matt"]["should_not_miss_ready_execution"]["passed"])

    def test_nako_runtime_block_consumption_surfaces_prompt_gains(self) -> None:
        scenario = load_scenario(
            ROOT / "docs" / "evals" / "scenarios" / "2026-06-02-nako-runtime-block-consumption.json"
        )
        result = evaluate(ROOT / "repo-ref" / "nako", scenario, False)

        self.assertEqual(result["scores"]["routing"]["score"], 2)
        self.assertEqual(result["recommended_route"]["skill"], "run-workstream-task")
        self.assertTrue(
            result["runtime_consumption"]["baseline_without_runtime_block"][
                "active_unit_must_be_reconstructed_manually"
            ]
        )
        self.assertTrue(result["runtime_consumption"]["enhanced_with_runtime_block"]["has_runtime_block"])
        self.assertTrue(result["runtime_consumption"]["enhanced_with_runtime_block"]["handoff_chain_runtime_aligned"])
        self.assertIn(
            "active unit can be injected without re-synthesizing planner prose",
            result["runtime_consumption"]["enhanced_with_runtime_block"]["gains"],
        )
        self.assertIn(
            "review/verify/integrate prompts share the same derived control state",
            result["runtime_consumption"]["enhanced_with_runtime_block"]["gains"],
        )

    def test_hajimi_runtime_block_refusal_surfaces_audit_gain(self) -> None:
        scenario = load_scenario(
            ROOT / "docs" / "evals" / "scenarios" / "2026-06-02-hajimi-runtime-block-refusal.json"
        )
        result = evaluate(ROOT / "repo-ref" / "hajimi", scenario, False)

        self.assertEqual(result["scores"]["routing"]["score"], 2)
        self.assertEqual(result["recommended_route"]["skill"], "plan-engineering-program")
        self.assertFalse(
            result["runtime_consumption"]["baseline_without_runtime_block"][
                "active_unit_must_be_reconstructed_manually"
            ]
        )
        self.assertTrue(result["runtime_consumption"]["enhanced_with_runtime_block"]["has_runtime_block"])
        self.assertTrue(result["runtime_consumption"]["enhanced_with_runtime_block"]["handoff_chain_runtime_aligned"])
        self.assertIn(
            "audit-only refusal is explicit enough to suppress fabricated worker dispatch",
            result["runtime_consumption"]["enhanced_with_runtime_block"]["gains"],
        )


if __name__ == "__main__":
    unittest.main()
