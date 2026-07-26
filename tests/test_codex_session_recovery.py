from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "engineering"
    / "codex-session-recovery"
    / "scripts"
    / "summarize_session.py"
)
SPEC = importlib.util.spec_from_file_location("codex_session_recovery", SCRIPT)
assert SPEC and SPEC.loader
RECOVERY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RECOVERY
SPEC.loader.exec_module(RECOVERY)


ROOT_ID = "00000000-0000-0000-0000-000000000001"
CHILD_ID = "00000000-0000-0000-0000-000000000002"
GRANDCHILD_ID = "00000000-0000-0000-0000-000000000003"
CLOSED_ID = "00000000-0000-0000-0000-000000000004"
LEGACY_ID = "00000000-0000-0000-0000-000000000005"
PREVIOUS_ID = "00000000-0000-0000-0000-000000000006"


class CodexSessionRecoverySubagentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.codex_home = Path(self.temp.name)
        self.sessions = self.codex_home / "sessions"
        self.sessions.mkdir()
        self.root_path = self.write_rollout(ROOT_ID, parent=None, events=[])
        self.child_path = self.write_rollout(
            CHILD_ID,
            parent=ROOT_ID,
            path="/root/worker",
            role="worker",
            nickname="Worker One",
            events=[
                self.event("2026-07-26T01:00:01Z", "turn_started"),
                self.event(
                    "2026-07-26T01:00:02Z",
                    "agent_message",
                    message="The worker had started inspecting the repository.",
                ),
            ],
        )
        self.grandchild_path = self.write_rollout(
            GRANDCHILD_ID,
            parent=CHILD_ID,
            path="/root/worker/reviewer",
            role="reviewer",
            nickname="Reviewer One",
            depth=2,
            events=[
                self.event("2026-07-26T01:01:01Z", "turn_started"),
                self.event(
                    "2026-07-26T01:01:02Z",
                    "agent_message",
                    message="Review complete with one finding.",
                ),
                self.event("2026-07-26T01:01:03Z", "turn_complete"),
            ],
        )
        self.closed_path = self.write_rollout(
            CLOSED_ID,
            parent=ROOT_ID,
            path="/root/closed-worker",
            role="worker",
            nickname="Closed Worker",
            events=[self.event("2026-07-26T01:02:01Z", "shutdown_complete")],
        )
        self.state_db = self.codex_home / "state_5.sqlite"
        self.create_state_db()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def event(timestamp: str, kind: str, **payload: object) -> dict[str, object]:
        return {
            "timestamp": timestamp,
            "type": "event_msg",
            "payload": {"type": kind, **payload},
        }

    def write_rollout(
        self,
        thread_id: str,
        *,
        parent: str | None,
        events: list[dict[str, object]],
        path: str | None = None,
        role: str | None = None,
        nickname: str | None = None,
        depth: int = 1,
        session_id: str = ROOT_ID,
    ) -> Path:
        rollout = self.sessions / f"rollout-2026-07-26T01-00-00-{thread_id}.jsonl"
        meta: dict[str, object] = {
            "session_id": session_id,
            "id": thread_id,
            "timestamp": "2026-07-26T01:00:00Z",
            "cwd": str(self.codex_home / "repo"),
            "originator": "codex-tui",
            "cli_version": "0.145.0",
            "source": "cli",
            "multi_agent_version": "v2",
        }
        if parent is not None:
            spawn = {
                "parent_thread_id": parent,
                "depth": depth,
                "agent_path": path,
                "agent_nickname": nickname,
                "agent_role": role,
            }
            meta.update(
                {
                    "parent_thread_id": parent,
                    "source": {"subagent": {"thread_spawn": spawn}},
                    "thread_source": "subagent",
                    "agent_path": path,
                    "agent_nickname": nickname,
                    "agent_role": role,
                }
            )
        records: list[dict[str, object]] = [
            {
                "timestamp": "2026-07-26T01:00:00Z",
                "type": "session_meta",
                "payload": meta,
            }
        ]
        if parent is not None:
            records.append(
                {
                    "timestamp": "2026-07-26T01:00:00Z",
                    "type": "event_msg",
                    "payload": {"type": "user_message", "message": f"Task for {path}"},
                }
            )
        records.extend(events)
        rollout.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )
        return rollout

    def create_state_db(self) -> None:
        connection = sqlite3.connect(self.state_db)
        try:
            connection.executescript(
                """
CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    rollout_path TEXT NOT NULL,
    agent_path TEXT,
    agent_nickname TEXT,
    agent_role TEXT,
    updated_at_ms INTEGER,
    thread_source TEXT,
    multi_agent_version TEXT
);
CREATE TABLE thread_spawn_edges (
    parent_thread_id TEXT NOT NULL,
    child_thread_id TEXT NOT NULL PRIMARY KEY,
    status TEXT NOT NULL
);
"""
            )
            thread_rows = [
                (
                    CHILD_ID,
                    str(self.child_path),
                    "/root/worker",
                    "Worker One",
                    "worker",
                    100,
                    "subagent",
                    "v2",
                ),
                (
                    GRANDCHILD_ID,
                    str(self.grandchild_path),
                    "/root/worker/reviewer",
                    "Reviewer One",
                    "reviewer",
                    200,
                    "subagent",
                    "v2",
                ),
                (
                    CLOSED_ID,
                    str(self.closed_path),
                    "/root/closed-worker",
                    "Closed Worker",
                    "worker",
                    300,
                    "subagent",
                    "v2",
                ),
            ]
            connection.executemany(
                "INSERT INTO threads VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                thread_rows,
            )
            connection.executemany(
                "INSERT INTO thread_spawn_edges VALUES (?, ?, ?)",
                [
                    (ROOT_ID, CHILD_ID, "open"),
                    (CHILD_ID, GRANDCHILD_ID, "open"),
                    (ROOT_ID, CLOSED_ID, "closed"),
                ],
            )
            connection.commit()
        finally:
            connection.close()

    def recover(
        self,
        selected: Path | None = None,
        max_agents: int = 10,
        scan_rollouts: bool = False,
    ) -> dict[str, object]:
        return RECOVERY.build_subagent_recovery(
            selected or self.root_path,
            self.sessions,
            self.state_db,
            max_agents,
            1600,
            scan_rollouts,
        )

    def test_state_db_recovers_nested_lineage_without_claiming_live_status(self) -> None:
        recovered = self.recover()

        self.assertEqual(recovered["rootThreadId"], ROOT_ID)
        self.assertEqual(recovered["descendantCount"], 3)
        self.assertEqual(recovered["edgeStatusCounts"], {"open": 2, "closed": 1})
        self.assertEqual(
            recovered["candidateStatusCounts"],
            {"running": 1, "completed": 1, "shutdown": 1},
        )
        self.assertEqual(recovered["candidateProbe"]["statusesFound"], 3)
        self.assertEqual(recovered["candidateProbe"]["selectedForProbe"], 3)
        self.assertEqual(recovered["candidateProbe"]["skippedCount"], 0)
        self.assertEqual(recovered["graphSource"], "state_db")
        self.assertEqual(recovered["recoveryCommand"], f"codex resume {ROOT_ID}")
        self.assertTrue(recovered["rootResumeRecommended"])

        agents = {agent["threadId"]: agent for agent in recovered["agents"]}
        self.assertEqual(agents[CHILD_ID]["lastKnownStatus"], "running")
        self.assertEqual(agents[CHILD_ID]["runtimeStatus"], "unknown_from_disk")
        self.assertEqual(agents[CHILD_ID]["recoveryState"], "open_or_resumable")
        self.assertEqual(agents[GRANDCHILD_ID]["depth"], 2)
        self.assertEqual(agents[GRANDCHILD_ID]["lastKnownStatus"], "completed")
        self.assertEqual(agents[CLOSED_ID]["recoveryState"], "historical_closed")

    def test_selecting_child_rollout_walks_back_to_family_root(self) -> None:
        recovered = self.recover(self.child_path)

        self.assertFalse(recovered["selectedThreadIsRoot"])
        self.assertEqual(recovered["selectedThreadId"], CHILD_ID)
        self.assertEqual(recovered["rootThreadId"], ROOT_ID)
        self.assertEqual(recovered["agents"][0]["threadId"], CHILD_ID)

    def test_missing_state_db_falls_back_to_rollout_metadata(self) -> None:
        recovered = RECOVERY.build_subagent_recovery(
            self.root_path,
            self.sessions,
            self.codex_home / "missing.sqlite",
            10,
            1600,
        )

        self.assertEqual(recovered["graphSource"], "rollout_metadata_scan")
        self.assertEqual(recovered["descendantCount"], 3)
        self.assertEqual(recovered["edgeStatusCounts"], {"unknown": 3})
        self.assertTrue(recovered["rootResumeRecommended"])
        agents = {agent["threadId"]: agent for agent in recovered["agents"]}
        self.assertEqual(agents[CHILD_ID]["lastKnownStatus"], "running")
        self.assertEqual(agents[CHILD_ID]["recoveryState"], "lineage_only")

    def test_report_limit_prioritizes_running_before_recent_completed_agent(self) -> None:
        recovered = self.recover(max_agents=2)

        self.assertEqual(recovered["reportedCount"], 2)
        self.assertEqual(recovered["omittedCount"], 1)
        self.assertEqual(
            [agent["threadId"] for agent in recovered["agents"]],
            [CHILD_ID, GRANDCHILD_ID],
        )
        self.assertEqual(recovered["agents"][0]["candidateStatus"], "running")

    def test_continuation_prompt_preserves_subagent_handles(self) -> None:
        summary = RECOVERY.summarize_session(self.root_path, 8, 1600, False)
        summary["subagents"] = self.recover()
        summary["recoveryBoundary"] = RECOVERY.recovery_boundary(
            summary,
            self.root_path,
            self.root_path,
            {"threadId": PREVIOUS_ID, "sessionId": PREVIOUS_ID},
        )

        prompt = RECOVERY.continuation_prompt(summary)

        self.assertIn(f"codex resume {ROOT_ID}", prompt)
        self.assertIn("call `list_agents`", prompt)
        self.assertIn("/root/worker", prompt)
        self.assertIn("cannot prove", prompt)
        self.assertIn("recovered task=Task for /root/worker", prompt)
        self.assertIn("Recovery boundary", prompt)
        self.assertIn("later compaction summaries are authoritative", prompt)
        self.assertIn("Ordinary compaction continues the current session", prompt)
        self.assertIn("Do not rerun this summarizer against the old source", prompt)
        self.assertIn(f"receiving thread recorded at recovery is `{PREVIOUS_ID}`", prompt)
        self.assertIn("while `CODEX_THREAD_ID` still matches it", prompt)

    def test_latest_excludes_the_current_receiving_session_family(self) -> None:
        previous_path = self.write_rollout(
            PREVIOUS_ID,
            parent=None,
            events=[],
            session_id=PREVIOUS_ID,
        )
        for current_path in (
            self.root_path,
            self.child_path,
            self.grandchild_path,
            self.closed_path,
        ):
            os.utime(current_path, (300, 300))
        os.utime(previous_path, (200, 200))

        with mock.patch.dict(os.environ, {"CODEX_THREAD_ID": CHILD_ID}):
            selected, notes = RECOVERY.resolve_session("latest", self.sessions)

        self.assertEqual(selected, previous_path)
        self.assertTrue(any("current Codex session" in note for note in notes))

    def test_latest_requires_a_session_outside_the_current_family(self) -> None:
        with mock.patch.dict(os.environ, {"CODEX_THREAD_ID": CHILD_ID}):
            with self.assertRaisesRegex(FileNotFoundError, "No previous Codex session"):
                RECOVERY.resolve_session("latest", self.sessions)

    def test_markdown_reports_probe_coverage_without_claiming_live_status(self) -> None:
        summary = RECOVERY.summarize_session(self.root_path, 8, 1600, False)
        summary["selection"] = {
            "requestedPath": str(self.root_path),
            "primaryPath": str(self.root_path),
            "promotedToRoot": False,
        }
        summary["subagents"] = self.recover()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            RECOVERY.print_markdown(summary)

        markdown = output.getvalue()
        self.assertIn("Candidate probe coverage", markdown)
        self.assertIn("statuses=3", markdown)
        self.assertIn("Live runtime status: unknown from disk", markdown)
        self.assertIn("## Recovery Boundary", markdown)
        self.assertIn("`historical_recovery_source`", markdown)
        self.assertIn("`continue_current_session`", markdown)

    def test_rollout_scan_augments_incomplete_state_graph(self) -> None:
        legacy_path = self.write_rollout(
            LEGACY_ID,
            parent=ROOT_ID,
            path="/root/legacy-worker",
            role="worker",
            events=[self.event("2026-07-26T01:03:01Z", "turn_complete")],
        )

        recovered = self.recover(scan_rollouts=True)

        self.assertEqual(recovered["graphSource"], "state_db+rollout_metadata_scan")
        self.assertEqual(recovered["descendantCount"], 4)
        self.assertEqual(recovered["edgeStatusCounts"], {"open": 2, "closed": 1, "unknown": 1})
        agents = {agent["threadId"]: agent for agent in recovered["agents"]}
        self.assertEqual(agents[LEGACY_ID]["rolloutPath"], str(legacy_path))
        self.assertEqual(agents[LEGACY_ID]["recoveryState"], "lineage_only")

    def test_rollout_scan_prefers_current_metadata_path_over_stale_db_path(self) -> None:
        connection = sqlite3.connect(self.state_db)
        try:
            connection.execute(
                "UPDATE threads SET rollout_path = ? WHERE id = ?",
                (str(self.codex_home / "stale" / "child.jsonl"), CHILD_ID),
            )
            connection.commit()
        finally:
            connection.close()

        recovered = self.recover(scan_rollouts=True)

        agents = {agent["threadId"]: agent for agent in recovered["agents"]}
        self.assertEqual(agents[CHILD_ID]["rolloutPath"], str(self.child_path))
        self.assertEqual(agents[CHILD_ID]["candidateStatus"], "running")
        self.assertEqual(agents[CHILD_ID]["edgeStatus"], "open")

    def test_rollout_scan_uses_newest_metadata_for_duplicate_thread_id(self) -> None:
        old_path = self.write_rollout(
            LEGACY_ID,
            parent=CHILD_ID,
            path="/root/worker/legacy",
            events=[],
        )
        old_directory = self.sessions / "older"
        old_directory.mkdir()
        old_path = old_path.replace(old_directory / old_path.name)
        os.utime(old_path, (100, 100))

        new_path = self.write_rollout(
            LEGACY_ID,
            parent=ROOT_ID,
            path="/root/legacy",
            events=[],
        )
        os.utime(new_path, (200, 200))

        graph = RECOVERY.load_rollout_metadata_graph(self.sessions)
        edge = next(edge for edge in graph["edges"] if edge["childThreadId"] == LEGACY_ID)

        self.assertEqual(edge["parentThreadId"], ROOT_ID)
        self.assertEqual(graph["threads"][LEGACY_ID]["rolloutPath"], str(new_path))

    def test_invalid_thread_ids_are_not_emitted_as_resume_commands(self) -> None:
        identity = RECOVERY.session_identity(
            {
                "id": "root; Remove-Item -Recurse C:\\",
                "parent_thread_id": "$(malicious)",
            }
        )

        self.assertIsNone(identity["threadId"])
        self.assertIsNone(identity["parentThreadId"])

    def test_status_tail_probe_crosses_large_trailing_event_with_a_hard_limit(self) -> None:
        rollout = self.write_rollout(
            LEGACY_ID,
            parent=ROOT_ID,
            path="/root/large-output",
            events=[
                self.event("2026-07-26T01:04:01Z", "turn_started"),
                self.event(
                    "2026-07-26T01:04:02Z",
                    "agent_message",
                    message="x" * 70_000,
                ),
            ],
        )

        recovered = RECOVERY.probe_persisted_status_tail(rollout)
        limited = RECOVERY.probe_persisted_status_tail(rollout, max_bytes=1024)

        self.assertEqual(recovered["lastKnownStatus"], "running")
        self.assertGreater(recovered["statusProbeBytes"], 64 * 1024)
        self.assertEqual(limited["lastKnownStatus"], "unknown")
        self.assertTrue(limited["statusProbeTruncated"])

    def test_json_cli_includes_subagent_recovery_by_default(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = RECOVERY.main(
                [
                    str(self.root_path),
                    "--sessions-root",
                    str(self.sessions),
                    "--state-db",
                    str(self.state_db),
                    "--max-subagents",
                    "2",
                    "--json",
                ]
            )

        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["subagents"]["rootThreadId"], ROOT_ID)
        self.assertEqual(payload["subagents"]["reportedCount"], 2)
        self.assertFalse(payload["selection"]["promotedToRoot"])
        self.assertEqual(
            payload["recoveryBoundary"]["sourceRole"],
            "historical_recovery_source",
        )
        self.assertEqual(
            payload["recoveryBoundary"]["rerunPolicy"],
            "explicit_cross_session_recovery_only",
        )

    def test_json_cli_records_receiver_and_rejects_its_session_family(self) -> None:
        previous_path = self.write_rollout(
            PREVIOUS_ID,
            parent=None,
            events=[],
            session_id=PREVIOUS_ID,
        )
        output = io.StringIO()
        with mock.patch.dict(os.environ, {"CODEX_THREAD_ID": CHILD_ID}):
            with contextlib.redirect_stdout(output):
                result = RECOVERY.main(
                    [
                        str(previous_path),
                        "--sessions-root",
                        str(self.sessions),
                        "--state-db",
                        str(self.state_db),
                        "--json",
                    ]
                )

        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        boundary = payload["recoveryBoundary"]
        self.assertEqual(boundary["receivingThreadId"], CHILD_ID)
        self.assertEqual(boundary["receivingSessionId"], ROOT_ID)
        self.assertEqual(boundary["sourceThreadId"], PREVIOUS_ID)
        self.assertFalse(boundary["sourceIsReceivingSession"])

        error_output = io.StringIO()
        with mock.patch.dict(os.environ, {"CODEX_THREAD_ID": CHILD_ID}):
            with contextlib.redirect_stderr(error_output):
                rejected = RECOVERY.main(
                    [
                        str(self.root_path),
                        "--sessions-root",
                        str(self.sessions),
                        "--state-db",
                        str(self.state_db),
                        "--json",
                    ]
                )

        self.assertEqual(rejected, 2)
        self.assertIn("current receiving Codex session", error_output.getvalue())

    def test_json_cli_promotes_selected_child_to_root_summary(self) -> None:
        self.root_path = self.write_rollout(
            ROOT_ID,
            parent=None,
            events=[
                self.event(
                    "2026-07-26T01:05:01Z",
                    "agent_message",
                    message="Root continuation state.",
                )
            ],
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = RECOVERY.main(
                [
                    str(self.child_path),
                    "--sessions-root",
                    str(self.sessions),
                    "--state-db",
                    str(self.state_db),
                    "--json",
                ]
            )

        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["source"], str(self.root_path))
        self.assertEqual(payload["selection"]["requestedPath"], str(self.child_path))
        self.assertEqual(payload["selection"]["primaryPath"], str(self.root_path))
        self.assertTrue(payload["selection"]["promotedToRoot"])
        self.assertEqual(payload["subagents"]["selectedThreadId"], CHILD_ID)
        self.assertEqual(
            payload["recoveryBoundary"]["sourcePath"],
            str(self.root_path),
        )
        self.assertEqual(
            payload["recoveryBoundary"]["requestedPath"],
            str(self.child_path),
        )
        self.assertEqual(
            payload["recentAssistantMessages"][-1]["text"],
            "Root continuation state.",
        )

    def test_json_cli_can_skip_subagent_discovery(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = RECOVERY.main(
                [
                    str(self.root_path),
                    "--sessions-root",
                    str(self.sessions),
                    "--no-subagents",
                    "--json",
                ]
            )

        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        self.assertNotIn("subagents", payload)
        self.assertFalse(payload["selection"]["promotedToRoot"])
        self.assertEqual(
            payload["recoveryBoundary"]["ordinaryCompactionAction"],
            "continue_current_session",
        )


if __name__ == "__main__":
    unittest.main()
