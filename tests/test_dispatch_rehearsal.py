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
    / "dispatch_rehearsal.py"
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


class DispatchRehearsalTests(unittest.TestCase):
    def test_ready_task_routes_to_run_workstream_task(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            write(
                root / "README.md",
                "Remote access, playback transcode, WebDAV storage, Android clients, Addon ecosystem, and backup observability are future product areas.\n",
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
            self.assertTrue(payload["product_parallelism"]["profile_family"]["detected"])
            self.assertGreater(payload["product_parallelism"]["product_recon_horizon"], 0)
            named_ids = {
                row["id"]
                for group in (
                    "top_recon_candidates",
                    "top_product_decisions",
                    "top_needs_workstream",
                )
                for row in payload["product_parallelism"][group]
            }
            self.assertIn("remote_access_nat_relay", named_ids)
            for group in (
                "top_recon_candidates",
                "top_product_decisions",
                "top_needs_workstream",
            ):
                for row in payload["product_parallelism"][group]:
                    self.assertIn("guardrail", row)
                    self.assertTrue(row["guardrail"])
            self.assertEqual(
                payload["product_parallelism"]["recon_result_contract"]["result_marker"],
                "CAPABILITY_RECON_RESULT:",
            )
            self.assertIn(
                "suggested_next_artifact",
                payload["product_parallelism"]["recon_result_contract"]["required_fields"],
            )
            self.assertIn("WORKSTREAM_RESULT:", payload["worker_prompt"])
            self.assertIn("<planner-runtime>", payload["runtime_prompt_block"])
            self.assertIn("Active Task: ALPHA-010", payload["runtime_prompt_block"])

    def test_audit_repo_refuses_worker_dispatch(self) -> None:
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
            self.assertEqual(payload["parallelism"]["parallel_safe_now"], False)
            self.assertFalse(payload["product_parallelism"]["profile_family"]["detected"])
            self.assertEqual(payload["worker_prompt"], "")
            self.assertIn("Operating Mode: AUDIT", payload["runtime_prompt_block"])


if __name__ == "__main__":
    unittest.main()
