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
    / "planner_turn_prelude.py"
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


class PlannerTurnPreludeTests(unittest.TestCase):
    def test_ready_repo_gets_assignment_guidance(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            write(
                root / "README.md",
                "Remote access, NAT relay, playback transcode, WebDAV storage, Android clients, Addon ecosystem, sharing, backup, and observability are future product areas.\n",
            )
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
            self.assertEqual(payload["recommended_route"]["skill"], "run-workstream-task")
            self.assertIn("<planner-runtime>", payload["prelude"])
            self.assertIn("<capability-parallelism>", payload["prelude"])
            self.assertIn("<planner-turn-guidance>", payload["prelude"])
            self.assertIn("Prefer bounded assignment from the active queue", payload["prelude"])
            self.assertIn("When discussing parallel work, separate ready implementation", payload["prelude"])
            self.assertIn("remote_access_nat_relay", payload["prelude"])
            self.assertGreater(payload["product_parallelism"]["product_recon_horizon"], 0)

    def test_audit_repo_gets_refusal_guidance(self) -> None:
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
            self.assertEqual(payload["recommended_route"]["skill"], "plan-engineering-program")
            self.assertIn("<planner-runtime>", payload["prelude"])
            self.assertIn("Stay read-only. Do not fabricate worker dispatch", payload["prelude"])


if __name__ == "__main__":
    unittest.main()
