# Workflow Workbench

A personal lab for designing, running, evaluating and improving agentic workflows with credible, repeatable workflow evals. OMP + Tern centric; Claude Code becomes the runtime only if OMP or Tern becomes a blocker.

**Published subset.** This folder is the shareable copy of the workbench: specification, assumption register, evidence base, research notes, decisions, proposed backlog, the frozen portability runner and its tests. The originating workspace's delivery plan, handoff, earlier review and local run evidence are not included because they reference machine-local runs. [RUN/DECISIONS.md](RUN/DECISIONS.md) records intent and choices; [RUN/BACKLOG.md](RUN/BACKLOG.md) holds proposed roadmap items.

## Read first

- [Workflow Evals Strategy](docs/WORKFLOW-EVALS-STRATEGY.md): **working specification** for what a workflow eval is, the seven-layer lab model, metrics, grading, protocol, durability, the OMP + Tern mapping, domain extension and the phased roadmap. Not a confirmed authority while the matching bullets in [RUN/DECISIONS.md](RUN/DECISIONS.md) remain [PROPOSED].
- [Riskiest assumptions](docs/RISKIEST-ASSUMPTIONS.md): 20 assumptions with tests, pass/kill criteria and proving order. Ids added in the 2026-10-19 revision: K1, M4, D3. Each experiment updates its status.
- [Evidence base](docs/EVIDENCE-BASE.md): cited research synthesis; full notes in [docs/research/](docs/research/).
- [Product strategy (parked)](docs/PRODUCT-STRATEGY.md): Proposal/PPTX pilot and the Tern editing safety contract. Its banner lists what the evals strategy supersedes (§1/§4 portable core, §6, §7, §8 Claude-Code-without-OMP path, §10 gates).

## Current direction

Prove the lab can measure before proving any workflow is better: Phase 0 instrument (`omp -p`, trial dirs outside any repo), Phase 1 calibration on one domain (text-only proposal storylines; 12 dev + 8 holdout), then the first pre-registered baseline-versus-variant comparison. Business development and PPTX production wait for an L2 result on non-synthetic cases. Nothing in Phase 0 or later is implemented yet.

The sections below document the portability runner from the first run. A freeze of that runner is still [PROPOSED] in [RUN/DECISIONS.md](RUN/DECISIONS.md). It is kept for its evidence and lessons, not extended. Its design of running OMP with tools, skills and rules disabled and strictly parsing OMP's event stream is what the evals specification avoids.

## Current scope

This delivery is project setup, reviewed strategy, and a narrow executable portability proof. The saved workflow produces a **proposal storyline and independent critique from supplied synthetic evidence**. It does not retrieve evidence, create slides/PPTX, implement a graph editor, enforce human business approval, compare experiments, or provide durable recovery.

The proposed complete product connects a versioned design to actual attempts/sessions/artifacts and comparative evaluation. Proposed Tern integration uses native whiteboard authoring with explicit Apply/Validate/Save, blocks for configuration, and canvas panels for dashboards. Tern is not required to execute a saved workflow.

## Runtime boundary

