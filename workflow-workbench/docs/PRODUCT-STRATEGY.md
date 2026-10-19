# Workflow Workbench — product strategy

Status: **parked** (2026-10-19). The user chose to step back from business development and PPTX production and scaffold the evaluation approach first. [WORKFLOW-EVALS-STRATEGY.md](WORKFLOW-EVALS-STRATEGY.md) is the working specification for evaluation and runtime direction. It supersedes: §6 (evals suite); the portable core in §4 and the Claude-Code-without-OMP path in §1 and §8 (now OMP + Tern centric, Claude Code only as a fallback; the corporate laptop runs OMP + Tern with Claude-only models); §7 (replaced by the strategy's learning loop and evidence levels); and the §10 gates (replaced by the strategy's phased roadmap, where business development and PPTX wait for an L2 result). §5 (Proposal pilot), the corporate policy checks in §8 and the Tern Apply/Validate/Save safety contract in §4 remain inputs for when the proposal domain is built on the lab. The original text below is unchanged. It was a strategy for review and staged delivery, not a claim that the complete product exists.

## 1. Decision and product thesis

Build a personal lab workbench that makes recurring advisory and product work explicit, observable, comparable, and improvable. Use OMP for execution and Tern for native authoring/inspection where available; saved workflows must also execute through Claude Code without OMP or Tern. Do not build another agent harness or a general-purpose automation platform before proving one useful workflow.

The product is the connection between **definition → execution evidence → evaluation → deliberate revision**, not the diagram alone. A workflow earns its complexity only when it beats a capable single-agent/manual baseline on accepted outcomes or human effort at an acceptable cost.

## 2. User, jobs, and constraints

Primary user: an individual knowledge worker in a small advisory/product lab, not a large platform team. Recurring jobs span advisory/proposal development, product discovery/design/development, and strategy/operations. The chosen pilot is Proposal Development: an effective proposal and ultimately an editable, reviewed presentation—not merely a generated file.

User-confirmed goals:

- Visual creation and adaptation of task/agent workflows, with inspectable saved execution logic.
- Linked sessions, artifacts, interventions, failures, and actual usage/cost evidence.
- A Workflow Evals Suite for comparisons across versions, models, prompts, tools, and skills.
- Low friction with OMP/Tern upgrades: supported external integration, no core forks.
- Development on this machine, eventual use on a corporate laptop, and sanitized product feedback returning here.
- Claude Code execution because workplace tooling may differ. Portability includes running without the Tern UI.

This delivery establishes the project, reviewed strategy, and a narrow cross-runtime execution proof. It is not the full visual workflow product, proposal/PPTX pipeline, or empirical validation of business value.

## 3. Product surfaces

| Surface | Question answered | Essential information |
|---|---|---|
| Design | What should happen? | Task dependencies, artifact contracts, role/runtime bindings, approval gates, limits, version and environment dependencies |
| Run | What actually happened? | Attempts, native session links, accepted/rejected outputs, failures, approvals, elapsed time, interventions, usage coverage |
| Experiments | Is a revision better? | Paired cases, repeats, frozen rubric, held-out cases, uncertainty, quality/effort/cost tradeoffs |

Planned graph and actual trace are separate views. A design node may have several attempts or nested sessions; one runtime session may include auxiliary calls. Never force these into a misleading one-to-one correspondence.

## 4. Architecture and authority

### Portable core

The canonical workflow definition is provider-neutral data: stable workflow/task identifiers, dependencies, prompt/resource references, declared inputs/outputs, approval points, and supported execution capabilities. Prompts, rubrics, and public/synthetic fixtures are versioned alongside it. Layout belongs in separate presentation state; Tern shape identifiers are not task identifiers.

Start with an explicitly supported finite sequential subset. Do not promise arbitrary DAGs, cycles, distributed recovery, or unrestricted code-to-graph conversion. Reject unsupported structures instead of silently reinterpreting them. The canonical manifest and referenced prompts are interpreted by one versioned runner. A future UI edits that manifest; its execution-plan/code view is derived and read-only, never another editable source of truth. Independent generated orchestration scripts are not part of the pilot.

