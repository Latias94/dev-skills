from __future__ import annotations

import concurrent.futures
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "engineering" / "engineering-wiki-memory" / "scripts" / "wiki_memory.py"
SPEC = importlib.util.spec_from_file_location("engineering_wiki_memory", SCRIPT)
assert SPEC and SPEC.loader
WIKI = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WIKI
SPEC.loader.exec_module(WIKI)


class EngineeringWikiMemoryTests(unittest.TestCase):
    def test_parallel_immutable_records_keep_every_payload(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            args = self.new_args(root, title="same title")

            def create(index: int) -> Path:
                def content_for(record_id: str, created_at: object) -> str:
                    return WIKI.frontmatter_document(
                        WIKI.standard_fields(args, "Work Progress", f"same title {index}", record_id, created_at),
                        f"# Summary\n\npayload-{index}\n",
                    )

                path, _record_id = WIKI.create_immutable_record(
                    root,
                    "Work Progress",
                    "same title",
                    None,
                    content_for,
                )
                return path

            with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
                paths = list(executor.map(create, range(100)))

            self.assertEqual(len(paths), 100)
            self.assertEqual(len(set(paths)), 100)
            records = WIKI.collect_records(root)
            self.assertEqual(len(records), 100)
            self.assertEqual({f"payload-{index}" for index in range(100)}, {record.text.split("# Summary\n\n", 1)[1].strip() for record in records})

    def test_registration_successor_preserves_an_immutable_history(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            first = self.registration_args(root)
            WIKI.register_work(first)
            first_record = WIKI.collect_records(root)[0]

            successor = self.registration_args(
                root,
                status="paused",
                supersedes=first_record.record_id,
                current_claim="waiting for review",
            )
            WIKI.register_work(successor)

            records = WIKI.collect_records(root)
            self.assertEqual(len(records), 2)
            heads = WIKI.registration_heads(records)
            self.assertEqual(["paused"], [record.fields.get("status") for record in heads["laptop-a-lane-alpha"]])
            self.assertIn("initial scope", first_record.text)
            self.assertIn("waiting for review", heads["laptop-a-lane-alpha"][0].text)

    def test_integration_successor_can_resolve_concurrent_heads(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            first = self.registration_args(root)
            WIKI.register_work(first)
            original = WIKI.collect_records(root)[0]

            left = self.registration_args(root, status="paused", supersedes=[original.record_id])
            right = self.registration_args(root, status="blocked", supersedes=[original.record_id])
            WIKI.register_work(left)
            WIKI.register_work(right)
            self.assertEqual(1, WIKI.render_bundle(root, owner="integrator", check=False))

            heads = WIKI.registration_heads(WIKI.collect_records(root))["laptop-a-lane-alpha"]
            self.assertEqual(2, len(heads))
            resolved = self.registration_args(
                root,
                status="active",
                supersedes=[head.record_id for head in heads],
                current_claim="resolved during integration",
            )
            WIKI.register_work(resolved)

            self.assertEqual(0, WIKI.render_bundle(root, owner="integrator", check=False))
            final_heads = WIKI.registration_heads(WIKI.collect_records(root))["laptop-a-lane-alpha"]
            self.assertEqual(1, len(final_heads))
            self.assertEqual("active", final_heads[0].fields.get("status"))

    def test_render_is_deterministic_and_check_detects_new_shards(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            WIKI.init_bundle(root)
            WIKI.new_concept(self.new_args(root, title="one"))
            self.assertEqual(1, WIKI.render_bundle(root, owner=None, check=True))
            self.assertEqual(0, WIKI.render_bundle(root, owner="integrator", check=False))
            first_current = (root / "current-state.md").read_text(encoding="utf-8")
            first_log = (root / "log.md").read_text(encoding="utf-8")
            self.assertEqual(0, WIKI.render_bundle(root, owner=None, check=True))
            self.assertEqual(0, WIKI.render_bundle(root, owner="integrator", check=False))
            self.assertEqual(first_current, (root / "current-state.md").read_text(encoding="utf-8"))
            self.assertEqual(first_log, (root / "log.md").read_text(encoding="utf-8"))

    def test_legacy_rollups_require_explicit_adoption_and_are_snapshotted(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            root.mkdir()
            legacy_current = "---\ntype: Current State\n---\n\n# Current State\n\nlegacy current summary\n"
            legacy_log = "---\ntype: Engineering Log\n---\n\n# Log\n\nlegacy historical entry\n"
            (root / "current-state.md").write_text(legacy_current, encoding="utf-8")
            (root / "log.md").write_text(legacy_log, encoding="utf-8")

            WIKI.init_bundle(root)
            self.assertEqual(1, WIKI.render_bundle(root, owner=None, check=True))
            self.assertEqual(1, WIKI.render_bundle(root, owner="integrator", check=False))
            self.assertEqual(legacy_current, (root / "current-state.md").read_text(encoding="utf-8"))
            self.assertEqual(legacy_log, (root / "log.md").read_text(encoding="utf-8"))

            self.assertEqual(
                0,
                WIKI.render_bundle(root, owner="integrator", check=False, adopt_rollups=True),
            )

            self.assertIn(WIKI.DERIVED_ROLLUP_MARKER, (root / "current-state.md").read_text(encoding="utf-8"))
            self.assertIn(WIKI.DERIVED_ROLLUP_MARKER, (root / "log.md").read_text(encoding="utf-8"))
            snapshots = [
                record
                for record in WIKI.collect_records(root)
                if record.concept_type == "Legacy Rollup Snapshot"
            ]
            self.assertEqual(2, len(snapshots))
            snapshot_text = "\n".join(record.text for record in snapshots)
            self.assertIn("legacy current summary", snapshot_text)
            self.assertIn("legacy historical entry", snapshot_text)

    def test_validation_distinguishes_legacy_rollups_from_stale_derived_views(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            root.mkdir()
            (root / "current-state.md").write_text("# Current State\n\nlegacy\n", encoding="utf-8")
            (root / "log.md").write_text("# Log\n\nlegacy\n", encoding="utf-8")

            warnings = WIKI.collect_warnings(root)
            messages = [warning.message for warning in warnings]

            self.assertTrue(any("Legacy root rollups have not been adopted" in message for message in messages))
            self.assertFalse(any("Derived rollups are stale" in message for message in messages))

    def test_source_fingerprint_without_derived_marker_is_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            root.mkdir()
            legacy_current = (
                "---\ntype: Current State\nsource_fingerprint: \"historical-value\"\n---\n\n"
                "# Current State\n\nlegacy\n"
            )
            (root / "current-state.md").write_text(legacy_current, encoding="utf-8")
            (root / "log.md").write_text("# Log\n\nlegacy\n", encoding="utf-8")

            WIKI.init_bundle(root)

            self.assertEqual(1, WIKI.render_bundle(root, owner="integrator", check=False))
            self.assertEqual(legacy_current, (root / "current-state.md").read_text(encoding="utf-8"))

    def test_block_list_frontmatter_preserves_registration_lineage(self) -> None:
        fields = WIKI.frontmatter_fields(
            "---\ntype: \"Work Registration\"\nsupersedes:\n  - \"first-id\"\n  - \"second-id\"\n---\n"
        )

        self.assertEqual(["first-id", "second-id"], WIKI.frontmatter_values(fields, "supersedes"))

    def test_external_workstream_runtime_is_reported_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            repository = Path(raw_temp) / "repository"
            root = repository / "docs" / "knowledge" / "engineering"
            workstream = repository / "docs" / "workstreams" / "parallel-lane" / "WORKSTREAM.json"
            workstream.parent.mkdir(parents=True)
            original = '{"status":"active","updated":"2000-01-01","active_tasks":["lane-1"]}\n'
            workstream.write_text(original, encoding="utf-8")
            WIKI.init_bundle(root)

            warnings = WIKI.external_workstream_warnings(root)

            self.assertTrue(any("active external workstream" in warning.message for warning in warnings))
            self.assertTrue(any("older than" in warning.message for warning in warnings))
            self.assertEqual(original, workstream.read_text(encoding="utf-8"))

            registration = self.registration_args(
                root,
                external_runtime="docs/workstreams/parallel-lane/WORKSTREAM.json",
            )
            WIKI.register_work(registration)
            original_registration = WIKI.collect_records(root)[0]
            WIKI.register_work(
                self.registration_args(
                    root,
                    supersedes=[original_registration.record_id],
                    status="paused",
                )
            )
            linked_warnings = WIKI.external_workstream_warnings(root, WIKI.collect_records(root))

            self.assertFalse(any("active external workstream" in warning.message for warning in linked_warnings))
            self.assertFalse(any("older than" in warning.message for warning in linked_warnings))
            self.assertEqual(original, workstream.read_text(encoding="utf-8"))

    def test_independent_initialization_has_identical_shared_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp)
            left = root / "left"
            right = root / "right"

            WIKI.init_bundle(left)
            WIKI.init_bundle(right)

            for name in ("index.md", "current-state.md", "log.md"):
                self.assertEqual(
                    (left / name).read_text(encoding="utf-8"),
                    (right / name).read_text(encoding="utf-8"),
                )

    def test_explicit_path_cannot_target_a_rollup(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"

            with self.assertRaises(SystemExit):
                WIKI.create_immutable_record(
                    root,
                    "Work Progress",
                    "bad path",
                    "log.md",
                    lambda _record_id, _created_at: "ignored",
                )

    def test_new_rejects_registration_without_a_lane_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            args = self.new_args(Path(raw_temp) / "memory", title="bad registration")
            args.type = "Work Registration"

            with self.assertRaises(SystemExit):
                WIKI.new_concept(args)

    def test_validate_rejects_conflict_markers_and_duplicate_record_ids(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            root.mkdir()
            content = "---\ntype: \"Work Progress\"\nrecord_id: \"duplicate\"\n---\n\n# Summary\n"
            (root / "one.md").write_text(content, encoding="utf-8")
            (root / "two.md").write_text(content + "<<<<<<< ours\n", encoding="utf-8")

            errors = WIKI.collect_validation_errors(root)

            self.assertTrue(any("duplicate record_id" in error for error in errors))
            self.assertTrue(any("conflict markers" in error for error in errors))

    def test_register_rejects_visible_cross_lane_predecessor(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            first = self.registration_args(root, registration_id="lane-a")
            WIKI.register_work(first)
            predecessor = WIKI.collect_records(root)[0]

            foreign_successor = self.registration_args(
                root,
                registration_id="lane-b",
                supersedes=[predecessor.record_id],
            )

            with self.assertRaises(SystemExit):
                WIKI.register_work(foreign_successor)

    def test_render_rejects_legacy_cross_lane_predecessor(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            root = Path(raw_temp) / "memory"
            WIKI.init_bundle(root)
            WIKI.register_work(self.registration_args(root, registration_id="lane-a"))
            predecessor = WIKI.collect_records(root)[0]
            invalid = WIKI.frontmatter_document(
                [
                    ("type", WIKI.yaml_string("Work Registration")),
                    ("title", WIKI.yaml_string("lane b")),
                    ("timestamp", "2026-07-10T00:00:00Z"),
                    ("record_id", WIKI.yaml_string("legacy-cross-lane")),
                    ("registration_id", WIKI.yaml_string("lane-b")),
                    ("producer_id", WIKI.yaml_string("laptop-b")),
                    ("supersedes", WIKI.yaml_values([predecessor.record_id])),
                ],
                "# Scope\n",
            )
            invalid_path = root / "registry" / "legacy-cross-lane.md"
            invalid_path.parent.mkdir(parents=True, exist_ok=True)
            invalid_path.write_text(invalid, encoding="utf-8")

            self.assertEqual(1, WIKI.render_bundle(root, owner="integrator", check=False))

    @staticmethod
    def new_args(root: Path, title: str) -> object:
        return WIKI.argparse.Namespace(
            root=root,
            type="Work Progress",
            title=title,
            description=None,
            path=None,
            resource=None,
            tags=None,
            status=None,
            producer_id="laptop-a",
            run_id="run-a",
            source_session=None,
            subagent_id=None,
            related_plan=None,
            related_issue=None,
            git_branch=None,
            git_commit=None,
            verified_by=None,
            supersedes=None,
            force=False,
        )

    @staticmethod
    def registration_args(root: Path, **overrides: object) -> object:
        values = {
            "root": root,
            "title": "lane alpha",
            "registration_id": "laptop-a-lane-alpha",
            "producer_id": "laptop-a",
            "description": None,
            "path": None,
            "resource": None,
            "tags": None,
            "status": "active",
            "run_id": "run-a",
            "source_workspace": None,
            "source_session": None,
            "related_plan": None,
            "related_issue": None,
            "git_branch": None,
            "git_commit": None,
            "external_runtime": None,
            "supersedes": None,
            "latest_link": None,
            "scope": "initial scope",
            "current_claim": "initial claim",
            "handoff": "initial handoff",
            "update": False,
            "force": False,
        }
        values.update(overrides)
        return WIKI.argparse.Namespace(**values)


if __name__ == "__main__":
    unittest.main()
