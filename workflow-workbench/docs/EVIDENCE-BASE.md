# Evidence base

Status: research synthesis, retrieved 2026-10-19. Full notes with quotes, numbers and per-section implications:

- [research/eval-science.md](research/eval-science.md): eval design, statistics, grading, dataset hygiene, long-horizon practice, tooling
- [research/workflow-frontier.md](research/workflow-frontier.md): multi-agent evidence, software factories, optimisers, graphs vs loops, domain exemplars

This file keeps only the findings that shaped [WORKFLOW-EVALS-STRATEGY.md](WORKFLOW-EVALS-STRATEGY.md) and [RISKIEST-ASSUMPTIONS.md](RISKIEST-ASSUMPTIONS.md). Engineering blogs and essays are evidence of practice, not controlled experiments; the table says which is which.

## Findings that shaped the design

| Area | Source | Finding | So for us |
|---|---|---|---|
| Eval process | [Husain, LLM-as-judge guide](https://hamel.dev/blog/posts/llm-judge/index.html) (practitioner) | Open-code real traces, group into a failure taxonomy, binary pass/fail with critiques; generic 1–5 quality scales mislead | Rule 1 and the M1 test; the taxonomy is the first grader list |
| Eval process | [Shankar et al., EvalGen](https://arxiv.org/abs/2404.12272) (paper) | Criteria drift: graders need criteria to grade, but grading changes the criteria | Version rubrics; editing after scoring invalidates a comparison |
| Agent evals | [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (engineering) | Task/trial/grader/transcript/outcome vocabulary; capability vs regression suites; 20–50 real tasks to start; grade outcomes; 0% over many trials usually means a broken task; isolate trials | Vocabulary, suites, case audit, trial isolation |
| Agent evals | [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (engineering) | Workflows (predefined paths) vs agents (model-directed); add complexity only when it demonstrably improves outcomes | Strong-baseline rule; loops for generation, graphs for plumbing |
| Multi-agent | [Anthropic, multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (engineering) | Lead plus parallel subagents beat a single agent by 90.2% on an internal breadth-heavy eval. Token usage alone explained 80% of BrowseComp variance; multi-agent used about 15× chat tokens. Started with about 20 queries | Cost columns are mandatory; V1 and V2 tests; small early suites are acceptable |
| Multi-agent | [Cognition, Don't build multi-agents](https://cognition.ai/blog/dont-build-multi-agents) and [follow-up](https://cognition.ai/blog/multi-agents-working) (engineering) | Parallel writers conflict on implicit decisions; what works is one writer plus clean-context review or capability routing | Default variants keep a single writer per deliverable; reviewers are read-only |
| Multi-agent | [Cemri et al., MAST](https://arxiv.org/abs/2503.13657) (paper) | Failures split across system design, inter-agent misalignment and task verification. Frontier note wording: a verifier is not sufficient (often checked compilation and comments, not behavior). The phrase "a verifier alone is not enough" is not in the notes | Starter taxonomy labels only. Do not treat verification as optional |
| Cost | [Kapoor et al., AI Agents That Matter](https://arxiv.org/abs/2407.01502) (paper) | Accuracy-only leaderboards hide cost; many agent benchmarks lack holdouts | Quality–cost frontier reporting; sealed holdout |
| Statistics | [Miller, Adding error bars to evals](https://arxiv.org/abs/2411.00640) (paper) | CLT standard errors, clustered SEs (naive SEs can be about 3× too small), paired differences, power formula with ω²; resampling cannot remove between-question variance; do not lower temperature to shrink bars | Paired cluster-level analysis at small G; MDE from an assumed ω² or a dev pilot, not from A/A; temperature warning is Miller's, not τ-bench's or Chen's |
| Statistics | [Yao et al., τ-bench](https://arxiv.org/abs/2406.12045) (paper) | pass^k measures reliability across repeated trials and falls with k | Reliability metric for re-run workflows |
| Statistics | [Chen et al., Codex/HumanEval](https://arxiv.org/abs/2107.03374) (paper) | pass@k measures "at least one success" and rises with k | Only when a picker exists |
| Statistics | [Dror et al., significance testing in NLP](https://aclanthology.org/P18-1128/) (paper) | Significance testing is often missing or misapplied | Pre-registration; uncorrected slices are exploratory |
| Judges | [Zheng et al., Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) (paper) | Strong judges reach over 80% agreement with humans but show position, verbosity and self-enhancement bias | Swap order, control length, calibrate |
| Judges | [Panickssery et al., self-preference](https://arxiv.org/abs/2404.13076) (paper) | Models recognise and favour their own outputs | Judge from a different family where possible |
| Judges | [OpenAI, evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) (docs) | Judges discriminate better than they generate; prefer pairwise, classification or criteria scoring; calibrate against humans | One criterion per call; TPR/TNR reporting |
| Hygiene | [OpenAI, SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) (engineering) | 68.3% of sampled original items removed as underspecified or unfairly tested; hidden fail-to-pass and pass-to-pass tests | Audit cases with a reference solution; hidden checks |
| Hygiene | [OpenAI, why SWE-bench Verified was retired](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) (engineering) | Remaining flaws plus contamination ended its usefulness; recommends privately authored tasks | Private cases for any repeated claim |
| Hygiene | [Zhang et al., GSM1k](https://arxiv.org/abs/2405.00332) (paper) | Fresh mirror sets showed accuracy drops up to 8% for some model families | Public benchmark scores are not evidence about our workflows |
| Optimisation | [Gao et al., reward model overoptimisation](https://arxiv.org/abs/2210.10760) (paper) | Optimising a proxy eventually hurts the true objective | Optimisers only against a frozen split, with a human audit set |
| Optimisation | [GEPA](https://arxiv.org/abs/2507.19457), [DSPy](https://arxiv.org/abs/2310.03714), [AFlow](https://arxiv.org/abs/2410.10762), [ADAS](https://arxiv.org/abs/2408.08435) (papers) | All climb a supplied metric; GEPA reflects on traces and is sample-efficient | Phase 5 option; keep transcripts so trace-reflective optimisers stay possible |
| Long horizon | [METR, time horizons](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) (research) | Success is predicted by the time a skilled human needs; report the 50% horizon | Difficulty axis by human time; the forecast itself is not used |
| Durability | [Sutton, The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) (essay); [Browser Use, bitter lesson of agent frameworks](https://browser-use.com/posts/bitter-lesson-agent-frameworks) (essay) | General methods outrun hand-encoded structure. No study measures the decay rate of hard-coded workflows | Ablation and deletion policy; measure scaffold lift per model generation (D2) |
| Software factory | [StrongDM, software factory](https://factory.strongdm.ai/) and [Willison's write-up](https://simonwillison.net/2026/Feb/7/software-factory/) (field report) | In-repo tests were reward-hacked; scenarios stored outside the codebase act as holdouts; "satisfaction" is a fraction of trajectories; digital twins give volume. No published satisfaction numbers | Software suites keep acceptance scenarios outside the agent's workspace |
| Software factory | [Factory, agent effectiveness](https://docs.factory.ai/agent-effectiveness/overview) (product docs) | Measures throughput, spend and attribution, not correctness | Cycle time is a covariate, not the objective |
| Documents | [PPTC](https://arxiv.org/abs/2311.01767), [PPTAgent/PPTEval](https://arxiv.org/abs/2501.03936) (papers) | Grade the resulting file, not the API path; multi-turn sessions collapse (6% session accuracy); content, design and coherence as separate dimensions | Proposal T0 and T1 design |
| Documents | [OpenAI, GDPval](https://openai.com/index/gdpval/) (benchmark) | Blind expert pairwise grading of real deliverables; the automated grader is not yet expert-grade; tasks are one-shot | T2 design; this lab's niche is multi-step workflows with revisions |
| Video | [VBench](https://arxiv.org/abs/2311.17982), [VMAF](https://github.com/Netflix/vmaf), [ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770/en) | Per-dimension generative quality with human validation; full-reference perceptual metric; loudness measurement standard. No end-to-end video workflow benchmark found | Video T0 and T1 split; delivery specs chosen per job |
| Tooling | [Inspect AI](https://inspect.aisi.org.uk/), [promptfoo](https://www.promptfoo.dev/docs/intro/) (open source) | Inspect: rigorous harness with external-agent support; promptfoo: fast declarative assertions | Optional engines writing into lab files; neither is the system of record |
| Portability | Not a research-note finding | The Agent Skills and Claude Code skills URLs were cited here without appearing in the notes. Removed from this table | See "Not verified". The lab relies on local OMP `SKILL.md` skills, not on those URLs |

## Local platform evidence

Observed on this machine on 2026-10-19 from help output only (no model runs):

- **OMP 18.12.2** (help only, 2026-10-19): `-p`, `--profile`, `--session-dir`, `--config` (repeatable), `--tools`, `--skills`, `--no-skills`, `--no-rules`, `--no-extensions`, `--model`, `--smol`, `--slow`, `--plan`, `--thinking` (`off`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, `auto`), `--approval-mode` (`always-ask`, `write`, `yolo`), `--auto-approve`, `--prewalk` / `--no-prewalk`, `--advisor`, `--no-title`, `--max-time`, `--cwd`, `--append-system-prompt`, `--export=<session file>` (export that file to HTML and exit; help text does not say the HTML includes subagents). Subcommands: `anonymize`, `stats` (`--json`, `--summary`, `--port`, `--host` only; no session or profile filter), `render --plain`, `agents unpack --dir --json`, `bench`, `if-bench`.
- **Tern 0.9.4:** `open`, `new`, `run`, `capture`, `events`, `plugin`. Presence is not permission to run or score trials via Tern.

Earlier observations (OMP 18.11.3, Tern 0.9.2) are in the originating workspace's local verification record (not published).

## Not verified, not relied on

- Landis & Koch κ interpretation bands. Not used. M1 does not drop a criterion on a κ cutoff; it reports κ beside positive and negative agreement (or Gwet's AC1).
- The 0.90 TPR/TNR target from aievals course material is guidance, not a peer-reviewed threshold. M2's working bar is point TPR and TNR ≥ 0.8 and a Wilson 95% lower bound ≥ 0.6, per arm, on the untouched test split.
- The publication date of OpenAI's SWE-bench Verified retirement post.
- Harbor (container trial runner) beyond Anthropic's mention.
- METR's current numerical horizons. Only the method is used.
- Caption accuracy thresholds and broadcast delivery specs. They are chosen per job.
- Netflix's VMAF overview post (returned 403).
- Whether graph-based workflows survive model upgrades better or worse than loops. No longitudinal study was found.
- Agent Skills standard (`https://agentskills.io`) and Claude Code skills docs (`https://code.claude.com/docs/en/skills`). Not in the research notes. Not relied on. Local OMP skills are `SKILL.md` files, which help confirms.
- Whether `omp --export` HTML includes subagents. The flag takes an existing session file and exits. Not relied on.
- Exact provider model id strings for the corporate role profile. The 2026-10-19 fact names families and seats only (Claude Sonnet, Claude Haiku, Claude Opus 5.5).