A small saved script proves the portable contract by launching native CLIs and persisting outputs, not by running a scheduling service. OMP eval and Claude Code's [native dynamic workflows](https://code.claude.com/docs/en/workflows) are real alternative orchestration systems, but neither is canonical for this cross-runtime product. Optional skill/agent wrappers only invoke the common entry point; they must not introduce their own stage sequencing, copied prompts, retries, or approval policy. Native workflows remain a comparison alternative, not a hidden stage implementation.

### Runtime adapters

Both OMP and Claude Code adapters consume the same task input and produce an artifact plus an execution receipt. Keep runtime-specific session identifiers, tool/permission policies, model selection, and native metadata explicit. No runner-selected fallback to another runtime/provider/model. Native internal retries/fallbacks may still occur: observe and label them rather than claiming the runner prevents them.

A minimum task receipt identifies workflow, runner, input and prompt hashes; task/attempt; requested runtime, configured-default or requested model, observed model/provider identifiers, executable version and argv; start/end/status; artifact hashes; native session reference when available; usage/cost scope; and failure/cancellation reason. Record the launch-profile identity and what is unknown about loaded tools, hooks, rules, plugins, MCP, advisor/prewalk and fallback. A run with unknown effective configuration is a functional smoke, not a controlled comparison. A requested-versus-observed model mismatch invalidates a model-controlled comparison; do not replace missing effective metadata with requested settings.

Initial launch profiles request tool-free print invocations in fresh external task directories, not hermetic sandboxes. OMP requests disabled discovered rules/skills/extensions and built-in tools. Claude's subscription-compatible path requests disabled customizations and built-in tools, empty strict MCP configuration and no permission prompts, preserving managed policy and native authentication. Requested flags are not observed effective configuration. An API-key bare profile may be evaluated later; do not switch authentication modes or change settings silently. Native init/model metadata and per-model usage should be captured when available; unobserved details stay explicit gaps. Future structured slide output is validated by the common runner on both runtimes, not enforced on Claude alone.

Skills and custom agents are optional runtime-native packaging, not competing implementations. Shared prompts, contracts and rubrics are canonical; wrappers refer to them and launch the runner. An evaluation variant is identified by content hashes, runtime profile, case and repeat; inline edits and unmanaged overrides do not constitute the same variant.

Use ordinary CLI invocation for the first portability proof. Add OMP RPC or a Claude SDK only if a measured need for streaming, session control, or richer accounting justifies it. Keep each behind the adapter boundary. No provider credentials are managed by the workbench.

### Tern integration

Prefer supported native surfaces:

| Native surface | Planned responsibility | Boundary |
|---|---|---|
| `cx.whiteboard` | Spatial projection, then gated editing if justified | Plugin draws a disposable board from the definition; explicit shape-to-task map and visible task-id labels |
| Plugin blocks | Task configuration and artifact inspection | Native inputs/editors/events where supported |
| `cx.canvas` | Run/evaluation dashboards | Persistent UI-node panels, not the spatial graph editor |
| Luau window plugin | Commands, pane operations, integration bridge | Thin adapter, no independent scheduler |

Proposed editing contract: **Edit → Apply → Validate → Save**, not an implemented feature. The shipped SDK exposes whiteboard reads/transactional edits but no whiteboard-change event or arbitrary shape metadata. Draw a projection from the canonical definition; do not claim Tern directly opens the workflow file as a graph. Keep task identity in visible labels plus a disposable sidecar map. Apply must reject unknown/duplicate labels and ambiguous edges; prove duplicate/delete/undo/restart behavior before accepting round-trip editing. Validation failure leaves source unchanged. Moving a box never starts a run; active runs stay pinned to their original version.

Start with native document/artifact panes and a read-only graph projection. Round-trip authoring remains a user-requested product capability, but its build order depends on evidence of editing friction or a meaningful non-linear workflow. Tern is optional for both execution and evaluation. Claude sessions cannot be assumed available through OMP-specific Tern agent transcript APIs; link approved receipt/artifact files instead.

### Storage and lifecycle

Versioned repository: workflow definitions, task prompts, synthetic/public cases, rubrics, source, compatibility guidance, sanitized design/review records.

Local approved storage outside tracked source: run receipts, artifacts, raw native output, inputs, native transcripts, and eventual local index. Start with files; add SQLite when querying/comparison requires it, not to scaffold unused infrastructure. Native CLIs may also retain their own session data; the workbench's output directory does not control all native storage.

