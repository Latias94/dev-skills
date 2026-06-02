#!/usr/bin/env python3
"""Unified CLI facade for read-only plan-engineering-program runtime helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable


Renderer = Callable[[dict[str, Any]], str]


def emit(payload: dict[str, Any], render: Renderer, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render(payload))


def selected_candidates(args: argparse.Namespace) -> list[str]:
    return [*args.candidate, *args.capability_id]


def add_root_and_format(parser: argparse.ArgumentParser) -> None:
    add_root(parser)
    parser.add_argument("--format", choices=["text", "json"], default="text")


def add_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")


def add_common(parser: argparse.ArgumentParser) -> None:
    add_root_and_format(parser)
    parser.add_argument("--strict-history", action="store_true")


def resolve_root(args: argparse.Namespace) -> Path:
    return Path(args.root_arg or args.root).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scale_parser = subparsers.add_parser(
        "scale",
        help="smallest workflow preset that fits the repository",
    )
    add_root_and_format(scale_parser)

    status_parser = subparsers.add_parser(
        "status",
        help="planner action, active unit, audit pressure, and runtime prompt block",
    )
    add_common(status_parser)

    dispatch_parser = subparsers.add_parser(
        "dispatch",
        help="recommended route, worker prompt, and implementation/product parallelism decision",
    )
    add_common(dispatch_parser)

    capability_parser = subparsers.add_parser(
        "capability",
        help="product capability RECON candidates separated from implementation readiness",
    )
    add_common(capability_parser)

    recon_packet_parser = subparsers.add_parser(
        "recon-packet",
        help="bounded subagent packet for one or more product capability RECON candidates",
    )
    add_common(recon_packet_parser)
    recon_packet_parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        help="capability id to include",
    )
    recon_packet_parser.add_argument(
        "--capability-id",
        action="append",
        default=[],
        help="compatibility alias for --candidate",
    )

    chain_parser = subparsers.add_parser(
        "chain",
        help="planner -> worker -> review -> verify -> integrate rehearsal prompts",
    )
    add_common(chain_parser)

    advanced_parser = subparsers.add_parser(
        "advanced",
        help="advanced debugging, hook, and result-intake helpers",
    )
    advanced_subparsers = advanced_parser.add_subparsers(dest="advanced_command", required=True)

    prelude_parser = advanced_subparsers.add_parser(
        "prelude",
        help="derived per-turn planner prelude for prompt-boundary experiments",
    )
    add_common(prelude_parser)

    hook_parser = advanced_subparsers.add_parser(
        "hook-payload",
        help="host-consumable hook payload for planner runtime injection",
    )
    add_root(hook_parser)
    hook_parser.add_argument("--event-name", default="UserPromptSubmit", help="hook event name to emit")
    hook_parser.add_argument("--strict-history", action="store_true")
    hook_parser.add_argument("--debug", action="store_true", help="include derived debug metadata")

    validate_parser = advanced_subparsers.add_parser(
        "validate-result",
        help="validate CAPABILITY_RECON_RESULT blocks from stdin or --input",
    )
    add_common(validate_parser)
    validate_parser.add_argument("--input", help="file containing CAPABILITY_RECON_RESULT blocks")

    args = parser.parse_args()
    root = resolve_root(args)

    if args.command == "status":
        from planner_payload import build_payload, render_text as render_status

        emit(build_payload(root, args.strict_history), render_status, args.format)
    elif args.command == "scale":
        from workflow_scale import classify as classify_scale
        from workflow_scale import render_text as render_scale

        emit(classify_scale(root), render_scale, args.format)
    elif args.command == "dispatch":
        from dispatch_rehearsal import render_text as render_dispatch
        from dispatch_rehearsal import summarize as summarize_dispatch

        emit(summarize_dispatch(root, args.strict_history), render_dispatch, args.format)
    elif args.command == "capability":
        from capability_parallelism import build_capability_summary
        from capability_parallelism import render_text as render_capability

        emit(build_capability_summary(root, args.strict_history), render_capability, args.format)
    elif args.command == "recon-packet":
        from capability_recon_packet import build_packet, render_text as render_recon_packet

        emit(
            build_packet(root, selected_candidates(args), args.strict_history),
            render_recon_packet,
            args.format,
        )
    elif args.command == "chain":
        from handoff_chain_rehearsal import render_text as render_chain
        from handoff_chain_rehearsal import summarize as summarize_chain

        emit(summarize_chain(root, args.strict_history), render_chain, args.format)
    elif args.command == "advanced":
        if args.advanced_command == "prelude":
            from planner_turn_prelude import render_text as render_prelude
            from planner_turn_prelude import summarize as summarize_prelude

            emit(summarize_prelude(root, args.strict_history), render_prelude, args.format)
        elif args.advanced_command == "hook-payload":
            from inject_planner_runtime import build_payload as build_hook_payload
            from planner_turn_prelude import summarize as summarize_prelude

            payload = build_hook_payload(root, args.event_name, args.strict_history)
            if args.debug:
                summary = summarize_prelude(root, args.strict_history)
                payload["debug"] = {
                    "root": str(root),
                    "recommended_route": summary["recommended_route"],
                    "program_action": summary["program_action"],
                    "active_unit": summary["active_unit"],
                    "product_parallelism": summary.get("product_parallelism"),
                }
            print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        elif args.advanced_command == "validate-result":
            from capability_recon_result_validator import render_text as render_validation
            from capability_recon_result_validator import validate_text

            if args.input:
                text = Path(args.input).read_text(encoding="utf-8")
            else:
                text = sys.stdin.read()
            summary = validate_text(root, text, args.strict_history)
            emit(summary, render_validation, args.format)
            return 0 if summary["valid"] else 1
        else:
            parser.error(f"unknown advanced command: {args.advanced_command}")
    else:
        parser.error(f"unknown command: {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
