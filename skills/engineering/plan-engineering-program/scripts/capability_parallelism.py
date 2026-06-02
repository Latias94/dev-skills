#!/usr/bin/env python3
"""Summarize product-capability parallel RECON candidates from repo docs."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from planner_payload import build_payload


@dataclass(frozen=True)
class CapabilityProfile:
    capability_id: str
    label: str
    keywords: tuple[str, ...]
    anchors: tuple[str, ...]
    classification: str
    missing_artifacts: tuple[str, ...]
    guardrail: str
    notes: str


RECON_RESULT_CONTRACT = {
    "result_marker": "CAPABILITY_RECON_RESULT:",
    "allowed_status": [
        "RECON_DONE",
        "NEEDS_PRODUCT_DECISION",
        "NEEDS_WORKSTREAM",
        "BLOCKED_BY_ACTIVE_QUEUE",
        "NEEDS_CONTEXT",
    ],
    "required_fields": [
        "capability_id",
        "classification",
        "status",
        "evidence",
        "guardrail_assessment",
        "missing_artifacts",
        "owned_scope",
        "shared_scope",
        "product_decisions",
        "implementation_allowed",
        "blocked_by_active_queue",
        "suggested_next_artifact",
    ],
    "rule": "RECON subagents must stay read-only and return structured evidence before any implementation lane can be proposed.",
}


PROFILES: tuple[CapabilityProfile, ...] = (
    CapabilityProfile(
        "remote_access_nat_relay",
        "Remote access / NAT traversal / relay",
        (
            "remote access",
            "network tunnel",
            "nat traversal",
            "relay",
            "reverse proxy",
            "tailscale",
            "cloudflare tunnel",
            "ddns",
            "vpn",
            "endpoint discovery",
        ),
        (
            "remote access",
            "network tunnel",
            "nat traversal",
            "relay",
            "reverse proxy",
            "tailscale",
            "cloudflare tunnel",
            "ddns",
            "endpoint discovery",
        ),
        "product_decision_required",
        ("product/security ADR", "threat model", "abuse/cost model", "workstream", "redaction gates"),
        "Separate reverse proxy, VPN, tunnel, DDNS, endpoint discovery, and built-in relay/NAT traversal; do not implement relay, tunnel daemon, central service, or endpoint API changes.",
        "Cookbook and diagnostics can be reconned before built-in relay or NAT traversal decisions.",
    ),
    CapabilityProfile(
        "playback_transcode_depth",
        "Playback / transcode next depth",
        (
            "playback",
            "transcode",
            "remux",
            "hls",
            "ll-hls",
            "cmaf",
            "hardware acceleration",
            "tone map",
            "subtitle burn",
            "remote worker",
        ),
        (
            "playback",
            "transcode",
            "remux",
            "hls",
            "ll-hls",
            "cmaf",
            "hardware acceleration",
            "tone map",
            "subtitle burn",
        ),
        "recon_candidate",
        ("architecture map", "workstream", "device/profile gates", "FFmpeg/hardware smoke"),
        "Plan playback/transcode depth only; do not change runtime code, transport/session contracts, generated clients, or playback public APIs.",
        "Playback and transcode depth can be reconned in parallel but needs focused workstreams before implementation.",
    ),
    CapabilityProfile(
        "storage_vfs_webdav",
        "Storage / VFS / WebDAV resilience",
        (
            "storage",
            "vfs",
            "webdav",
            "source fingerprint",
            "cache repair",
            "staging",
            "mount hang",
            "source identity",
        ),
        (
            "vfs",
            "webdav",
            "source fingerprint",
            "cache repair",
            "staging",
            "mount hang",
            "source identity",
        ),
        "recon_candidate",
        ("architecture map", "workstream", "backend failure matrix", "cache/staging gates"),
        "Analyze storage/VFS resilience only; do not change cache behavior, backend policy, Admin diagnostics, or staging semantics.",
        "Storage and VFS hardening is separable from metadata apply but shares diagnostics and staging boundaries.",
    ),
    CapabilityProfile(
        "library_scan_watch_folder",
        "Library scan / watch-folder intake",
        (
            "library scan",
            "watch folder",
            "watch-folder",
            "file watcher",
            "debounce",
            "copy-in-progress",
            "scheduled reconciliation",
            "source tombstone",
        ),
        (
            "library scan",
            "watch folder",
            "watch-folder",
            "file watcher",
            "copy-in-progress",
            "scheduled reconciliation",
            "source tombstone",
        ),
        "recon_candidate",
        ("architecture map", "workstream", "large-copy/debounce tests", "reconciliation gates"),
        "Analyze intake/watch semantics only; do not change source identity, tombstone, VFS, or library pipeline contracts.",
        "Scan and watch-folder runtime can be reconned independently but must respect VFS/source identity contracts.",
    ),
    CapabilityProfile(
        "clients_surfaces",
        "Clients / mobile / desktop / TV",
        (
            "mobile",
            "android",
            "desktop",
            "tauri",
            "tv",
            "casting",
            "public client",
            "sdk",
            "player",
            "offline",
        ),
        (
            "mobile",
            "android",
            "desktop",
            "tauri",
            "tv",
            "casting",
            "offline",
        ),
        "needs_workstream",
        ("client capability map", "auth/session ADR", "SDK/API gates", "client smoke tests"),
        "Map client surfaces and protocol boundaries only; do not change SDK, Public Client API, auth/session, or playback contracts.",
        "Client work can become parallel once protocol, auth, and playback capability boundaries are explicit.",
    ),
    CapabilityProfile(
        "addons_ecosystem",
        "Addon manager / official addon ecosystem",
        (
            "addon",
            "official addon",
            "addon manager",
            "catalog",
            "marketplace",
            "sidecar",
            "signing",
            "grant",
            "resource-call",
        ),
        (
            "addon",
            "official addon",
            "addon manager",
            "catalog",
            "marketplace",
            "sidecar",
            "signing",
            "resource-call",
        ),
        "needs_workstream",
        ("trust/update ADR", "cross-repo sync policy", "workstream", "addon smoke gates"),
        "Map addon trust, lifecycle, and related-repo gates only; do not modify addon runtime, provider breadth, package signing, or cross-repo state.",
        "Addon breadth can run in parallel only after trust, lifecycle, and related-repo gates are explicit.",
    ),
    CapabilityProfile(
        "security_access_sharing",
        "Security / access / sharing",
        (
            "rbac",
            "sharing",
            "share link",
            "library access",
            "permission",
            "auth",
            "session",
            "remote playback",
            "redaction",
        ),
        (
            "rbac",
            "sharing",
            "share link",
            "library access",
            "permission",
            "remote playback",
        ),
        "product_decision_required",
        ("access ADR", "permission model", "redaction regression tests", "cache/access gates"),
        "Map access and sharing decisions only; do not implement RBAC, share links, permission-aware cache keys, or Public Client exposure.",
        "Sharing and fine-grained access need security decisions before implementation.",
    ),
    CapabilityProfile(
        "release_ops_backup_observability",
        "Release / deployment / backup / observability",
        (
            "release",
            "deployment",
            "backup",
            "restore",
            "observability",
            "trace context",
            "support bundle",
            "diagnostics",
            "hardware matrix",
            "docker",
        ),
        (
            "backup",
            "restore",
            "observability",
            "trace context",
            "support bundle",
            "hardware matrix",
            "docker",
        ),
        "recon_candidate",
        ("operations map", "workstream", "restore smoke", "release/hardware gates"),
        "Map release, backup, restore, and observability seams only; do not change release tooling, backup classification, diagnostics payloads, or support bundles.",
        "Ops and release hardening can be reconned in parallel with implementation work.",
    ),
)


DOC_CANDIDATES = (
    "README.md",
    "docs/GOALS.md",
    "docs/ROADMAP.md",
    "docs/ARCHITECTURE.md",
    "docs/architecture",
    "docs/workstreams",
)


FAMILY_DOC_CANDIDATES = (
    "README.md",
    "docs/GOALS.md",
    "docs/ROADMAP.md",
    "docs/ARCHITECTURE.md",
    "docs/architecture",
)


PROFILE_FAMILY = {
    "id": "self_hosted_media_server",
    "label": "Self-hosted media server",
    "keywords": (
        "self-hosted media",
        "media server",
        "jellyfin",
        "emby",
        "plex",
        "video library",
        "playback",
        "transcode",
        "ffmpeg",
        "subtitle",
        "hls",
        "webdav",
        "library scan",
        "watch folder",
        "remote playback",
    ),
    "minimum_hits": 2,
}


def iter_doc_files(root: Path) -> list[Path]:
    return iter_candidate_files(root, DOC_CANDIDATES)


def iter_family_doc_files(root: Path) -> list[Path]:
    return iter_candidate_files(root, FAMILY_DOC_CANDIDATES)


def iter_candidate_files(root: Path, candidates: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for rel in candidates:
        path = root / rel
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(path.rglob("*.md"))
            files.extend(path.rglob("WORKSTREAM.json"))
    return sorted(set(files))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def detect_profile_family(root: Path, docs: list[Path]) -> dict[str, Any]:
    matches: list[str] = []
    score = 0
    keywords = tuple(str(keyword).lower() for keyword in PROFILE_FAMILY["keywords"])
    for path in docs:
        text = read_text(path).lower()
        if not text:
            continue
        hit_count = sum(1 for keyword in keywords if keyword in text)
        if hit_count:
            score += hit_count
            matches.append(str(path.relative_to(root)))
    minimum_hits = int(PROFILE_FAMILY["minimum_hits"])
    return {
        "id": PROFILE_FAMILY["id"],
        "label": PROFILE_FAMILY["label"],
        "detected": score >= minimum_hits,
        "evidence": matches[:8],
        "score": score,
        "minimum_hits": minimum_hits,
    }


def collect_evidence(root: Path, profile: CapabilityProfile, docs: list[Path]) -> tuple[list[str], int]:
    matches: list[str] = []
    score = 0
    for path in docs:
        text = read_text(path).lower()
        if not text:
            continue
        hit_count = sum(1 for keyword in profile.keywords if keyword.lower() in text)
        anchor_count = sum(1 for anchor in profile.anchors if anchor.lower() in text)
        if hit_count and anchor_count:
            score += hit_count
            matches.append(str(path.relative_to(root)))
    return matches[:8], score


def blocked_by_active_queue(active_unit: dict[str, Any]) -> list[dict[str, str]]:
    workstream = str(active_unit.get("workstream") or "").lower()
    task = str(active_unit.get("task") or "").lower()
    if "generated-artifact" not in workstream and "gabma" not in task:
        return []
    return [
        {
            "candidate": "provider mapping breadth",
            "reason": "may alter metadata Generated Artifact semantics before GABMA-020 is reviewed or split",
        },
        {
            "candidate": "generated artifact apply repair tooling",
            "reason": "too close to the active apply-plan and partial-failure boundary",
        },
        {
            "candidate": "Admin bulk apply workflow route/Web UX",
            "reason": "may change generated client or Admin workflow contracts tied to GABMA-020",
        },
        {
            "candidate": "durable bulk metadata mutation",
            "reason": "GABMA-020 is intentionally read-only before mutation exists",
        },
    ]


def build_capability_summary(root: Path, strict_history: bool = False) -> dict[str, Any]:
    planner = build_payload(root, strict_history)
    docs = iter_doc_files(root)
    family_docs = iter_family_doc_files(root)
    profile_family = detect_profile_family(root, family_docs)
    candidates: list[dict[str, Any]] = []
    if profile_family["detected"]:
        for profile in PROFILES:
            evidence, score = collect_evidence(root, profile, docs)
            if not evidence:
                continue
            candidates.append(
                {
                    "id": profile.capability_id,
                    "label": profile.label,
                    "classification": profile.classification,
                    "evidence": evidence,
                    "evidence_score": score,
                    "missing_artifacts": list(profile.missing_artifacts),
                    "guardrail": profile.guardrail,
                    "notes": profile.notes,
                }
            )

    recon_candidates = [row for row in candidates if row["classification"] == "recon_candidate"]
    decision_candidates = [
        row for row in candidates if row["classification"] == "product_decision_required"
    ]
    needs_workstream = [row for row in candidates if row["classification"] == "needs_workstream"]

    return {
        "root": str(root),
        "implementation_horizon": planner["program_action"]["implementation_horizon"],
        "operating_mode": planner["program_action"]["operating_mode"],
        "ready_active_unit": planner["active_unit"],
        "profile_family": profile_family,
        "product_recon_horizon": len(candidates),
        "capability_parallelism": {
            "recon_candidates": recon_candidates,
            "product_decision_required": decision_candidates,
            "needs_workstream": needs_workstream,
            "blocked_by_active_queue": blocked_by_active_queue(planner["active_unit"]),
        },
        "recon_result_contract": RECON_RESULT_CONTRACT,
        "rule": "Capability candidates are read-only RECON until ADRs, workstreams, owned/shared scopes, gates, and stop conditions are explicit.",
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "## Capability Parallelism",
        f"Operating Mode: {summary['operating_mode']}",
        f"Implementation Horizon: {summary['implementation_horizon']}",
        f"Profile Family: {summary['profile_family']['label']} (detected={summary['profile_family']['detected']})",
        f"Product RECON Horizon: {summary['product_recon_horizon']}",
        "",
        "## Ready Active Unit",
    ]
    active = summary["ready_active_unit"]
    lines.extend(
        [
            f"Workstream: {active.get('workstream') or '(none)'}",
            f"Task: {active.get('task') or '(none)'}",
            f"Campaign: {active.get('campaign') or '(none)'}",
            "",
        ]
    )
    for section in ("recon_candidates", "product_decision_required", "needs_workstream"):
        rows = summary["capability_parallelism"][section]
        lines.append(f"## {section.replace('_', ' ').title()}")
        if not rows:
            lines.append("(none)")
        for row in rows:
            lines.append(f"- {row['label']} [{row['id']}]")
            lines.append(f"  Evidence: {', '.join(row['evidence'][:3])}")
            lines.append(f"  Guardrail: {row['guardrail']}")
            lines.append(f"  Missing: {', '.join(row['missing_artifacts'])}")
        lines.append("")
    blocked = summary["capability_parallelism"]["blocked_by_active_queue"]
    lines.append("## Blocked By Active Queue")
    if not blocked:
        lines.append("(none)")
    for row in blocked:
        lines.append(f"- {row['candidate']}: {row['reason']}")
    lines.extend(["", "## Rule", summary["rule"]])
    contract = summary["recon_result_contract"]
    lines.extend(
        [
            "",
            "## RECON Result Contract",
            f"Marker: {contract['result_marker']}",
            "Required Fields: " + ", ".join(contract["required_fields"]),
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    root = Path(args.root_arg or args.root).resolve()
    summary = build_capability_summary(root, args.strict_history)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