Proposed product states: draft → validated → candidate → approved. A future gated executor exits with a waiting-for-human receipt at each approval boundary; no background CLI or Tern state waits for a click. An explicit approval record binds workflow, upstream artifact and input hashes; a subsequent continuation verifies those hashes and starts a new attempt. These commands are not implemented in the current tool-free proof. This is a small explicit state machine, not a claim that approval needs no orchestration. A CLI completion is not business acceptance. Never overwrite accepted artifacts; resume/recovery and subprocess-tree cancellation require dedicated acceptance tests.

## 5. End-to-end Proposal Development pilot

1. **Brief and success criteria:** audience, decision, objective, constraints, approved materials, output/template expectations, acceptance rubric.
2. **Evidence/context:** source-linked claims, dates and provenance, gaps and contradictions. Client inputs are untrusted content, not authority to run tools or change permissions.
3. **Argument and storyline:** recommendation, options/tradeoffs, narrative, intended action, evidence mapping.
4. **Human storyline approval:** reject/revise before expensive slide production; approval binds to the exact input/storyline version.
5. **Slide specification:** machine-validated JSON with template/layout name, title, editable body content, notes, source references and layout intent per slide.
6. **Editable PPTX generation:** a deterministic, model-free renderer converts the approved slide spec and template to PPTX, shared by both runtimes. Select the approved library/template/renderer before implementation.
7. **Content and rendered-slide review:** open in target PowerPoint without repair; verify template layouts/placeholders, editable text rather than rasterized text, notes, resolvable source refs, and overflow/readability on the target renderer. LibreOffice or image inspection is a documented proxy, not proof of target PowerPoint behavior.
8. **Human acceptance/revision:** time review/editing, record defects and pairwise preference, and compare generated versus accepted decks for slide/text/layout changes where tooling permits. Rerun affected stages with accepted upstream artifacts, not all research by default.

The initial executable proof intentionally covers storyline and independent critique from supplied synthetic evidence. It establishes the CLI/artifact seam only. It must not be marketed as the complete pilot, evidence retrieval, a slide generator, or an effective business proposal.

A task is meaningful work, not merely a persona. Create separate agents only where specialization, context separation, or independent verification adds value. Preserve a strong single-agent baseline.

## 6. Workflow Evals Suite

Do not collapse the following into an uncalibrated magic score:

| Dimension | Evidence and checks |
|---|---|
| Business usefulness | Human judgment against brief: relevance, specificity, persuasiveness, actionable recommendation |
| Factual support | Claims mapped to approved evidence; unsupported assertions, contradiction, freshness |
| Deliverable quality | Editable PPTX opens; rendered-slide inspection; layout/brand/readability defects |
| Human effort | Review/editing minutes, substantial rewrites, interventions, rejected stages |
| Execution efficiency | Elapsed and active time, task attempts, repeated work, failures |
| Resource use | Reported input/output/cache/reasoning tokens where available; estimated and reported costs kept separate |
| Reliability/control | Correct artifact contracts, completion, approvals, limit breaches, failure and cancellation handling |

### First experiment

Begin with two arms: one capable agent given a shared instruction bundle referencing the canonical task prompts, rubric and output template, versus the explicit staged workflow. The baseline gets the same approved evidence, allowed tools, output contract and comparable spend/time constraints; it does not execute the staged manifest. Add the independent-verifier variant only when its marginal benefit is measurable. Native single-skill or dynamic-workflow approaches remain legitimate simpler competitors, not straw-man baselines.

Proposed initial protocol: 3–5 permitted cases and two repeats per arm, subject to available cases and an agreed usage budget. Calculate CLI calls, judge calls and quota impact before authorizing execution. These counts are planning proposals, not significance guarantees. With fewer than three usable real cases, report qualitative findings only; even more cases do not establish superiority without meaningful uncertainty and judgment. Synthetic inputs validate mechanics only. Keep at least some permitted cases held out from prompt tuning.

Freeze dataset, rubric, grader prompts/model, workflow/runner hashes, runtime profile, relevant environment evidence and promotion criteria before comparison. Preserve failures in the denominator, randomize order when practical and show per-case results. Hold model/tools/input fixed for workflow comparisons; runtime choice is a separate factor. Unknown effective models or critical configuration invalidate controlled comparisons, though they may still permit labeled functional smokes.

