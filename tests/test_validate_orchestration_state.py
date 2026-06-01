import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "engineering" / "plan-engineering-program" / "scripts" / "validate_orchestration_state.py"


def run_validator(repo: Path, *extra: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(repo), "--format", "json", *extra],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        payload = json.loads(result.stdout)
    else:
        payload = {"errors": [result.stderr]}
    return result.returncode, payload


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def create_repo() -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "docs" / "workstreams").mkdir(parents=True)
    (root / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
    return tmp


def create_active_workstream(root: Path, slug: str = "active-lane") -> Path:
    ws = root / "docs" / "workstreams" / slug
    ws.mkdir(parents=True)
    write_json(
        ws / "WORKSTREAM.json",
        {
            "schema_version": 1,
            "slug": slug,
            "status": "active",
            "current_task": "LANE-010",
        },
    )
    (ws / "TODO.md").write_text("- [ ] LANE-010\n", encoding="utf-8")
    (ws / "EVIDENCE_AND_GATES.md").write_text("# Evidence\n", encoding="utf-8")
    (ws / "HANDOFF.md").write_text("# Handoff\n", encoding="utf-8")
    return ws


class ValidateOrchestrationStateTests(unittest.TestCase):
    def test_active_workstream_missing_runtime_artifacts_blocks_assignment(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            create_active_workstream(root)

            code, payload = run_validator(root)

            self.assertEqual(code, 1)
            errors = "\n".join(payload["errors"])
            self.assertIn("missing TASKS.jsonl", errors)
            self.assertIn("missing CAMPAIGNS.jsonl", errors)
            self.assertIn("missing context manifest", errors)
            self.assertIn("current_task 'LANE-010' is not in TASKS.jsonl", errors)

    def test_legacy_closed_history_is_not_required_to_have_current_runtime_artifacts(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "old-lane"
            write_json(ws / "WORKSTREAM.json", {"slug": "old-lane", "status": "completed"})

            code, payload = run_validator(root)

            self.assertEqual(code, 0)
            self.assertEqual(payload["status_counts"], {"completed": 1})
            self.assertEqual(payload["errors"], [])

    def test_legacy_closed_history_context_shape_is_skipped_by_default(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "old-lane"
            write_json(ws / "WORKSTREAM.json", {"slug": "old-lane", "status": "closed"})
            write_jsonl(ws / "CONTEXT.jsonl", [{"kind": "legacy-note", "note": "old format"}])

            code, payload = run_validator(root)

            self.assertEqual(code, 0)
            self.assertEqual(payload["errors"], [])

    def test_strict_history_requires_runtime_artifacts_for_legacy_history(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "old-lane"
            write_json(ws / "WORKSTREAM.json", {"slug": "old-lane", "status": "completed"})

            code, payload = run_validator(root, "--strict-history")

            self.assertEqual(code, 1)
            errors = "\n".join(payload["errors"])
            self.assertIn("missing TASKS.jsonl", errors)
            self.assertIn("missing CAMPAIGNS.jsonl", errors)

    def test_active_workstream_with_tasks_campaign_and_context_passes(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = create_active_workstream(root)
            (ws / "DESIGN.md").write_text("# Design\n", encoding="utf-8")
            write_jsonl(
                ws / "TASKS.jsonl",
                [
                    {
                        "task_id": "LANE-010",
                        "status": "todo",
                        "owner": "codex",
                        "deps": [],
                        "scope": ["crates/example"],
                        "validation": ["cargo nextest run -p example"],
                        "context": ["CONTEXT.md"],
                        "evidence": [],
                    }
                ],
            )
            write_jsonl(
                ws / "CAMPAIGNS.jsonl",
                [
                    {
                        "campaign_id": "LANE-CAMP-001",
                        "status": "approved",
                        "lane_slug": "example",
                        "ordered_tasks": ["LANE-010"],
                        "gates": ["cargo nextest run -p example"],
                        "side_effect_policy": "manual",
                        "stop_conditions": ["failed gate"],
                        "approved_by_user": True,
                    }
                ],
            )
            write_jsonl(
                ws / "CONTEXT.jsonl",
                [
                    {"path": "CONTEXT.md", "required": True},
                    {"file": "docs/workstreams/active-lane/DESIGN.md", "required": False},
                ],
            )

            code, payload = run_validator(root)

            self.assertEqual(code, 0)
            self.assertEqual(payload["errors"], [])
            self.assertEqual(payload["warnings"], [])

    def test_campaign_references_unknown_task_blocks_assignment(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = create_active_workstream(root)
            write_jsonl(
                ws / "TASKS.jsonl",
                [
                    {
                        "task_id": "LANE-010",
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
                        "campaign_id": "LANE-CAMP-001",
                        "status": "approved",
                        "lane_slug": "example",
                        "ordered_tasks": ["LANE-999"],
                        "gates": ["cargo test"],
                        "side_effect_policy": "manual",
                        "stop_conditions": ["failed gate"],
                        "approved_by_user": True,
                    }
                ],
            )
            write_jsonl(ws / "CONTEXT.jsonl", [{"path": "CONTEXT.md", "required": True}])

            code, payload = run_validator(root)

            self.assertEqual(code, 1)
            self.assertIn("references unknown task LANE-999", "\n".join(payload["errors"]))


if __name__ == "__main__":
    unittest.main()
