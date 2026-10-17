---
name: delivery-best-practice
description: Proportional playbook for substantive delivery, multi-session resume, or explicit board use. Main owns shared state and integration. Optional records, evidence-based acceptance, isolated writes reviewed before they land.
---

# Delivery best practice

Only main loads the whole skill, and only after the always-on rule has sized the work as substantive, multi-session, or explicit board use. A child may read a named section when the brief names it. A child does not load the whole skill to set up, interview, or open a second plan. Paths are relative to this skill.

Native system and tool instructions still win. Do not restate live schema fields, model roles, or isolation settings. Use the schema you were given.

## Loop

1. Confirm the work is substantive. If it is quick, stop using this skill.
2. Create durable records only when the user asked to track work, or a later session must resume it.
3. Clarify only a material tradeoff. Otherwise take the sensible default and continue.
4. Before routine work on a plan, record `Authorized by` with a quote or pointer. A draft may be authorized. Do not wait for status `approved`. Ask only for a material scope change, an irreversible action, or an unresolved tradeoff. Do not stop after each wave for ceremony.
5. Deliver those slices. Prefer isolated checkouts for substantive writes when the schema, a committed `HEAD`, and the repo allow it.
6. Review returned artifacts, integrate through main, smoke the integrated surface, and recheck any serious fix.
7. Hand off in proportion to what the next session would otherwise lose. Close only when the success criteria pass or the user stops the run.

## Start

Project root is the explicit user or workspace boundary, or the root of an established project tracker. It may be inside a Git repository or in an explicitly chosen worktree/clone. Otherwise use the Git top-level, then cwd only without Git. Inspect ancestor state and instructions first; cwd alone does not establish a child project. Ask only when boundaries conflict.

A repository may contain several related projects with separate optional records. Workspace-level records cover workspace work, not every child project's delivery. A project folder is not a separate Git checkout or runtime environment.

Follow established project layout and trackers. For a new sustained project in an umbrella repository with no existing convention, prefer `projects/<slug>/README.md` naming scope, entry points/checks, authoritative records, and shared dependencies. A bounded experiment may need only `experiments/<slug>/README.md` containing its question, method, evidence, conclusion, and limits. Use only needed source/docs and optional `RUN/` records; a board must be deliberately adopted. Do not create speculative folders, mandatory strategy/review bundles, or another board per feature or evaluation run.

Before adding a project, assess repository fit. Keep it together when purpose is coherent, access/data policies are compatible, and shared changes and review history are useful. A shared product or technology label alone is insufficient. Recommend a sibling folder with its own Git repository when scope is unrelated, access/sensitivity differs, independent ownership/releases have little coupling, or tooling/size/churn would harm the shared repository. Releases and toolchains are signals, not automatic split rules; there is no project-count threshold. Explain the recommendation and ask only for a materially unresolved choice. Do not create, move, split, or nest repositories, run `git init`, commit, or rewrite history without user authority. Avoid casual nested repositories/submodules; do not relocate completed history merely to adopt a convention.

Before first-use record creation as well as resume, perform the checkout-authority check in Resume. A worktree's copied tracker or old released handoff is not proof that this checkout owns shared state.

On first use, look for an existing board and `RUN/` at that project root before creating anything. Missing files are not a reason to stop work the user already authorized. Create a missing record only when this run will use it, from the matching template, and only if that path is absent.

On resume, use the Resume section. Do not rebuild an authorized plan from scratch.

## Records

The coordinating main owns shared records for its project; a top-level session assigned as an execution worker does not become another coordinator. Workers own only their bounded slice/checkout and report evidence; they do not edit shared plans, boards, or coordinator handoffs, including copied versions. Name record authority and integration owner in existing records, not a new registry. Workspace root trackers cover workspace-level work only.

