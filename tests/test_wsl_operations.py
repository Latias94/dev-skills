from __future__ import annotations

import argparse
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "engineering"
    / "wsl-operations"
    / "scripts"
    / "wsl_run.py"
)
SPEC = importlib.util.spec_from_file_location("wsl_run", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
wsl_run = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wsl_run
SPEC.loader.exec_module(wsl_run)


class OutputCleanupTests(unittest.TestCase):
    def test_decodes_utf16_without_a_byte_order_mark(self) -> None:
        encoded = "Ubuntu-26.04\r\n".encode("utf-16-le")

        self.assertEqual(wsl_run.decode_output(encoded), "Ubuntu-26.04\r\n")

    def test_removes_terminal_controls_and_del(self) -> None:
        noisy = "before\x1b[I\x1b[O\x1b[31mred\x1b[0m\x9b32mgreen\x9b0m\x7fafter\r\n"

        self.assertEqual(wsl_run.sanitize_output(noisy), "beforeredgreenafter\n")

    def test_preserves_raw_c1_bytes_until_sanitizing(self) -> None:
        decoded = wsl_run.decode_output(b"before\x9b32mgreen\x9b0mafter\n")

        self.assertEqual(wsl_run.sanitize_output(decoded), "beforegreenafter\n")


class CommandConstructionTests(unittest.TestCase):
    def test_run_uses_direct_argv_and_quiet_environment(self) -> None:
        args = argparse.Namespace(
            distro="Ubuntu-26.04",
            user="root",
            env=["HTTP_PROXY=http://127.0.0.1:10809"],
            command=["--", "uname", "-a"],
        )

        arguments = wsl_run.run_arguments(args)

        self.assertEqual(
            arguments[:5],
            ["--distribution", "Ubuntu-26.04", "--user", "root", "--exec"],
        )
        self.assertIn("TERM=dumb", arguments)
        self.assertIn("HTTP_PROXY=http://127.0.0.1:10809", arguments)
        self.assertEqual(arguments[-2:], ["uname", "-a"])

    def test_rejects_invalid_environment_names(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid environment"):
            wsl_run.parse_environment(["BAD-NAME=value"])


class InvocationTests(unittest.TestCase):
    def test_returns_the_child_exit_code(self) -> None:
        completed = mock.Mock(stdout=b"", stderr=b"", returncode=23)

        with mock.patch.object(wsl_run.subprocess, "run", return_value=completed):
            exit_code = wsl_run.invoke_wsl(["--list", "--verbose"])

        self.assertEqual(exit_code, 23)


class DestructiveGuardTests(unittest.TestCase):
    def test_normalizes_extended_windows_paths(self) -> None:
        self.assertEqual(
            wsl_run.normalize_windows_path(r"\\?\H:\WSL\Ubuntu"),
            wsl_run.normalize_windows_path(r"h:\wsl\ubuntu"),
        )

    def test_rejects_a_filesystem_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "below a filesystem root"):
            wsl_run.validated_base_path("H:\\")

    def test_rejects_a_mismatched_confirmation_without_reading_registry(self) -> None:
        args = argparse.Namespace(
            distro="Ubuntu",
            expected_base_path=r"H:\WSL\Ubuntu",
            confirm_destroy="Ubuntu-26.04",
        )

        with (
            mock.patch.object(wsl_run, "registry_distributions") as registry,
            mock.patch.object(wsl_run.sys, "stderr", io.StringIO()),
        ):
            exit_code = wsl_run.unregister(args)

        self.assertEqual(exit_code, 2)
        registry.assert_not_called()

    def test_rejects_a_mismatched_registered_base_path(self) -> None:
        args = argparse.Namespace(
            distro="Ubuntu",
            expected_base_path=r"H:\WSL\Ubuntu",
            confirm_destroy="Ubuntu",
        )
        registered = [wsl_run.Distribution("Ubuntu", r"H:\WSL\Other", 2)]

        with (
            mock.patch.object(wsl_run, "registry_distributions", return_value=registered),
            mock.patch.object(wsl_run, "invoke_wsl") as invoke,
            mock.patch.object(wsl_run.sys, "stderr", io.StringIO()),
        ):
            exit_code = wsl_run.unregister(args)

        self.assertEqual(exit_code, 2)
        invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
