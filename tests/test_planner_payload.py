import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = (
    ROOT
    / "skills"
    / "engineering"
    / "plan-engineering-program"
    / "scripts"
    / "planner_payload.py"
)


def run_payload(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PAYLOAD), str(repo), "--format", "json", *extra],
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


class PlannerPayloadTests(unittest.TestCase):
    def test_ready_queue_yields_assignment_payload(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "alpha"
            write(
                ws / "WORKSTREAM.json",
                json.dumps(
                    {
                        "slug": "alpha",
                        "status": "active",
                        "lane_slug": "example",
                        "current_task": "ALPHA-010",
                    },
                    indent=2,
                ),
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

            result = run_payload(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["program_action"]["mode"], "ASSIGN")
            self.assertEqual(payload["program_action"]["operating_mode"], "READINESS")
            self.assertEqual(payload["active_unit"]["task"], "ALPHA-010")
            self.assertEqual(payload["program_action"]["safe_next_move"], "assignment")
            self.assertIn("<planner-runtime>", payload["runtime_prompt_block"])
            self.assertIn("Active Task: ALPHA-010", payload["runtime_prompt_block"])

    def test_historical_only_repo_yields_audit_payload(self) -> None:
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

            result = run_payload(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["program_action"]["operating_mode"], "AUDIT")
            self.assertEqual(payload["program_action"]["safe_next_move"], "read-only inspection")
            self.assertGreater(payload["audit_pressure"]["warning_count"], 0)
            self.assertIn("Operating Mode: AUDIT", payload["runtime_prompt_block"])


if __name__ == "__main__":
    unittest.main()
