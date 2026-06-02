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
    / "planner_prompt_wrapper.py"
)


def run_script(repo: Path, prompt: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--prompt", prompt, "--format", "json", *extra],
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


class PlannerPromptWrapperTests(unittest.TestCase):
    def test_ready_repo_wraps_assignment_request(self) -> None:
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

            result = run_script(root, "Confirm the next safe task and hand off if still valid.")
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["recommended_route"]["skill"], "run-workstream-task")
            self.assertIn("<planner-runtime>", payload["wrapped_prompt"])
            self.assertIn("<planner-turn-guidance>", payload["wrapped_prompt"])
            self.assertIn("<user-request>", payload["wrapped_prompt"])
            self.assertIn("Confirm the next safe task and hand off if still valid.", payload["wrapped_prompt"])

    def test_audit_repo_wraps_refusal_request(self) -> None:
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

            result = run_script(root, "Explain whether anything is assignable or if this stays audit-only.")
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["recommended_route"]["skill"], "plan-engineering-program")
            self.assertIn("Stay read-only. Do not fabricate worker dispatch", payload["wrapped_prompt"])
            self.assertIn("Explain whether anything is assignable", payload["wrapped_prompt"])


if __name__ == "__main__":
    unittest.main()