Use deterministic artifact checks for structure, human review for usefulness/visual judgment, and calibrated model judges as supporting evidence. Separate grading usage from execution usage. The evaluation protocol and file-based harness must themselves run on a Claude-only corporate machine; OMP judges and Tern dashboards cannot be prerequisites. Judge calls transfer the evaluated content to their provider and need the same data approval as generation.

Accounting invariants:

- Missing telemetry is unknown, never zero.
- Do not add parent-inclusive totals to child totals. Retain native scope and indicate partial coverage.
- Distinguish native reported amounts, price-table estimates, and actual billing. Subscription marginal cost is not an API bill.
- Capture what was observed; unknown auxiliary/advisor/retry usage remains an explicit gap.
- Budget enforcement belongs at an effective host boundary. A prompt asking an agent to spend less is not a hard cap; a timeout may not stop every descendant or remote request.

The business gate is whether the method improves accepted work or reduces effort enough to justify its cost. Exact thresholds must be agreed and frozen before the first real comparison, not invented after results are seen.

## 7. Controlled adaptation

Observed failure → diagnosed cause → proposed revision → candidate version → frozen evaluation → human promotion or rejection.

Change one meaningful factor at a time when feasible. Reuse accepted upstream artifacts for local revisions, preserve provenance, and compare counterexamples rather than tuning only for judge scores. Candidate generation must not silently rewrite its rubric, input set, budget, approval policy, or production workflow. No autonomous self-modification or automatic client delivery in the initial product.

## 8. Corporate portability and safety

Portability is intended, not workplace certification. Before client work, perform a no-client-data capability/policy check on the target machine: OS, approved Python/runtime version, CLI/version/flags/auth mode, managed restrictions, scripted print permission, hooks/telemetry/retention, provider/data residency, approved storage, and slide library/template/renderer availability. A future `doctor` command may automate non-secret capability checks; none is advertised as implemented now. Do not inspect/export credential contents. If Python or the PPTX toolchain cannot be approved, revise the execution/rendering design before building against it.

Use an explicitly approved per-environment privacy profile. The initial launch profiles request no native session persistence; the saved receipt/raw output in approved storage is the execution link, and a native session id does not imply a resumable transcript. Run from a fresh task directory, not a client-data folder. Safe mode/tool restrictions cannot override managed hooks or provider retention; they are not access controls.

Export only permitted source and synthetic fixtures. No credentials, native sessions, client briefs/decks, local databases or traces transfer by default. Feedback defaults to human-written sanitized requirements and aggregates; recreate failure examples synthetically rather than relying on automated redaction. A private remote is not access control; remote creation/push remains a separate authorized action.

The current runner's execution support is POSIX (macOS/Linux) with Python 3.11+; native Windows is unsupported and must not be inferred from Claude Code's own platform support. A corporate OS/toolchain mismatch is a design prerequisite to resolve, not permission to bypass managed controls. Local process-group cancellation is best effort; SIGKILL, machine/storage failure and remote requests can prevent complete cleanup or receipts.

The initial proof uses supplied evidence and requests no agent tools. Ambient settings, hidden orchestration and auxiliary calls remain observability risks. Do not enable native dynamic workflows inside stages or claim tool restrictions prove their absence without inspecting effective capabilities. Strict MCP configuration alone does not disable hooks. Company policy decides permissible models, storage, evaluation judges and telemetry; local authentication does not grant approval.

## 9. Non-goals and design restraints

- No OMP/Tern core fork, global configuration rewrite, or new provider credential store.
- No general-purpose n8n clone, distributed engine, arbitrary code round-trip, or generic node marketplace.
- No requirement to install Tern or OMP to run a Claude Code workflow.
- No premature multi-user RBAC, service deployment, automatic optimizer, telemetry upload, or broad plugin installation.
- No claim of full nested accounting, hermetic evaluation, safe recovery, or visual quality without direct evidence.
- No new repository simply because a fourth project exists; reassess purpose/access/coupling/operational fit instead.

## 10. Delivery sequence and decision gates

