#!/usr/bin/env python3
"""Find stale Codex subagents from session logs."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


AGENT_ID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.I,
)
NOTIFICATION_RE = re.compile(
    r"<subagent_notification>\s*(.*?)\s*</subagent_notification>",
    re.S,
)


@dataclass
class AgentRecord:
    agent_id: str
    session_path: str = ""
    session_id: str = ""
    agent_type: str = ""
    nickname: str = ""
    spawn_time: datetime | None = None
    last_event_time: datetime | None = None
    status: str = "spawned"
    closed: bool = False
    shutdown: bool = False
    close_time: datetime | None = None
    source_line: int = 0
    events: list[str] = field(default_factory=list)

    def age_hours(self, now: datetime) -> float | None:
        if self.spawn_time is None:
            return None
        return max(0.0, (now - self.spawn_time).total_seconds() / 3600)

    def to_dict(self, now: datetime) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "nickname": self.nickname,
            "agent_type": self.agent_type,
            "status": self.status,
            "closed": self.closed,
            "shutdown": self.shutdown,
            "age_hours": round(self.age_hours(now), 2) if self.age_hours(now) is not None else None,
            "session_id": self.session_id,
            "session_path": self.session_path,
            "source_line": self.source_line,
            "events": self.events,
        }


@dataclass
class SessionScan:
    files_scanned: int
    spawn_failures: int
    agents: dict[str, AgentRecord]


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured)
    return Path.home() / ".codex"


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.astimezone()
    return parsed.astimezone()


def now_local() -> datetime:
    return datetime.now().astimezone()


def load_json_object(text: object) -> Any:
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def shorten(text: str, limit: int = 160) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."


def iter_session_files(
    root: Path,
    explicit_paths: list[Path],
    days: float,
    max_files: int,
) -> list[Path]:
    if explicit_paths:
        return [path.expanduser() for path in explicit_paths]

    sessions_root = root / "sessions"
    if not sessions_root.exists():
        return []

    cutoff = now_local() - timedelta(days=days)
    files = [
        path
        for path in sessions_root.rglob("*.jsonl")
        if datetime.fromtimestamp(path.stat().st_mtime).astimezone() >= cutoff
    ]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return files[:max_files]


def content_texts(payload: dict[str, Any]) -> list[str]:
    content = payload.get("content")
    if not isinstance(content, list):
        return []
    texts: list[str] = []
    for item in content:
        if isinstance(item, dict):
            text = item.get("text") or item.get("input_text") or item.get("output_text")
            if isinstance(text, str):
                texts.append(text)
    return texts


def update_from_notification(
    records: dict[str, AgentRecord],
    text: str,
    timestamp: datetime | None,
    session_path: Path,
    session_id: str,
) -> None:
    for match in NOTIFICATION_RE.finditer(text):
        payload = load_json_object(match.group(1))
        if not isinstance(payload, dict):
            continue

        agent_id = payload.get("agent_path")
        if not isinstance(agent_id, str) or not AGENT_ID_RE.fullmatch(agent_id):
            continue

        record = records.setdefault(
            agent_id,
            AgentRecord(agent_id=agent_id, session_path=str(session_path), session_id=session_id),
        )
        record.last_event_time = timestamp or record.last_event_time
        status = payload.get("status")
        if status == "shutdown":
            record.shutdown = True
            record.status = "shutdown"
            record.events.append("notification: shutdown")
        elif isinstance(status, dict) and "completed" in status:
            record.status = "completed"
            record.events.append("notification: completed")
        elif isinstance(status, str):
            record.status = status
            record.events.append(f"notification: {status}")


def scan_session_file(path: Path, records: dict[str, AgentRecord]) -> tuple[int, int]:
    pending_spawns: dict[str, dict[str, Any]] = {}
    spawn_failures = 0
    session_id = ""

    try:
        handle = path.open("r", encoding="utf-8")
    except OSError:
        return 0, 0

    with handle:
        for line_no, line in enumerate(handle, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            timestamp = parse_time(row.get("timestamp"))
            payload = row.get("payload")
            if not isinstance(payload, dict):
                continue

            if row.get("type") == "session_meta":
                meta = payload
                if isinstance(meta.get("id"), str):
                    session_id = meta["id"]
                continue

            payload_type = payload.get("type")
            if payload_type == "function_call" and payload.get("namespace") == "multi_agent_v1":
                name = payload.get("name")
                call_id = payload.get("call_id")
                args = load_json_object(payload.get("arguments"))
                if not isinstance(call_id, str):
                    continue

                if name == "spawn_agent":
                    pending_spawns[call_id] = {
                        "timestamp": timestamp,
                        "line": line_no,
                        "args": args if isinstance(args, dict) else {},
                    }
                elif name == "close_agent" and isinstance(args, dict):
                    target = args.get("target")
                    if isinstance(target, str) and AGENT_ID_RE.fullmatch(target):
                        record = records.setdefault(
                            target,
                            AgentRecord(
                                agent_id=target,
                                session_path=str(path),
                                session_id=session_id,
                            ),
                        )
                        record.closed = True
                        record.close_time = timestamp
                        record.last_event_time = timestamp or record.last_event_time
                        record.events.append("close_agent called")

            elif payload_type == "function_call_output":
                call_id = payload.get("call_id")
                output = payload.get("output")
                if isinstance(call_id, str) and call_id in pending_spawns:
                    spawn = pending_spawns.pop(call_id)
                    parsed = load_json_object(output)
                    if isinstance(parsed, dict) and isinstance(parsed.get("agent_id"), str):
                        agent_id = parsed["agent_id"]
                        record = records.setdefault(
                            agent_id,
                            AgentRecord(
                                agent_id=agent_id,
                                session_path=str(path),
                                session_id=session_id,
                            ),
                        )
                        args = spawn.get("args") if isinstance(spawn.get("args"), dict) else {}
                        record.spawn_time = spawn.get("timestamp")
                        record.last_event_time = timestamp or record.last_event_time
                        record.source_line = int(spawn.get("line") or 0)
                        record.agent_type = str(args.get("agent_type") or record.agent_type or "")
                        record.nickname = str(parsed.get("nickname") or record.nickname or "")
                        record.session_path = str(path)
                        record.session_id = session_id
                        record.events.append("spawn_agent succeeded")
                    else:
                        spawn_failures += 1

            elif payload_type == "message":
                for text in content_texts(payload):
                    update_from_notification(records, text, timestamp, path, session_id)

    return 1, spawn_failures


def scan_sessions(args: argparse.Namespace) -> SessionScan:
    records: dict[str, AgentRecord] = {}
    files = iter_session_files(args.codex_home, args.session, args.days, args.max_files)
    files_scanned = 0
    spawn_failures = 0
    for path in files:
        scanned, failures = scan_session_file(path, records)
        files_scanned += scanned
        spawn_failures += failures
    return SessionScan(files_scanned=files_scanned, spawn_failures=spawn_failures, agents=records)


def session_groups(
    scan: SessionScan,
    min_completed_idle_minutes: float,
) -> tuple[list[AgentRecord], list[AgentRecord], list[AgentRecord]]:
    current = now_local()
    close_candidates: list[AgentRecord] = []
    recent_completed: list[AgentRecord] = []
    active_agents: list[AgentRecord] = []
    for record in scan.agents.values():
        if record.closed or record.shutdown:
            continue
        if record.status == "completed":
            age = record.age_hours(current)
            if age is None:
                recent_completed.append(record)
            elif age * 60 >= min_completed_idle_minutes:
                close_candidates.append(record)
            else:
                recent_completed.append(record)
            continue
        active_agents.append(record)

    fallback_time = current - timedelta(days=36500)
    close_candidates.sort(key=lambda item: item.spawn_time or fallback_time)
    recent_completed.sort(key=lambda item: item.spawn_time or fallback_time)
    active_agents.sort(key=lambda item: item.spawn_time or fallback_time)
    return close_candidates, recent_completed, active_agents


def print_session_report(scan: SessionScan, args: argparse.Namespace) -> None:
    current = now_local()
    close_candidates, recent_completed, active_agents = session_groups(
        scan,
        args.min_completed_idle_minutes,
    )
    closed_count = sum(1 for record in scan.agents.values() if record.closed or record.shutdown)

    print("Session scan")
    print(f"- files scanned: {scan.files_scanned}")
    print(f"- agents observed: {len(scan.agents)}")
    print(f"- already closed or shutdown: {closed_count}")
    print(f"- spawn failures observed: {scan.spawn_failures}")
    print(f"- ready to close: {len(close_candidates)}")
    print(
        f"- completed but younger than {args.min_completed_idle_minutes:.0f} minutes: "
        f"{len(recent_completed)}"
    )
    print(f"- still active: {len(active_agents)}")

    if close_candidates:
        print("\nClose these with multi_agent_v1.close_agent:")
        print("If close_agent returns not found, the historical agent is no longer in the registry.")
        for record in close_candidates:
            age = record.age_hours(current)
            age_text = f"{age:.1f}h" if age is not None else "unknown age"
            label = " ".join(part for part in [record.nickname, record.agent_type] if part)
            print(f"- {record.agent_id}  status={record.status} age={age_text} {label}".rstrip())
            if record.session_path:
                print(f"  session={record.session_path}")

    if recent_completed:
        print(
            f"\nRecently completed agents under {args.min_completed_idle_minutes:.0f} minutes:"
        )
        for record in recent_completed:
            age = record.age_hours(current)
            age_text = f"{age:.1f}h" if age is not None else "unknown age"
            print(f"- {record.agent_id}  status={record.status} age={age_text}")

    if active_agents:
        print("\nActive agents still running:")
        for record in active_agents:
            age = record.age_hours(current)
            age_text = f"{age:.1f}h" if age is not None else "unknown age"
            print(f"- {record.agent_id}  status={record.status} age={age_text}")


def emit_json(
    session_scan: SessionScan | None,
    args: argparse.Namespace,
) -> None:
    current = now_local()
    data: dict[str, Any] = {"generated_at": current.isoformat()}
    if session_scan is not None:
        close_candidates, recent_completed, active_agents = session_groups(
            session_scan,
            args.min_completed_idle_minutes,
        )
        data["sessions"] = {
            "files_scanned": session_scan.files_scanned,
            "spawn_failures": session_scan.spawn_failures,
            "agents_observed": len(session_scan.agents),
            "close_candidates": [record.to_dict(current) for record in close_candidates],
            "recent_completed": [record.to_dict(current) for record in recent_completed],
            "active_agents": [record.to_dict(current) for record in active_agents],
        }
    print(json.dumps(data, indent=2, ensure_ascii=False))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run stale Codex subagent cleanup from session logs."
    )
    parser.add_argument("--mode", choices=["sessions"], default="sessions")
    parser.add_argument("--codex-home", type=Path, default=codex_home())
    parser.add_argument(
        "--session",
        action="append",
        type=Path,
        default=[],
        help="Specific Codex session JSONL file to scan. Can be passed multiple times.",
    )
    parser.add_argument("--days", type=float, default=3, help="Recent session window to scan.")
    parser.add_argument("--max-files", type=int, default=200, help="Maximum session files to scan.")
    parser.add_argument(
        "--min-completed-idle-minutes",
        type=float,
        default=30,
        help="Minimum idle minutes before a completed agent is recommended for closure.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    session_scan: SessionScan | None = None

    session_scan = scan_sessions(args)

    if args.json:
        emit_json(session_scan, args)
        return 0

    if session_scan is not None:
        print_session_report(session_scan, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
