"""Recover persisted Codex subagent lineage and continuation candidates."""

from __future__ import annotations

import collections
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Deque

from _recovery_common import (
    THREAD_ID_RE,
    load_json_maybe,
    text_from_content,
    truncate,
    valid_thread_id,
)


SUBAGENT_DISPLAY_LIMIT = 24
STATUS_PROBE_CHUNK_BYTES = 64 * 1024
STATUS_PROBE_LIMIT_BYTES = 8 * 1024 * 1024
STATUS_PROBE_POOL_FLOOR = 128
STATUS_PROBE_POOL_MULTIPLIER = 8
STATUS_MARKER_OVERLAP_BYTES = 128
STATUS_RECORD_LIMIT_BYTES = 256 * 1024
STATUS_MARKER_RE = re.compile(
    br'"type"\s*:\s*"(?:turn_started|turn_complete|turn_aborted|error|shutdown_complete)"'
)


def thread_spawn_details(meta: dict[str, Any]) -> dict[str, Any]:
    source = meta.get("source")
    if not isinstance(source, dict):
        return {}
    subagent = source.get("subagent") or source.get("SubAgent")
    if not isinstance(subagent, dict):
        return {}
    spawn = subagent.get("thread_spawn") or subagent.get("ThreadSpawn")
    return spawn if isinstance(spawn, dict) else {}


