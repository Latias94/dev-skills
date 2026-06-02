import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BREADCRUMB = (
    ROOT
    / "skills"
    / "engineering"
    / "plan-engineering-program"
    / "scripts"
    / "planner_breadcrumb.py"
)


def run_breadcrumb(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BREADCRUMB), str(repo), *extra],
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


def create_active(root: Path, slug: str, ready: bool) -> Path:
    ws = root / "docs" / "workstreams" / slug
    write(
        ws / "WORKSTREAM.json",
        json.dumps(
            {
                "slug": slug,
                "status": "active",
                "lane_slug": "example",
                "current_task": "WS-010",
            },
            indent=2,
        ),
    )
    write(ws / "TODO.md", "- [ ] WS-010\n")
    write(ws / "EVIDENCE_AND_GATES.md", "# Gates\n")
    write(ws / "HANDOFF.md", "# Handoff\n")
    if ready:
        write(
            ws / "TASKS.jsonl",
            json.dumps(
                {
                    "task_id": "WS-010",
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
                    "ordered_tasks": ["WS-010"],
                    "gates": ["cargo nextest run -p example"],
                    "side_effect_policy": "manual",
                    "stop_conditions": ["failed gate"],
                    "approved_by_user": True,
                }
            )
            + "\n",
        )
        write(
            ws / "CONTEXT.jsonl",
            json.dumps({"path": "CONTEXT.md", "required": True}) + "\n",
        )
    return ws


class PlannerBreadcrumbTests(unittest.TestCase):
    def test_ready_active_queue_reports_assign_phase(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            create_active(root, "ready-lane", ready=True)

            result = run_breadcrumb(root, "--format", "json")
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["phase"], "ASSIGN")
            self.assertEqual(payload["operating_mode"], "READINESS")
            self.assertEqual(payload["implementation_horizon"], 1)
            self.assertEqual(payload["active_workstream"], "ready-lane")
            self.assertEqual(payload["active_task"], "WS-010")
            self.assertEqual(payload["active_campaign"], "CAMP-001")

    def test_blocked_active_queue_reports_plan_phase(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            create_active(root, "blocked-lane", ready=False)

            result = run_breadcrumb(root, "--format", "json")
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["phase"], "PLAN")
            self.assertEqual(payload["operating_mode"], "READINESS")
            self.assertEqual(payload["implementation_horizon"], 0)
            self.assertTrue(payload["blockers"])

    def test_historical_only_repo_reports_audit_discovery(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "old-lane"
            write(ws / "WORKSTREAM.json", json.dumps({"slug": "old-lane", "status": "completed"}, indent=2))

            result = run_breadcrumb(root, "--format", "json")
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["phase"], "DISCOVERY")
            self.assertEqual(payload["operating_mode"], "AUDIT")
            self.assertEqual(payload["implementation_horizon"], 0)

    def test_prompt_format_emits_runtime_block(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            create_active(root, "ready-lane", ready=True)

            result = run_breadcrumb(root, "--format", "prompt")

            self.assertEqual(result.returncode, 0)
            self.assertIn("<planner-runtime>", result.stdout)
            self.assertIn("Phase: ASSIGN", result.stdout)
            self.assertIn("Operating Mode: READINESS", result.stdout)
            self.assertIn("Implementation Horizon: 1", result.stdout)
            self.assertIn("Active Workstream: ready-lane", result.stdout)
            self.assertIn("Rule: Treat this as derived runtime guidance only", result.stdout)


if __name__ == "__main__":
    unittest.main()
