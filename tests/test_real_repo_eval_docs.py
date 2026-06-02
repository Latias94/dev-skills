import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class RealRepoEvalDocsTests(unittest.TestCase):
    def test_analysis_doc_records_three_way_comparison(self) -> None:
        doc = read("docs/analysis/dev-skills-vs-trellis-vs-matt-skills.md")
        self.assertIn("Dev Skills vs Trellis vs Matt Skills", doc)
        self.assertIn("Trellis", doc)
        self.assertIn("Matt Skills", doc)
        self.assertIn("runtime breadcrumb", doc.lower())
        self.assertIn("repo-ref/nako", doc)
        self.assertIn("repo-ref/hajimi", doc)

    def test_eval_framework_defines_four_layers_and_initial_scenarios(self) -> None:
        doc = read("docs/evals/dev-skills-real-repo-eval-framework.md")
        for heading in [
            "Layer 1: Routing Correctness",
            "Layer 2: Artifact Correctness",
            "Layer 3: Execution Usefulness",
            "Layer 4: Operator Cost",
            "NAKO-001",
            "NAKO-002",
            "HAJIMI-001",
            "HAJIMI-002",
        ]:
            with self.subTest(heading=heading):
                self.assertIn(heading, doc)

    def test_refactor_roadmap_preserves_authority_model(self) -> None:
        doc = read("docs/roadmaps/dev-skills-refactor-roadmap.md")
        self.assertIn("artifact modeling", doc)
        self.assertIn("project-owned truth", doc)
        self.assertIn("runtime breadcrumb", doc)
        self.assertIn("Do Not Introduce", doc)
        self.assertIn("a second source of truth", doc)

    def test_user_facing_docs_explain_operating_mode_and_horizon(self) -> None:
        readme = read("README.md")
        workflow = read("docs/workflow.md")
        usage = read("docs/usage.md")

        for doc in [readme, workflow, usage]:
            self.assertIn("Operating Mode", doc)
            self.assertIn("Implementation Horizon", doc)

        self.assertIn("READINESS", workflow)
        self.assertIn("AUDIT", workflow)
        self.assertIn("downshift to `tdd`, `diagnose`, or one lightweight workstream path", workflow)

    def test_iteration_backlog_and_decision_log_exist(self) -> None:
        backlog = read("docs/roadmaps/dev-skills-next-iteration-backlog.md")
        decisions = read("docs/analysis/dev-skills-decision-log-2026-06-02.md")

        self.assertIn("Highest-Value Next Steps", backlog)
        self.assertIn("READINESS", backlog)
        self.assertIn("AUDIT", backlog)
        self.assertIn("Decision Log", decisions)
        self.assertIn("Separate `READINESS` from `AUDIT`", decisions)

    def test_rehearsal_and_usage_docs_cover_planner_facade(self) -> None:
        readme = read("README.md")
        usage = read("docs/usage.md")
        workflow = read("docs/workflow.md")
        rehearsal = read("docs/evals/results/2026-06-02-nako-planner-rehearsal-v2.md")
        hajimi_audit = read("docs/evals/results/2026-06-02-hajimi-audit-summary-notes.md")
        dispatch = read("docs/evals/results/2026-06-02-dispatch-rehearsal-notes.md")
        handoff = read("docs/evals/results/2026-06-02-handoff-chain-rehearsal-notes.md")
        live = read("docs/evals/results/2026-06-02-live-experiment-playbook.md")
        eval_doc = read("docs/evals/large-rust-workflow.md")
        nako_runbook = read("docs/evals/results/2026-06-02-nako-live-runbook.md")
        evaluator = read("docs/evals/results/2026-06-02-scenario-evaluator-notes.md")
        medium = read("docs/evals/results/2026-06-02-medium-task-over-escalation-design.md")
        medium_candidates = read("docs/evals/results/2026-06-02-medium-fixture-candidate-audit.md")
        prelude = read("docs/evals/results/2026-06-02-planner-turn-prelude-notes.md")
        wrapper = read("docs/evals/results/2026-06-02-planner-prompt-wrapper-notes.md")
        wrapper_vs_raw = read("docs/evals/results/2026-06-02-wrapper-vs-raw-experiment-notes.md")
        phase_audit = read("docs/analysis/dev-skills-phase-audit-2026-06-02.md")
        hook_adapter = read("docs/evals/results/2026-06-02-pseudo-hook-adapter-notes.md")
        live_matrix = read("docs/evals/results/2026-06-02-live-subagent-matrix.md")
        hajimi_live_refusal = read("docs/evals/results/2026-06-02-hajimi-live-refusal-runbook.md")
        skills_live_restraint = read("docs/evals/results/2026-06-02-skills-live-restraint-runbook.md")
        live_packet = read("docs/evals/results/2026-06-02-live-experiment-packet-notes.md")

        for doc in [readme, usage, workflow]:
            self.assertIn("planner.py", doc)
            self.assertIn("planner.py scale", doc)
            self.assertIn("planner.py status", doc)
            self.assertIn("planner.py dispatch", doc)
            self.assertIn("planner.py capability", doc)
            self.assertIn("planner.py recon-packet", doc)
            self.assertIn("planner.py chain", doc)
            self.assertIn("planner.py advanced", doc)
            self.assertIn("planner.py advanced prelude", doc)

        self.assertIn("Nako Planner Rehearsal V2", rehearsal)
        self.assertIn("GABMA-020", rehearsal)
        self.assertIn("historical audit drift exists but does not affect active-queue readiness", rehearsal)
        self.assertIn("Hajimi Audit Summary Notes", hajimi_audit)
        self.assertIn("missing_terminal_task_evidence: 152", hajimi_audit)
        self.assertIn("Dispatch Rehearsal Notes", dispatch)
        self.assertIn("run-workstream-task", dispatch)
        self.assertIn("plan-engineering-program", dispatch)
        self.assertIn("Handoff Chain Rehearsal Notes", handoff)
        self.assertIn("execution_chain_ready", handoff)
        self.assertIn("planner_only", handoff)
        self.assertIn("Live Experiment Playbook", live)
        self.assertIn("repo-ref/nako", live)
        self.assertIn("repo-ref/hajimi", live)
        self.assertIn("Scenario 11: Live Experiment Preflight", eval_doc)
        self.assertIn("Scenario 12: Historical Repo Must Refuse Live Execution", eval_doc)
        self.assertIn("Scenario 13: Wrapper Vs Raw Planner Prompt", eval_doc)
        self.assertIn("Nako Live Runbook", nako_runbook)
        self.assertIn("GABMA-020", nako_runbook)
        self.assertIn("WORKSTREAM_RESULT:", nako_runbook)
        self.assertIn("Scenario Evaluator Notes", evaluator)
        self.assertIn("execution_chain_ready", evaluator)
        self.assertIn("planner_only", evaluator)
        self.assertIn("follow-through guidance", evaluator)
        self.assertIn("Medium Task Over-Escalation Design", medium)
        self.assertIn("should_avoid_program_escalation_for_medium_task", medium)
        self.assertIn("Medium Fixture Candidate Audit", medium_candidates)
        self.assertIn("repo-ref/skills", medium_candidates)
        self.assertIn("repo-ref/codex", medium_candidates)
        self.assertIn("audit-project-scale", medium_candidates)
        self.assertIn("tdd` or `diagnose", medium_candidates)
        self.assertIn("light-substrate bounded", evaluator)
        self.assertIn("Planner Turn Prelude Notes", prelude)
        self.assertIn("planner_turn_prelude.py", prelude)
        self.assertIn("Planner Prompt Wrapper Notes", wrapper)
        self.assertIn("planner_prompt_wrapper.py", wrapper)
        self.assertIn("Wrapper vs Raw Experiment Notes", wrapper_vs_raw)
        self.assertIn("raw user prompt", wrapper_vs_raw.lower())
        self.assertIn("wrapped planner prompt", wrapper_vs_raw.lower())
        self.assertIn("Dev Skills Phase Audit", phase_audit)
        self.assertIn("What Is Now Proven", phase_audit)
        self.assertIn("What Is Not Yet Proven", phase_audit)
        self.assertIn("Net Judgment", phase_audit)
        self.assertIn("Pseudo-Hook Adapter Notes", hook_adapter)
        self.assertIn("planner_hook_adapter.py", hook_adapter)
        self.assertIn("hookSpecificOutput", hook_adapter)
        self.assertIn("Live Subagent Matrix", live_matrix)
        self.assertIn("repo-ref/nako", live_matrix)
        self.assertIn("repo-ref/hajimi", live_matrix)
        self.assertIn("repo-ref/skills", live_matrix)
        self.assertIn("Hajimi Live Refusal Runbook", hajimi_live_refusal)
        self.assertIn("Operating Mode: AUDIT", hajimi_live_refusal)
        self.assertIn("Skills Live Restraint Runbook", skills_live_restraint)
        self.assertIn("sharpest safe execution skill", skills_live_restraint)
        self.assertIn("Live Experiment Packet Notes", live_packet)
        self.assertIn("live_experiment_packet.py", live_packet)
        self.assertIn("hajimi_refusal", live_packet)
        self.assertIn("nako_chain", live_packet)
        self.assertIn("skills_restraint", live_packet)


if __name__ == "__main__":
    unittest.main()
