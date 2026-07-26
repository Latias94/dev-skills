#!/usr/bin/env python3
"""Summarize Codex session JSONL files for safe handoff recovery."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any, Deque


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from _recovery_common import (  # noqa: E402,F401
    CODEX_THREAD_ID_ENV_VAR,
    THREAD_ID_RE,
    current_codex_identity,
    default_codex_home,
    load_json_maybe,
    normalize_ws,
    now_utc,
    redact,
    resolve_session,
    rollout_identity,
    same_codex_session,
    sessions_root,
    state_db_path,
    text_from_content,
    truncate,
    valid_thread_id,
)
from _subagent_recovery import (  # noqa: E402,F401
    STATUS_PROBE_CHUNK_BYTES,
    STATUS_PROBE_LIMIT_BYTES,
    STATUS_PROBE_POOL_FLOOR,
    STATUS_PROBE_POOL_MULTIPLIER,
    SUBAGENT_DISPLAY_LIMIT,
    build_subagent_recovery,
    find_rollout_path,
    load_rollout_metadata_graph,
    load_state_graph,
    merge_lineage_graphs,
    merge_present,
    persisted_agent_status,
    probe_persisted_status_tail,
    probe_subagent_rollout,
    read_session_meta,
    session_identity,
    sqlite_table_names,
    thread_spawn_details,
    useful_user_text,
)

from _recovery_render import (  # noqa: E402,F401
    continuation_prompt,
    format_goal,
    git_recovery_commands,
    md_list_item,
    print_markdown,
)


GOAL_RE = re.compile(
    r"<untrusted_objective>\s*(?P<objective>.*?)\s*</untrusted_objective>",
    re.DOTALL,
)


def compact_command(args_text: str, max_text: int) -> dict[str, Any]:
    args = load_json_maybe(args_text)
    if not isinstance(args, dict):
        return {"arguments": truncate(args_text, max_text)}
    result: dict[str, Any] = {}
    for key in ("command", "workdir", "timeout_ms"):
        if key in args:
            value = args[key]
            result[key] = truncate(str(value), max_text if key == "command" else 300)
    return result


def compact_arguments(args_text: str, max_text: int) -> Any:
    args = load_json_maybe(args_text)
    if isinstance(args, dict):
        compact: dict[str, Any] = {}
        for key, value in args.items():
            if key in {"command", "workdir", "timeout_ms"}:
                compact[key] = truncate(str(value), max_text if key == "command" else 300)
            elif isinstance(value, (str, int, float, bool)) or value is None:
                compact[key] = truncate(str(value), 300)
            else:
                compact[key] = truncate(json.dumps(value, ensure_ascii=False), 500)
        return compact
    return truncate(args_text, max_text)


def parse_goal_from_text(text: str) -> dict[str, Any] | None:
    match = GOAL_RE.search(text)
    if not match:
        return None
    goal: dict[str, Any] = {
        "objective": normalize_ws(match.group("objective")),
        "source": "developer_continuation_message",
    }
    budget_match = re.search(r"Budget:\s*(.*?)(?:\n\s*\n|$)", text, re.DOTALL)
    if budget_match:
        goal["budget_text"] = normalize_ws(budget_match.group(1))
    return goal


def parse_goal_output(output: str) -> dict[str, Any] | None:
    data = load_json_maybe(output)
    if not isinstance(data, dict):
        return None
    goal = data.get("goal")
    if not isinstance(goal, dict):
        return None
    result = dict(goal)
    result["remainingTokens"] = data.get("remainingTokens")
    result["completionBudgetReport"] = data.get("completionBudgetReport")
    return result


def parse_patch_changes(payload: dict[str, Any], max_text: int) -> dict[str, Any]:
    changes = payload.get("changes")
    compact_changes: list[str] = []
    if isinstance(changes, dict):
        for path, value in changes.items():
            if isinstance(value, dict):
                change_type = value.get("type", "change")
                move_path = value.get("move_path")
                diff = str(value.get("unified_diff") or "")
                added = 0
                removed = 0
                for diff_line in diff.splitlines():
                    if diff_line.startswith("+++") or diff_line.startswith("---"):
                        continue
                    if diff_line.startswith("+"):
                        added += 1
                    elif diff_line.startswith("-"):
                        removed += 1
                detail = f"{path}: {change_type}, +{added}/-{removed}"
                if move_path:
                    detail += f", move_path={move_path}"
                compact_changes.append(detail)
            else:
                compact_changes.append(truncate(f"{path}: {value}", 300))
    elif isinstance(changes, list):
        compact_changes = [truncate(str(item), 300) for item in changes]
    return {
        "timestamp": payload.get("timestamp"),
        "success": payload.get("success"),
        "status": payload.get("status"),
        "changes": compact_changes[:20],
        "stdout": truncate(str(payload.get("stdout") or ""), max_text),
        "stderr": truncate(str(payload.get("stderr") or ""), max_text),
    }


def summarize_session(
    path: Path,
    recent: int,
    max_text: int,
    include_tool_output: bool,
) -> dict[str, Any]:
    counters: collections.Counter[str] = collections.Counter()
    payload_counters: collections.Counter[str] = collections.Counter()
    users: Deque[dict[str, Any]] = collections.deque(maxlen=recent)
    assistants: Deque[dict[str, Any]] = collections.deque(maxlen=recent)
    tool_calls: Deque[dict[str, Any]] = collections.deque(maxlen=recent)
    shell_commands: Deque[dict[str, Any]] = collections.deque(maxlen=recent)
    tool_outputs: Deque[dict[str, Any]] = collections.deque(maxlen=recent)
    patches: Deque[dict[str, Any]] = collections.deque(maxlen=recent)
    compactions: Deque[dict[str, Any]] = collections.deque(maxlen=3)
    errors: Deque[dict[str, Any]] = collections.deque(maxlen=recent)
    encrypted_reasoning = 0

    call_names: dict[str, str] = {}
    meta: dict[str, Any] = {}
    latest_turn_summary = ""
    latest_goal: dict[str, Any] | None = None
    latest_plan: list[dict[str, Any]] | None = None
    first_ts: str | None = None
    last_ts: str | None = None
    line_count = 0
    bad_json_lines: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            line_count = line_number
            try:
                record = json.loads(line)
            except Exception as exc:
                if len(bad_json_lines) < recent:
                    bad_json_lines.append({"line": line_number, "error": str(exc)})
                continue

            ts = record.get("timestamp")
            if isinstance(ts, str):
                first_ts = first_ts or ts
                last_ts = ts

            record_type = record.get("type")
            counters[str(record_type)] += 1
            payload = record.get("payload")
            if isinstance(payload, dict):
                payload_type = payload.get("type") or payload.get("role") or "<none>"
                payload_counters[f"{record_type}:{payload_type}"] += 1
            else:
                payload_type = "<none>"

            if record_type == "session_meta" and isinstance(payload, dict):
                meta = {k: v for k, v in payload.items() if k not in {"base_instructions"}}

            if record_type == "turn_context" and isinstance(payload, dict):
                summary = payload.get("summary")
                if (
                    isinstance(summary, str)
                    and summary.strip()
                    and summary.strip().lower() not in {"none", "null"}
                ):
                    latest_turn_summary = truncate(summary, max_text * 2)

            if record_type == "compacted" and isinstance(payload, dict):
                compactions.append(
                    {
                        "line": line_number,
                        "timestamp": ts,
                        "message": truncate(str(payload.get("message") or ""), max_text * 3),
                    }
                )

            if record_type == "event_msg" and isinstance(payload, dict):
                kind = payload.get("type")
                if kind == "user_message":
                    users.append(
                        {
                            "line": line_number,
                            "timestamp": ts,
                            "text": truncate(str(payload.get("message") or ""), max_text),
                        }
                    )
                elif kind == "agent_message":
                    assistants.append(
                        {
                            "line": line_number,
                            "timestamp": ts,
                            "phase": payload.get("phase"),
                            "text": truncate(str(payload.get("message") or ""), max_text),
                        }
                    )
                elif kind in {"turn_aborted", "error"}:
                    errors.append(
                        {
                            "line": line_number,
                            "timestamp": ts,
                            "type": kind,
                            "text": truncate(json.dumps(payload, ensure_ascii=False), max_text),
                        }
                    )
                elif kind == "patch_apply_end":
                    patch = parse_patch_changes(payload, max_text)
                    patch["line"] = line_number
                    patch["timestamp"] = ts
                    patches.append(patch)

            if record_type != "response_item" or not isinstance(payload, dict):
                raw = line.lower()
                if "invalid_encrypted_content" in raw or "encrypted content could not" in raw:
                    errors.append(
                        {
                            "line": line_number,
                            "timestamp": ts,
                            "type": "encrypted_content_error",
                            "text": truncate(line, max_text),
                        }
                    )
                continue

            item_type = payload.get("type")

            if item_type == "reasoning" and payload.get("encrypted_content"):
                encrypted_reasoning += 1

            if item_type == "message":
                role = payload.get("role")
                text = text_from_content(payload.get("content"))
                if role == "developer":
                    parsed_goal = parse_goal_from_text(text)
                    if parsed_goal:
                        parsed_goal.update({"line": line_number, "timestamp": ts})
                        latest_goal = parsed_goal
                elif role == "user":
                    short = truncate(text, max_text)
                    if short and "AGENTS.md instructions" not in short:
                        users.append({"line": line_number, "timestamp": ts, "text": short})
                elif role == "assistant":
                    short = truncate(text, max_text)
                    if short:
                        assistants.append(
                            {
                                "line": line_number,
                                "timestamp": ts,
                                "phase": payload.get("phase"),
                                "text": short,
                            }
                        )

            elif item_type in {"function_call", "custom_tool_call"}:
                call_id = payload.get("call_id")
                name = str(payload.get("name") or item_type)
                if isinstance(call_id, str):
                    call_names[call_id] = name
                args_text = str(payload.get("arguments") or payload.get("input") or "")
                compact_args = compact_arguments(args_text, max_text)
                entry = {
                    "line": line_number,
                    "timestamp": ts,
                    "name": name,
                    "arguments": compact_args,
                }
                tool_calls.append(entry)
                if name == "shell_command":
                    shell_commands.append(
                        {
                            "line": line_number,
                            "timestamp": ts,
                            **compact_command(args_text, max_text),
                        }
                    )
                if name == "update_plan":
                    args = load_json_maybe(args_text)
                    if isinstance(args, dict) and isinstance(args.get("plan"), list):
                        latest_plan = args["plan"]

            elif item_type in {"function_call_output", "custom_tool_call_output"}:
                call_id = payload.get("call_id")
                name = call_names.get(call_id, str(item_type))
                output = str(payload.get("output") or "")
                if name in {"create_goal", "get_goal", "update_goal"}:
                    parsed = parse_goal_output(output)
                    if parsed:
                        parsed.update({"line": line_number, "timestamp": ts, "source": name})
                        latest_goal = parsed
                if include_tool_output or "invalid_encrypted_content" in output.lower():
                    tool_outputs.append(
                        {
                            "line": line_number,
                            "timestamp": ts,
                            "name": name,
                            "output": truncate(output, max_text),
                        }
                    )
                if (
                    "invalid_encrypted_content" in output.lower()
                    or "encrypted content could not" in output.lower()
                ):
                    errors.append(
                        {
                            "line": line_number,
                            "timestamp": ts,
                            "type": "encrypted_content_error",
                            "text": truncate(output, max_text),
                        }
                    )

    return {
        "generatedAt": now_utc(),
        "source": str(path),
        "sizeBytes": path.stat().st_size,
        "lineCount": line_count,
        "firstTimestamp": first_ts,
        "lastTimestamp": last_ts,
        "meta": meta,
        "notes": [],
        "eventCounts": dict(counters.most_common()),
        "payloadCounts": dict(payload_counters.most_common(20)),
        "encryptedReasoningItems": encrypted_reasoning,
        "badJsonLines": bad_json_lines,
        "activeGoal": latest_goal,
        "latestTurnSummary": latest_turn_summary,
        "latestCompactions": list(compactions),
        "recentUserMessages": list(users),
        "recentAssistantMessages": list(assistants),
        "latestPlan": latest_plan,
        "recentToolCalls": list(tool_calls),
        "recentShellCommands": list(shell_commands),
        "recentToolOutputs": list(tool_outputs),
        "patchEvents": list(patches),
        "errors": list(errors),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "session",
        help="Prior session path, rollout filename, id fragment, or explicit 'latest'.",
    )
    parser.add_argument(
        "--sessions-root",
        help=(
            "Override the sessions root. Defaults to $CODEX_HOME/sessions or "
            "~/.codex/sessions."
        ),
    )
    parser.add_argument(
        "--recent",
        type=int,
        default=8,
        help="Number of recent messages/tool calls to keep.",
    )
    parser.add_argument(
        "--max-text",
        type=int,
        default=1600,
        help="Maximum characters per extracted text block.",
    )
    parser.add_argument(
        "--max-subagents",
        type=int,
        default=SUBAGENT_DISPLAY_LIMIT,
        help=(
            "Maximum subagent descendants to probe and report, prioritized by "
            "resumability and recency."
        ),
    )
    parser.add_argument(
        "--state-db",
        help=(
            "Override the read-only Codex state_5.sqlite path used for persisted "
            "subagent lineage."
        ),
    )
    parser.add_argument(
        "--scan-rollout-lineage",
        action="store_true",
        help=(
            "Augment state DB edges by scanning all rollout metadata for older or "
            "incomplete lineage."
        ),
    )
    parser.add_argument(
        "--no-subagents",
        action="store_true",
        help="Skip persisted subagent lineage and rollout probing.",
    )
    parser.add_argument(
        "--include-tool-output",
        action="store_true",
        help=(
            "Include recent tool outputs. Off by default to reduce sensitive "
            "context leakage."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    return parser.parse_args(argv)


def primary_summary_path(
    selected_path: Path,
    subagents: dict[str, Any] | None,
) -> tuple[Path, bool, str | None]:
    if not subagents or not subagents.get("available"):
        return selected_path, False, None
    if subagents.get("selectedThreadIsRoot"):
        return selected_path, False, None

    root_value = subagents.get("rootRolloutPath")
    root_path = Path(root_value) if isinstance(root_value, str) and root_value else None
    if root_path is not None and root_path.is_file():
        return root_path, True, None
    return (
        selected_path,
        False,
        "The selected rollout belongs to a subagent, but its family root rollout "
        "could not be read; kept the child as the primary summary.",
    )


def recovery_boundary(
    summary: dict[str, Any],
    requested_path: Path,
    primary_path: Path,
    receiving_identity: dict[str, str | None],
) -> dict[str, Any]:
    meta = summary.get("meta") or {}
    source_identity = {
        "threadId": valid_thread_id(meta.get("id")),
        "sessionId": valid_thread_id(meta.get("session_id")),
    }
    return {
        "sourceRole": "historical_recovery_source",
        "sourcePath": str(primary_path),
        "requestedPath": str(requested_path),
        "sourceThreadId": meta.get("id"),
        "sourceSessionId": source_identity.get("sessionId"),
        "receivingThreadId": receiving_identity.get("threadId"),
        "receivingSessionId": receiving_identity.get("sessionId"),
        "sourceIsReceivingSession": same_codex_session(
            source_identity,
            receiving_identity,
        ),
        "authorityAfterHandoff": "receiving_or_resumed_session",
        "ordinaryCompactionAction": "continue_current_session",
        "rerunPolicy": "explicit_cross_session_recovery_only",
    }


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = sessions_root(args.sessions_root)
    try:
        selected_path, notes = resolve_session(args.session, root)
        receiving_identity = current_codex_identity(root)
        if receiving_identity.get("threadId") and same_codex_session(
            rollout_identity(selected_path),
            receiving_identity,
        ):
            raise ValueError(
                "The selected rollout belongs to the current receiving Codex session. "
                "Ordinary compaction is continuation, not cross-session recovery; "
                "provide a different prior session path or id."
            )
        subagents = None
        if not args.no_subagents:
            subagents = build_subagent_recovery(
                selected_path,
                root,
                state_db_path(args.state_db, root),
                max(1, args.max_subagents),
                max(200, args.max_text),
                args.scan_rollout_lineage,
            )
        summary_path, promoted, promotion_note = primary_summary_path(
            selected_path,
            subagents,
        )
        if promoted:
            notes.append(
                "Selected a subagent rollout; promoted its family root to the primary summary."
            )
        elif promotion_note:
            notes.append(promotion_note)

        summary = summarize_session(
            summary_path,
            max(1, args.recent),
            max(200, args.max_text),
            args.include_tool_output,
        )
        summary["selection"] = {
            "requestedPath": str(selected_path),
            "primaryPath": str(summary_path),
            "promotedToRoot": promoted,
        }
        summary["recoveryBoundary"] = recovery_boundary(
            summary,
            selected_path,
            summary_path,
            receiving_identity,
        )
        if subagents is not None:
            summary["subagents"] = subagents
        summary["notes"] = notes
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_markdown(summary)
        if notes:
            print("\n## Resolution Notes")
            for note in notes:
                print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
