import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRAM_STATUS = ROOT / "skills" / "engineering" / "plan-engineering-program" / "scripts" / "program_status.py"


def run_status(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PROGRAM_STATUS), str(repo), *extra],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def create_repo() -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "docs" / "workstreams").mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=False)
    return tmp


def create_workstream(root: Path, slug: str, status: str, current_task: str | None = None) -> Path:
    ws = root / "docs" / "workstreams" / slug
    write_json(
        ws / "WORKSTREAM.json",
        {
            "schema_version": 1,
            "slug": slug,
            "status": status,
            "lane_slug": "example",
            "current_task": current_task,
        },
    )
    return ws


def make_ready_active(ws: Path, task_id: str) -> None:
    (ws / "TODO.md").write_text(f"- [ ] {task_id}\n", encoding="utf-8")
    (ws / "CONTEXT.jsonl").write_text('{"path":"CONTEXT.md","required":false}\n', encoding="utf-8")
    (ws / "EVIDENCE_AND_GATES.md").write_text("# Evidence\n", encoding="utf-8")
    (ws / "HANDOFF.md").write_text("# Handoff\n", encoding="utf-8")
    write_jsonl(
        ws / "TASKS.jsonl",
        [
            {
                "task_id": task_id,
                "status": "todo",
                "owner": "codex",
                "deps": [],
                "scope": ["crates/example"],
                "validation": ["cargo test"],
                "context": [],
                "evidence": [],
            }
        ],
    )
    write_jsonl(
        ws / "CAMPAIGNS.jsonl",
        [
            {
                "campaign_id": "CAMP-001",
                "status": "approved",
                "lane_slug": "example",
                "ordered_tasks": [task_id],
                "gates": ["cargo test"],
                "side_effect_policy": "manual",
                "stop_conditions": ["failed gate"],
                "approved_by_user": True,
            }
        ],
    )


class ProgramStatusTests(unittest.TestCase):
    def test_default_text_output_hides_historical_rows_and_reports_active_blockers(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            create_workstream(root, "old", "completed")
            create_workstream(root, "active", "active", "ACT-010")

            result = run_status(root)

            self.assertEqual(result.returncode, 0)
            self.assertIn("Status counts: active=1, completed=1", result.stdout)
            self.assertIn("Legacy closed history skipped by default: 1", result.stdout)
            self.assertIn("Historical rows hidden: 1. Use --all to print them.", result.stdout)
            self.assertIn("missing-TASKS.jsonl", result.stdout)
            self.assertIn("Implementation Horizon: 0 ready active rows; 1 active rows blocked", result.stdout)

    def test_all_flag_prints_historical_rows(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            create_workstream(root, "old", "completed")

            result = run_status(root, "--all")

            self.assertEqual(result.returncode, 0)
            self.assertIn("All Workstreams", result.stdout)
            self.assertIn("old", result.stdout)

    def test_json_output_reports_ready_and_blocked_active_workstreams(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ready = create_workstream(root, "ready", "active", "READY-010")
            make_ready_active(ready, "READY-010")
            create_workstream(root, "blocked", "active", "BLOCK-010")
            create_workstream(root, "old", "complete")

            result = run_status(root, "--format", "json")
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["status_counts"], {"active": 2, "complete": 1})
            self.assertEqual(payload["implementation_horizon"], 1)
            self.assertEqual([row["slug"] for row in payload["ready_workstreams"]], ["ready"])
            self.assertEqual([row["slug"] for row in payload["blocked_workstreams"]], ["blocked"])
            self.assertEqual([row["slug"] for row in payload["historical_workstreams"]], ["old"])


if __name__ == "__main__":
    unittest.main()
