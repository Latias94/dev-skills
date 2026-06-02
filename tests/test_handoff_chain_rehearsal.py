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
    / "handoff_chain_rehearsal.py"
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


class HandoffChainRehearsalTests(unittest.TestCase):
    def test_ready_repo_builds_execution_chain(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "alpha"
            write(
                ws / "WORKSTREAM.json",
                json.dumps({"slug": "alpha", "status": "active", "current_task": "ALPHA-010"}, indent=2),
            )
            write(ws / "TODO.md", "- [ ] ALPHA-010\n")
            write(ws / "EVIDENCE_AND_GATES.md", "# Gates\n")
            write(ws / "HANDOFF.md", "# Handoff\n")
            write(
                ws / "TASKS.jsonl",
                json.dumps(
                    {
                        "task_id": "ALPHA-010",
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
                        "campaign_id": "CAMP-001",
                        "status": "approved",
                        "lane_slug": "example",
                        "ordered_tasks": ["ALPHA-010"],
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

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["chain_state"], "execution_chain_ready")
            self.assertIn("<planner-runtime>", payload["planner_prompt"])
            self.assertIn("<planner-runtime>", payload["review_prompt"])
            self.assertIn("<planner-runtime>", payload["verify_prompt"])
            self.assertIn("<planner-runtime>", payload["integrate_prompt"])
            self.assertIn("REVIEW_RESULT:", payload["review_prompt"])
            self.assertIn("VERIFY_RESULT:", payload["verify_prompt"])
            self.assertIn("INTEGRATION_RESULT:", payload["integrate_prompt"])

    def test_historical_repo_stays_planner_only(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "legacy"
            write(ws / "TODO.md", "- [x] LEG-010\n")
            write(
                ws / "WORKSTREAM.json",
                json.dumps(
                    {
                        "slug": "legacy",
                        "status": "completed",
                        "evidence": [{"type": "task", "task_id": "LEG-010", "result": "blocked"}],
                    },
                    indent=2,
                ),
            )

            result = run_script(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["chain_state"], "planner_only")
            self.assertEqual(payload["worker_prompt"], "")
            self.assertIn("<planner-runtime>", payload["planner_prompt"])
            self.assertIn("<planner-runtime>", payload["integrate_prompt"])
            self.assertTrue(payload["refusal_reason"])

    def test_direct_route_gets_follow_through_prompts(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            result = run_script(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["chain_state"], "direct_execution_ready")
            self.assertIn("<planner-runtime>", payload["planner_prompt"])
            self.assertIn("<planner-runtime>", payload["review_prompt"])
            self.assertIn("<planner-runtime>", payload["verify_prompt"])
            self.assertIn("<planner-runtime>", payload["integrate_prompt"])
            self.assertIn("review the resulting diff", payload["review_prompt"])
            self.assertIn("fresh evidence", payload["verify_prompt"])
            self.assertIn("promoted into a durable workstream", payload["integrate_prompt"])


if __name__ == "__main__":
    unittest.main()
