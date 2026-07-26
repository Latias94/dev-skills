# Recover subagent continuity

Codex persists enough information to reconstruct a subagent family, but no disk artifact is a live
runtime registry. Preserve that distinction throughout recovery.

## Recovery boundary

Recovery imports evidence from a different previous session. The selected JSONL and its subagent
rollouts are historical sources, not a second context that should keep competing with the receiving
session. Once the handoff is accepted or the original root is resumed, that receiving or resumed
session becomes authoritative. Its later compaction summaries continue the same context.

Do not run the summarizer again against the old source after an ordinary compaction. Invoke recovery
again only to import an explicitly selected different prior session, or from a new session when the
current session itself has become unusable. Avoid `latest` after handoff unless it is being resolved
for a new, explicit cross-session recovery.

Codex injects `CODEX_THREAD_ID` into shell processes. The CLI records that receiving thread in
`recoveryBoundary`, rejects an explicitly selected rollout from the same session family, and excludes
that family when resolving an explicit `latest`. This is a safety signal rather than authentication:
concurrent unrelated Codex sessions still make `latest` ambiguous, so prefer a stable path or id.

## Evidence and meaning

| Evidence | What it establishes | What it does not establish |
| --- | --- | --- |
| Child `session_meta.id` | The child thread id and rollout identity | Whether the child is currently loaded |
| `parent_thread_id` or `source.subagent.thread_spawn` | Direct parent, depth, path, nickname, and role | Whether the parent can currently contact it |
| `state_5.sqlite.thread_spawn_edges` | Persisted `open` or `closed` spawn-edge state | Current `running`, `completed`, or errored status |
| Child rollout lifecycle events | Last persisted `running`, `completed`, `interrupted`, `errored`, or `shutdown` state | Current state after a crash or process restart |
| `list_agents` after root resume | Current status of agents loaded in the resumed runtime | Persisted handles that have not been lazily reloaded |

`open` means the edge was not explicitly closed and the child may be resumable. Completed agents
commonly remain open so they can receive follow-up work. A persisted `running` event means only that
the turn had started when the rollout was last written; a crash can leave it stale.

## Preferred recovery sequence

1. Run `summarize_session.py` on the root or any child rollout. Subagent discovery is on by default.
2. If a child was selected, verify that `selection.promotedToRoot` is true. The top-level summary then
   describes the root while `subagents.selectedThreadId` preserves the requested child.
3. Read `subagents.rootThreadId`, `recoveryCommand`, the edge status, and each child's last persisted
   status.
4. If this is a forced new chat or a cold process, do not immediately spawn replacements. Resume the
   original root with `codex resume <root-thread-id>`.
5. In the resumed root, call `list_agents` to obtain authoritative status for agents loaded in that
   runtime. A missing persisted handle is not proof that it cannot be resumed.
6. Continue according to the reconciled state:
   - `running`: wait or send a non-triggering message when appropriate.
   - `completed`: consume the result; use `followup_task` only when more work is needed.
   - `interrupted`: send an explicit follow-up if the task should continue.
   - missing from the live registry but persisted as open: MultiAgent V2 `followup_task` can lazily
     reload a known child by canonical path after the root is resumed. Older V1 flows may expose
     `resume_agent` by thread id.
   - persisted as closed: treat it as history and do not reopen it automatically.
7. Spawn a replacement only after verifying that the original handle cannot or should not continue.
   Give the replacement the recovered task and state explicitly; do not pretend it is the old agent.

If the original root cannot be resumed, treat child rollouts as handoff evidence. Inspect each task,
last message, compaction, plan, and repository state before deciding what remains.

## Script behavior

The script reads `state_5.sqlite` with a read-only SQLite connection. It honors
`CODEX_SQLITE_HOME`; otherwise it looks next to the sessions directory. Use `--state-db` for a
nonstandard layout.

When the state DB or spawn-edge tables are unavailable, the script scans rollout `session_meta`
records and reports lineage with `edgeStatus=unknown`. This fallback cannot distinguish open from
closed edges. If a state DB exists but its graph appears incomplete, rerun with
`--scan-rollout-lineage` to augment DB edges from all rollout metadata. DB edge state wins when both
sources describe the same child. The scan can take several seconds on a large archive.

Long-lived root sessions can have hundreds of historical descendants. The script first shortlists
the selected child and the most recent non-closed descendants, up to the greater of 128 or eight
times `--max-subagents`. It scans backward through at most 8 MiB of each shortlisted rollout for its
most recent persisted lifecycle event, then fully reads only the 24 highest-priority descendants.
The ranking prefers selected, non-closed, `running`, `interrupted`, and `errored` candidates before
completed or unknown candidates. It never establishes live status. Inspect `candidateProbe` for
selected, skipped, truncated, and successful probes; increase `--max-subagents` for a wider audit or
use `--no-subagents` when only the selected rollout matters.

Ephemeral subagents may have no durable edge or rollout. No recovery script can recreate state that
Codex did not persist.

## Safety

- Keep the SQLite connection read-only. Do not update edge status or thread metadata during recovery.
- Do not call `close_agent`, `resume_agent`, `followup_task`, or spawn tools solely from persisted
  status; reconcile the original root first.
- Keep recovered prompts and messages truncated and redacted. Read exact child excerpts only when
  they answer a concrete recovery question.
- Preserve agent paths, roles, thread ids, and parentage in the handoff so nested work is not flattened
  into unrelated tasks.