- Tasks: keep one durable task authority, only when useful. Tern renders `TODO.md`; it is not another task store. The OMP session todo tool is only for transient execution steps when useful or required by native instructions, never a mirrored backlog/status queue. Do not create a durable card for every session or one-off change.
- Board: optional `TODO.md` at the project root, only after the ownership check in `references/board.md`. Four matching lanes are not ownership. Use an existing tracker rather than opening another board. Do not point the session todo tool at `TODO.md` or synchronize their lists.
- Other records, and only the ones this run needs, live in `RUN/` at that root: `PLAN.md`, `DECISIONS.md`, `HANDOFF.md`, `BACKLOG.md`. Copy from `templates/`. If that path exists, do not overwrite it. If an existing tracker already has that role, use it. Do not open a second set. These four files are optional. Do not require the old ledger (`STATE`, `LOG`, `SESSIONS`, `LEARNINGS`, `FINDINGS`) or any other ceremony file. Do not put a child project's plan in the workspace root `RUN/`.
- The effective writer is the latest writer-transfer Revision on the active run, otherwise that run's initial `Writer`. This coordinator alone owns shared-record edits; assigned execution sessions do not gain that ownership. A released handoff transfers the coordinator's own unfinished claims, not claims of workers that may still be live. Independent child projects may own separate scoped trackers and writers.
- Canonical records live in the explicitly nominated checkout. With a single unambiguous checkout, use its owned records; with multiple relevant checkouts, name authority before writing. Same-run worktrees use that location and one writer, not their copied files. Independent child projects may nominate different record locations.
- Verify nested private/runtime paths are ignored before use; root-anchored rules do not cover child roots. Add scoped exclusions as authorized routine work, preserving tracked content and intended source/configuration; ask only for an actual conflict. Track sanitized records only. Ignore rules do not provide access control or untrack files.

## Identifiers

Workflow run and session ids are letters and digits only. Use a runtime id only when it is already alphanumeric. If it contains punctuation, do not strip it and do not use it as the workflow id. Generate a separate alphanumeric id from a UTC timestamp plus a random suffix, and record the runtime id as `Runtime` provenance. Ids are scoped to the authoritative project tracker. Never reuse a run, session, task, or backlog id within that tracker, including after done or closed. A collision across projects is not reuse. Scan that tracker before allocating; do not scan every project in the git root. If a candidate collides, generate another unique id before anything references it. Do not change an id after it has been written or cited. Create files so an existing path is never overwritten. A released handoff is reused by the successor.

For a coordinated worker, the coordinator allocates its alphanumeric workflow session id before launch and includes it in the brief/assignment. The worker adopts that id, not a competing generated one; its native runtime id is separate provenance. Qualify cross-project references with the project/record location.

Keep one effective writer. An exceptional second writer, authorized by the user while the first has not released, does not gain shared-board ownership and does not become a second effective writer. It writes a separate report at that project's `RUN/handoffs/<session-id>.md` only when that path is absent. `<session-id>` is the alphanumeric workflow session id. It then returns that report to the effective writer for integration. If the path is already present, do not overwrite it; return the report in the reply for the same integration. The effective writer integrates it into the canonical records. The report is not a second plan or a second board.

## Lifecycle

The first run is the top-level block in `RUN/PLAN.md`. Later runs do not overwrite it and do not require an archive. After a run is `closed` or `superseded`, append `## Run <alnum-id>` with that run's own status, writer, `Authorized by`, and the same fields. Do not add a second `# Plan` title. The latest active run is authoritative. Earlier sections stay. A file that has only the top-level block is that first run. Leave it. Status on each run is `draft`, `approved`, `closed`, or `superseded`. There is no `none`. A draft may be authorized. Routine reversible work needs `Authorized by` before it starts. Explicit approval is required before a material scope change, an irreversible action, or an unresolved tradeoff is built. Record that approval, and any writer transfer, as an appended Revision on that run. Do not close or supersede because a file got long. Manual archive only when the user authorizes it. Never delete records.

## Plan and slices

A plan states the goal, checkable success criteria, approach, slices, verification, boundaries, risks, and stop conditions. Cut slices by result, riskiest first. Parallel slices have no dependency and disjoint outputs. Write each check before the build when the work is large enough to plan: the command or observation, the actual path, and the expected result.

When the project root, checkout, or integration owner is not the single obvious workspace checkout, record repo, project, checkout, branch, record authority, and integration owner in Boundaries. Leave those labels blank otherwise. Do not open a registry or a shared root plan for a child project.

