#!/usr/bin/env python3
"""Run WSL commands without exposing terminal control or encoding noise."""

from __future__ import annotations

import argparse
import ntpath
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence, TextIO


LXSS_KEY = r"Software\Microsoft\Windows\CurrentVersion\Lxss"
ENVIRONMENT = (
    "TERM=dumb",
    "NO_COLOR=1",
    "CLICOLOR=0",
    "PAGER=cat",
    "GIT_PAGER=cat",
    "GIT_TERMINAL_PROMPT=0",
)
ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
OSC = re.compile(r"(?:\x1b\]|\x9d).*?(?:\x07|\x1b\\|\x9c)", re.DOTALL)
STRING_CONTROL = re.compile(
    r"(?:\x1b[P^_X]|[\x90\x98\x9e\x9f]).*?(?:\x1b\\|\x9c)", re.DOTALL
)
CSI = re.compile(r"(?:\x1b\[|\x9b)[0-?]*[ -/]*[@-~]")
ESCAPE = re.compile(r"\x1b(?:[@-_]|[ -/][@-~])")


@dataclass(frozen=True)
class Distribution:
    name: str
    base_path: str
    version: int


def decode_output(data: bytes) -> str:
    if not data:
        return ""
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="replace")

    even_nuls = data[0::2].count(0)
    odd_nuls = data[1::2].count(0)
    pair_count = max(1, len(data) // 2)
    if odd_nuls / pair_count > 0.25:
        return data.decode("utf-16-le", errors="replace")
    if even_nuls / pair_count > 0.25:
        return data.decode("utf-16-be", errors="replace")

    decoded = data.decode("utf-8", errors="surrogateescape")
    return "".join(
        chr(codepoint - 0xDC00)
        if 0xDC80 <= (codepoint := ord(character)) <= 0xDC9F
        else "\ufffd"
        if 0xDCA0 <= codepoint <= 0xDCFF
        else character
        for character in decoded
    )


def sanitize_output(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = OSC.sub("", text)
    text = STRING_CONTROL.sub("", text)
    text = CSI.sub("", text)
    text = ESCAPE.sub("", text)
    return "".join(
        character
        for character in text
        if character in "\n\t" or (ord(character) >= 32 and not 127 <= ord(character) <= 159)
    )


def emit(data: bytes, stream: TextIO) -> None:
    cleaned = sanitize_output(decode_output(data))
    if cleaned:
        stream.write(cleaned)
        stream.flush()


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def invoke_wsl(arguments: Sequence[str]) -> int:
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        result = subprocess.run(
            ["wsl.exe", *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            creationflags=creation_flags,
        )
    except FileNotFoundError:
        print("wsl.exe was not found. Run this script from Windows.", file=sys.stderr)
        return 127

    emit(result.stdout, sys.stdout)
    emit(result.stderr, sys.stderr)
    return result.returncode


def registry_distributions() -> list[Distribution]:
    if os.name != "nt":
        raise RuntimeError("The WSL registry is available only on Windows.")

    import winreg

    distributions: list[Distribution] = []
    try:
        root_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, LXSS_KEY)
    except FileNotFoundError:
        return distributions

    with root_key as root:
        subkey_count = winreg.QueryInfoKey(root)[0]
        for index in range(subkey_count):
            with winreg.OpenKey(root, winreg.EnumKey(root, index)) as entry:
                try:
                    name = str(winreg.QueryValueEx(entry, "DistributionName")[0])
                    base_path = str(winreg.QueryValueEx(entry, "BasePath")[0])
                    version = int(winreg.QueryValueEx(entry, "Version")[0])
                except FileNotFoundError:
                    continue
                distributions.append(Distribution(name, base_path, version))
    return sorted(distributions, key=lambda item: item.name.casefold())


def normalize_windows_path(path: str) -> str:
    normalized = path.strip().rstrip("\\/")
    if normalized.startswith("\\\\?\\"):
        normalized = normalized[4:]
    return ntpath.normcase(ntpath.normpath(normalized))


def validated_base_path(path: str) -> str:
    normalized = normalize_windows_path(path)
    drive, tail = ntpath.splitdrive(normalized)
    if not drive or tail in {"", "\\"}:
        raise ValueError(f"base path must be an absolute directory below a filesystem root: {path!r}")
    return normalized


def parse_environment(values: Sequence[str]) -> list[str]:
    parsed: list[str] = []
    for value in values:
        name, separator, _content = value.partition("=")
        if not separator or not ENVIRONMENT_NAME.fullmatch(name):
            raise ValueError(f"invalid environment assignment: {value!r}")
        if "\x00" in value:
            raise ValueError("environment assignments cannot contain NUL")
        parsed.append(value)
    return parsed


def run_arguments(args: argparse.Namespace) -> list[str]:
    command = list(args.command)
    if command[:1] == ["--"]:
        command.pop(0)
    if not command:
        raise ValueError("run requires a command after --")

    arguments = ["--distribution", args.distro]
    if args.user:
        arguments.extend(["--user", args.user])
    arguments.extend(["--exec", "env", *ENVIRONMENT, *parse_environment(args.env), *command])
    return arguments


def unregister(args: argparse.Namespace) -> int:
    if args.confirm_destroy != args.distro:
        print("--confirm-destroy must exactly match --distro.", file=sys.stderr)
        return 2

    matches = [item for item in registry_distributions() if item.name == args.distro]
    if len(matches) != 1:
        print(f"Expected exactly one registered distribution named {args.distro!r}.", file=sys.stderr)
        return 2

    actual_path = validated_base_path(matches[0].base_path)
    expected_path = validated_base_path(args.expected_base_path)
    if actual_path != expected_path:
        print(
            f"Base path mismatch for {args.distro!r}: expected {expected_path!r}, "
            f"registered {actual_path!r}.",
            file=sys.stderr,
        )
        return 2

    exit_code = invoke_wsl(["--unregister", args.distro])
    if exit_code:
        return exit_code
    if any(item.name == args.distro for item in registry_distributions()):
        print(f"Distribution {args.distro!r} remains registered.", file=sys.stderr)
        return 1
    print(f"Unregistered {args.distro} from {matches[0].base_path}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run WSL operations with captured and sanitized output."
    )
    commands = parser.add_subparsers(dest="operation", required=True)
    commands.add_parser("list", help="List WSL distributions and state")
    commands.add_parser("registry", help="List registered distribution base paths")

    run = commands.add_parser("run", help="Run a non-interactive command in a distribution")
    run.add_argument("--distro", required=True)
    run.add_argument("--user")
    run.add_argument("--env", action="append", default=[])
    run.add_argument("command", nargs=argparse.REMAINDER)

    terminate = commands.add_parser("terminate", help="Stop one distribution")
    terminate.add_argument("--distro", required=True)
    commands.add_parser("shutdown", help="Stop all WSL distributions")

    remove = commands.add_parser("unregister", help="Permanently destroy one distribution")
    remove.add_argument("--distro", required=True)
    remove.add_argument("--expected-base-path", required=True)
    remove.add_argument("--confirm-destroy", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_output()
    args = build_parser().parse_args(argv)
    try:
        if args.operation == "list":
            return invoke_wsl(["--list", "--verbose"])
        if args.operation == "registry":
            print("Distribution\tVersion\tBasePath")
            for item in registry_distributions():
                print(f"{item.name}\t{item.version}\t{item.base_path}")
            return 0
        if args.operation == "run":
            return invoke_wsl(run_arguments(args))
        if args.operation == "terminate":
            return invoke_wsl(["--terminate", args.distro])
        if args.operation == "shutdown":
            return invoke_wsl(["--shutdown"])
        if args.operation == "unregister":
            return unregister(args)
    except (OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled operation: {args.operation}")


if __name__ == "__main__":
    raise SystemExit(main())