def session_identity(meta: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    spawn = thread_spawn_details(meta)
    thread_id = valid_thread_id(meta.get("id"))
    if thread_id is None and path is not None:
        match = THREAD_ID_RE.search(path.name)
        thread_id = match.group(0) if match else None

    def first_string(*values: Any) -> str | None:
        return next((value for value in values if isinstance(value, str) and value), None)

    def first_thread_id(*values: Any) -> str | None:
        for value in values:
            candidate = valid_thread_id(value)
            if candidate is not None:
                return candidate
        return None

    depth = spawn.get("depth")
    return {
        "threadId": thread_id,
        "sessionId": meta.get("session_id") if isinstance(meta.get("session_id"), str) else None,
        "parentThreadId": first_thread_id(
            meta.get("parent_thread_id"),
            spawn.get("parent_thread_id"),
        ),
        "depth": depth if isinstance(depth, int) else None,
        "agentPath": first_string(meta.get("agent_path"), spawn.get("agent_path")),
        "agentNickname": first_string(meta.get("agent_nickname"), spawn.get("agent_nickname")),
        "agentRole": first_string(
            meta.get("agent_role"),
            meta.get("agent_type"),
            spawn.get("agent_role"),
            spawn.get("agent_type"),
        ),
        "multiAgentVersion": meta.get("multi_agent_version"),
        "cwd": str(meta.get("cwd")) if meta.get("cwd") else None,
        "cliVersion": meta.get("cli_version"),
        "rolloutPath": str(path) if path is not None else None,
    }


def read_session_meta(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                payload = record.get("payload")
                if record.get("type") == "session_meta" and isinstance(payload, dict):
                    return payload
    except OSError:
        return {}
    return {}


def sqlite_table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    return {str(row[0]) for row in rows}


def load_state_graph(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, [f"State DB not found at {path}; falling back to rollout metadata."]

    connection: sqlite3.Connection | None = None
    try:
        uri = f"{path.resolve().as_uri()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True, timeout=2.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        tables = sqlite_table_names(connection)
        if "thread_spawn_edges" not in tables or "threads" not in tables:
            return None, ["State DB does not contain the persisted subagent graph tables."]

        thread_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(threads)")
        }
        optional_columns = (
            "rollout_path",
            "agent_path",
            "agent_nickname",
            "agent_role",
            "updated_at_ms",
            "thread_source",
            "multi_agent_version",
        )
        selected_columns = [
            f't."{column}" AS "{column}"'
            if column in thread_columns
            else f'NULL AS "{column}"'
            for column in optional_columns
        ]
        query = f"""
SELECT
    e.parent_thread_id,
    e.child_thread_id,
    e.status,
    {", ".join(selected_columns)}
FROM thread_spawn_edges AS e
LEFT JOIN threads AS t ON t.id = e.child_thread_id
"""
        edges: list[dict[str, Any]] = []
        threads: dict[str, dict[str, Any]] = {}
        invalid_edge_count = 0
        for row in connection.execute(query):
            parent = valid_thread_id(row["parent_thread_id"])
            child = valid_thread_id(row["child_thread_id"])
            if parent is None or child is None:
                invalid_edge_count += 1
                continue
            status = str(row["status"])
            edges.append(
                {
                    "parentThreadId": parent,
                    "childThreadId": child,
                    "edgeStatus": status,
                }
            )
            threads[child] = {
                "threadId": child,
                "parentThreadId": parent,
                "edgeStatus": status,
                "rolloutPath": row["rollout_path"],
                "agentPath": row["agent_path"],
                "agentNickname": row["agent_nickname"],
                "agentRole": row["agent_role"],
                "updatedAtMs": row["updated_at_ms"],
                "threadSource": row["thread_source"],
                "multiAgentVersion": row["multi_agent_version"],
            }
        notes = []
        if invalid_edge_count:
            notes.append(
                f"Ignored {invalid_edge_count} spawn edges with invalid thread ids in the state DB."
            )
        return {
            "source": "state_db",
            "edges": edges,
            "threads": threads,
            "stateDb": str(path),
        }, notes
    except (OSError, sqlite3.Error) as exc:
        return None, [f"Could not read the state DB ({exc}); falling back to rollout metadata."]
    finally:
        if connection is not None:
            connection.close()


def load_rollout_metadata_graph(root: Path) -> dict[str, Any]:
    edges_by_child: dict[str, dict[str, Any]] = {}
    threads: dict[str, dict[str, Any]] = {}
    if not root.is_dir():
        return {"source": "rollout_metadata_scan", "edges": [], "threads": threads}

    for path in root.rglob("*.jsonl"):
        meta = read_session_meta(path)
        if not meta:
            continue
        identity = session_identity(meta, path)
        thread_id = identity.get("threadId")
        if not isinstance(thread_id, str):
            continue
        try:
            identity["updatedAtMs"] = int(path.stat().st_mtime * 1000)
        except OSError:
            identity["updatedAtMs"] = None
        previous = threads.get(thread_id)
        previous_updated = previous.get("updatedAtMs") if previous else None
        current_updated = identity.get("updatedAtMs")
        if (
            isinstance(previous_updated, (int, float))
            and isinstance(current_updated, (int, float))
            and previous_updated >= current_updated
        ):
            continue
        identity["edgeStatus"] = "unknown"
        threads[thread_id] = identity
        parent = identity.get("parentThreadId")
        if isinstance(parent, str):
            edges_by_child[thread_id] = {
                "parentThreadId": parent,
                "childThreadId": thread_id,
                "edgeStatus": "unknown",
            }
        else:
            edges_by_child.pop(thread_id, None)
    return {
        "source": "rollout_metadata_scan",
        "edges": list(edges_by_child.values()),
        "threads": threads,
    }


def merge_present(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    merged.update(
        {
            key: value
            for key, value in overlay.items()
            if value is not None and value != ""
        }
    )
    return merged


def merge_lineage_graphs(
    state_graph: dict[str, Any],
    metadata_graph: dict[str, Any],
) -> dict[str, Any]:
    edges_by_child = {
        edge["childThreadId"]: edge
        for edge in metadata_graph.get("edges") or []
        if isinstance(edge.get("childThreadId"), str)
    }
    edges_by_child.update(
        {
            edge["childThreadId"]: edge
            for edge in state_graph.get("edges") or []
            if isinstance(edge.get("childThreadId"), str)
        }
    )

    threads = {
        thread_id: dict(details)
        for thread_id, details in (state_graph.get("threads") or {}).items()
    }
    for thread_id, details in (metadata_graph.get("threads") or {}).items():
        threads[thread_id] = merge_present(threads.get(thread_id, {}), details)

    return {
        "source": "state_db+rollout_metadata_scan",
        "edges": list(edges_by_child.values()),
        "threads": threads,
        "stateDb": state_graph.get("stateDb"),
    }


def persisted_agent_status(payload: dict[str, Any]) -> tuple[str, str | None] | None:
    kind = payload.get("type")
    if kind == "turn_started":
        return "running", None
    if kind == "turn_complete":
        return "completed", None
    if kind == "turn_aborted":
        reason = str(payload.get("reason") or "unknown")
        if reason in {"interrupted", "budget_limited"}:
            return "interrupted", reason
        return "errored", reason
    if kind == "error":
        return "errored", str(payload.get("message") or "error")
    if kind == "shutdown_complete":
        return "shutdown", None
    return None


def probe_persisted_status_tail(
    path: Path,
    max_bytes: int = STATUS_PROBE_LIMIT_BYTES,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "lastKnownStatus": "unknown",
        "lastKnownStatusDetail": None,
        "lastKnownStatusTimestamp": None,
        "statusProbeBytes": 0,
        "statusProbeTruncated": False,
    }

    def event_record_at_offset(handle: Any, offset: int) -> dict[str, Any] | None:
        prefix_size = min(STATUS_PROBE_CHUNK_BYTES, offset)
        handle.seek(offset - prefix_size)
        prefix = handle.read(prefix_size)
        newline = prefix.rfind(b"\n")
        if newline < 0 and offset > prefix_size:
            return None
        line_start = offset - prefix_size + newline + 1
        handle.seek(line_start)
        raw_line = handle.readline(STATUS_RECORD_LIMIT_BYTES)
        try:
            record = json.loads(raw_line)
        except Exception:
            return None
        return record if isinstance(record, dict) else None

    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            position = handle.tell()
            later_prefix = b""
            while position > 0 and result["statusProbeBytes"] < max_bytes:
                remaining = max_bytes - int(result["statusProbeBytes"])
                read_size = min(STATUS_PROBE_CHUNK_BYTES, position, remaining)
                position -= read_size
                handle.seek(position)
                block = handle.read(read_size)
                result["statusProbeBytes"] += len(block)

                search_block = block + later_prefix
                for match in reversed(list(STATUS_MARKER_RE.finditer(search_block))):
                    record = event_record_at_offset(handle, position + match.start())
                    if record is None:
                        continue
                    payload = record.get("payload")
                    if record.get("type") != "event_msg" or not isinstance(payload, dict):
                        continue
                    lifecycle = persisted_agent_status(payload)
                    if lifecycle is None:
                        continue
                    status, detail = lifecycle
                    result["lastKnownStatus"] = status
                    result["lastKnownStatusDetail"] = (
                        truncate(detail, 300) if detail else None
                    )
                    timestamp = record.get("timestamp")
                    result["lastKnownStatusTimestamp"] = (
                        timestamp if isinstance(timestamp, str) else None
                    )
                    return result
                later_prefix = block[:STATUS_MARKER_OVERLAP_BYTES]

            result["statusProbeTruncated"] = position > 0
    except OSError as exc:
        result["statusProbeError"] = str(exc)
    return result


def useful_user_text(text: str) -> bool:
    return bool(text.strip()) and "AGENTS.md instructions" not in text


def probe_subagent_rollout(path: Path, max_text: int) -> dict[str, Any]:
    identity: dict[str, Any] = {}
    first_user_message = ""
    last_assistant_message = ""
    latest_compaction = ""
    latest_plan: list[dict[str, Any]] | None = None
    last_status = "unknown"
    last_status_detail: str | None = None
    last_status_timestamp: str | None = None
    last_timestamp: str | None = None
    line_count = 0

    try:
        handle = path.open("r", encoding="utf-8", errors="replace")
    except OSError as exc:
        return {
            "rolloutReadable": False,
            "rolloutError": str(exc),
            "lastKnownStatus": "unknown",
            "runtimeStatus": "unknown_from_disk",
        }

    with handle:
        for line_number, line in enumerate(handle, 1):
            line_count = line_number
            try:
                record = json.loads(line)
            except Exception:
                continue
            timestamp = record.get("timestamp")
            if isinstance(timestamp, str):
                last_timestamp = timestamp
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue

            record_type = record.get("type")
            if record_type == "session_meta":
                identity = session_identity(payload, path)
                continue
            if record_type == "compacted":
                message = payload.get("message")
                if isinstance(message, str) and message.strip():
                    latest_compaction = truncate(message, max_text)
                continue
            if record_type == "event_msg":
                lifecycle = persisted_agent_status(payload)
                if lifecycle:
                    last_status, detail = lifecycle
                    last_status_detail = truncate(detail, 300) if detail else None
                    last_status_timestamp = timestamp if isinstance(timestamp, str) else None
                kind = payload.get("type")
                if kind == "user_message":
                    message = str(payload.get("message") or "")
                    if not first_user_message and useful_user_text(message):
                        first_user_message = truncate(message, max_text)
                elif kind == "agent_message":
                    message = str(payload.get("message") or "")
                    if message.strip():
                        last_assistant_message = truncate(message, max_text)
                elif kind == "turn_complete" and not last_assistant_message:
                    message = payload.get("last_agent_message")
                    if isinstance(message, str) and message.strip():
                        last_assistant_message = truncate(message, max_text)
                continue
            if record_type != "response_item":
                continue

            item_type = payload.get("type")
            if item_type == "message":
                role = payload.get("role")
                message = text_from_content(payload.get("content"))
                if role == "user" and not first_user_message and useful_user_text(message):
                    first_user_message = truncate(message, max_text)
                elif role == "assistant" and message.strip():
                    last_assistant_message = truncate(message, max_text)
            elif item_type in {"function_call", "custom_tool_call"}:
                name = str(payload.get("name") or "")
                if name == "update_plan":
                    args_text = str(payload.get("arguments") or payload.get("input") or "")
                    args = load_json_maybe(args_text)
                    if isinstance(args, dict) and isinstance(args.get("plan"), list):
                        latest_plan = args["plan"]

    return {
        "rolloutReadable": True,
        "lineCount": line_count,
        "lastTimestamp": last_timestamp,
        "identity": identity,
        "task": first_user_message,
        "lastAssistantMessage": last_assistant_message,
        "latestCompaction": latest_compaction,
        "latestPlan": latest_plan,
        "lastKnownStatus": last_status,
        "lastKnownStatusDetail": last_status_detail,
        "lastKnownStatusTimestamp": last_status_timestamp,
        "runtimeStatus": "unknown_from_disk",
    }


def find_rollout_path(root: Path, thread_id: str) -> Path | None:
    matches = list(root.rglob(f"*{thread_id}*.jsonl")) if root.is_dir() else []
    if not matches:
        return None
    return max(matches, key=lambda candidate: candidate.stat().st_mtime)


def build_subagent_recovery(
    selected_path: Path,
    root: Path,
    database_path: Path,
    max_agents: int,
    max_text: int,
    scan_rollouts: bool = False,
) -> dict[str, Any]:
    selected_meta = read_session_meta(selected_path)
    selected_identity = session_identity(selected_meta, selected_path)
    selected_thread_id = selected_identity.get("threadId")
    if not isinstance(selected_thread_id, str):
        return {
            "available": False,
            "notes": ["Could not identify the selected rollout's thread id."],
            "agents": [],
        }

    graph, graph_notes = load_state_graph(database_path)
    if graph is None:
        graph = load_rollout_metadata_graph(root)
        graph_notes.append(
            "Spawn-edge lifecycle status is unavailable in fallback mode; "
            "lineage is metadata-derived."
        )
    elif scan_rollouts:
        graph = merge_lineage_graphs(graph, load_rollout_metadata_graph(root))
        graph_notes.append(
            "Augmented persisted spawn edges with rollout metadata; "
            "state DB edge status remains authoritative."
        )

    edges = list(graph.get("edges") or [])
    threads = dict(graph.get("threads") or {})
    threads[selected_thread_id] = merge_present(
        threads.get(selected_thread_id, {}),
        selected_identity,
    )
    incoming: dict[str, str] = {}
    edge_by_child: dict[str, dict[str, Any]] = {}
    for edge in edges:
        parent = edge.get("parentThreadId")
        child = edge.get("childThreadId")
        if isinstance(parent, str) and isinstance(child, str):
            incoming[child] = parent
            edge_by_child[child] = edge

    selected_parent = selected_identity.get("parentThreadId")
    if isinstance(selected_parent, str) and selected_thread_id not in incoming:
        inferred_edge = {
            "parentThreadId": selected_parent,
            "childThreadId": selected_thread_id,
            "edgeStatus": "unknown",
        }
        edges.append(inferred_edge)
        incoming[selected_thread_id] = selected_parent
        edge_by_child[selected_thread_id] = inferred_edge

    root_thread_id = selected_thread_id
    ancestry_seen = {root_thread_id}
    while root_thread_id in incoming:
        parent = incoming[root_thread_id]
        if parent in ancestry_seen:
            graph_notes.append(
                "A cycle was detected in persisted subagent ancestry; traversal stopped."
            )
            break
        ancestry_seen.add(parent)
        root_thread_id = parent

    children_by_parent: dict[str, list[str]] = collections.defaultdict(list)
    for child, parent in incoming.items():
        children_by_parent[parent].append(child)
    for children in children_by_parent.values():
        children.sort()

    descendants: list[tuple[str, int]] = []
    traversal_seen = {root_thread_id}
    queue: Deque[tuple[str, int]] = collections.deque([(root_thread_id, 0)])
    while queue:
        parent, depth = queue.popleft()
        for child in children_by_parent.get(parent, []):
            if child in traversal_seen:
                continue
            traversal_seen.add(child)
            descendants.append((child, depth + 1))
            queue.append((child, depth + 1))

    def updated_at(thread_id: str) -> int:
        value = threads.get(thread_id, {}).get("updatedAtMs")
        return int(value) if isinstance(value, (int, float)) else 0

    def edge_priority(thread_id: str) -> int:
        status = edge_by_child.get(thread_id, {}).get("edgeStatus")
        return {"open": 0, "unknown": 1, "closed": 2}.get(str(status), 1)

    def closure_priority(thread_id: str) -> int:
        status = edge_by_child.get(thread_id, {}).get("edgeStatus")
        return 1 if status == "closed" else 0

    preliminary_ids = [thread_id for thread_id, _depth in descendants]
    preliminary_ids.sort(
        key=lambda thread_id: (
            0 if thread_id == selected_thread_id and selected_thread_id != root_thread_id else 1,
            closure_priority(thread_id),
            edge_priority(thread_id),
            -updated_at(thread_id),
            thread_id,
        )
    )
    probe_capacity = max(
        STATUS_PROBE_POOL_FLOOR,
        max(1, max_agents) * STATUS_PROBE_POOL_MULTIPLIER,
    )
    probed_ids = set(preliminary_ids[:probe_capacity])

    candidate_paths: dict[str, Path | None] = {}
    candidate_statuses: dict[str, dict[str, Any]] = {}
    for thread_id, _depth in descendants:
        stored = threads.get(thread_id) or {}
        rollout_value = stored.get("rolloutPath")
        rollout_path = (
            Path(rollout_value)
            if isinstance(rollout_value, str) and rollout_value
            else None
        )
        if thread_id == selected_thread_id:
            rollout_path = selected_path
        if rollout_path is not None and not rollout_path.is_file():
            rollout_path = None
        candidate_paths[thread_id] = rollout_path
        if thread_id in probed_ids and rollout_path is not None:
            candidate_statuses[thread_id] = probe_persisted_status_tail(rollout_path)
        else:
            candidate_statuses[thread_id] = {
                "lastKnownStatus": "unknown",
                "statusProbeBytes": 0,
                "statusProbeTruncated": False,
                "statusProbeSkipped": thread_id not in probed_ids,
            }

    def lifecycle_priority(thread_id: str) -> int:
        status = candidate_statuses.get(thread_id, {}).get("lastKnownStatus")
        return {
            "running": 0,
            "interrupted": 1,
            "errored": 2,
            "completed": 3,
            "unknown": 4,
            "shutdown": 5,
        }.get(str(status), 4)

    depth_by_thread = dict(descendants)
    ranked_ids = [thread_id for thread_id, _depth in descendants]
    ranked_ids.sort(
        key=lambda thread_id: (
            0 if thread_id == selected_thread_id and selected_thread_id != root_thread_id else 1,
            closure_priority(thread_id),
            lifecycle_priority(thread_id),
            edge_priority(thread_id),
            -updated_at(thread_id),
            depth_by_thread.get(thread_id, 0),
            thread_id,
        )
    )
    reported_ids = ranked_ids[: max(1, max_agents)]

    agents: list[dict[str, Any]] = []
    for thread_id in reported_ids:
        stored = dict(threads.get(thread_id) or {})
        edge = edge_by_child.get(thread_id) or {}
        rollout_path = candidate_paths.get(thread_id)
        if rollout_path is None or not rollout_path.is_file():
            rollout_path = find_rollout_path(root, thread_id)
        probe = (
            probe_subagent_rollout(rollout_path, min(max_text, 800))
            if rollout_path is not None
            else {
                "rolloutReadable": False,
                "lastKnownStatus": "unknown",
                "runtimeStatus": "unknown_from_disk",
            }
        )
        identity = probe.pop("identity", {})
        edge_status = str(edge.get("edgeStatus") or stored.get("edgeStatus") or "unknown")
        recovery_state = {
            "open": "open_or_resumable",
            "closed": "historical_closed",
        }.get(edge_status, "lineage_only")
        agents.append(
            {
                "threadId": thread_id,
                "parentThreadId": edge.get("parentThreadId") or stored.get("parentThreadId"),
                "depth": depth_by_thread.get(thread_id),
                "agentPath": identity.get("agentPath") or stored.get("agentPath"),
                "agentNickname": identity.get("agentNickname") or stored.get("agentNickname"),
                "agentRole": identity.get("agentRole") or stored.get("agentRole"),
                "multiAgentVersion": identity.get("multiAgentVersion")
                or stored.get("multiAgentVersion"),
                "edgeStatus": edge_status,
                "recoveryState": recovery_state,
                "rolloutPath": str(rollout_path) if rollout_path is not None else None,
                "candidateStatus": candidate_statuses.get(thread_id, {}).get(
                    "lastKnownStatus",
                    "unknown",
                ),
                **probe,
            }
        )

    status_counts = collections.Counter(
        str(edge_by_child.get(thread_id, {}).get("edgeStatus") or "unknown")
        for thread_id, _depth in descendants
    )
    candidate_status_counts = collections.Counter(
        str(candidate_statuses.get(thread_id, {}).get("lastKnownStatus") or "unknown")
        for thread_id, _depth in descendants
    )
    candidate_probe = {
        "descendantCount": len(descendants),
        "selectedForProbe": len(probed_ids),
        "rolloutsFound": sum(path is not None for path in candidate_paths.values()),
        "statusesFound": sum(
            status != "unknown"
            for status in (
                probe.get("lastKnownStatus") for probe in candidate_statuses.values()
            )
        ),
        "truncatedCount": sum(
            bool(probe.get("statusProbeTruncated"))
            for probe in candidate_statuses.values()
        ),
        "skippedCount": sum(
            bool(probe.get("statusProbeSkipped"))
            for probe in candidate_statuses.values()
        ),
        "maxBytesPerRollout": STATUS_PROBE_LIMIT_BYTES,
    }
    root_rollout = (
        selected_path
        if root_thread_id == selected_thread_id
        else find_rollout_path(root, root_thread_id)
    )
    if len(descendants) > len(reported_ids):
        graph_notes.append(
            f"Reported the {len(reported_ids)} most relevant descendants out of "
            f"{len(descendants)}; "
            "increase --max-subagents to inspect more."
        )
    graph_notes.append(
        "An open edge means the agent was not explicitly closed and may be resumable; "
        "it is not proof of a live process."
    )
    graph_notes.append(
        "Last-known agent status comes from persisted rollout events; current runtime status "
        "requires list_agents after resuming the root session."
    )
    return {
        "available": True,
        "selectedThreadId": selected_thread_id,
        "rootThreadId": root_thread_id,
        "selectedThreadIsRoot": selected_thread_id == root_thread_id,
        "rootRolloutPath": str(root_rollout) if root_rollout is not None else None,
        "graphSource": graph.get("source"),
        "stateDb": graph.get("stateDb"),
        "descendantCount": len(descendants),
        "reportedCount": len(agents),
        "omittedCount": max(0, len(descendants) - len(agents)),
        "edgeStatusCounts": dict(status_counts),
        "candidateStatusCounts": dict(candidate_status_counts),
        "candidateProbe": candidate_probe,
        "hasOpenOrResumableAgents": status_counts.get("open", 0) > 0,
        "rootResumeRecommended": (
            status_counts.get("open", 0) > 0 or status_counts.get("unknown", 0) > 0
        ),
        "recoveryCommand": f"codex resume {root_thread_id}",
        "agents": agents,
        "notes": graph_notes,
    }
