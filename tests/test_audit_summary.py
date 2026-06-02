import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = (
    ROOT
    / "skills"
    / "engineering"
    / "plan-engineering-program"
    / "scripts"
    / "audit_summary.py"
)


def run_audit(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDIT), str(repo), "--format", "json", *extra],
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


class AuditSummaryTests(unittest.TestCase):
    def test_groups_terminal_evidence_gaps(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            for slug in ["alpha", "beta"]:
                ws = root / "docs" / "workstreams" / slug
                write(ws / "TODO.md", "- [x] WS-010\n")
                write(
                    ws / "WORKSTREAM.json",
                    json.dumps(
                        {
                            "slug": slug,
                            "status": "completed",
                            "evidence": [
                                {"type": "task", "task_id": "WS-010", "result": "blocked"},
                            ],
                        },
                        indent=2,
                    ),
                )

            result = run_audit(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            top = payload["top_patterns"][0]
            self.assertEqual(top["pattern"], "missing_terminal_task_evidence")
            self.assertEqual(top["count"], 2)
            self.assertEqual(set(top["example_workstreams"]), {"alpha", "beta"})

    def test_groups_gate_command_mismatch(self) -> None:
        with create_repo() as tmp:
            root = Path(tmp)
            ws = root / "docs" / "workstreams" / "gamma"
            write(
                ws / "WORKSTREAM.json",
                json.dumps(
                    {
                        "slug": "gamma",
                        "status": "closed",
                        "gates": ["cargo test -p example"],
                        "evidence": [
                            {
                                "type": "gate",
                                "command": "cargo nextest run -p example",
                                "result": "pass",
                            }
                        ],
                    },
                    indent=2,
                ),
            )

            result = run_audit(root)
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            patterns = {row["pattern"]: row["count"] for row in payload["top_patterns"]}
            self.assertEqual(patterns["gate_command_not_listed"], 1)


if __name__ == "__main__":
    unittest.main()
