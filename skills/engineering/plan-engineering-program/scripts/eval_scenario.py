#!/usr/bin/env python3
"""Evaluate a real-repo scenario against dev-skills, Trellis-like, and Matt-skills-like scorecards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_summary import summarize as summarize_audit
from dispatch_rehearsal import summarize as summarize_dispatch
from handoff_chain_rehearsal import summarize as summarize_handoff
from planner_payload import build_payload


def expected_route_ok(expected: str, actual: str) -> bool:
    if expected == actual:
        return True
    aliases = {
        "planner": {"plan-engineering-program", "audit-project-scale"},
        "resume": {"resume-workstream", "run-workstream-task"},
    }
    return actual in aliases.get(expected, set())


def score_routing(payload: dict[str, Any], dispatch: dict[str, Any], scenario: dict[str, Any]) -> tuple[int, str]:
    expected_scale = scenario["scale_expectation"]
    actual_skill = dispatch["recommended_route"]["skill"]
    mode = payload["program_action"]["mode"]
    operating_mode = payload["program_action"]["operating_mode"]
    safe_move = payload["program_action"]["safe_next_move"]

    expected_route = str(scenario.get("expected_route") or "")
    expected_derived_route = str(scenario.get("expected_derived_route") or "")

    if expected_route == "planner":
        planner_ok = expected_scale == "program" and mode in {"ASSIGN", "DISCOVERY", "PLAN"}
        if not planner_ok:
            return 0, f"scenario expected planner-layer handling, but mode was `{mode}`"
        if expected_derived_route and not expected_route_ok(expected_derived_route, actual_skill):
            return 0, f"scenario expected derived route `{expected_derived_route}` but actual skill was `{actual_skill}`"
        if expected_derived_route:
            return 2, f"planner-layer handling correctly derived `{actual_skill}`"
        return 2, f"planner-layer handling was preserved with mode `{mode}`"

    if expected_route and not expected_route_ok(expected_route, actual_skill):
        return 0, f"scenario expected route `{expected_route}` but actual skill was `{actual_skill}`"
    if expected_route and expected_route_ok(expected_route, actual_skill):
        return 2, f"expected route matched actual skill `{actual_skill}`"
    if expected_scale == "program" and actual_skill == "run-workstream-task" and mode == "ASSIGN" and safe_move == "assignment":
        return 2, "planner-derived program evaluation correctly resolved to an assignable bounded task"
    if expected_scale == "program" and actual_skill == "plan-engineering-program":
        return 2, "program-scale scenario stayed on planner route"
    if expected_scale == "lane" and actual_skill in {"plan-engineering-program", "audit-project-scale"}:
        return 1, f"lane-scale scenario stayed read-only via `{actual_skill}`, but lane-specific routing is not explicit"
    if expected_scale == "workstream" and actual_skill in {"resume-workstream", "run-workstream-task"}:
        return 2, f"workstream-scale scenario routed through `{actual_skill}`"
    if expected_scale == "direct" and actual_skill == "audit-project-scale":
        return 1, "direct scenario stayed conservative because no active queue was derivable"
    if operating_mode == "AUDIT" and mode == "DISCOVERY":
        return 2, "historical-only repo correctly stayed in audit/discovery mode"
    return 0, f"route `{actual_skill}` does not convincingly satisfy expected scale `{expected_scale}`"


def score_artifacts(payload: dict[str, Any], audit: dict[str, Any]) -> tuple[int, str]:
    active = payload["active_unit"]
    action = payload["program_action"]
    warnings = audit["warning_count"]
    errors = audit["error_count"]

    if errors:
        return 0, f"{errors} validator errors remain in authoritative artifacts"
    if action["operating_mode"] == "READINESS" and action["implementation_horizon"] > 0 and not active["required_context"]:
        return 0, "active ready queue has no derived required context"
    if action["operating_mode"] == "AUDIT" and warnings:
        return 1, f"historical drift is visible ({warnings} warnings) but separated from readiness"
    if warnings:
        return 1, f"artifacts are actionable but still show drift ({warnings} warnings)"
    return 2, "artifacts appear aligned for the evaluated scope"


def score_execution(payload: dict[str, Any], dispatch: dict[str, Any], handoff: dict[str, Any]) -> tuple[int, str]:
    action = payload["program_action"]
    worker_prompt = dispatch["worker_prompt"]
    chain_state = handoff["chain_state"]

    if action["operating_mode"] == "AUDIT":
        if chain_state == "planner_only" and not worker_prompt:
            return 2, "audit scenario refused fabricated execution and stayed planner-only"
        return 0, "audit scenario still generated execution guidance"
    if action["mode"] == "ASSIGN" and worker_prompt and chain_state == "execution_chain_ready":
        return 2, "assignable scenario produced planner, worker, review, verify, and integrate chain"
    if action["mode"] == "PLAN":
        return 1, "execution guidance correctly stopped at readiness repair"
    return 1, "execution guidance is partially useful but not yet a full chain"


def score_cost(payload: dict[str, Any], audit: dict[str, Any], dispatch: dict[str, Any]) -> tuple[int, str]:
    evidence_count = len(payload["evidence_read"])
    horizon = payload["program_action"]["implementation_horizon"]
    warning_count = audit["warning_count"]
    route = dispatch["recommended_route"]["skill"]

    if horizon == 0 and route == "plan-engineering-program" and evidence_count <= 6:
        return 2, "zero-horizon answer stayed compact and read-only"
    if horizon > 0 and route in {"run-workstream-task", "resume-workstream"} and evidence_count <= 6:
        return 2, "active queue answer stays reasonably small for repo scale"
    if warning_count > 100 and route == "audit-project-scale":
        return 1, "cost is acceptable but audit pressure still requires secondary interpretation"
    return 1, "operator cost looks acceptable but not yet clearly optimized"


def score_trellis_runtime(payload: dict[str, Any], dispatch: dict[str, Any], handoff: dict[str, Any]) -> tuple[int, str]:
    action = payload["program_action"]
    active = payload["active_unit"]
    if action["operating_mode"] == "AUDIT" and handoff["chain_state"] == "planner_only":
        return 2, "runtime state clearly refused execution when no active task existed"
    if action["mode"] == "ASSIGN" and active["task"] and dispatch["worker_prompt"]:
        return 2, "runtime state resolved to one bounded active task with explicit handoff"
    if action["mode"] == "PLAN":
        return 1, "runtime state identifies blockers, but enforcement still depends on prompt discipline"
    return 1, "runtime state is visible, but not as tightly injected as Trellis task-state hooks"


def score_trellis_context(payload: dict[str, Any], dispatch: dict[str, Any]) -> tuple[int, str]:
    context_count = len(payload["active_unit"]["required_context"])
    if payload["program_action"]["operating_mode"] == "AUDIT":
        return 2, "audit mode avoided unnecessary context loading"
    if context_count >= 3 and dispatch["worker_prompt"]:
        return 2, "bounded execution includes an explicit derived context manifest"
    if context_count:
        return 1, "some required context is derived, but injection remains softer than Trellis jsonl/task hooks"
    return 0, "no explicit task context was derived for the active unit"


def score_trellis_entry(payload: dict[str, Any], dispatch: dict[str, Any]) -> tuple[int, str]:
    route = dispatch["recommended_route"]["skill"]
    if payload["program_action"]["operating_mode"] == "AUDIT" and route == "plan-engineering-program":
        return 1, "entry remains planner-heavy, but it still answers cleanly without fabricated execution"
    if route == "run-workstream-task":
        return 1, "entry is useful once the active queue exists, but less frictionless than Trellis task-create/start flow"
    return 0, "entry path is still more ceremonious than a task-first execution harness"


def score_matt_sharpness(payload: dict[str, Any], dispatch: dict[str, Any]) -> tuple[int, str]:
    route = dispatch["recommended_route"]["skill"]
    if route in {"tdd", "diagnose"}:
        return 2, f"route `{route}` is a sharp engineering skill with a narrow behavioral contract"
    if route in {"run-workstream-task", "resume-workstream"}:
        return 1, f"route `{route}` is reasonably narrow, but still sits inside a larger orchestration layer"
    if route == "plan-engineering-program":
        return 0, "planner route is intentionally broad and less sharp than a Matt-style focused skill"
    return 1, "route is moderately focused"


def score_matt_design_pressure(payload: dict[str, Any]) -> tuple[int, str]:
    context_count = len(payload["active_unit"]["required_context"])
    safe_move = payload["program_action"]["safe_next_move"]
    now = str(payload["program_action"]["now"])
    if safe_move == "read-only inspection" and payload["program_action"]["operating_mode"] == "AUDIT":
        return 2, "the flow stays in analysis mode instead of forcing implementation"
    if safe_move == "assignment" and ("tdd" in now or "diagnose" in now):
        return 2, "direct route still names test-first or diagnosis-first execution before coding"
    if context_count >= 3:
        return 2, "execution path stays anchored to design and authority docs before coding"
    if context_count:
        return 1, "some design pressure exists, but it is lighter than a dedicated Matt analysis skill"
    return 0, "design pressure before implementation is weak in this scenario"


def build_comparison(result: dict[str, Any], payload: dict[str, Any], dispatch: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    trellis_runtime, trellis_runtime_reason = score_trellis_runtime(payload, dispatch, handoff)
    trellis_context, trellis_context_reason = score_trellis_context(payload, dispatch)
    trellis_entry, trellis_entry_reason = score_trellis_entry(payload, dispatch)
    matt_sharpness, matt_sharpness_reason = score_matt_sharpness(payload, dispatch)
    matt_design, matt_design_reason = score_matt_design_pressure(payload)

    return {
        "dev_skills": result["scores"],
        "trellis_like": {
            "runtime_enforcement": {"score": trellis_runtime, "reason": trellis_runtime_reason},
            "context_injection": {"score": trellis_context, "reason": trellis_context_reason},
            "entry_friction": {"score": trellis_entry, "reason": trellis_entry_reason},
        },
        "matt_skills_like": {
            "skill_sharpness": {"score": matt_sharpness, "reason": matt_sharpness_reason},
            "design_pressure": {"score": matt_design, "reason": matt_design_reason},
        },
    }


def build_runtime_consumption_view(payload: dict[str, Any], dispatch: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    runtime_block = str(payload.get("runtime_prompt_block") or "")
    active = payload["active_unit"]
    action = payload["program_action"]
    has_runtime_block = bool(runtime_block)
    names_active_unit = bool(active.get("workstream") or active.get("task") or active.get("campaign"))
    names_context = bool(active.get("required_context"))
    worker_prompt = str(dispatch.get("worker_prompt") or "")
    chain_state = str(handoff.get("chain_state") or "")

    baseline_limitations = []
    if action["operating_mode"] == "AUDIT":
        baseline_limitations.append("planner-only audit turns can be mistaken for generic zero-horizon summaries")
    if action["implementation_horizon"] > 0:
        baseline_limitations.append("active queue turns require operators to restate active unit and context manually")
    if not names_context and action["operating_mode"] == "READINESS":
        baseline_limitations.append("required context is weak even before prompt consumption")

    runtime_gains = []
    if has_runtime_block:
        runtime_gains.append("phase/mode/horizon are available as one compact prompt-ready block")
    if has_runtime_block and names_active_unit:
        runtime_gains.append("active unit can be injected without re-synthesizing planner prose")
    if has_runtime_block and names_context:
        runtime_gains.append("required context can travel with the same runtime block")
    if has_runtime_block and worker_prompt and chain_state == "execution_chain_ready":
        runtime_gains.append("execution-chain prompts can share the same derived control state")
    if has_runtime_block and action["operating_mode"] == "AUDIT" and chain_state == "planner_only":
        runtime_gains.append("audit-only refusal is explicit enough to suppress fabricated worker dispatch")
    if has_runtime_block and str(handoff.get("review_prompt") or "").startswith("<planner-runtime>"):
        runtime_gains.append("review/verify/integrate prompts share the same derived control state")

    return {
        "baseline_without_runtime_block": {
            "has_runtime_block": False,
            "active_unit_must_be_reconstructed_manually": names_active_unit,
            "limitations": baseline_limitations,
        },
        "enhanced_with_runtime_block": {
            "has_runtime_block": has_runtime_block,
            "active_unit_named": names_active_unit,
            "required_context_named": names_context,
            "worker_prompt_present": bool(worker_prompt),
            "chain_state": chain_state,
            "handoff_chain_runtime_aligned": (
                str(handoff.get("planner_prompt") or "").startswith("<planner-runtime>")
                and (
                    chain_state == "planner_only"
                    or str(handoff.get("review_prompt") or "").startswith("<planner-runtime>")
                )
            ),
            "gains": runtime_gains,
        },
    }


def expectation_row(passed: bool, reason: str) -> dict[str, Any]:
    return {"passed": passed, "reason": reason}


def evaluate_trellis_expectations(
    scenario: dict[str, Any], payload: dict[str, Any], dispatch: dict[str, Any], handoff: dict[str, Any]
) -> dict[str, Any]:
    expectations = scenario.get("trellis_expectations") or {}
    rows: dict[str, Any] = {}
    active_task = bool(payload["active_unit"]["task"])
    worker_prompt = bool(dispatch["worker_prompt"])
    planner_only = handoff["chain_state"] == "planner_only"
    entry_low = dispatch["recommended_route"]["skill"] != "plan-engineering-program"
    context_count = len(payload["active_unit"]["required_context"])

    if "must_resolve_active_task" in expectations:
        wanted = bool(expectations["must_resolve_active_task"])
        passed = active_task if wanted else True
        rows["must_resolve_active_task"] = expectation_row(
            passed,
            "active task was derived" if active_task else "no active task was derived",
        )
    if "must_emit_execution_handoff" in expectations:
        wanted = bool(expectations["must_emit_execution_handoff"])
        passed = worker_prompt if wanted else True
        rows["must_emit_execution_handoff"] = expectation_row(
            passed,
            "worker handoff prompt exists" if worker_prompt else "worker handoff prompt was not emitted",
        )
    if "must_refuse_fabricated_execution" in expectations:
        wanted = bool(expectations["must_refuse_fabricated_execution"])
        passed = planner_only if wanted else True
        rows["must_refuse_fabricated_execution"] = expectation_row(
            passed,
            "planner-only chain was preserved" if planner_only else "execution chain was still opened",
        )
    if "must_keep_entry_friction_low" in expectations:
        wanted = bool(expectations["must_keep_entry_friction_low"])
        passed = entry_low if wanted else True
        rows["must_keep_entry_friction_low"] = expectation_row(
            passed,
            f"route `{dispatch['recommended_route']['skill']}` {'is' if entry_low else 'is not'} a low-friction entry",
        )
    if "must_minimize_unnecessary_context" in expectations:
        minimized = payload["program_action"]["operating_mode"] == "AUDIT" and context_count == 0
        wanted = bool(expectations["must_minimize_unnecessary_context"])
        passed = minimized if wanted else True
        rows["must_minimize_unnecessary_context"] = expectation_row(passed, f"derived context count = {context_count}")
    if "should_not_remain_planner_only" in expectations:
        wanted = bool(expectations["should_not_remain_planner_only"])
        stayed_planner_only = handoff["chain_state"] == "planner_only"
        passed = (not stayed_planner_only) if wanted else True
        rows["should_not_remain_planner_only"] = expectation_row(
            passed,
            "execution chain was opened" if not stayed_planner_only else "result stayed planner-only",
        )
    return rows


def evaluate_matt_expectations(
    scenario: dict[str, Any], payload: dict[str, Any], dispatch: dict[str, Any]
) -> dict[str, Any]:
    expectations = scenario.get("matt_expectations") or {}
    rows: dict[str, Any] = {}
    route = dispatch["recommended_route"]["skill"]
    sharp = route in {"tdd", "diagnose", "run-workstream-task", "resume-workstream", "audit-project-scale"}
    design = score_matt_design_pressure(payload)[0] >= 2
    heavy = route == "plan-engineering-program"

    if "should_prefer_sharp_skill" in expectations:
        wanted = bool(expectations["should_prefer_sharp_skill"])
        passed = sharp if wanted else True
        rows["should_prefer_sharp_skill"] = expectation_row(
            passed,
            f"route `{route}` {'is' if sharp else 'is not'} a relatively sharp skill boundary",
        )
    if "must_preserve_design_pressure" in expectations:
        wanted = bool(expectations["must_preserve_design_pressure"])
        passed = design if wanted else True
        rows["must_preserve_design_pressure"] = expectation_row(
            passed,
            "design pressure remained high" if design else "design pressure was weaker than expected",
        )
    if "should_avoid_heavy_orchestration" in expectations:
        avoided = not heavy
        wanted = bool(expectations["should_avoid_heavy_orchestration"])
        passed = avoided if wanted else True
        rows["should_avoid_heavy_orchestration"] = expectation_row(
            passed,
            f"route `{route}` {'avoids' if avoided else 'uses'} heavy orchestration",
        )
    if "should_not_miss_ready_execution" in expectations:
        wanted = bool(expectations["should_not_miss_ready_execution"])
        ready_execution = route in {"run-workstream-task", "tdd", "diagnose"} and payload["program_action"]["safe_next_move"] == "assignment"
        passed = ready_execution if wanted else True
        rows["should_not_miss_ready_execution"] = expectation_row(
            passed,
            "ready execution was selected" if ready_execution else "ready execution was not selected",
        )
    return rows


def evaluate(root: Path, scenario: dict[str, Any], strict_history: bool) -> dict[str, Any]:
    payload = build_payload(root, strict_history)
    audit = summarize_audit(root, strict_history)
    dispatch = summarize_dispatch(root, strict_history)
    handoff = summarize_handoff(root, strict_history)

    routing_score, routing_reason = score_routing(payload, dispatch, scenario)
    artifact_score, artifact_reason = score_artifacts(payload, audit)
    execution_score, execution_reason = score_execution(payload, dispatch, handoff)
    cost_score, cost_reason = score_cost(payload, audit, dispatch)

    result = {
        "scenario": scenario,
        "root": str(root),
        "scores": {
            "routing": {"score": routing_score, "reason": routing_reason},
            "artifact_integrity": {"score": artifact_score, "reason": artifact_reason},
            "execution_quality": {"score": execution_score, "reason": execution_reason},
            "operator_cost": {"score": cost_score, "reason": cost_reason},
        },
        "program_action": payload["program_action"],
        "active_unit": payload["active_unit"],
        "recommended_route": dispatch["recommended_route"],
        "chain_state": handoff["chain_state"],
        "audit_pressure": audit,
    }
    result["comparison"] = build_comparison(result, payload, dispatch, handoff)
    result["runtime_consumption"] = build_runtime_consumption_view(payload, dispatch, handoff)
    result["expectation_checks"] = {
        "trellis": evaluate_trellis_expectations(scenario, payload, dispatch, handoff),
        "matt": evaluate_matt_expectations(scenario, payload, dispatch),
    }
    return result


def render_text(result: dict[str, Any]) -> str:
    scenario = result["scenario"]
    lines = [
        f"## Scenario Evaluation: {scenario['name']}",
        f"Repo: {result['root']}",
        f"Scale Expectation: {scenario['scale_expectation']}",
        f"Recommended Route: {result['recommended_route']['skill']}",
        f"Program Mode: {result['program_action']['mode']} / {result['program_action']['operating_mode']}",
        f"Implementation Horizon: {result['program_action']['implementation_horizon']}",
        f"Chain State: {result['chain_state']}",
        "",
        "## Scorecard",
    ]
    for key in ["routing", "artifact_integrity", "execution_quality", "operator_cost"]:
        row = result["scores"][key]
        lines.append(f"- {key}: {row['score']} ({row['reason']})")
    lines.extend(["", "## Comparison View"])
    for family, metrics in result["comparison"].items():
        lines.append(f"- {family}:")
        for metric, row in metrics.items():
            lines.append(f"  - {metric}: {row['score']} ({row['reason']})")
    lines.extend(["", "## Runtime Consumption"])
    runtime = result["runtime_consumption"]
    baseline = runtime["baseline_without_runtime_block"]
    enhanced = runtime["enhanced_with_runtime_block"]
    lines.append(f"- baseline_without_runtime_block: manual_active_unit_reconstruction={baseline['active_unit_must_be_reconstructed_manually']}")
    for item in baseline["limitations"]:
        lines.append(f"  - limitation: {item}")
    lines.append(f"- enhanced_with_runtime_block: has_runtime_block={enhanced['has_runtime_block']}, chain_state={enhanced['chain_state']}")
    for item in enhanced["gains"]:
        lines.append(f"  - gain: {item}")
    lines.extend(["", "## Expectation Checks"])
    for family, checks in result["expectation_checks"].items():
        lines.append(f"- {family}:")
        if not checks:
            lines.append("  - (none declared)")
            continue
        for key, row in checks.items():
            lines.append(f"  - {key}: {'PASS' if row['passed'] else 'FAIL'} ({row['reason']})")
    return "\n".join(lines)


def load_scenario(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", help="path to scenario json")
    parser.add_argument("root_arg", nargs="?", help="repository root")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict-history", action="store_true")
    args = parser.parse_args()

    scenario = load_scenario(Path(args.scenario).resolve())
    root = Path(args.root_arg or args.root).resolve()
    result = evaluate(root, scenario, args.strict_history)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
