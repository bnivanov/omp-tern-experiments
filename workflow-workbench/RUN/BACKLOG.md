# Backlog

Ids are stable and never reused within this authoritative project tracker. Main owns this file. Agent proposals are not approved implementation. This project has no adopted board; do not duplicate this queue in root records or session todos.

## Open

Sequencing (2026-10-19): rows dated 2026-10-17 are parked behind the evals roadmap in `docs/WORKFLOW-EVALS-STRATEGY.md` §14. They are not cancelled. The corporate laptop has OMP + Tern with Claude-only models (user-provided fact, 2026-10-19). `work20261017evalsuite` is fallback only (Claude Code if OMP or Tern blocks), not the corporate path. `work20261017baseline` is superseded by `work20261019phase2`. `work20261017profiles` is superseded by `work20261019phase0`. Do not run a superseded row in parallel with its replacement.

| Id | Item | Why | Source | Added |
|---|---|---|---|---|
| work20261017pptxseam | [PROPOSED] Target capability check and deterministic slide-spec → PPTX seam | Parked until Phase 2 has an L2 result on non-synthetic cases. Not a Phase 1 workstream | Strategy review findings 4–5; PRODUCT-STRATEGY.md G1; user chose Proposal Development | 2026-10-17 |
| work20261017approvals | [PROPOSED] Hash-bound storyline approval and explicit continuation | Full proposal execution must stop before slide production until the exact storyline is approved; no daemon or silent resume. Not part of Phase 0–3 autonomous trials | Strategy review finding 9; PRODUCT-STRATEGY.md G2 | 2026-10-17 |
| work20261017ternview | [PROPOSED] Native Tern definition/receipt projection, then validated round-trip editing | Parked behind P1. Phase 2 may use Tern `open` and Markdown only | Strategy review finding 8; PRODUCT-STRATEGY.md G3; user wants OMP and Tern | 2026-10-17 |
| work20261017evalsuite | [PROPOSED] Claude Code fallback for a file-based suite, only if OMP or Tern blocks | Not the corporate path. Corporate comparisons run on OMP + Tern with the Claude-only role profile | Strategy review findings 6,7,10; PRODUCT-STRATEGY.md G4–G5; user requires a Claude Code fallback | 2026-10-17 |
| work20261017claudesmoke | [PREREQUISITE] Complete the saved synthetic workflow with approved, independently restored Claude authentication | Native invocation failed on expired OAuth; successful Claude generation remains unverified. Do not change auth or bypass workplace controls. This is the frozen proof, not Phase 0 | Native Claude evidence; integrated review; README execution command | 2026-10-17 |
| work20261019phase0 | [PROPOSED] Phase 0 instrument: lab skeleton, case card, `variant.md`, small `omp -p` wrapper, `--session-dir`, explicit `--approval-mode` and `--tools`, trial manifest with role map, ledger template; baseline vs one skill variant on two synthetic cases outside any repo | Tests P2, C1, C2. Skill arm must record skill loaded. Canary markers in the global profile, an ancestor `AGENTS.md`, and `.omp/rules` | WORKFLOW-EVALS-STRATEGY.md §4, §10, §11, §14; RISKIEST-ASSUMPTIONS.md | 2026-10-19 |
| work20261019phase1 | [PROPOSED] Phase 1 calibrate, one domain only: text-only proposal storylines, 12 dev + 8 holdout split by cluster, ≤ 5 criteria, labels at `labels/<criterion>@<rubric>.jsonl`. A/A on that suite. No required mini-suite | Tests K1, S1, E1, M1, M2. MDE from the §7 table or a dev pilot, not from A/A | WORKFLOW-EVALS-STRATEGY.md §6–§8, §14 | 2026-10-19 |
| work20261019phase2 | [PROPOSED] Phase 2 first pre-registered comparison on the same domain: strong single-agent baseline vs skill variant, dev then one holdout look | Tests V1. An L2 on non-synthetic cases gates PPTX work. Synthetic-only results do not | WORKFLOW-EVALS-STRATEGY.md §7, §14 | 2026-10-19 |
| work20261019phase3to5 | [PROPOSED] Phases 3–5: learning-loop cycles and one bundled push-harder sweep; per-output real-work validation, sampled human effort, update canaries and anchor re-grade; software-factory suite and Tern views only if P1 says so | Tests V2, V3, G1, M3, M4, D1, D2, D3, G2, G3, P1. G2 is Phase 4. G3 and P1 are Phase 5 | WORKFLOW-EVALS-STRATEGY.md §14 | 2026-10-19 |

## Superseded

| Id | Item | Superseded by | Added |
|---|---|---|---|
| work20261017baseline | Compare capable single-agent instruction bundle with staged proposal workflow | work20261019phase2. Same comparison; running both would double the protocol | 2026-10-17 |
| work20261017profiles | Controlled runtime profiles and effective-configuration evidence | work20261019phase0. Profile isolation, role map and manifest are the Phase 0 instrument | 2026-10-17 |

## Done

| Id | Item | Done | Evidence |
|---|---|---|---|
