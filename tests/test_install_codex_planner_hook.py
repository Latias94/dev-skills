import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_codex_planner_hook.py"


def run_script(target_repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target_repo), *extra],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class InstallCodexPlannerHookTests(unittest.TestCase):
    def test_installs_template_into_target_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = run_script(repo)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "installed")
            installed = repo / ".codex" / "hooks.json"
            self.assertTrue(installed.exists())
            data = json.loads(installed.read_text(encoding="utf-8"))
            self.assertIn("hooks", data)
            self.assertIn("UserPromptSubmit", data["hooks"])
            command = data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
            self.assertIn("planner.py advanced hook-payload", command)

    def test_refuses_to_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            first = run_script(repo)
            self.assertEqual(first.returncode, 0, msg=first.stderr)

            second = run_script(repo)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("already exists", second.stderr)

    def test_merge_adds_second_event_into_existing_hooks_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            first = run_script(repo)
            self.assertEqual(first.returncode, 0, msg=first.stderr)

            second = run_script(repo, "--merge", "--event-name", "BeforeAgent")
            self.assertEqual(second.returncode, 0, msg=second.stderr)

            installed = repo / ".codex" / "hooks.json"
            data = json.loads(installed.read_text(encoding="utf-8"))
            self.assertIn("UserPromptSubmit", data["hooks"])
            self.assertIn("BeforeAgent", data["hooks"])


if __name__ == "__main__":
    unittest.main()
