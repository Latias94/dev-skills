#!/usr/bin/env python3
"""Build a portable live experiment packet for subagent-capable hosts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from planner_payload import build_payload
from dispatch_rehearsal import summarize as summarize_dispatch
from handoff_chain_rehearsal import summarize as summarize_handoff
from planner_prompt_wrapper import summarize as summarize_wrapper


EXPERIMENTS: dict[str, dict[str, Any]] = {
    "hajimi_refusal": {
        "repo": "repo-ref/hajimi",
        "prompt": "Use dev-skills to inspect repo-ref/hajimi and explain whether anything is assignable now or whether this should stay in audit mode.",
        "roles": ["planner"],
        "primary_question": "Can the system refuse fabricated execution cleanly under real prompt pressure?",
    },
    "nako_chain": {
        "repo": "repo-ref/nako",
        "prompt": "Use dev-skills to inspect repo-ref/nako, confirm the next safe bounded task, and only hand off if the active queue is still valid.",
        "roles": ["planner", "worker", "reviewer", "verifier", "integrator"],
        "primary_question": "Can the full chain stay aligned on one active task without broad replanning?",
    },
    "skills_restraint": {
        "repo": "repo-ref/skills",
        "prompt": "Use dev-skills on repo-ref/skills to handle one bounded engineering task. Keep the workflow light, avoid planner/lane/program ceremony unless current repo evidence proves it is necessary, and move toward the sharpest safe execution skill.",
        "roles": ["planner"],
        "primary_question": "Can the system avoid ceremony creep and move toward a sharp execution skill?",
    },
}


def summarize_packet(root: Path, prompt: str, strict_history: bool) -> dict[str, Any]:
    payload = build_payload(root, strict_history)
    dispatch = summarize_dispatch(root, strict_history)
    handoff = summarize_handoff(root, strict_history)
    wrapper = summarize_wrapper(root, prompt, strict_history)
    return {
        "root": str(root),
        "program_action": payload["program_action"],
        "active_unit": payload["active_unit"],
        "recommended_route": dispatch["recommended_route"],
        "chain_state": handoff["chain_state"],
        "wrapped_prompt": wrapper["wrapped_prompt"],
        "planner_prompt": handoff["planner_prompt"],
        "worker_prompt": handoff["worker_prompt"],
        "review_prompt": handoff["review_prompt"],
        "verify_prompt": handoff["verify_prompt"],
        "integrate_prompt": handoff["integrate_prompt"],
    }


def render_text(packet: dict[str, Any]) -> str:
    lines = [
        "## Live Experiment Packet",
        f"Repo: {packet['root']}",
        f"Recommended Route: {packet['recommended_route']['skill']}",
        f"Operating Mode: {packet['program_action']['operating_mode']}",
        f"Chain State: {packet['chain_state']}",
        "",
        "## Wrapped Planner Prompt",
        packet["wrapped_prompt"],
    ]
    for key, title in [
        ("worker_prompt", "Worker Prompt"),
        ("review_prompt", "Review Prompt"),
        ("verify_prompt", "Verify Prompt"),
        ("integrate_prompt", "Integrate Prompt"),
    ]:
        value = packet.get(key) or ""
        if value:
            lines.extend(["", f"## {title}", value])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=sorted(EXPERIMENTS.keys()), help="named live experiment")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    config = EXPERIMENTS[args.experiment]
    root = Path(config["repo"]).resolve()
    packet = summarize_packet(root, str(config["prompt"]), args.strict_history)
    packet["experiment"] = args.experiment
    packet["roles"] = config["roles"]
    packet["primary_question"] = config["primary_question"]

    if args.format == "json":
        print(json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_text(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