A slice is ready when its acceptance check is written, its inputs exist, its output paths do not overlap a running slice, and its dependencies are accepted. If one of those is missing, fix the plan or the brief. Do not start the slice.

A brief carries the goal, allowed paths, non-goals, the acceptance check, and where to write the result. It does not carry a model name, a token budget, or an instruction to update shared delivery files. Questions that block the slice come back as questions, not as guessed work.

When more than one project or checkout exists, the brief names the project root, checkout, record authority, and integration owner. It still does not tell the child to open a second plan or board.

New work found mid-run goes to the backlog when records exist. It does not silently enter the current slices. A result that changes the approach is a Revision, not a quiet edit.

## Acceptance

Evidence is the check, the actual path, and the result, recorded on the plan or handoff. The card lane is not evidence. A GUI move does not authorize work. Smoke the surface the next step will actually use, after integration, not a substitute tree. Main judges the whole. A subagent returns slice evidence and does not certify the integrated result.

When every slice is integrated, run each success criterion once against the integrated tree and record the command and result. A failure becomes a new slice or a fix, not a verbal pass. Only then is the run ready to close.

## Concurrency

State the repository, project, checkout, branch, allowed paths, record authority, and integration owner in the existing plan, handoff, or brief. Do not create a registry, lock file, or configuration change to do that.

Default to one writing main per checkout. Independent mains use separate worktrees with distinct branches, or equivalent separate checkouts; branches alone in one checkout do not isolate files or the index. A shared-tree write requires explicitly assigned disjoint ownership, including records/generated files. Coordinate repository-wide operations and shared refs. Do not change runtime settings, commit, push, or rewrite history without the required user authority.

For several sessions working from one backlog, keep one coordinator as shared-record writer. The adopted board shows selected deliverables, assigned execution-session tags, and reported state—not internal checklists. Durably record each bounded assignment, session id, checkout, tab/pane identity, and record authority in the existing plan or handoff's Claims; a brief alone is insufficient. Workers report progress, blockers, and evidence to that writer without gaining shared-record edits.

Tern renders the recorded file; this package provides no automatic live-session aggregation, scheduling, locking, or monitoring. Show reported status, not inferred liveness or completion. Independent project boards remain scoped to their projects; a workspace index may link them without copying their task queues.

Child task isolation does not isolate main. In a normal git worktree, refs and objects are shared with the repository. cwd is not a security or instruction boundary. The live omp task-isolation backend may differ from a git worktree, including a clone-first copy. Use the schema you were given. Do not assume the backend or name one you were not given.

Copies of `TODO.md` or `RUN/` in another worktree are not shared locks. Worktrees of the same run use the nominated canonical tree and its single writer. An independent child project may own a separate scoped tracker. There is no blanket ban on a worktree or clone being the project root, and canonical records may live in any explicitly chosen checkout.

Do not integrate into a checkout another live writer is editing. Serialize shared root files, shared dependencies, and the target integration: dry-run, then smoke the integrated result. A chosen tab, window, or board is not isolation. Name the explicit cwd and the actual board path.

Plugin install, link, or reload can affect a running daemon outside the source tree. Coordinate ports, databases, services, and other shared resources separately. A worktree does not do that, and task isolation does not do that.

### Visible interactive sessions

When the user requests visible Tern sessions, launch only ready work covered by the user's execution authorization in this conversation; backlog presence, including a quoted user item, is not authorization. Check dependencies, overlapping outputs, shared files, and runtime resources. The brief explicitly names the execution-worker role, coordinator, preassigned workflow session id, allowed paths, checkout/project root, canonical records, acceptance check, and integration owner. It forbids edits to shared plans/boards/handoffs, even copied versions. This does not authorize commits, installation, or settings changes.

Resolve the intended Tern window/session with the native CLI before launch; do not silently use an arbitrary first window. Launch one interactive OMP process per tab, not print/RPC/headless mode or a `task` substitute. The native shape is `tern new tab <tern-session> --cwd <project-checkout> -- omp --cwd <project-checkout> "<sanitized brief or pointer>"`; use `--window` when targeting requires it and verify current CLI help. A Tern session is a tab container, not an OMP conversation. Do not put secrets in command arguments.

