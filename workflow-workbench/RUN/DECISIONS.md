# Decisions

Append only. User decisions are distinguished from implementation choices and proposals. This project owns these records; workspace records are not a second project tracker.

## Confirmed intent

- User chose Proposal Development as the proving workflow, with future advisory, product discovery/development, and strategy/operations workflows.
- User wants visual creation/adaptation, linked execution sessions, real usage/cost visibility, quality improvement, and a Workflow Evals Suite—not a replacement agent harness.
- User wants development here and eventual transfer to a corporate laptop; corporate data/provider/tool policy still requires local approval. No remote, push, or new repository is authorized in this run.
- User authorized scaffolding, strategy capture, reviewer challenge, and a recommendation on how to proceed.
- User: "there is a chance that we might have to use claude code at work so lets make the workflows executable by claude code."

## Implementation decisions for this delivery

- Project root: `projects/workflow-workbench/`, within the existing umbrella repository. Preserve existing setup and workspace history.
- Authoritative delivery state: this project's `RUN/PLAN.md` and only useful supporting records. No project board is adopted merely to populate Tern.
- Provider-neutral saved workflow/task definitions, prompts, artifact contracts, and evaluation rubrics. Runtime-specific skills/agents are optional wrappers; OMP eval globals are not the portable execution API.
- Native Tern is the preferred future authoring/inspection surface, not a prerequisite for executing a saved workflow. Explicit Apply/Validate/Save is the conservative graph-editing contract.
- The current implementation scope is a small executable portability proof and reviewed product strategy. Full graph authoring, editable PPTX creation/rendering, experiment management, and recovery are separately gated product slices.
- No automatic publication, delivery, promotion, self-modification, unlimited revision loops, or telemetry upload. Unknown usage is unknown, not zero. Subscription estimates are not billed cost.

## Open decision boundaries

- Select approved slide-generation/rendering tools and corporate storage/providers before real client work.
- Confirm what native runtime metadata can be attributed without double-counting nested/auxiliary calls.
- Only consider a sibling repository when access, ownership, release/tooling coupling, or distribution needs justify it; project count is not the criterion.

## Review revisions

- Adversarial reviewer verdict: revise, then proceed. Main accepted the consequential design corrections; see `docs/reviews/strategy-adversarial-review.md` for finding-level disposition.
- Clarification of the earlier Tern entry: Apply/Validate/Save and the native surface mapping are proposed product contracts, not implemented capabilities. Native document rendering alone does not establish a graph editor.
- [SUPERSEDED 2026-10-19 for new lab work] Canonical implementation was one provider-neutral manifest plus referenced prompts, interpreted by one versioned runner. OMP eval and Claude dynamic workflows were alternatives, not independent orchestration inside a stage. That remains true of the portability-proof runner, which is not extended. New experiments use skill and agent variants run via `omp -p`. See the revision note at the end of this file.
- Functional smoke evidence is not a controlled evaluation. Record observed models/configuration and gaps; unknown critical context or a requested/observed model mismatch blocks comparative claims.
- [PROPOSED] Change delivery order: target capability/privacy check and deterministic PPTX seam, then a small capable-single-agent versus staged comparison, before round-trip Tern authoring. The user's visual-authoring goal remains; sequencing is the review's recommendation, not a new user decision.
- [PROPOSED] Full proposal approval exits with a hash-bound receipt and requires explicit continuation; the current proof has no approval/recovery commands.
- Integrated execution review found four P2 defects and two P3 corrections: strict OMP event/turn validation, TERM/HUP cancellation, declared POSIX support, complete failure receipts, stable source hash, and requested-versus-effective control wording. These are in-scope runner corrections, not approval for a general engine.
- Execution support for this proof is POSIX (macOS/Linux), Python 3.11+. Native Windows is unsupported. The corporate capability gate must resolve OS/toolchain compatibility before any workplace adoption.
- Local Claude execution encountered expired OAuth. Authentication/configuration remains untouched; successful Claude generation is an explicit missing prerequisite, not an accepted portability result. No automatic retry or substitute runtime is authorized.
- Targeted recheck corrections preserve inherited ignored signals, retain cancellation diagnostics through terminal persistence, and record only unexpected exception type/errno rather than resolved executable paths. `command_run` owns restoration of SIGINT/TERM/HUP on exit.
- The final process launch uses anonymous capture files in the external task directory and bounded public `Popen.wait`, not private pipe buffers. Signals during process creation are remembered until the process handle is owned. This is local cleanup, not a remote-cancellation or durable-recovery guarantee.
- Final targeted reviewer verdict was correct with one nonblocking signal-deferral race. Main reproduced and corrected that race with a failing-before/passing-after real-child regression. Initial setup interruption, background/escaped descendants, auxiliary accounting and remote cancellation remain declared limits, not claims of a production isolation/recovery system.

## Run run20261019T115253Z420e34 — workflow evals strategy

- User: "Before we evern deep-dive to business development and powerpoing production i want to take a step back and really scaffold our approach here." Proposal/PPTX product work is parked behind the evaluation approach.
- User: "Lets make this OMP + Tern centric for now, we will shift to Claude Code specific if this becomes a problem". This supersedes the earlier "executable by Claude Code" emphasis as a design driver; Claude Code is a fallback runtime.
- User goal: "real and credible Workflow Evals. Not just model evals or harness evals, but scientifically scaffolded workflow evals to push as hard as possible what the models can output but have ways to measure, learn and improve over time", extensible to a software factory and end-to-end video production.
- [PROPOSED] `docs/WORKFLOW-EVALS-STRATEGY.md` is the working specification for evaluation and runtime direction, not a confirmed authority until this bullet and the four below are accepted. `docs/PRODUCT-STRATEGY.md` is parked with a banner listing the superseded sections (§1/§4 portable core, §6, §7, §8 Claude-Code-without-OMP path, §10 gates); its body is unchanged.
- [PROPOSED] Freeze `scripts/run_workflow.py`, its tests and the saved workflow: keep, do not extend, do not delete without authorization. Rationale: it disables the OMP features under test (tools, skills, rules) and strictly parses OMP's event stream, which conflicts with the durability requirement.
- [PROPOSED] Variants are defined as skills, agents and model-role choices run via `omp -p`; files are the system of record. Grader files and the ledger are portable. Judge calibration is not runtime-independent: switching runtime re-calibrates judges.
- [PROPOSED] Proving order: measurement before value (P2, C1, C2, and K1 → S1, E1, M1, M2 → V1). Phase 1 is one domain: text-only proposal storylines. The earlier inference that the first calibration suite should be a cheap-ground-truth mini-suite is withdrawn.
- [PROPOSED] No graph editor, optimiser or vendor eval platform until the gating assumptions in `docs/RISKIEST-ASSUMPTIONS.md` pass.

## Revision 2026-10-19 — evals package review

- User-provided fact, 2026-10-19: the corporate laptop has OMP and Tern (same versions as the help check, OMP 18.12.2 and Tern 0.9.4) with Claude models only. Role map, by family and seat, not by invented provider model id: default = Claude Sonnet, high thinking, 200k context; task and scout subagents = Claude Haiku, context cap 100k; slow seat = Claude Opus 5.5, high thinking, 200k. Claude Code is fallback only. No GPT or other-provider dependency. Home-lab results on any other role map are not evidence for this profile.
- This revision applied the evals-strategy review to the working specification and the assumption register (20 assumptions: added K1, M4, D3).
