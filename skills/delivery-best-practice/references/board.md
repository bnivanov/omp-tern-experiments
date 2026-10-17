# Board

`TODO.md` at the project root defined in the skill is the board only after main checks ownership and the user wants a board, or this project already owns it. The effective writer is the latest writer-transfer Revision on the active run, otherwise that run's initial Writer. A subagent does not create or edit the board unless the brief assigns that one edit.

Tern renders this Markdown file; it is not another task store. Use one durable task authority only when useful, not a card for every session or one-off. The session OMP todo tool is for transient execution steps when useful or required by native instructions; never mirror or synchronize the board's backlog/status in it. Do not export its checklist onto this file.

## Authority across checkouts

The authoritative board is the adopted `TODO.md` at the project root in the nominated record checkout. With one unambiguous checkout, use its owned board; with multiple relevant checkouts, name authority before writing. A copy in another worktree or clone is not a lock or another claim. Same-run worktrees use the nominated file and one effective writer. Authority may itself be in a worktree or clone.

An independent child project may own a separate scoped board at its own root. That ownership does not extend to the workspace board, and the workspace board is not that project's plan. An exceptional second writer does not receive shared-board edits. That writer returns a separate report for the effective writer to integrate, as the skill's Identifiers section describes.

A Tern tab, window, or rendered board is not isolation and not authority. Use the explicit cwd and the actual file path before reading or editing. Do not integrate board edits into a checkout another live writer is editing.

## Schema check

Read `TODO.md` before using it.

- Missing, and the user wants a board: create it from `templates/TODO.md` (relative to this skill). Do not add cards in that create.
- Present: four matching lanes are not proof this file is our board. Adopt it only when this project already owns it as the delivery board, or the user explicitly authorizes that adoption, and the lanes are `Todo`, `Doing`, `Blocked`, `Done` in that order. If the shape differs, do not rewrite it to force the schema.
- Otherwise do not adopt it. Ask once which board is authoritative. Until answered, keep status in the reply.

Lanes are workflow status only. Acceptance and integration evidence live in `RUN/PLAN.md` or `RUN/HANDOFF.md`. Moving a card does not prove a check passed, and it does not approve the plan.

## Cards

A card is one selected deliverable: one line with `- [ ]` or `- [x]`, a never-reused task id, short title, then optional `#<run>` and `#<session>` tags. An active claim names its assigned execution session, which may differ from the coordinator editing the board. Tags use letters and digits. A blocker is an indented `Blocker:` line. Do not copy session checklists onto cards or add subtasks, due dates, or sample cards.

A card selected from the backlog cites its source backlog id in the title text, not as another run/session tag.

Task ids follow the skill: stable, never reused, generated unique before any reference. If a candidate collides, generate another id before writing it. Do not change an id after it has been written or cited. Never overwrite a file to mint an id.

## Claims

Only the effective writer/coordinator edits the canonical board. It records each bounded assignment, session id, checkout, tab/pane identity, and record authority in the existing plan or handoff's Claims, then claims by adding the execution session's tag and moving the card to `Doing` in one fresh edit. A brief alone is not durable assignment evidence. Execution ownership does not grant board-edit ownership. Workers report state, blockers, and evidence. A tag is not authorization. Do not retag an unverified copy or reassign a possibly live owner's work without release or explicit takeover authority. Reconcile stale edits; fresh reads are not mutual exclusion.

## Drift

Re-read a card before acting. These are drift, not permission to start:

- `Doing` with no claim, or a claim for a session with neither coordinator ownership nor a recorded bounded assignment.
- `Blocked` with no `Blocker:` line, or a `Blocker:` line outside `Blocked`.
- `Done` while a `Blocker:` line remains.
- An active card, not `Done`, whose run is `closed` or `superseded`.
- A lane that disagrees with the latest handoff.
- A non-authoritative checkout copy treated as the board, or a claim that exists only on that copy.

`Doing` on an authorized `draft` is not drift. Stop and reconcile real drift. Ask if reconciliation changes who owns an unreleased card. A GUI edit is a file change. It does not approve work, authorize a claim, or replace evidence.

## Takeover

A normal `Writer released: yes` handoff transfers the coordinator's writer role and own unfinished claims, not claims of potentially live workers. When the user asks a successor to resume, append the writer-transfer Revision, update the handoff writer and set release to `no`, then retag only the prior coordinator's released claims. Preserve live worker assignments and last reports. Require explicit takeover if the prior coordinator or execution owner may still be live and has not released. Silence, age, or a GUI move is not release. Record authorized reassignment and the previous claim without deleting its id.
