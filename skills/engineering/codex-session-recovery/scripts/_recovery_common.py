"""Shared parsing and path utilities for Codex session recovery."""

from __future__ import annotations

import datetime as dt
import glob
import json
import os
import re
from pathlib import Path
from typing import Any


KEY_VALUE_SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|authorization)(\s*[:=]\s*)([^\s,;]+)"
)
BEARER_SECRET_RE = re.compile(r"(?i)(bearer\s+)[a-z0-9._~+/=-]{12,}")
THREAD_ID_RE = re.compile(
    r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
)
CODEX_THREAD_ID_ENV_VAR = "CODEX_THREAD_ID"


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def default_codex_home() -> Path:
    env = os.environ.get("CODEX_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".codex"


def sessions_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    return default_codex_home() / "sessions"


def state_db_path(explicit: str | None, root: Path) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    sqlite_home = os.environ.get("CODEX_SQLITE_HOME")
    if sqlite_home:
        return Path(sqlite_home).expanduser() / "state_5.sqlite"
    if root.name.lower() == "sessions":
        return root.parent / "state_5.sqlite"
    return default_codex_home() / "state_5.sqlite"


def valid_thread_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value if THREAD_ID_RE.fullmatch(value) else None


def redact(text: str) -> str:
    redacted = KEY_VALUE_SECRET_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", text)
    return BEARER_SECRET_RE.sub(lambda m: f"{m.group(1)}[REDACTED]", redacted)


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\x00", "")).strip()


def truncate(text: str, limit: int) -> str:
    text = redact(text.strip())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def load_json_maybe(text: Any) -> Any:
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if isinstance(item, dict):
            value = item.get("text")
            if isinstance(value, str):
                parts.append(value)
    return "\n".join(parts)


def rollout_identity(path: Path) -> dict[str, str | None]:
    identity: dict[str, str | None] = {"threadId": None, "sessionId": None}
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for _ in range(32):
                line = handle.readline()
                if not line:
                    break
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") != "session_meta":
                    continue
                payload = record.get("payload")
                if not isinstance(payload, dict):
                    break
                identity["threadId"] = valid_thread_id(payload.get("id"))
                identity["sessionId"] = valid_thread_id(payload.get("session_id"))
                break
    except OSError:
        pass
    return identity


def current_codex_identity(
    root: Path,
    candidates: list[Path] | None = None,
) -> dict[str, str | None]:
    current_thread_id = valid_thread_id(os.environ.get(CODEX_THREAD_ID_ENV_VAR))
    identity: dict[str, str | None] = {
        "threadId": current_thread_id,
        "sessionId": current_thread_id,
    }
    if current_thread_id is None:
        return identity

    paths = candidates if candidates is not None else list(root.rglob("*.jsonl"))
    for path in paths:
        if current_thread_id.lower() not in path.name.lower():
            continue
        candidate_identity = rollout_identity(path)
        if candidate_identity.get("threadId") != current_thread_id:
            continue
        identity["sessionId"] = candidate_identity.get("sessionId") or current_thread_id
        return identity
    return identity


def same_codex_session(
    left: dict[str, str | None],
    right: dict[str, str | None],
) -> bool:
    left_thread = left.get("threadId")
    right_thread = right.get("threadId")
    if left_thread is not None and left_thread == right_thread:
        return True
    left_session = left.get("sessionId")
    right_session = right.get("sessionId")
    return left_session is not None and left_session == right_session


def resolve_session(spec: str | None, root: Path) -> tuple[Path, list[str]]:
    notes: list[str] = []
    root = root.expanduser()

    if not spec or spec.lower() == "latest":
        matches = list(root.rglob("*.jsonl"))
        if not matches:
            raise FileNotFoundError(f"No .jsonl sessions found under {root}")
        current_identity = current_codex_identity(root, matches)
        skipped_current = 0
        for candidate in sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True):
            if current_identity.get("threadId") and same_codex_session(
                rollout_identity(candidate),
                current_identity,
            ):
                skipped_current += 1
                continue
            if skipped_current:
                notes.append(
                    f"Excluded {skipped_current} newer rollout(s) from the current "
                    "Codex session while resolving 'latest'."
                )
            return candidate, notes
        current_thread_id = current_identity.get("threadId")
        raise FileNotFoundError(
            "No previous Codex session found after excluding the current receiving "
            f"session ({current_thread_id}); provide an explicit prior path or id."
        )

    expanded = Path(spec).expanduser()
    if expanded.exists():
        return expanded, notes

    glob_matches = [Path(p) for p in glob.glob(spec)]
    glob_matches = [p for p in glob_matches if p.is_file()]
    if glob_matches:
        chosen = max(glob_matches, key=lambda p: p.stat().st_mtime)
        if len(glob_matches) > 1:
            notes.append(f"Matched {len(glob_matches)} files from glob; chose newest.")
        return chosen, notes

    needle = spec.lower()
    matches = [
        p
        for p in root.rglob("*.jsonl")
        if needle in p.name.lower() or needle in str(p).lower()
    ]
    if not matches:
        raise FileNotFoundError(f"No session matching {spec!r} under {root}")

    chosen = max(matches, key=lambda p: p.stat().st_mtime)
    if len(matches) > 1:
        notes.append(f"Matched {len(matches)} sessions; chose newest modified file.")
    return chosen, notes