Before launch, durably record the assignment, workflow session id, checkout/branch, starting commit and scoped starting-state baseline in the existing plan or handoff's Claims; append the returned tab/pane identity. A launch argument or brief alone is not a durable assignment. Fresh worktrees start from commits and may lack uncommitted canonical inputs: supply and record required scoped inputs or resolve the dependency before starting, never silently commit them.

Observe OMP in the intended tab/directory; launch exit status is not acceptance. Use targeted native capture/send for observation or steering, never guessed focus or indiscriminate input. Report waiting/blocked states; do not bypass approvals or infer completion from a quiet tab.

Workers report evidence and a completion/stopped state to the coordinator. For recoverable handoff, write a sanitized report only to the assigned worker checkout's `RUN/handoffs/<session-id>.md` if absent, or return it in the reply; never overwrite a report or edit `RUN/HANDOFF.md` / `TODO.md`. The coordinator records durable report/evidence pointers in canonical records before releasing.

Before capture, stop writes and keep the worker checkout frozen through handoff. Capture only its delta from the recorded starting state as a reviewable patch, including intended new/untracked files, binary changes, deletions, and modes; a plain `git diff` omits untracked files. Use a temporary-index capture or equivalent that preserves the worker's index and inherited baseline; never sweep ignored/private/unrelated files. Record the artifact and base. Use a committed branch artifact only with commit authority.

The coordinator reviews scope, dry-runs the patch against the current integration target, applies one artifact at a time, and smokes the integrated result; do not integrate into another live writer's checkout or force conflicts. Bounded helper subagents may assist but do not replace requested visible sessions. No automatic scheduler, live collector, or self-starting backlog loop is provided.

## Isolation and integration

The flag below isolates a delegated write checkout, not its main session; use Concurrency for main-session and runtime boundaries.

Prefer `isolated: true` on a substantive write slice only when all of these hold: the live task schema includes `isolated`, the target is an eligible git repository, and `HEAD` is a valid commit. A repository without a committed `HEAD` failed patch capture with `object not found` on the verified runtime. Do not set the flag then. Dirty or untracked files in a repository with a committed `HEAD` are not the same failure; the runtime captures uncommitted baseline state. Use the shared checkout when isolation is ineligible, or ask the user to authorize an initial local commit. `git init` and staging are not that commit. Omit isolation for read-only work, when the field is absent, or when the brief assigns a shared-tree write. Omitted or false means the shared checkout. A shared-tree write remains valid for disjoint ownership and when isolation cannot be used. Do not set the flag blindly, and do not describe isolation as a shell, network, or credential sandbox.

Do not assume a successful isolated task landed. Require the returned patch artifact, or a branch artifact only if the runtime actually returned one. Do not request a branch-mode commit. Main reviews the diff for the intended paths, then integrates it only after a dry-run conflict check succeeds. If the check fails, keep the conflict artifact and report it. Do not force it. After a clean integrate, smoke those integrated paths. Do not change isolation config unless the user explicitly asks. If they do, change only the requested knob and preserve the others.

Record the artifact path, the scope review, the conflict-check result, the integrated path, and the smoke result on the handoff or plan. A subagent reply that says the work landed is not that record.

## Delegation

Main may implement. Delegate independent substantial work with the goal, constraints, allowed paths, and the acceptance check. Do not impose reply, turn, or read caps. Do not send subagents to recreate this setup, interview the user, or update shared delivery state unless the brief assigns one named edit. Judge the return against the check and the decisions, not against confidence.

## Review

Match review to risk. Use a dedicated pass for security, data loss, hard-to-reverse change, or when the user asks. Skip it for a trivial edit. After a serious fix, recheck that fix against the finding before accepting it. Plan approval is not a review request.

## Clarification

