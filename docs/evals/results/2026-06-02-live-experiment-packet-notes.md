# Live Experiment Packet Notes — 2026-06-02

## Purpose

This note records the final preparation layer before true subagent execution on a host that
actually exposes subagent capabilities.

The current host in this repository work session does not expose a callable subagent API.
So instead of pretending to have completed live execution, the repo now produces portable
experiment packets that can be moved into a subagent-capable host with minimal manual repair.

## Artifact

Script:

- `skills/engineering/plan-engineering-program/scripts/live_experiment_packet.py`

Supported experiment names:

- `hajimi_refusal`
- `nako_chain`
- `skills_restraint`

## What A Packet Includes

Depending on the scenario, the packet includes:

- wrapped planner prompt
- worker prompt
- review prompt
- verify prompt
- integrate prompt
- recommended route
- operating mode
- chain state

This turns the current live-run materials into one portable handoff artifact.

## Why This Matters

The previous runbooks were useful, but they still required the operator to gather pieces from
several scripts and notes.

The packet generator reduces that friction:

- one command per scenario
- one normalized output shape
- ready to paste into a host that supports real subagent execution

## Current Limitation

This still does not satisfy the full live-subagent objective inside the current host.

What is now true:

- the experiment design is mature
- the repo-state derivation is mature
- the prompt packets are portable

What is not yet true in this host:

- real subagent execution has not been performed here

## Recommended Use

When moving to a subagent-capable host:

1. generate the packet locally in this repo
2. paste the planner prompt into the planner session
3. paste role-specific prompts into worker/reviewer/verifier/integrator sessions only when the
   packet actually contains them
4. record outcomes using the runbook templates already present in `docs/evals/results/`