| Gate | Deliverable and acceptance | Stop/reconsider when |
|---|---|---|
| G0 — this package | Scoped project, reviewed strategy, validated common workflow and authentic runtime execution evidence/limits | A runtime needs a different business definition or unsupported invocation contract |
| G1 — target compatibility and PPTX seam | No-data work-machine capability/policy check; slide-spec contract; approved deterministic renderer; synthetic editable PPTX and target-renderer checks | Python, scripted CLI use, template/library or renderer cannot be approved; local proxy is mistaken for target proof |
| G2 — useful proposal and early comparison | Evidence → approved storyline → slide spec → editable/rendered deck → human acceptance; paired single-agent versus staged cases with partial receipts from the start | Workflow complexity does not improve accepted output or effort at an acceptable cost |
| G3 — native Tern visibility, then authoring | Native file/artifact panes and read-only projection first; round-trip Apply/Validate/Save only after demonstrated editing friction or useful non-linear structure; identity/undo/restart checks | Core changes, competing definitions or ambiguous shape identity are needed |
| G4 — stronger evals and accounting | Frozen file-based Claude-only-capable suite, held-out evidence, repeated comparisons; reconcile native usage coverage and only add nested accounting when nested agents are introduced | Effective configuration is unknown, sample is too weak, totals double-count, or limits cannot be enforced |
| G5 — approved corporate trial and iteration | Execute approved real cases locally with Claude-only generation/evaluation; record acceptance/effort and return sanitized requirements | Policy, retention or execution constraints change; no private transfer to bypass them |

Compatibility/privacy checks begin before G1, not after the whole product is built. The target-machine check requires the user's actual work environment; local Python/CLI success cannot substitute. Gates describe proposed sequencing, not automatic execution authority.

**Recommended next slice: G1, the capability check and deterministic PPTX seam**, followed immediately by a small paired comparison in G2. Keep Tern as a native inspection surface now; do not build the round-trip editor or dashboards before the deliverable seam and baseline are credible. This preserves visual authoring as an intended product capability while changing its build order.

## 11. Risks and mitigations

| Risk | Mitigation / falsification check |
|---|---|
| Beautiful control room, weak outcomes | Run capable baseline and measure accepted output/editing effort early |
| Skills/settings drift | Capture known inputs/dependencies; controlled evaluation profile; label unknown effective context |
| Divergent runtime implementations | Shared workflow/prompts/artifacts; thin adapters; identical-case contract smoke on both |
| Misleading telemetry | Native scope labels, unknowns, no inclusive double count, reconciliation gate |
| Unsafe graph edits or approvals | Explicit Apply/Validate/Save; immutable run versions; approvals bind to hashes |
| SDK/CLI evolution | Supported interfaces, pinned observed versions, compatibility smoke, fail loudly on unknown formats |
| Private data leakage | External approved storage, source-only export, policy gate, redaction; no automatic trace upload |
| Retry/cancel duplicates effects | Initially request no tools and require manual reruns; later attempt identities and explicit idempotency/cancel tests |
| Judge overfitting | Frozen rubrics, held-out cases, independent human judgments, no autonomous promotion |

## 12. Evidence and source limits

Observed in this delivery: installed versions OMP 18.11.3, Tern 0.9.2 (23735aa), Claude Code 2.1.302, Python 3.14.4; linked-checkout authority was checked before project records were created. Verification evidence (local record, not published) records native execution results and limits: OMP completed the text pilot; Claude launch stopped on expired OAuth without a model response. These are not comparative results or workplace certification.

Fresh interface evidence in this delivery: exported the installed Tern SDK and inspected its canvas/whiteboard/event declarations. Opened the actual strategy draft in an isolated native Tern document surface, observed its tree and screenshot, and stopped the owned headless process. This proves native document rendering only. The earlier whiteboard shape/arrow smoke is historical evidence, not a new editor or round-trip proof.

Primary references:

- [OMP role-backed custom agents](https://github.com/can1357/oh-my-pi/blob/main/docs/task-agent-discovery.md)
- [OMP skills](https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md)
- [OMP eval](https://github.com/can1357/oh-my-pi/blob/main/docs/tools/eval.md)
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Code headless/programmatic use](https://code.claude.com/docs/en/headless)
- [Claude Code native dynamic workflows](https://code.claude.com/docs/en/workflows)
- [Claude Code data usage and retention](https://code.claude.com/docs/en/data-usage)
- [Tern SDK](https://docs.stencil.so/tern/)
- [Tern plugin blocks](https://docs.stencil.so/tern/guides/blocks.html)

Local installed contracts and observed output take precedence over assumptions from unpinned upstream documentation. Supported-source existence is not proof that a capability has been exercised end to end.