Look up facts yourself. Ask only when a material tradeoff changes the deliverable and cannot be defaulted: incompatible goals, an irreversible choice, or a missing requirement. One round, each question with a recommended default. Do not interview until every assumption is spoken. Subagents put questions in their reply. They do not open a user interview. When records exist, main appends confirmed decisions, quotes the user, and tags inferences `[INFERENCE]`.

## Resume

Before creating shared records or taking a released writer transfer, establish checkout authority from the assignment and existing records. Inspect `git worktree list` for linked checkouts and any known separate clones from the brief/runtime; Git cannot enumerate arbitrary clones. If multiple relevant checkouts exist and authority remains unnamed, treat local `TODO.md` / `RUN/` as unverified copies and resolve the location before writing, asking only if tools/records cannot settle it. A committed old `Writer released: yes` does not release an uncommitted live coordinator elsewhere. Workers never take the coordinator role merely by resuming.

Main reads the active run, including Revisions, writer transfers, boundary fields, decisions, the handoff, any adopted board, and authoritative sources. Recheck stale facts, then continue authorized work, including a draft. Do not require status `approved` or apply fixed read quotas. If `Writer released` is `yes` and the user said to resume, take the transfer in Handoff. Skip archives unless pointed to or named. Use the nominated record authority, not an unverified copy in another checkout.

## Handoff

Write a handoff when a later session would lose the next action or the user is about to clear context. `Writer released: yes` releases the coordinator and the coordinator's own unfinished claims. Preserve assignments of potentially live workers, including checkout and last reported state; they are not released by the coordinator's handoff. Record authority, integration evidence, blockers, and claims without copying the conversation. Reuse the handoff; do not rotate, archive without authority, or delete records.

When a later session could open the wrong tree, fill the handoff's boundary labels: repo, project, checkout, branch, record authority, and integration owner. Name a distinguishing checkout location/worktree and branch, never just “this checkout”; separate clones may share branch names. Leave labels blank only for one unambiguous checkout. A copied handoff does not transfer authority.

The user's instruction to resume a released run authorizes the successor coordinator. Append a writer-transfer Revision naming both writers and the instruction; update the handoff writer/runtime provenance, set `Writer released: no`, and retag only the prior coordinator's released claims before implementation. Keep live worker assignments intact until completion, explicit release, or authorized reassignment. Do not ask again for the released transfer. Require an explicit takeover if the prior coordinator may still be live or did not release.

If no later session needs the work, the reply is the handoff. Do not create `RUN/HANDOFF.md` for a one-shot answer.

## Backlog

When records exist, deferred work and unresolved findings go to the existing backlog without silently expanding scope. Quote user items and tag agent proposals `[PROPOSED]` until confirmed. Before selecting work, obtain execution authorization. If an adopted board tracks execution, add `Selected: <card-id>` and its project/board pointer to the backlog row's Source, then let that card own live execution status. A newly allocated card id references the stable backlog id; do not allocate an already used id to a different item.

When accepted work finishes, the backlog's Done row is historical disposition, with pointers to the card and plan/handoff evidence—not another live status queue or copied evidence log. Session todos hold transient steps, not another backlog or board.

## Templates

Copy only the file you are creating. Leave tables empty. Plan and handoff boundary labels are optional; leave them blank when this checkout is already obvious. Do not add example rows.

- `templates/TODO.md`
- `templates/PLAN.md`
- `templates/DECISIONS.md`
- `templates/HANDOFF.md`
- `templates/BACKLOG.md`

Board ownership, claims, drift, and takeover: `references/board.md`.

## Do not

- Do not imitate or copy native `/init`, and do not invent a project-init or bootstrap command. When the user explicitly asks for repository guidance, run the real native `/init`. Preserve existing `AGENTS.md` and other user guidance unless they asked to update it.
- Do not commit, push, rotate, or delete records unless this conversation authorizes that exact action. That includes the initial local commit required before isolation can capture a patch.
- Do not assert model names, prices, token ceilings, or borrowed approvals.
- Do not change task eagerness, model roles, badges, or isolation config unless the user explicitly requests that change. Preserve every unrelated knob.
- Do not scaffold unused records, a per-feature board, or a child plan on the workspace root. Do not create, move, split, or nest repositories or add submodules without user authority.
