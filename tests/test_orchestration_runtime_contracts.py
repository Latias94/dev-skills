import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class OrchestrationRuntimeContractTests(unittest.TestCase):
    def test_runtime_state_machine_names_all_program_states(self) -> None:
        runtime = read("skills/engineering/dev-flow/references/orchestration-runtime.md")
        for state in [
            "DISCOVERY",
            "SHAPE",
            "PLAN",
            "ASSIGN",
            "EXECUTE",
            "INTAKE",
            "REVIEW",
            "VERIFY",
            "INTEGRATE",
            "RECON",
            "DECISION",
        ]:
            self.assertIn(f"`{state}`", runtime)
        self.assertIn("Never jump from `EXECUTE` to a new `ASSIGN`", runtime)
        self.assertIn("`READINESS`", runtime)
        self.assertIn("`AUDIT`", runtime)
        self.assertIn("Implementation Horizon", runtime)

    def test_agent_contract_defines_parseable_role_markers(self) -> None:
        contracts = read("skills/engineering/dev-flow/references/agent-contracts.md")
        for marker in [
            "WORKSTREAM_RESULT:",
            "REVIEW_RESULT:",
            "VERIFY_RESULT:",
            "INTEGRATION_RESULT:",
        ]:
            self.assertIn(marker, contracts)

    def test_role_skills_reference_their_required_markers(self) -> None:
        expectations = {
            "skills/engineering/run-workstream-task/SKILL.md": "WORKSTREAM_RESULT:",
            "skills/engineering/run-architecture-lane/SKILL.md": "WORKSTREAM_RESULT:",
            "skills/engineering/review-workstream/SKILL.md": "REVIEW_RESULT:",
            "skills/engineering/verify-rust-workstream/SKILL.md": "VERIFY_RESULT:",
            "skills/engineering/integrate-lane-results/SKILL.md": "INTEGRATION_RESULT:",
        }
        for path, marker in expectations.items():
            with self.subTest(path=path):
                self.assertIn(marker, read(path))

    def test_parallel_dispatch_contract_keeps_worker_from_choosing_global_next_task(self) -> None:
        playbook = read("docs/playbooks/multi-terminal-development.md")
        self.assertIn("## Worker Prompt", playbook)
        self.assertIn("Do not choose the global next task", playbook)
        self.assertIn("Include a `WORKSTREAM_RESULT:` marker", playbook)

    def test_codex_subagent_dispatch_requires_state_gates_before_workers(self) -> None:
        dispatch = read("skills/engineering/dev-flow/references/codex-subagent-dispatch.md")
        self.assertIn("Do not spawn workers in `DISCOVERY`, `SHAPE`, or `PLAN`", dispatch)
        self.assertIn("Explorer subagents may run earlier", dispatch)
        self.assertIn("Implementation Horizon: 0", dispatch)
        self.assertIn("You are not alone in the codebase", dispatch)
        self.assertIn("Subagent output is never accepted directly", dispatch)

    def test_upper_planner_is_thin_and_does_not_accept_plain_done(self) -> None:
        planner = read("skills/engineering/plan-engineering-program/SKILL.md")
        self.assertIn("does\nnot implement lane work or accept worker `DONE` reports", planner)
        self.assertIn("Use `ASSIGN` only when", planner)
        self.assertIn("Operating Mode: READINESS | AUDIT", planner)
        self.assertIn("Implementation Horizon: <N>", planner)

    def test_upper_planner_output_contract_reference_keeps_terminal_prompt_requirements(self) -> None:
        output = read("skills/engineering/plan-engineering-program/references/output-contract.md")
        self.assertIn("Mode: DISCOVERY | SHAPE | PLAN | ASSIGN | RECON | DECISION", output)
        self.assertIn("Minimal User Input Needed", output)
        self.assertIn("DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT", output)
        self.assertIn("WORKSTREAM_RESULT:", output)
        self.assertIn("../../dev-flow/references/agent-contracts.md", output)
        self.assertIn("integrate-lane-results", output)

    def test_side_effect_policy_allows_auto_commit_without_reprompt(self) -> None:
        policy = read("skills/engineering/dev-flow/references/side-effect-policy.md")
        self.assertIn("`auto-commit`", policy)
        self.assertIn("Do not ask again before committing", policy)
        self.assertIn("Push is denied by default", policy)
        self.assertIn("Use explicit path staging", policy)

        runtime = read("skills/engineering/dev-flow/references/orchestration-runtime.md")
        validator = read("skills/engineering/plan-engineering-program/scripts/validate_orchestration_state.py")
        schema = read("skills/engineering/dev-flow/references/planner-state.schema.json")
        integrator = read("skills/engineering/integrate-lane-results/SKILL.md")

        for text in [runtime, validator, schema]:
            self.assertIn("auto-commit", text)
        self.assertIn("side-effect-policy.md", integrator)

    def test_resume_and_lane_skills_distinguish_readiness_from_historical_audit(self) -> None:
        resume = read("skills/engineering/resume-workstream/SKILL.md")
        lane = read("skills/engineering/run-architecture-lane/SKILL.md")
        integrator = read("skills/engineering/integrate-lane-results/SKILL.md")
        dev_flow = read("skills/engineering/dev-flow/SKILL.md")

        self.assertIn("operating mode: `READINESS`", resume)
        self.assertIn("Implementation Horizon: 0 | 1", resume)
        self.assertIn("historical audit concern", lane)
        self.assertIn("Historical audit findings", integrator)
        self.assertIn("Operating Mode: READINESS | AUDIT", dev_flow)
        self.assertIn("Implementation Horizon: <N>", dev_flow)


if __name__ == "__main__":
    unittest.main()