This section describes the portability proof, not the corporate eval path. The corporate laptop (user-provided fact, 2026-10-19) runs OMP + Tern with Claude models only; Claude Code is the fallback if OMP or Tern becomes a blocker. See [Data and corporate portability](#data-and-corporate-portability).

A common saved definition, task prompts, input, and output contract feed thin CLI adapters. No OMP eval globals, custom-agent discovery, or skill invocation is required for the portable path. Runtime-native agents and skills can be optional wrappers later.

Execution currently requires POSIX (macOS/Linux), Python 3.11+, and the selected authenticated CLI for a standalone source copy. Native Windows execution is unsupported; the target work-machine capability check must settle OS and toolchain approval before adoption. Inside a Git checkout, Git is also required to protect repository/worktree output boundaries. No Python packages, Node dependencies, server, database, or Tern plugin installation is required. Observed local versions are Python 3.14.4, OMP 18.11.3, Claude Code 2.1.302, and Tern 0.9.2.

`validate` and `plan` are non-model operations; `run` explicitly launches the selected CLI and can incur model usage. This proof accepts only briefs explicitly marked `fictional: true` with supplied sources and known gaps; it is not ready for client data. Do not bypass native permissions, alter global configuration, or assume workplace approval from local authentication.

## Execute a saved workflow

Run from this project directory. Validation and planning do not invoke a model or create run files:

```sh
python3 scripts/run_workflow.py validate workflows/proposal-storyline.workflow.json
python3 scripts/run_workflow.py plan workflows/proposal-storyline.workflow.json \
  --runtime claude --input examples/synthetic-brief.json
```

For an authenticated execution, choose a **new directory outside the repository**, in approved storage, and pass it as `<new-output-dir>`. It must not already exist:

```sh
python3 scripts/run_workflow.py run workflows/proposal-storyline.workflow.json \
  --runtime omp --input examples/synthetic-brief.json \
  --output-dir <new-output-dir> --timeout-seconds 180

python3 scripts/run_workflow.py run workflows/proposal-storyline.workflow.json \
  --runtime claude --input examples/synthetic-brief.json \
  --output-dir <new-output-dir> --timeout-seconds 180
```

Use a fresh output path for every attempt. A temporary directory is suitable only for this disposable synthetic example, not a corporate storage recommendation. The runner must not silently change runtimes, retry, overwrite a previous run, or reinterpret an unsupported definition.

The supported definition is deliberately small: `schema_version: 1`, a workflow `id`/`description`, and an ordered `stages` list. Each stage declares `id`, `role`, `prompt` (relative to the workflow file), and `handoffs` containing `{ "from": "<earlier-stage-id>" }`. Unknown fields, invalid references, duplicate ids, forward dependencies, and unsupported versions are rejected. This is the linear subset, not an arbitrary DAG editor.

Each stage requests a fresh native CLI session and receives the approved supplied input plus its declared earlier artifacts. The launch profiles request disabled agent tools for this text-only proof; requested flags are not proof of effective configuration. The runner does not implement retrieval, native subagent spawning, or slide-generation tools. Native roles/models are not assumed interchangeable: the role is a shared prompt contract and the selected CLI keeps its configured model.

Inspect the generated run receipt and task artifacts before accepting anything. Native usage is reported at its observed scope, missing fields remain unknown, and reported price estimates are not actual bills. Claude `usage` and `modelUsage` are not additive totals. Runtime errors, truncated/unknown completion formats, timeout, or interruption must remain non-success states.

Timeout and handled interruption stop/reap the local child process group and retain captured diagnostics where storage remains writable. SIGKILL, machine failure, escaped descendants, remote requests, and storage failure cannot be given the same guarantee. A cancelled stage must not publish an accepted artifact.

Inherited ignored signals are preserved: a run started with SIGHUP ignored (for example under `nohup`) does not cancel on hangup. Once cancellation is handled, repeat cancellation signals are ignored through terminal receipt persistence; the caller's signal settings are restored before exit.

Tool restrictions and fresh task directories are not a sandbox or hermetic evaluation environment. Claude requests `--safe-mode` to disable user customizations; managed policy still applies and effective configuration is not fully observed. The runner does not use `--bare` because that changes subscription authentication. No global configuration is rewritten.

## Data and corporate portability

Keep client briefs/decks, raw runtime output, native sessions, run artifacts, credentials, and local evaluation data outside tracked source in approved storage. Synthetic fixtures are safe examples, not evidence of business quality. The runner's output location does not control all storage/retention of native tools, hooks, or providers.

The intended corporate path is OMP + Tern under a Claude-only role profile, not Claude Code without OMP or Tern. User-provided fact, 2026-10-19: the corporate laptop has the same OMP and Tern versions as the help check recorded in the evals strategy (OMP 18.12.2, Tern 0.9.4). Default seat: Claude Sonnet, high thinking, 200k context. Task and scout subagents: Claude Haiku, 100k context cap. Slow seat: Claude Opus 5.5, high thinking, 200k. No GPT or other-provider dependency. Claude Code is fallback only. Workplace policy and approval are not verified here. A home-lab result on any other role map is not evidence for this profile; re-run the baseline there. Copy only permitted project source and synthetic fixtures; do not copy personal configuration or native session directories. Return sanitized requirements and aggregate results, not private traces by default. No remote creation, commit, or push is part of this delivery.

## Local regression checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

These deterministic completion-boundary and local subprocess-lifecycle checks use no installed agent CLI, model, credentials, or client data. They do not replace authenticated runtime smoke runs or the target-machine capability check.

## Delivery ownership

Main owns this project's shared records and integration. Independent project sessions need explicit roots and record authority; independent writing mains normally use separate checkouts. A folder, Tern tab, or copied plan is not isolation or authority. Keep one plan for evidence and bounded assignments rather than opening a second tracker.
