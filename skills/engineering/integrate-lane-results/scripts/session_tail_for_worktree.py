#!/usr/bin/env python3
"""Find the newest Codex session for a worktree and print its last visible message."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

KEY_VALUE_SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|authorization)(\s*[:=]\s*)([^\s,;]+)"
)
BEARER_SECRET_RE = re.compile(r"(?i)(bearer\s+)[a-z0-9._~+/=-]{12,}")


def default_sessions_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "sessions"
    return Path.home() / ".codex" / "sessions"


def normalize_path(path: str | Path) -> str:
    resolved = Path(path).expanduser().resolve(strict=False)
    return os.path.normcase(os.path.normpath(str(resolved)))


def path_matches(candidate: str, target: str) -> bool:
    try:
        candidate_norm = normalize_path(candidate)
    except (OSError, RuntimeError):
        return False
    if candidate_norm == target:
        return True
    try:
        Path(candidate_norm).relative_to(Path(target))
        return True
    except ValueError:
        return False


def redact(text: str) -> str:
    redacted = KEY_VALUE_SECRET_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", text)
    return BEARER_SECRET_RE.sub(lambda m: f"{m.group(1)}[REDACTED]", redacted)


def truncate(text: str, limit: int) -> str:
    text = redact(re.sub(r"\s+", " ", text.replace("\x00", "")).strip())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts)


def iter_session_files(root: Path) -> Iterable[tuple[float, Path]]:
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False) and entry.name.endswith(".jsonl"):
                            stat = entry.stat(follow_symlinks=False)
                            yield stat.st_mtime, Path(entry.path)
                    except OSError:
                        continue
        except OSError:
            continue


def load_json_line(line: str) -> dict[str, Any] | None:
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def extract_paths_from_record(record: dict[str, Any]) -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    payload = record.get("payload")
    if isinstance(payload, dict):
        cwd = payload.get("cwd")
        if isinstance(cwd, str):
            paths.append(("cwd", cwd))
        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            cwd = metadata.get("cwd")
            if isinstance(cwd, str):
                paths.append(("metadata.cwd", cwd))
        if payload.get("type") in {"function_call", "custom_tool_call"}:
            args_text = payload.get("arguments") or payload.get("input")
            if isinstance(args_text, str):
                try:
                    args = json.loads(args_text)
                except json.JSONDecodeError:
                    args = None
                if isinstance(args, dict):
                    for key in ("workdir", "cwd"):
                        value = args.get(key)
                        if isinstance(value, str):
                            paths.append((key, value))
    return paths


def session_matches(path: Path, target: str, scan_lines: int) -> tuple[bool, str, str | None]:
    matched_by = ""
    matched_path: str | None = None
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_number, line in enumerate(handle, 1):
                if line_number > scan_lines:
                    break
                record = load_json_line(line)
                if not record:
                    continue
                for source, candidate in extract_paths_from_record(record):
                    if path_matches(candidate, target):
                        matched_by = source
                        matched_path = candidate
                        return True, matched_by, matched_path
    except OSError:
        return False, matched_by, matched_path
    return False, matched_by, matched_path


def extract_messages(path: Path, max_text: int) -> dict[str, Any]:
    last_any: dict[str, Any] | None = None
    last_user: dict[str, Any] | None = None
    last_assistant: dict[str, Any] | None = None
    line_count = 0
    first_timestamp: str | None = None
    last_timestamp: str | None = None

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            line_count = line_number
            record = load_json_line(line)
            if not record:
                continue
            timestamp = record.get("timestamp")
            if isinstance(timestamp, str):
                first_timestamp = first_timestamp or timestamp
                last_timestamp = timestamp

            role = ""
            text = ""
            payload = record.get("payload")
            if record.get("type") == "event_msg" and isinstance(payload, dict):
                if payload.get("type") == "user_message":
                    role = "user"
                    text = str(payload.get("message") or "")
                elif payload.get("type") == "agent_message":
                    role = "assistant"
                    text = str(payload.get("message") or "")
            elif record.get("type") == "response_item" and isinstance(payload, dict):
                if payload.get("type") == "message":
                    payload_role = payload.get("role")
                    if payload_role in {"user", "assistant"}:
                        role = str(payload_role)
                        text = text_from_content(payload.get("content"))

            if not role or not text.strip():
                continue
            item = {
                "role": role,
                "line": line_number,
                "timestamp": timestamp,
                "text": truncate(text, max_text),
            }
            last_any = item
            if role == "user":
                last_user = item
            elif role == "assistant":
                last_assistant = item

    return {
        "lineCount": line_count,
        "firstTimestamp": first_timestamp,
        "lastTimestamp": last_timestamp,
        "lastMessage": last_any,
        "lastUserMessage": last_user,
        "lastAssistantMessage": last_assistant,
    }


def choose_message(messages: dict[str, Any], role: str) -> dict[str, Any] | None:
    if role == "assistant":
        return messages.get("lastAssistantMessage")
    if role == "user":
        return messages.get("lastUserMessage")
    return messages.get("lastMessage")


def find_latest(worktree: Path, root: Path, max_files: int, scan_lines: int, max_text: int) -> dict[str, Any] | None:
    target = normalize_path(worktree)
    files = sorted(iter_session_files(root), key=lambda item: item[0], reverse=True)
    scanned = 0
    for mtime, path in files[:max_files]:
        scanned += 1
        matched, matched_by, matched_path = session_matches(path, target, scan_lines)
        if not matched:
            continue
        messages = extract_messages(path, max_text)
        return {
            "worktree": str(worktree),
            "sessionsRoot": str(root),
            "scannedFiles": scanned,
            "session": str(path),
            "sessionMtime": dt.datetime.fromtimestamp(mtime, dt.timezone.utc).isoformat(timespec="seconds"),
            "matchedBy": matched_by,
            "matchedPath": matched_path,
            **messages,
        }
    return {
        "worktree": str(worktree),
        "sessionsRoot": str(root),
        "scannedFiles": scanned,
        "session": None,
    }


def print_text(result: dict[str, Any], role: str) -> int:
    if not result.get("session"):
        print(f"No matching Codex session found for worktree: {result['worktree']}")
        print(f"Sessions root: {result['sessionsRoot']}")
        print(f"Files scanned: {result['scannedFiles']}")
        return 1

    print(f"Session: {result['session']}")
    print(f"Session mtime: {result['sessionMtime']}")
    print(f"Matched by: {result['matchedBy']} = {result.get('matchedPath')}")
    print(f"Files scanned: {result['scannedFiles']}")
    print(f"Session lines: {result['lineCount']}")
    print(f"Session timestamps: {result.get('firstTimestamp')} -> {result.get('lastTimestamp')}")
    message = choose_message(result, role)
    if not message:
        print(f"\nNo {role} message found in matching session.")
        return 1
    print(f"\nLast {role} message:")
    print(f"Role: {message['role']}")
    print(f"Line: {message['line']}")
    print(f"Timestamp: {message.get('timestamp')}")
    print(message["text"])
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worktree", help="Worktree path to match against session cwd/workdir.")
    parser.add_argument("--sessions-root", default=str(default_sessions_root()), help="Defaults to $CODEX_HOME/sessions or ~/.codex/sessions.")
    parser.add_argument("--max-files", type=int, default=2000, help="Newest JSONL files to inspect before giving up.")
    parser.add_argument("--scan-lines", type=int, default=250, help="Lines to scan per file for cwd/workdir match.")
    parser.add_argument("--max-text", type=int, default=2400, help="Maximum characters from the returned message.")
    parser.add_argument("--role", choices=["assistant", "user", "any"], default="assistant", help="Which last visible message to print.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.sessions_root).expanduser()
    worktree = Path(args.worktree).expanduser()
    result = find_latest(worktree, root, max(1, args.max_files), max(1, args.scan_lines), max(200, args.max_text))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("session") else 1
    return print_text(result, args.role)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
