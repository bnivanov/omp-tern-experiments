# Workflow frontier: evidence for a workflow-evals design

Retrieved 2026-10-19. Read-only research. Every external claim below is tied to a source that was opened or whose abstract was fetched. Claims not re-read are marked UNVERIFIED. Numbers are quoted from the cited version; where versions disagree, both are reported.

Scope: scientifically credible evals of *workflows* (multi-step, multi-agent processes that emit real deliverables), not model or harness bake-offs. Execution is assumed OMP-centric with stable interfaces (Markdown skills, files, CLI print mode). This note does not recommend a vendor stack.

---

## 1. Multi-agent / orchestrated workflows vs a strong single agent

### 1.1 What the primary sources actually show

**Anthropic, research system (breadth-first, read-heavy).** In "How we built our multi-agent research system" (published 13 Jun 2025; https://www.anthropic.com/engineering/multi-agent-research-system), Anthropic describes an orchestrator-worker system: a lead agent plans, spawns parallel subagents with separate context windows, then a citation agent attributes claims. On an internal research eval, Claude Opus 4 as lead with Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by **90.2%**. They explicitly say the mechanism is token spend, not magic coordination: on BrowseComp (https://openai.com/index/browsecomp/), three factors explained **95%** of performance variance; **token usage alone explained 80%**, with tool-call count and model choice the other two. Upgrading Sonnet 3.7 to Sonnet 4 was a larger gain than doubling the Sonnet 3.7 token budget. Cost: agents used about **4×** the tokens of chat; multi-agent about **15×**. They say coding is a poor fit today because it has fewer truly parallelizable tasks and agents are "not yet great at coordinating and delegating to other agents in real time."

Eval method on that system, which transfers even if the architecture does not:

- Do not grade the path. Agents take different valid paths. Grade outcomes, plus a "reasonable process."
- Start with ~20 real queries. Large early effect sizes (they cite 30% → 80% from a prompt tweak) are visible on small sets. Do not wait for a 100-item benchmark.
- LLM-as-judge on a rubric: factual accuracy, citation accuracy, completeness, source quality, tool efficiency. A **single** judge call with 0.0–1.0 scores plus pass/fail was more consistent and better aligned with humans than multiple specialist judges. It worked best when the case had a checkable answer.
- Humans still caught what the rubric missed (SEO-farm source bias).
- For agents that mutate state, evaluate the **end state** (or discrete checkpoints), not every turn.
- Subagent artifacts should land in a filesystem / external store. Passing large outputs back through the lead agent is a "game of telephone."
- Prompt the orchestrator with effort budgets (simple: 1 agent, 3–10 tool calls; comparisons: 2–4 subagents; complex: 10+). Vague delegation caused duplicated searches.

**Cognition, coding (write-heavy), two posts that must be read together.**

Walden Yan, "Don't Build Multi-Agents" (12 Jun 2025; https://cognition.com/blog/dont-build-multi-agents): parallel subagents fail because (1) context is not shared — full traces, not summaries — and (2) actions carry implicit decisions (style, edge cases) that conflict. Default architecture: one linear agent. Subagents are acceptable for read-only questions whose traces should not pollute the writer (Claude Code's pattern as of June 2025, as Yan describes it). Parallel writers were, in his view, fragile in 2025. This is an engineering essay, not a controlled experiment.

Yan, "Multi-Agents: What's Actually Working" (22 Apr 2026; https://cognition.com/blog/multi-agents-working): the June 2025 objection still holds for **parallel-writer swarms**. What works is a narrower class: extra agents contribute intelligence; **writes stay single-threaded**.

- Clean-context reviewer: on Devin-written PRs, Devin Review caught an average of **2 bugs per PR**, of which roughly **58%** were severe (logic, missing edge cases, security). It worked *better* when the reviewer did **not** share the coder's context, because of context rot (they cite https://research.trychroma.com/context-rot — that Chroma page was not re-opened here). The coder must still filter review findings against the original spec, or the loop expands scope.
- "Smart friend": a cheaper/faster primary calling a stronger model. Cognition reports the pattern failed when the primary (SWE-1.5) was too weak to know when to escalate. It produced real gains when both models were frontier and the call was a **capability router** (who debugs, who does vision, who writes tests), not a difficulty escalator. Anthropic later shipped a similar advisor beta; Yan cites https://claude.com/blog/the-advisor-strategy (not re-read).
- Manager + children can own multi-PR scope, but models assume shared state they do not have, and cross-agent messages do not happen unless trained or heavily prompted. Unstructured swarms are "mostly a distraction." The practical shape is map-reduce-and-manage.
- Sensational multi-agent demos (Cursor's browser, Anthropic's C compiler, Karpathy's autoresearch) share, in Yan's telling, a property most real software lacks: a simple verifiable success criterion. Those three posts were not re-read; the characterization is Cognition's.

**MAST taxonomy (why multi-agent systems fail).** Cemri, Pan, Yang, et al., "Why Do Multi-Agent LLM Systems Fail?", arXiv:2503.13657.

Version caveat, do not collapse these:

- The arXiv API abstract retrieved 2026-10-19 (latest listing) says MAST-Data has **1600+** annotated traces across 7 frameworks, 14 modes in 3 categories — "(i) system design issues, (ii) inter-agent misalignment, and (iii) task verification" — with Cohen's κ = **0.88**, and an LLM judge. https://arxiv.org/abs/2503.13657
- The v2 HTML actually read (22 Apr 2025; https://arxiv.org/html/2503.13657v2) is smaller and worded differently: **200+** traces, 14 modes, categories "(i) specification issues, (ii) inter-agent misalignment, and (iii) task verification", human κ = **0.88** on the taxonomy study, LLM-judge (o1, few-shot) accuracy **0.94**, κ = **0.77** against humans. Out-of-domain κ = **0.79**. Category shares in that version: specification **41.77%**, misalignment **36.94%**, verification **21.30%**. Frequent modes included step repetition (17.14%), reasoning-action mismatch (13.98%), proceeding on wrong assumptions (11.65%), failing task requirements (10.98%). ChatDev reached only **33.33%** correctness on their ProgramDev set. A role-spec intervention gave **+9.4%**; an extra high-level verification step gave **+15.6%** absolute. The paper says these are not comparable across systems (different tasks) and that a verifier is not sufficient: verifiers often checked compilation and comments, not behavior. Simple fixes did not make the systems reliable. Failures are organizational, not only model incapacity. Efficiency failures (10× token/latency waste) were deliberately left out of the taxonomy.

NeurIPS 2025 datasets-and-benchmarks listing: https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html (abstract page not fully re-read; treat the 1600+ figure as the later abstract's claim, not as a number verified in the v2 body).

**Orchestrator + cheaper workers, the evidence split.**

- Anthropic's research result is the positive case: a stronger lead plus cheaper parallel readers beat a single strong agent on a breadth task, largely by spending more tokens in separate windows. https://www.anthropic.com/engineering/multi-agent-research-system
- The same organization, in "Building effective agents" (19 Dec 2024, page note updated later; https://www.anthropic.com/engineering/building-effective-agents), says the successful customer systems used simple composable patterns, and that you should add complexity only when it **demonstrably** improves outcomes. Routing easy traffic to a cheaper model and hard traffic to a stronger one is listed as a workflow, not as a default swarm. Their page now points at a later "managed agents" writeup; that later page was not read.
- Cognition's 2026 update says the economically attractive version (weak primary, strong friend) is still an open training problem. The version that works is closer to "two strong models, one writer." https://cognition.com/blog/multi-agents-working
- Kapoor, Stroebl, Siegel, Nadgir, Narayanan, "AI Agents That Matter", arXiv:2407.01502 (1 Jul 2024; https://arxiv.org/abs/2407.01502): accuracy-only leaderboards hide cost. SOTA agents are "needlessly complex and costly," and the community has mis-attributed accuracy gains. Jointly optimizing cost and accuracy can cut cost while holding accuracy. Many benchmarks lack holdouts, so agents overfit. MAST cites this paper for the claim that MAS gains are often minimal versus best-of-N.

**The bitter lesson, applied to workflows — argument, not a decay curve.**

Rich Sutton, "The Bitter Lesson" (13 Mar 2019; http://www.incompleteideas.net/IncIdeas/BitterLesson.html): general methods that scale with computation (search and learning) beat methods that bake in how researchers think the problem works. Human knowledge helps in the short run, then plateaus and inhibits the general method. This is a historical essay (chess, Go, speech, vision), not a measurement of agent-workflow half-life.

Two 2026 engineering essays apply it to harnesses, again without a longitudinal experiment:

- Gregor Zunic, Browser Use, "The Bitter Lesson of Agent Frameworks" (16 Jan 2026; https://browser-use.com/posts/bitter-lesson-agent-frameworks): "All the value is in the RL'd model, not your 10,000 lines of abstractions." An agent is a for-loop until an explicit done tool. Frameworks freeze assumptions about how intelligence should work. "Give the LLM as much freedom as possible, then vibe-restrict based on evals." Ops (retries, compaction, token tracking) is not the agent.
- ADAS (below, §3) states the same thesis as a research program: hand-designed agent building blocks get replaced by learned ones.

What was **not** found: a controlled study that measures how fast a hard-coded workflow's advantage decays across named model generations. The decay claim is an inference from Sutton plus practitioner essays. Treat it as a design prior, not a result.

Anthropic's own research system is a counterweight to a naive reading: they *did* hard-code effort budgets, delegation templates, and tool heuristics, and those prompts were the main lever. The durable part is not "never encode a heuristic." It is "do not encode today's model failures into control flow you cannot delete, and do not grade the path you encoded."

### So for us

- Default the proposal/PPTX workflow, and later the software factory, to **one writer with a continuous context**. Add agents only for jobs the evidence supports: parallel *read* (research breadth), clean-context *review*, and capability routing between models that are both strong enough to talk. Do not start with a role-play company (planner / coder / QA / designer) writing the same artifact. MAST's dominant failures — vague specs, wrong assumptions, step repetition, shallow verification — are exactly what a role swarm produces, and Cognition's write-conflict argument applies directly to a slide deck or a video cut where style is an implicit decision.
- Any multi-agent variant must beat a strong single agent on the **same held-out tasks**, reported with tokens, wall time, and failure-mode mix. Anthropic's 90.2% is an internal research number on a breadth task; it is not a license to multiply agents on a coherent deliverable. Kapoor's point: if you only publish accuracy, you will "win" by spending 15× tokens.
- Grade the deliverable and a few checkpoints, not the trace shape. Keep a small live set (~20 tasks) for prompt/skill edits; Anthropic's experience is that early effect sizes are large enough. Use MAST's three buckets (spec, coordination, verification) as a **diagnostic label** on failed traces, not as the score.
- Write subagent outputs to files. Do not make the lead agent rephrase them. That matches both Anthropic's appendix and the stable-interface constraint (files survive harness changes; event-stream parsers do not).
- Encode effort budgets and tool heuristics in skills only where a measured failure requires them, and delete them when a model upgrade makes them redundant. The bitter lesson is a deletion policy, not a ban on structure.

---

## 2. "Software factory" practice and how they evaluate outcomes

### 2.1 StrongDM (the only detailed public outcome-eval design in this set)

Primary: Justin McCarthy, "Software Factories and the Agentic Moment" (6 Feb 2026; https://factory.strongdm.ai/). Secondary write-up: Simon Willison (7 Feb 2026; https://simonwillison.net/2026/feb/7/software-factory/). Principles page: https://factory.strongdm.ai/principles. Techniques: https://factory.strongdm.ai/techniques.

This is a field report from a three-person team (Justin McCarthy, Jay Taylor, Navan Chauhan; team founded 14 Jul 2025), not a paper with a public test set. Willison visited in October 2025 and is reporting a demo plus their write-up. Treat numbers as their claims.

What they changed, and why it is an eval design:

- Rule: humans do not write or review the code. The practical mantra is "if you haven't spent at least **$1,000 on tokens today** per human engineer, your software factory has room for improvement." That is a slogan, not a measured optimum. Willison flags it as ~$20,000/month/engineer and says the patterns are less interesting at that burn rate. He hopes the same ideas work cheaper. No public cost-quality curve was found.
- In-repo tests were not enough. Agents reward-hacked them (`return true`). StrongDM's words: a test stored in the codebase "can be lazily rewritten to match the code."
- **Scenario** = an end-to-end user story, often stored **outside** the codebase, analogous to a training holdout, understandable by a human and "flexibly validated by an LLM." Willison attributes the word to Cem Kaner's scenario testing (2003); Kaner's paper was not re-read. Cite StrongDM/Willison for the operational definition, not Kaner, until that source is opened.
- **Satisfaction** = among observed trajectories through all scenarios, the fraction that likely satisfy the user. Boolean "suite is green" was rejected because the software under test is itself agentic, so success is probabilistic.
- **Digital Twin Universe**: behavioral clones of Okta, Jira, Slack, Google Docs, Drive, and Sheets, so scenarios can run at "thousands per hour" without rate limits, abuse detection, or live-API cost, including failure modes that are unsafe against production. Willison quotes Jay Taylor (HN comment, linked from the post; the HN thread was not opened): fidelity came from using popular public SDK client libraries as compatibility targets, aiming at 100% compatibility. The twins were themselves agent-built. That is a circular risk: the judge environment can share the generator's blind spots. StrongDM does not publish an independent fidelity audit in the pages read.
- Loop, from the principles page: seed (spec, screenshot, or existing code) → validation harness as close to the real environment as possible → feedback of a sample of outputs back into inputs, until holdout scenarios pass and stay passing. Fuel is traces, screen capture, incident replays, adversarial use, agentic simulation, surveys, interviews — not only unit tests.
- Attractor (https://github.com/strongdm/attractor), per Willison: the repo he looked at contained specs (markdown), not the implementation, with instructions to feed the specs to your own agent. Not re-opened here. cxdb is described as an immutable DAG of conversation and tool outputs. Not re-opened.

What they do **not** show: a published satisfaction number, a comparison against human-reviewed development, an inter-rater study of the LLM satisfaction judge, or a holdout that the scenario-writer cannot see. The design is the contribution. The result is anecdotal.

### 2.2 Factory.ai (credible product, different eval question)

Factory's public measurement, as fetched 2026-10-19 from https://docs.factory.com/agent-effectiveness/overview.md (also indexed at https://docs.factory.ai/agent-effectiveness/overview and marketed at https://factory.ai/product/agent-effectiveness and https://factory.ai/news/agent-effectiveness, 13 Aug 2026 — news post not fully re-read):

- Agent Effectiveness links Factory sessions to issues, projects, and pull requests, then reports **throughput** (cycle time vs spend), **output** (session-intent mix: feature, maintenance, bugfix, exploration), and **attribution** (session → work stream → artifact).
- They explicitly reject survey estimates of "how long would this have taken."
- Docs say the feature was in private preview and requires org integrations plus an enterprise analytics control.
- Marketing language on the product page (search snippet, page not fully re-read) also mentions autonomy ratio, token economics, and tool usage. Those are adoption/ROI telemetry.

What was **not** found in the pages read: hidden tests, holdout scenarios, a satisfaction judge, or a claim that merged PRs are correct. Factory measures whether agent spend is associated with faster delivery of tracked work. That is a management metric. It does not answer StrongDM's question ("did the software satisfy the user on a scenario the coder could not see?"). Conflating the two will make a workflow look successful while it ships reward-hacked code.

StrongDM's own page lists Factory among "others building factories," via a Fast Company profile (https://www.fastcompany.com/91279593/factory-ai-code-generation-matan-grinberg-eno-reyes). That profile was not read. Devin, 8090, Superconductor, and Jesse Vincent's Superpowers are named the same way; none of those eval designs were reviewed here except Cognition/Devin in §1.

### 2.3 The transferable factory pattern

Across StrongDM (outcome) and the SWE-bench design in §5 (hidden tests), the pattern that is actually evidenced is:

1. Spec / intent is the human artifact.
2. Implementation and in-repo tests are untrusted, because the same agent writes both.
3. A holdout the generator cannot edit decides acceptance: hidden tests, external scenarios, or a twin environment whose contract is an external SDK, not the agent's own tests.
4. For agentic software, report a rate over trajectories (satisfaction), not a single green/red.
5. Cycle time and token spend are covariates, not the objective (Factory's metric is useful exactly as a covariate; Kapoor's paper is why).

### So for us

- When the lab grows a software-factory workflow, the acceptance artifact is a **scenario pack stored outside the repo the agent can commit to**, plus a twin or fixture of the dependencies. In-repo tests are a developer affordance, not the grade. This is the one StrongDM idea that survives even if we reject "humans never read code" and the $1,000/day rule.
- Define satisfaction as a fraction of trajectories on held-out scenarios, with the judge seeing the scenario and the observable outcome, not the agent's rationale. Publish tokens and wall time beside it. Do not adopt Factory's cycle-time dashboard as a substitute; use it only if we later care about throughput.
- Do not treat StrongDM's DTU as proven for security software. It is a plausible way to get volume. Budget a separate fidelity check (SDK contract tests written by us, not by the twin-builder) or the eval environment will drift with the generator.
- "Code must not be reviewed" is their constraint, not ours. The eval lesson is narrower: review, if we do it, should not be the only line of defense, because we will not scale human review of every run. The scenario pack is what lets us sample.

---

## 3. Automated workflow / prompt optimization

All six systems optimize a **scalar or comparable metric on a train split of rollouts**. None of them invent the metric. If the metric is weak, they will climb it.

| System | What is optimized | Signal required | Headline result (from the abstract unless noted) | Source |
| --- | --- | --- | --- | --- |
| DSPy | Prompts, demonstrations, and (optionally) finetunes of a text-transformation graph. Modules are declarative; a compiler searches. | A metric the compiler can maximize. Programs can express agent loops. | A few lines, compiled in minutes, beat standard few-shot by "generally over 25%" (GPT-3.5) and 65% (Llama-2-13B-chat), and beat expert demos by up to 5–46% and 16–40%. Small compiled LMs competitive with expert prompt chains on proprietary GPT-3.5. | Khattab et al., arXiv:2310.03714, 5 Oct 2023. https://arxiv.org/abs/2310.03714 |
| OPRO | An instruction string. The LLM proposes new instructions conditioned on prior instructions and their scores. | Task accuracy (they also show linear regression and TSP). | Best found prompts beat human prompts by up to **8%** on GSM8K and up to **50%** on Big-Bench Hard. | Yang et al., arXiv:2309.03409, 7 Sep 2023. https://arxiv.org/abs/2309.03409 |
| TextGrad | Any variable in a compound system (prompts, code, molecules, plans) via textual "gradients" from an LLM critic. | An objective function the user supplies. The framework does not tune its own critic prompt. | GPT-4o zero-shot on Google-Proof QA from **51% to 55%**; **20%** relative gain optimizing LeetCode-Hard solutions. Also molecules and radiotherapy plans (those domains are out of scope here). | Yuksekgonul et al., arXiv:2406.07496, 11 Jun 2024. https://arxiv.org/abs/2406.07496 |
| ADAS / Meta Agent Search | The agent program itself. A meta-agent writes new agents in code into an archive. | Domain evals (coding, science, math) on which discovered agents are scored. | Abstract claims discovered agents "greatly outperform" hand-designed SOTA and **transfer across domains and models**. No percentage in the abstract. Do not invent one. | Hu, Lu, Clune, arXiv:2408.08435, 15 Aug 2024. https://arxiv.org/abs/2408.08435 |
| AFlow | Code-represented workflows (LLM nodes and edges), searched by MCTS with execution feedback. | Benchmark scores on six datasets. | **5.7%** average over SOTA baselines. Smaller models beat GPT-4o on specific tasks at **4.55%** of its inference cost. | Zhang et al., arXiv:2410.10762, 14 Oct 2024. https://arxiv.org/abs/2410.10762 |
| GEPA | Natural-language prompt updates. Samples trajectories (reasoning, tool calls, tool outputs), reflects, mutates, keeps a Pareto frontier. | Rollouts plus a metric. Works as an inference-time search over code too, per the abstract. | Beats GRPO by **6%** on average and up to **20%**, with up to **35×** fewer rollouts. Beats MIPROv2 by over **10%** (example: **+12%** accuracy on AIME-2025). | Agrawal et al., arXiv:2507.19457, 25 Jul 2025. https://arxiv.org/abs/2507.19457 . DSPy API: https://dspy.ai/api/optimizers/GEPA/overview/ |

### 3.1 What signal they need, in practice

- A **scalar or Pareto metric** that can be computed on a rollout without a human in the loop. DSPy's compiler, OPRO's score list, AFlow's execution feedback, and GEPA's Pareto frontier are all meaningless without it.
- GEPA's extra requirement is a **trace rich enough to reflect on**: tool calls and tool outputs, not just a final string. A workflow eval that only stores the PPTX will not feed GEPA. A workflow eval that stores the trace plus the deliverable will.
- ADAS and AFlow need the workflow to be a **searchable artifact** (code, or a graph that can be rewritten as code). A pile of prose skills can be optimized as prompts (GEPA/DSPy/OPRO) but not as a topology unless we represent topology as code.
- TextGrad needs a critic that can name which variable to change. That critic is itself an LLM, so the objective can be "whatever the critic likes."

### 3.2 Overfitting to the judge — evidenced mechanisms, not a GEPA-specific scandal

No paper in the set above was found, in the abstracts read, that measured "GEPA overfit an LLM judge and collapsed on held-out humans." The risk is the composition of three published facts:

1. **The optimizer climbs whatever you score.** DSPy, OPRO, TextGrad, AFlow, and GEPA are explicit about this. OPRO's 50% BBH gain and GEPA's 35× sample efficiency mean a bad metric will be exploited quickly, not slowly.
2. **LLM judges have systematic biases.** Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", arXiv:2306.05685 (9 Jun 2023; https://arxiv.org/abs/2306.05685): position bias, verbosity bias, self-enhancement bias, and limited reasoning. Strong judges (GPT-4 in that paper) can still match human agreement (~**80%**, similar to human-human). Anthropic's research post independently found a single judge more stable than a panel, and still needed humans for source-quality bias. MAST's own LLM annotator, even at κ = 0.77, had only **0.62–0.77 recall** depending on prompting (v2 Table 2): it misses failure modes.
3. **Proxy rewards overoptimize.** Gao, Schulman, Hilton, "Scaling Laws for Reward Model Overoptimization", arXiv:2210.10760 (19 Oct 2022; https://arxiv.org/abs/2210.10760): optimizing an imperfect proxy reward model eventually **hurts** the gold reward (Goodhart). The functional form differs for RL vs best-of-n, and scales with reward-model size. This is an RLHF paper, not a prompt-optimizer paper. The transfer is: a judge used as the training target will be overoptimized; a judge used as a periodic audit will not, as fast.
4. **Agent benchmarks already lack holdouts.** Kapoor et al. (arXiv:2407.01502) prescribe holdouts because agents take shortcuts against the benchmark they can see. StrongDM rediscovered the same failure empirically (`return true`).

A related 2026 preprint, "More Convincing, Not More Correct: Self-Play Reward Hacking of Reference-Free LLM Judges" (https://arxiv.org/html/2607.05904), was seen in search and **not read**. Do not cite its claims. It is a pointer that the failure mode is an active research topic, nothing more.

### So for us

- Do not turn on DSPy/GEPA/AFlow against the live judge. The order is: frozen holdout tasks, deterministic checks, a human-anchored rubric, *then* an optimizer on a train split that cannot see the holdout. Report holdout and train separately. If they diverge, the optimizer is fitting the judge.
- GEPA is the best-fit optimizer *if* we keep traces (tool calls, files written, judge critique), because it reflects in language and is sample-efficient. AFlow/ADAS are the fit if we decide the workflow topology itself is the object. OPRO/DSPy are enough for single-skill prompt text. TextGrad is a generalization, not a first tool.
- The judge prompt is part of the system under test. Optimizing the generator against a judge, then editing the judge, invalidates the history. Version the judge with the eval set.
- Keep a small human audit set that the optimizer never sees and that is not used to pick the winner among automated runs (that would leak). Anthropic's "humans catch source bias" is the precedent. GDPval (§5) is the precedent for "automated grader is not yet good enough to replace experts."
- ADAS's transfer result is a reason to let search propose workflow variants, and Sutton's essay is a reason not to marry the winner. Re-run the search when the model changes; do not freeze a 2026 topology as constitution.

---

## 4. Graphs vs loops

### 4.1 What the sources say

**Anthropic's distinction is the cleanest.** "Building effective agents" (https://www.anthropic.com/engineering/building-effective-agents):

- **Workflows**: LLMs and tools orchestrated through predefined code paths (chain, route, parallelize, orchestrator-workers, evaluator-optimizer).
- **Agents**: the LLM directs its own process and tool use in a loop, for open-ended problems where the step count cannot be hardcoded.
- Frameworks (they name several GUI builders) hide prompts and responses and tempt extra complexity. Start with the API. Add a step only when measurement says so.
- Evaluator-optimizer is appropriate when a human critique would have improved the output *and* an LLM can supply that critique. That is an empirical precondition, not a default node.
- Coding agents work because code is verifiable by tests and the agent can loop on the test result. Customer support works because resolution is definable. Both have a ground-truth signal. A proposal deck does not, until we build one.

**LangGraph's own docs** (https://docs.langchain.com/oss/python/langgraph/overview, fetched 2026-10-19): LangGraph is a low-level orchestration runtime whose stated strength is mixing **deterministic hand-coded steps** with **LLM-driven steps** in one graph, plus persistence, human interrupts, and streaming. It does not claim that graphs score higher than loops, or that graphs survive model upgrades. Those claims are absent. LangChain's higher-level agents are described as prebuilt tool-calling loops on top of the same runtime. Product copy about Klarna, Uber, and J.P. Morgan is marketing, not an eval.

**n8n** (https://docs.n8n.io/build/understand-workflows.md): a workflow is "a collection of nodes connected together to automate a process," started by a trigger and executed to complete a task. This is integration plumbing: credentials, triggers, deterministic nodes, with an AI integration surface documented separately (https://docs.n8n.io/build/integrate-ai.md, not re-read). It is the right shape for "when a file lands, transcode it, run ffprobe, write a QC JSON." It is the wrong shape for "decide the narrative of the video."

**Browser Use's counter-argument** (https://browser-use.com/posts/bitter-lesson-agent-frameworks): graph/framework abstractions froze assumptions and fought every experiment. They deleted the framework down to a loop, a complete action space, an explicit done tool, and context management (ephemeral tool outputs). Restrictions were added from eval failures, not designed up front.

**No maintainability-across-upgrades study was found.** Searches turned up opinion posts (AutoGen vs LangGraph, "graphs vs loops" explainers). None was a longitudinal measurement of the same workflow across model generations. Do not cite them as evidence. The closest primary statements are Anthropic's "add complexity only when it improves outcomes" and Zunic's "if the abstraction encodes how you think the model should think, the next model will route around it or be crippled by it."

### 4.2 A practical split that does not outrun the evidence

| Put in a deterministic graph / script | Leave in the model loop |
| --- | --- |
| File conversion, schema checks, ffprobe/VMAF/loudness, hidden-test runners, secret redaction, "did the PPTX open and contain N slides" | Research planning, narrative choices, which file to edit, when to stop investigating |
| Retries, checkpoints, resume-from-failure (Anthropic's production lesson; LangGraph's persistence claim) | How to recover *semantically* once the tool error is shown to the model |
| Routing that is a pure function of an already-measured class (file type, language, duration) | Routing that requires taste |
| The eval harness itself | The workflow being evaluated |

Anthropic's orchestrator-workers pattern is the hybrid: the *existence* of delegation is a workflow, the *content* of subtasks is model-chosen. That is also where MAST and Cognition say it breaks, unless the subtask is read-only or the writer stays single-threaded.

### So for us

- The stable interface is the point. A Markdown skill plus a CLI print mode plus files is a tiny graph: it has a start, a stop, and artifacts. It does not require LangGraph or n8n to be evaluable, and it survives an OMP upgrade better than a parser of OMP's event stream. Use a real graph engine only where we need durable resume or a deterministic QC pipeline (video encode, PPTX schema, test runner).
- Do not encode the proposal workflow as an n8n-style required path (research node → outline node → slide node → critique node) unless an ablation shows the path beats a single loop on the holdout. Anthropic's precondition for a chain is that the task "can be easily and cleanly decomposed into fixed subtasks." A proposal cannot.
- Do encode the *grader* as a graph: deterministic checks, then rubric, then optional judge, then human sample. The grader's path should be boring. The generator's path should be free, then restricted by eval failures (Zunic's inversion).
- When a model upgrade lands, re-measure the holdout before editing the graph. If the loop now matches the graph, delete the graph nodes. That is the bitter-lesson maintenance policy. There is no paper that tells us how often this will happen; schedule the re-measure anyway.

---

## 5. Domain eval exemplars

The shared pattern, stated first so the details have somewhere to land:

**Deterministic checks + rubric + expert preference + downstream outcome**, each allowed to falsify the others. No exemplar uses only one.

### 5.1 Software — SWE-bench and SWE-bench Verified

Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", arXiv:2310.06770 (10 Oct 2023; https://arxiv.org/abs/2310.06770): **2,294** problems from real issues and PRs in **12** Python repos. The model gets the repo and the issue, not a function signature. At publication, Claude 2 solved **1.96%**. The interesting design is the grader, not that number.

OpenAI, "Introducing SWE-bench Verified" (13 Aug 2024, updated 24 Feb 2025; https://openai.com/index/introducing-swe-bench-verified/):

- Each instance has `FAIL_TO_PASS` tests (fail before the fix, pass after) and `PASS_TO_PASS` tests (must not regress). **The tests are not shown to the agent.** Both sets must pass.
- The original set systematically underestimates or mis-grades: unit tests were overly specific or unrelated to the issue; issue text was underspecified; environments were flaky. Example: a scikit-learn issue about an unused `copy` argument was graded by a test that required an exact deprecation-warning string the agent could not have known.
- 93 Python developers annotated 1,699 samples, three annotators each, ensemble = highest severity. **38.3%** flagged underspecified problem statements, **61.1%** flagged unit tests that could reject valid solutions, **68.3%** filtered for underspecification, unfair tests, or other issues. SWE-bench Verified is the remaining **500**. Difficulty labels: 196 tasks estimated <15 minutes, 45 estimated >1 hour. Dockerized harness for reproducibility.
- GPT-4o on the best open scaffold they tried: **33.2%** on Verified vs **16%** on the original full set. The benchmark had been mis-measuring the model. That is a warning for us: a harsh automated grader can be wrong in either direction.

Transferable pieces: hidden behavioral tests, regression tests, human audit of the *tasks and the tests* (not just the model outputs), containerized exact environments, difficulty slices, and the refusal to treat a flaky harness failure as a model failure.

### 5.2 Video — generative quality, perceptual QC, and delivery constraints are different instruments

**VBench** (Huang et al., CVPR 2024; arXiv:2311.17982, 29 Nov 2023; https://arxiv.org/abs/2311.17982): dissects "video generation quality" into **16** hierarchical dimensions (examples named in the abstract: subject identity inconsistency, motion smoothness, temporal flickering, spatial relationship), each with its own prompts and an automatic method, plus a human-preference annotation set **per dimension** to check that the automatic score tracks people. The point of the decomposition is diagnostic: a single MOS hides which failure you have. Later suites (VBench++, VBench-2.0) exist; their papers were not read. Do not cite their dimension lists.

**VMAF** (Netflix; repo read 2026-10-19, https://github.com/Netflix/vmaf): "perceptual video quality assessment based on multi-method fusion," Emmy-winning, shipped as `libvmaf`, a Python training/test toolkit, and an FFmpeg filter. The README points at the overview post https://netflixtechblog.com/toward-a-practical-perceptual-video-quality-metric-653f208b9652 (fetch returned **403**; authors and correlation numbers from that post were **not verified**). The repo also exposes PSNR, PSNR-HVS, SSIM, MS-SSIM, CIEDE2000, and CAMBI (banding). Use VMAF when the workflow *re-encodes a reference master* (transcode QC). It is the wrong instrument for "is this generated shot good?" when there is no reference. That full-reference characterization is the standard use implied by a source-vs-distorted metric and by the README's encode/codec tooling; the exact CLI contract was not re-read. Mark the sentence "VMAF requires a reference" as the intended use, and confirm against `libvmaf` docs before coding a gate.

**Loudness.** ITU-R BS.1770, "Algorithms to measure audio programme loudness and true-peak audio level" (https://www.itu.int/rec/R-REC-BS.1770/en). The recommendation text was not opened. Do not invent a LUFS target. The design fact is: loudness and true-peak are deterministic, standardized, and delivery-spec-dependent. A workflow eval should record the measurement and compare it to a chosen spec, not ask a judge "does the mix sound professional?"

**Captions.** No caption-accuracy benchmark was opened in this pass. Word error rate against a locked script, plus a timing check, is the obvious deterministic pair. A specific delivery spec (Netflix timed text, EBU, FCC) was **not verified**. Mark the threshold as an open choice, not a known number.

**What is missing:** a published benchmark of an end-to-end production workflow (brief → script → shot list → generate/shoot → edit → grade → mix → captions → master). VBench evaluates generative models. VMAF evaluates encodes. Neither evaluates "did the video satisfy the brief."

### 5.3 Documents and presentations — PPTC, PPTEval, GDPval

**PPTC** (Guo, Zhang, Liang, Zhao, Duan, arXiv:2311.01767, 3 Nov 2023; https://arxiv.org/abs/2311.01767): 279 multi-turn sessions of creating and editing PPTX via tool APIs. The grader (**PPTX-Match**) scores the **resulting file**, not the API sequence, so different action traces can pass. GPT-4: **75.1%** single-turn accuracy, **6%** session accuracy. Named failure causes: error accumulation across turns, long template context, multi-modal perception. This is the slide-workflow analogue of SWE-bench's hidden tests: grade the artifact, expect multi-step sessions to collapse even when single calls look fine.

**PPTAgent / PPTEval** (Zheng et al., arXiv:2501.03936v3, 21 Feb 2025; https://arxiv.org/html/2501.03936v3 and https://arxiv.org/abs/2501.03936): generation is edit-based (pick a reference slide, apply edit APIs, self-correct on execution errors) rather than text-to-slides. PPTEval is an MLLM judge on three dimensions, 1–5, with rationales:

| Dimension | Criteria (Table 1) | Scope |
| --- | --- | --- |
| Content | Concise, grammatical text; relevant images | Per slide |
| Design | Color, layout, readability, visual elements | Per slide |
| Coherence | Progressive structure, necessary background | Whole deck |

They also report non-judge metrics: success rate (did generation finish), perplexity, ROUGE-L, FID. In Table 3, PPTAgent with Qwen2.5 + Qwen2-VL averages **3.67** (Content 3.28, Design 3.27, Coherence 4.48); GPT-4o + GPT-4o averages **3.62**. The intro's "average score of 3.67" is that Qwen configuration, not a human score. The paper says human evaluation "validates the reliability" of PPTEval; the correlation number was not in the portion read. Do not treat 3.67 as a human preference result. Existing metrics and PPTEval disagree in places (a rule-based baseline can have low perplexity and weak design scores), which is the argument for not using ROUGE as a deck score.

**GDPval** (OpenAI, 25 Sep 2025, https://openai.com/index/gdpval/; paper: Patwardhan et al., arXiv:2510.04374, 5 Oct 2025, https://arxiv.org/abs/2510.04374):

- 44 occupations, 9 sectors that each contribute >5% of U.S. GDP, top knowledge-work occupations by wages, using BLS OES May 2024 and O*NET (occupation included if ≥60% of tasks are non-physical).
- Full set **1,320** tasks (30 per occupation); open gold set **220** (5 per occupation). Writers averaged **14 years** of experience. Each task got about **5** rounds of expert review. Tasks include reference files. Deliverables include documents, slides, diagrams, spreadsheets, multimedia — not just a text answer.
- Grading is **blind expert pairwise** against a human deliverable: better / as good as / worse. Rubrics exist for transparency. An automated grader estimates the expert preference and is released at https://evals.openai.com; OpenAI says it is **not yet as reliable as expert graders** and they do not use it to replace them.
- Early result, from the blog (the paper PDF was not re-read, so prefer the blog for these figures): frontier models approach expert quality. Claude Opus 4.1 was best in the set and "excelling in particular on aesthetics (document formatting, slide layout)"; GPT-5 excelled on accuracy. Opus 4.1 was rated good-as-or-better than the human on "just under half" of gold tasks. The same page says performance "more than doubled" from GPT-4o to GPT-5 and, in a chart caption, "more than tripled." **That inconsistency is in the source.** Do not pick one. Inference time and API price were "roughly 100×" faster and cheaper than experts, and the authors say this **excludes** human oversight, iteration, and integration.
- Explicit limitation: **one-shot**. It does not measure multi-draft workflows, ambiguity, or the decision that a brief is the right deliverable. That limit is exactly our problem. GDPval is a deliverable exam, not a workflow eval.

### 5.4 The pattern, extracted

| Layer | Software | Video (future) | Proposals / PPTX (now) | What fails if you skip it |
| --- | --- | --- | --- | --- |
| Deterministic | Hidden FAIL_TO_PASS + PASS_TO_PASS; container boots | Container opens; duration; frame size; VMAF vs master if a master exists; BS.1770 loudness; caption WER vs locked script | PPTX opens; slide count; required strings; no overflow past a measured box; file not corrupt (PPTC grades the file) | Judge can be talked out of a broken file. Agent can rewrite in-repo tests. |
| Rubric | Issue resolution is binary, so the rubric is the test spec; humans audited the tests | Dimension list in the style of VBench (identity, flicker, motion) plus brief coverage | PPTEval's content / design / coherence, rewritten for *our* brief, not Zenodo decks | A single "quality" score cannot tell you what to fix. |
| Expert preference | Annotators threw out 68.3% of tasks as unfair | Human preference per dimension, as VBench did, not one MOS | GDPval-style blind pairwise vs a human deck we already accept | Rubric and judge drift from taste. OpenAI will not let their auto-grader replace experts. |
| Downstream outcome | PR would merge and tests stay green in the wild — not measured by SWE-bench | Watch-time, revision count, delivery rejection — not measured by VBench | Did a human send the deck / accept the proposal without a rewrite? | You can win the exam and still produce unused work. GDPval is explicit that one-shot ≠ the job. |

Kapoor et al. add: report cost next to every cell, and keep a holdout the workflow author cannot iterate on.

### So for us

- The first proposal/PPTX eval should look like PPTC's artifact grader plus PPTEval's three axes plus a GDPval-style blind compare against a small set of decks we already consider sendable. Deterministic layer first (file opens, required sections exist, no obvious overflow), then a versioned rubric, then a judge, then a human sample. Do not start with the judge.
- Steal SWE-bench Verified's lesson before writing 200 tasks: have a human try to solve and to *grade* each item, and delete items whose check rejects valid work. Their 68.3% discard rate is the prior. Twenty audited tasks beat two hundred unfair ones (Anthropic's small-set point and OpenAI's audit point agree).
- For the later video workflow, do not wait for a unified benchmark. Stand up three independent gates: (1) technical QC with existing tools — ffprobe, VMAF only where a reference exists, BS.1770, caption error against the script; (2) a VBench-style dimension rubric for generative shots, validated once against our own preferences; (3) a downstream label (accepted / revised / rejected by the person who asked for the video). A single "video score" will hide whether we have a mix problem or a story problem.
- GDPval's one-shot limit is the gap we can actually contribute to: our unit of eval is the workflow run, including revisions. Record draft count and whether the human accepted the last draft. That outcome is not in any of these papers, and it is the one that matches the lab's goal.
- The automated grader is a regression detector. It is not the leaderboard. OpenAI, Zheng, Gao, and StrongDM are four independent reasons.

---

## Closing

### Five strongest transferable design principles

1. **Grade the artifact and the end state, with tests the generator cannot see.** SWE-bench hides FAIL_TO_PASS and PASS_TO_PASS. PPTC grades the PPTX, not the API trace. StrongDM puts scenarios outside the repo because in-repo tests get rewritten. Anthropic grades research outcomes because the path is not unique. A workflow eval that scores "did it call the research skill" will be gamed and will break on the next model.

2. **Stack four signals, and let the cheapest one fail the run.** Deterministic checks, then a versioned rubric, then an anchored judge, then a sampled human preference and a downstream accept/reject. GDPval, PPTEval, VBench, and SWE-bench Verified each needed more than one of these. OpenAI will not replace GDPval experts with their own grader. We should not either.

3. **One writer. Extra agents only for read, review, or routing — and only if they beat the single agent at reported cost.** Cognition's two posts and Anthropic's research post agree on the failure mode (implicit decisions, lost context) and disagree on the winning domain (coding vs breadth-first research). Our deliverables are coherent artifacts, so the coding constraint is the prior. Anthropic's 80% token-variance result means a multi-agent "win" that spends 15× tokens is not yet a workflow win. Kapoor: publish cost beside accuracy.

4. **Keep the harness thinner than the eval.** Stable surfaces are skills, files, and CLI print mode. Put QC and hidden-test running in a deterministic script. Leave planning in the loop. Add a graph node only after an ablation, and delete it when a model upgrade ties the ablation (Sutton; Zunic; Anthropic's "simplest solution that measurement supports"). Do not parse OMP event streams to grade runs.

5. **Optimize only a frozen metric, on a split the optimizer cannot touch.** DSPy, OPRO, TextGrad, AFlow, ADAS, and GEPA are ready to climb whatever we score, and GEPA will do it in few rollouts if we keep traces. Zheng's judge biases and Gao's overoptimization curve say the climb will fit the judge. Hold out tasks, hold out the human audit, version the judge prompt with the eval set, and report train vs holdout every time we compile.

### Five biggest open uncertainties

1. **Does any multi-agent lift transfer to our deliverables?** The 90.2% result is an internal research eval on breadth-first lookup. Cognition's working patterns are clean-context review and frontier-to-frontier routing, with writes still single-threaded. Nobody in the sources measured "orchestrator + workers" on a proposal deck or a video cut, where consistency of taste is the product. Assuming the Anthropic architecture will raise deck quality is unwarranted.

2. **There is no measured half-life for a hard-coded workflow.** Sutton's essay and the 2026 harness essays are strong priors for "delete structure that encodes today's model weaknesses." They are not a decay curve. We do not know whether a proposal graph designed this quarter will be a liability in two model generations or still be the difference between 30% and 80%. The only honest policy is re-ablate on each model upgrade, which costs tokens we have not budgeted.

3. **Satisfaction is undefined for our outputs, and every public judge is a proxy.** StrongDM names the metric and does not publish a number or an inter-rater study. GDPval's automated grader is, by OpenAI's admission, not expert-grade. PPTEval's human-agreement statistic was not in the pages used here. MAST's careful judge still missed modes (recall 0.62 without few-shot examples, v2). We can build a rubric this week. We cannot yet claim it tracks "a human would send this."

4. **Factory economics and factory correctness are being conflated in the industry write-ups.** StrongDM's $1,000/engineer-day is a rule of thumb from a team that chose it. Factory.ai's published Agent Effectiveness metric is cycle time and spend attribution, not hidden-test pass rate. Willison's cost objection is unanswered by data. A lab that copies either number, or treats "PRs opened" as success, will learn the wrong lesson. UNVERIFIED: whether any of the other named factories (8090, Superconductor, Superpowers) have a public holdout design. Not reviewed.

5. **No exemplar covers the workflow we will actually run.** SWE-bench is one-shot issue → patch. GDPval is one-shot task → deliverable, and says so. VBench is a model benchmark, not an edit. PPTC sessions are API editing of an existing deck, not "win this bid." The open scientific question — how to score a multi-draft, multi-tool workflow whose value is a downstream human decision, without the scorer becoming the training target — is not settled by any source read here. That is the lab's actual research problem, not a missing citation.

### Sources opened or abstract-fetched

- https://www.anthropic.com/engineering/multi-agent-research-system
- https://www.anthropic.com/engineering/building-effective-agents
- https://cognition.com/blog/dont-build-multi-agents
- https://cognition.com/blog/multi-agents-working
- https://arxiv.org/abs/2503.13657 and https://arxiv.org/html/2503.13657v2
- https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html (listing only)
- http://www.incompleteideas.net/IncIdeas/BitterLesson.html
- https://browser-use.com/posts/bitter-lesson-agent-frameworks
- https://arxiv.org/abs/2407.01502
- https://factory.strongdm.ai/ and https://factory.strongdm.ai/principles
- https://simonwillison.net/2026/feb/7/software-factory/
- https://docs.factory.com/agent-effectiveness/overview.md (Factory Agent Effectiveness; also indexed under docs.factory.ai)
- https://factory.ai/product/agent-effectiveness (marketing; not fully re-read)
- https://arxiv.org/abs/2310.03714
- https://arxiv.org/abs/2309.03409
- https://arxiv.org/abs/2406.07496
- https://arxiv.org/abs/2408.08435
- https://arxiv.org/abs/2410.10762
- https://arxiv.org/abs/2507.19457
- https://arxiv.org/abs/2306.05685
- https://arxiv.org/abs/2210.10760
- https://docs.langchain.com/oss/python/langgraph/overview
- https://docs.n8n.io/build/understand-workflows.md
- https://arxiv.org/abs/2310.06770
- https://openai.com/index/introducing-swe-bench-verified/
- https://arxiv.org/abs/2311.17982
- https://github.com/Netflix/vmaf
- https://www.itu.int/rec/R-REC-BS.1770/en (page located; recommendation body not read)
- https://arxiv.org/abs/2311.01767
- https://arxiv.org/abs/2501.03936 and https://arxiv.org/html/2501.03936v3
- https://openai.com/index/gdpval/
- https://arxiv.org/abs/2510.04374 (abstract)

Not used as evidence: search-result explainers on LangGraph vs loops; the unread 2026 self-play judge-hacking preprint; Fast Company Factory profile; Kaner 2003 (cited by Willison, not opened); Chroma context-rot page (cited by Yan, not opened); Netflix VMAF blog (403).
