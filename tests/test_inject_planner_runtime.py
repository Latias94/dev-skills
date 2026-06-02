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
    / "inject_planner_runtime.py"
)


def run_script(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), *extra],
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


class InjectPlannerRuntimeTests(unittest.TestCase):
    def test_ready_repo_emits_host_consumable_payload(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            write(
                root / "README.md",
                "Remote access, NAT relay, playback transcode, WebDAV storage, clients, addons, sharing, backup, and observability are future product areas.\n",
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
            self.assertEqual(
                sorted(payload.keys()),
                ["hookSpecificOutput"],
            )
            self.assertEqual(payload["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
            self.assertIn("<planner-runtime>", payload["hookSpecificOutput"]["additionalContext"])
            self.assertIn("<capability-parallelism>", payload["hookSpecificOutput"]["additionalContext"])
            self.assertIn("Recommended Route: run-workstream-task", payload["hookSpecificOutput"]["additionalContext"])

    def test_debug_mode_adds_derived_metadata_without_changing_contract(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "legacy"
            write(ws / "TODO.md", "- [x] LEG-010\n")
            write(
                ws / "WORKSTREAM.json",
                json.dumps({"slug": "legacy", "status": "completed"}, indent=2),
            )

            result = run_script(root, "--event-name", "BeforeAgent", "--debug")
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertIn("hookSpecificOutput", payload)
            self.assertIn("debug", payload)
            self.assertEqual(payload["hookSpecificOutput"]["hookEventName"], "BeforeAgent")
            self.assertEqual(payload["debug"]["recommended_route"]["skill"], "plan-engineering-program")
            self.assertIn("product_parallelism", payload["debug"])


if __name__ == "__main__":
    unittest.main()
