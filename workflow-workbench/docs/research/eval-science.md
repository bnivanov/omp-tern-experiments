# Workflow evals: scientific methodology notes

Research memo for a small-N personal workflow-eval lab (OMP + Tern; deliverables now are proposals/PPTX, later a software factory and end-to-end video). Read-only. External claims below were checked against the cited page or abstract on 2026-10-19. Anything not confirmed in the fetched text is marked **UNVERIFIED**.

Design constraint this memo keeps in view: the eval contract must survive OMP and model upgrades. Prefer Markdown skills, files, and CLI print-mode artifacts. Do not parse harness-internal event streams.

---

## 1. Eval design process

### What the sources actually say

**Error analysis before metrics.** Husain and Shankar treat error analysis as the activity that decides which evals to write. Their operational loop, adapted from qualitative coding, is: (1) collect representative traces, or synthetic inputs only if you have none; (2) **open coding** — a domain expert writes open notes on traces, preferably the *first* failure, because upstream errors cause downstream ones; start with at least 30 traces yourself before accepting an agent’s suggestions; (3) **axial coding** — group notes into a failure taxonomy and count each bin (an LLM may help cluster, a human accepts or rejects); (4) iterate toward **theoretical saturation**, when new reviews stop revealing or revising failure modes. A working pool of about 100 diverse traces is their guardrail, not a requirement to read all 100 in order. They explicitly warn against platform-default generic metrics. Source: Hamel Husain and Shreya Shankar, “Why is error analysis so important in AI evals, and how is it performed?”, 27 June 2025 (modified 1 Sept 2026), https://hamel.dev/blog/posts/evals-faq/why-is-error-analysis-so-important-in-llm-evals-and-how-is-it-performed.html

**Criteria are not independent of the outputs you grade.** Shankar, Zamfirescu-Pereira, Hartmann, Parameswaran, and Arawjo (EvalGen; UIST 2024) built a mixed-initiative tool that proposes criteria and grader implementations (Python or LLM prompts), then asks the human to grade a subset so the tool can pick implementations that match those grades. Their qualitative finding, which they name **criteria drift**: users need criteria in order to grade, but grading is what lets them define criteria. Some criteria are *dependent* on the specific outputs observed, not specifiable a priori. That undercuts any process that freezes a rubric before anyone has looked at traces. Source: Shreya Shankar et al., “Who Validates the Validators?”, arXiv:2404.12272, 18 April 2024, https://arxiv.org/abs/2404.12272

**Anthropic’s agent-eval vocabulary and roadmap.** “Demystifying evals for AI agents” (9 Jan 2026; page modified 18 March 2026) is the most direct primary engineering source for this lab. Definitions worth adopting verbatim:

- **Task**: one test with inputs and success criteria.
- **Trial**: one attempt. Models vary, so run multiple trials.
- **Grader**: logic scoring some aspect; a task can have several, each with assertions.
- **Transcript / trace / trajectory**: the full record (outputs, tool calls, reasoning, intermediate results).
- **Outcome**: final environment state, not what the agent *said* happened. Their example: the agent says the flight is booked; the outcome is whether a reservation row exists.
- **Evaluation harness** vs **agent harness**: the thing that runs and grades trials, versus the scaffold+model being measured. You never evaluate “the model” alone.
- **Suite**: tasks sharing a goal.

They split **capability evals** (“what can it do?”, start at a low pass rate, a hill to climb) from **regression evals** (“does it still do what it used to?”, near 100%). Saturated capability tasks should graduate into the regression suite.

Roadmap claims that matter at our scale:

- Do not wait for hundreds of tasks. **20–50 tasks from real failures** is a real start, because early changes have large effects. Mature agents need larger, harder sets to see small effects.
- A good task is one **two domain experts would pass/fail the same way**, and that an instruction-following agent can pass. A reference solution should pass every grader. With frontier models, **0% pass@100 is usually a broken task**, not an incapable agent. They cite a Terminal-Bench audit where tests assumed a filepath the task never specified.
- Build **balanced** sets: cases where a behavior should happen *and* where it should not. One-sided sets produce one-sided agents (their web-search overtrigger/undertrigger example).
- Isolate trials. Shared state causes correlated failures *and* unfair wins (they saw Claude read git history from previous trials).
- Grade **what was produced, not the path**. Prescribed tool-call sequences are brittle; agents find valid approaches designers did not anticipate. Give partial credit on multi-part tasks.
- Combine code graders (fast, objective, brittle), model graders (flexible, must be calibrated), and occasional human graders (gold standard, used to calibrate the model graders).
- Read transcripts. Opus 4.5 scored 42% on CORE-Bench until rigid numeric grading, ambiguous specs, and irreproducible stochastic tasks were fixed, then 95% on a less constrained scaffold (Anthropic citing an external post). METR had tasks whose stated threshold was lower than the grader’s threshold, so instruction-following models were penalized. **Do not take a score at face value until someone has read traces.**
- Saturation: SWE-bench Verified moved from about 30% to frontier scores **>80%** in the year of that post, and a one-shot coding eval missed Opus 4.5 gains that showed up only on longer tasks (Qodo, as reported by Anthropic).
- Automated evals are one layer. They pair them with production monitoring, A/B tests, user feedback, transcript review, and structured human studies (Swiss-cheese model). A personal lab has no production traffic, so transcript review and a sealed human spot-check *are* the other layers.

Source: Anthropic, “Demystifying evals for AI agents”, 9 Jan 2026, https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

**Workflows vs agents, and where nondeterminism enters.** Anthropic’s earlier architecture post distinguishes **workflows** (LLMs and tools on predefined code paths) from **agents** (the model directs its own process). They argue for the simplest system that works, and for adding complexity only when evals show it helps. Evaluator-optimizer is appropriate when a human can articulate feedback that improves the draft *and* a model can give that feedback. Agents need environmental ground truth each step, stopping conditions, and sandbox testing, because autonomy raises cost and compounding error. Coding agents are a good fit when tests can verify the artifact; human review still matters for system fit. Source: Anthropic, “Building effective agents”, 19 Dec 2024, https://www.anthropic.com/engineering/building-effective-agents

Their multi-agent research post is the closest analogue to an orchestrator-worker workflow lab. Effective evaluation, in their words: start immediately with a small sample (they began with **about 20 queries** representing real usage; a prompt tweak might move success from 30% to 80%, which a handful of cases can show). Do not require a prescribed path. Judge outcomes plus a reasonable process. Their research-judge rubric was factual accuracy, citation accuracy, completeness, source quality, and tool efficiency. They tried multiple judges and found **one LLM call, scores in \[0, 1\] plus pass/fail, most consistent with humans**, especially when the case had a checkable answer. Humans still caught what automation missed (early agents preferred SEO farms over primary sources). Small lead-agent prompt changes unpredictably changed subagent behavior, so the unit of evaluation is the system, not one agent. End-state evaluation beat turn-by-turn grading for agents that mutate state; for long workflows, grade **checkpoints** of state, not every step. Source: Anthropic, “How we built our multi-agent research system”, 13 June 2025, https://www.anthropic.com/engineering/multi-agent-research-system

**OpenAI’s product-eval guide** (still the official design guide; the Evals *platform* is a different, deprecated product — see §6) says: define the objective, collect a dataset that matches real traffic (typical, edge, adversarial), define metrics, compare, then continuously evaluate. Tips: eval-driven development, task-specific tests, log everything so logs become cases, automate scoring, calibrate against humans. Anti-patterns: generic academic metrics alone (perplexity, BLEU), datasets that do not match the real distribution, vibe checks, skipping human calibration. They note **LLMs are better at discriminating than at open-ended generation**, so judges should do pairwise comparison, classification, or scoring against criteria. Architecturally, workflows add more model calls but not a new kind of nondeterminism; agents add tool selection; multi-agent adds handoff. **The decision to go multi-agent should be driven by evals**, not by the architecture diagram. Source: OpenAI, “Evaluation best practices”, https://developers.openai.com/api/docs/guides/evaluation-best-practices (markdown mirror: https://developers.openai.com/api/docs/guides/evaluation-best-practices.md). Platform deprecation dates in that same page: read-only for existing users 31 Oct 2026, shutdown 30 Nov 2026.

### So for us

Do not start by importing a “proposal quality” or “agent quality” dashboard. Run the workflow on a handful of real briefs, open-code the first failure in each trace (skill miss, handoff gap, ungrounded slide, broken PPTX, runaway cost), then axial-code a taxonomy. That taxonomy *is* the first grader list. Expect criteria drift: the rubric you write before seeing decks will be wrong; version it (see §4). Twenty to fifty tasks is enough to start, split into a hard capability set and a near-perfect regression set of briefs the current system already nails. Two-expert agreement is the task-quality test: if you and a second reader would not pass/fail a deck the same way, the task is underspecified, not the model. Write a reference artifact that passes the graders before you blame the agent. Grade the PPTX/repo/video files and any side-effect state, not “the agent must have called tool X then Y”. Read every surprising transcript before changing a skill. OMP print-mode logs and Tern are how you do that review without coupling the eval to OMP’s internal event schema.

---

## 2. Statistics

### What the sources actually say

**Evals are experiments, and point estimates without error bars mislead.** Evan Miller (Anthropic), “Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations”, arXiv:2411.00640, 1 Nov 2024, https://arxiv.org/abs/2411.00640 (HTML: https://arxiv.org/html/2411.00640v1). Recommendations, in his order:

1. Standard error of the mean via the central limit theorem, not a bootstrap, unless the sampling scheme or estimator is complicated. Bernoulli scores: \(\mathrm{SE}=\sqrt{\bar s(1-\bar s)/n}\). Fractional scores (F1 and similar): use the sample variance, not the Bernoulli formula (Llama 3’s intervals were too wide on fractional scores and, he argues, too narrow on clustered reading-comprehension sets).
2. **Clustered standard errors** when questions are drawn in groups (same passage, same item translated across languages). Naive SEs assume independent draws. On real Anthropic runs he reports clustered/naive ratios of about **3.05 (DROP), 1.10 (RACE-H), and 1.88 (MGSM)** — up to 3×. Report question count *and* cluster count.
3. Variance has two parts: variance of question difficulty (immutable, shrinks only by adding questions) and per-question sampling noise (shrinks by repeating). Repeat each question \(K\) times and analyze the **question-level mean**. Stop increasing \(K\) once per-question variance over \(K\) is much smaller than between-question variance. In his uniform-difficulty binary example, \(K=2\) cuts total variance by 1/3, \(K=4\) by 1/2, and resampling cannot remove more than 2/3. Pooling all \(KN\) answers as if independent is inconsistent — repeats are a cluster.
4. **Do not lower temperature to shrink error bars.** Temperature changes the behavior under study, and can move noise into the question means or bias the estimate. His toy examples: rounding a uniform \([0,1]\) score at \(T=0\) triples the variance of the conditional means (1/12 → 1/4); a shifted uniform changes both the mean (2/3 → 3/4) and the variance (~5×).
5. **Paired differences.** When two systems see the same questions, inference belongs on \(s_{A,i}-s_{B,i}\), not on two separate headline scores. Paired variance is unpaired variance minus twice the covariance of question difficulties. If models agree on what is hard, pairing is a free variance reduction (his \(\rho=0.5\) continuous example: about 1/3). Report the difference, its SE, a 95% CI, and the correlation. A difference whose CI covers 0 is noise even if it “wins” two of three evals. Cluster the paired differences the same way.
6. **Power / minimum detectable effect.** For a paired comparison, his sample-size formula is

\[
n=(z_{\alpha/2}+z_{\beta})^{2}(\omega^{2}+\sigma_A^{2}/K_A+\sigma_B^{2}/K_B)/\delta^{2}
\]

where \(\delta\) is the smallest difference you care about, \(\omega^{2}\) is the variance of the paired conditional-mean difference, and the \(\sigma^{2}/K\) terms are residual sampling noise. Worked example under his assumptions (\(\sigma=0\), \(\omega^{2}=1/9\), \(\delta=0.03\), 80% power, 5% two-sided false-positive rate): **\(n\approx 969\)**. If \(n\) is fixed, invert the formula and decide whether the eval can see the effect you care about *before* paying for the run.

**A small-N calculation from his Bernoulli formula, not an empirical result.** At \(p=0.5\), \(n=25\): \(\mathrm{SE}=\sqrt{0.25/25}=0.10\), so a 95% interval is about \(\pm 0.20\). A single pass/fail run on 25 briefs cannot support a 5-point claim. Pairing and a pre-specified large effect are what make a personal lab informative; more repeats help the *per-task rate*, not the *across-task* mean, once \(K\) has beaten sampling noise.

**pass@k vs pass^k.** These answer different product questions.

- **pass@k** (Chen et al., Codex / HumanEval, arXiv:2107.03374, 7 July 2021, https://arxiv.org/abs/2107.03374): probability of at least one correct sample in \(k\) draws. It rises with \(k\). Codex solved 28.8% of HumanEval problems; 100 samples per problem solved 70.2%. The paper gives an **unbiased** estimator of pass@k (naive \(1-((n-c)/n)^k\) is biased). Equation number and algebraic form were **not re-derived from the PDF in this pass**; a secondary notebook restates it as \(1-\binom{n-c}{k}/\binom{n}{k}\) and attributes it to Chen et al. appendix A / eq. 1 (https://hassan11196.github.io/llm-systems-cookbook/notebooks/06_eval/03_humaneval_unbiased_pass_k.html). Treat the formula as secondary until checked against the PDF. Anthropic’s engineering post uses pass@k for “one success is enough” (best-of-n with a verifier) and cites the NeurIPS Codex line: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- **pass^k** (Yao, Shinn, Razavi, Narasimhan, \(\tau\)-bench, arXiv:2406.12045, 17 June 2024, https://arxiv.org/abs/2406.12045): probability that *all* \(k\) trials succeed. It falls with \(k\). Anthropic’s illustration: 75% per-trial success and \(k=3\) gives \(0.75^3\approx 42\%\). \(\tau\)-bench found even gpt-4o under 50% task success, and **pass^8 < 25% in retail**. That is the metric for a workflow a person would re-run and expect to work.

At \(k=1\) the two metrics match. By \(k=10\) they tell opposite stories. For a proposal pipeline, pass^k (or the per-task success rate, with its CI) is the reliability number. pass@k is only honest if the product is “generate several and a verifier or a human picks one”.

**Nondeterminism is part of the estimand, not a nuisance to delete.** Anthropic: each task has its own success rate; a pass on one run can fail on the next; sometimes the thing you want is the proportion of trials that succeed. Miller: resampling estimates that rate; changing temperature to hide it studies a different system. Isolate trials so infrastructure flakiness is not mistaken for agent variance (Anthropic, same post).

**Multiple comparisons and pre-registration.** Dror, Baumer, Shlomov, and Reichart surveyed ACL and TACL 2017 and found significance testing often ignored or misused, and that the right test depends on the metric and the dependence structure (“The Hitchhiker’s Guide to Testing Statistical Significance in Natural Language Processing”, ACL 2018, https://aclanthology.org/P18-1128/). Miller’s power section is the planning half of the same idea: pick \(\alpha\), power, and \(\delta\) before looking. This memo did **not** re-read a preregistration-methods paper; the operational rule below is the conjunction of Miller’s “decide MDE before you run” and Dror’s “do not treat an uncorrected significant slice as a result”. Looking at ten skill variants, three rubrics, and five slices, then reporting the winner, is a garden-of-forking-paths error. **UNVERIFIED** as a citation to Gelman & Loken specifically (not fetched); the statistical point is standard and is why Miller wants the hypothesis specified up front.

### So for us

The unit of analysis is the **task** (a brief, a repo ticket, a video job), not the trial and not the agent turn. Repeats estimate reliability; they do not multiply \(n\). Tasks that share a template, client, or skill family are a **cluster** — five variants of one brief are not five independent observations. Compare workflow versions with a **paired** difference and a CI. If the interval covers zero, the change did not win, regardless of the point estimate. Before a paid run, write down the primary metric and the smallest effect worth the money; with a few dozen tasks you can only see large effects (think “this skill moves pass^3 a lot”, not “+3 points on a 1–5 judge”). Do not turn temperature down, pin a seed, or drop retries just to make the chart look tight — that studies a different system than the one you will run. Use pass^k for “ship this workflow”; use pass@k only if a human or a verifier will actually pick among \(k\) artifacts. Pre-register the comparison. Extra slices are exploratory until replicated on held-out tasks.

---

## 3. Grading

### What the sources actually say

**LLM judges match humans only under conditions, and they have named biases.** Zheng et al. studied LLM-as-a-judge on MT-Bench and Chatbot Arena. They document **position bias, verbosity bias, self-enhancement bias, and limited reasoning**, and propose mitigations. Strong judges (GPT-4 in that paper) reached **over 80% agreement** with both controlled and crowdsourced human preferences, matching human–human agreement. Source: Lianmin Zheng et al., “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena”, arXiv:2306.05685, 9 June 2023, https://arxiv.org/abs/2306.05685

**Self-preference is not just “the judge likes good writing”.** Panickssery, Bowman, and Feng show GPT-4 and Llama 2 can distinguish their own outputs from other models’ and from humans’ at non-trivial accuracy, and that fine-tuning produces a **linear correlation between self-recognition and self-preference**. Humans in their setup rated the compared texts equal; the model still scored its own higher. Source: Arjun Panickssery, Samuel R. Bowman, Shi Feng, “LLM Evaluators Recognize and Favor Their Own Generations”, arXiv:2404.13076, 15 April 2024, https://arxiv.org/abs/2404.13076

**Rubric + chain-of-thought helps, and still prefers model text.** G-Eval uses CoT and a form-filling rubric rather than a single holistic score. With GPT-4 it reached Spearman **0.514** with humans on summarization, above prior automatic metrics, and the authors flag a bias toward LLM-generated text. Source: Yang Liu et al., “G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment”, arXiv:2303.16634, 29 March 2023, https://arxiv.org/abs/2303.16634

**Pairwise vs pointwise.** OpenAI’s guide: judges are more reliable at pairwise comparison, classification, or criteria scoring than at open-ended generation. They name position bias and verbosity bias, and recommend pairwise or pass/fail, length control, CoT before the score, the strongest judge you can afford, then human-agreement checks before you cheapen the judge. Reference-guided grading (a gold answer in the prompt) is a third mode. Source: https://developers.openai.com/api/docs/guides/evaluation-best-practices

Anthropic’s agent post adds: give the judge an **“Unknown”** escape so it does not hallucinate a grade; use a structured rubric; **grade each dimension with an isolated judge call** rather than one call scoring everything; calibrate closely against experts; once robust, human review can be occasional. Their research team’s later experience (one call, 0–1 plus pass/fail) is not a contradiction if the rubric is tight and the answer is checkable — it is evidence that judge *structure* has to be validated on your traces, not copied. Sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents and https://www.anthropic.com/engineering/multi-agent-research-system

**Binary outcome first, critiques as the few-shot fuel.** Husain’s judge guide argues that uncalibrated 1–5 dashboards are the failure mode: a 3 vs a 4 is not actionable, and those scales often do not correlate with what a domain expert actually cares about. His “critique shadowing” loop: one principal domain expert; a diverse set; **pass/fail plus a critique detailed enough to serve as a few-shot example**; only then an LLM judge. He is explicit that off-the-shelf framework metrics lead people astray. Source: Hamel Husain, “Using LLM-as-a-Judge For Evaluation: A Complete Guide”, 29 Oct 2024 (modified 1 Sept 2026), https://hamel.dev/blog/posts/llm-judge/index.html

**Agreement metrics.** Zheng’s headline is raw agreement (~80%, matching humans). Accuracy and Cohen’s kappa can look fine on an imbalanced pass/fail set (almost everything passes, the judge always says pass). Practitioner course material from the same evals lineage recommends a train/dev/test split of human labels and reporting **true positive rate and true negative rate**, with an iteration target of both ≥ 0.90. That 0.90 figure is **course guidance**, confirmed from the page description at https://www.aievals.co/learn/llm-as-judge/calibration-to-humans (published/modified 1 Oct 2026); the article body did not load in this pass, so do not treat 0.90 as a peer-reviewed threshold. Cohen’s kappa is still worth computing when both classes exist, because it corrects for chance agreement. **UNVERIFIED** here: specific Landis & Koch band cutoffs (not fetched). Report the confusion matrix; do not hide behind a single kappa.

**Correction (2026-10-19, review finding 16).** The previous paragraph is wrong about κ. If the judge always says pass, Cohen's κ is 0, not "fine": agreement beyond chance is zero. Accuracy is what looks fine in that case. κ's actual failure under imbalance is the opposite: low κ despite high raw agreement, so a rare-failure criterion can be dropped on κ even when raters mostly agree. M1 reports positive and negative agreement, or Gwet's AC1, alongside κ, and does not drop a criterion on κ alone. The wrong sentence is left in place so this note is the correction, not a silent rewrite.

**Preference aggregation (Bradley-Terry / Elo).** LMSYS moved Chatbot Arena from online Elo to a **Bradley-Terry** MLE because model strength is approximately static and they have the full comparison graph. Online Elo’s order-dependence and their earlier bootstrap CIs were misleading; BT bootstrap intervals were tighter and scaled with vote count. Ties counted as half a win. They still separate API versions because hosted models are not actually static. Source: Wei-Lin Chiang, Tim Li, Joseph E. Gonzalez, Ion Stoica, “Chatbot Arena: New models & Elo system update”, 7 Dec 2023, https://www.lmsys.org/blog/2023-12-07-leaderboard/ . The platform paper is Wei-Lin Chiang et al., arXiv:2403.04132, 7 March 2024, https://arxiv.org/abs/2403.04132 (pairwise crowdsourced votes; the abstract fetched here does not itself say “Bradley-Terry”; the blog does). Original model: Bradley & Terry, *Biometrika*, 1952, cited by LMSYS via https://www.jstor.org/stable/2334029

Elo/BT is the right aggregator when you have **many blinded pairwise votes** and a stable “player”. It is the wrong headline for 15 briefs × 2 workflow versions. There, the honest summary is the paired win rate and its CI.

**Deterministic graders where the world will check.** Anthropic’s grader table: string/regex, fail-to-pass and pass-to-pass tests, static analysis, outcome verification, tool-call checks, transcript constraints (turns, tokens). Strengths: fast, cheap, reproducible. Weakness: valid variation fails. Use them for “the PPTX opens and has the required slides”, “the cited number matches the source file”, “tests pass”, “the video file exists and is within duration”. Use a judge only for the residual judgment a script cannot make.

### So for us

Split every grade into (a) **checks a program can do** on the artifact and (b) **a short list of binary assertions** a human would make (“every quantitative claim has a source in the brief pack”, “the deck does not invent a customer logo”). Do not start with a 1–5 “quality” score. Write critiques on the first human passes and fails; those critiques become the judge prompt’s few-shots. Calibrate the judge on a **held-out** labeled slice and publish TPR and TNR (and the confusion counts), not accuracy. Swap order on every pairwise judge call. Control for length so a longer deck does not win by verbosity. Do not let the generating model family be the only judge — Panickssery’s result is exactly our setup if OMP’s model grades OMP’s deck. A different family, or a human spot-check each experiment, is the mitigation. Use pairwise (“version B’s deck vs version A’s, same brief, blinded”) when the question is which workflow to keep. Use pointwise checklists when the question is whether this artifact meets the bar. Do not compute an Elo until you have a real comparison graph; until then, paired case outcomes are the result.

---

## 4. Dataset hygiene

### What the sources actually say

**Held-out data and distribution match.** OpenAI’s guide: the eval set should reproduce the real task distribution, including edge and adversarial cases, and their worked example scores a **held-out** transcript set. A dataset that only contains the briefs you tuned on will not tell you if the skill generalized. Source: https://developers.openai.com/api/docs/guides/evaluation-best-practices

**Goodhart: four different ways a metric rots.** Manheim and Garrabrant argue “Goodhart’s law” is at least four mechanisms (regressional, extremal, causal, adversarial), and that the damage scales with optimization pressure — which is why it is acute once you point a strong optimizer at a proxy. Source: David Manheim and Scott Garrabrant, “Categorizing Variants of Goodhart’s Law”, arXiv:1803.04585, 13 March 2018, https://arxiv.org/abs/1803.04585 . For this lab the relevant modes are: hill-climbing a judge until it no longer matches the human (extremal/causal), and an agent exploiting a grader loophole (adversarial). Anthropic’s Opus 4.5 \(\tau\)2-bench flight-booking loophole is the second kind: the agent failed the eval as written and still did better for the user. That is a **grader bug**, and also a warning that a clever workflow will find the check you forgot. Source: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

**Contamination is measurable, and public benchmarks leak.** Zhang et al. built GSM1k to mirror GSM8k (matched on human solve rate, solution length, answer magnitude, and more). Leading models dropped **up to 8%**; several families overfit across sizes; a model’s probability of emitting a GSM8k example correlated with its GSM8k–GSM1k gap (Spearman \(r^{2}=0.36\)). Frontier models in that study showed less overfitting, and all models still generalized to novel problems. Source: Hugh Zhang et al., “A Careful Examination of Large Language Model Performance on Grade School Arithmetic”, arXiv:2405.00332, 1 May 2024, https://arxiv.org/abs/2405.00332

LiveCodeBench’s response to the same problem is **time-based collection**: new contest problems after training cutoffs, plus tasks beyond generation (self-repair, execution, test-output prediction). Source: Naman Jain et al., “LiveCodeBench”, arXiv:2403.07974, 12 March 2024, https://arxiv.org/abs/2403.07974

**SWE-bench Verified is the cautionary dataset-hygiene case for agent evals.** Two OpenAI writeups, read together:

Creation (13 Aug 2024, updated 24 Feb 2025), https://openai.com/index/introducing-swe-bench-verified :

- Original SWE-bench graded patches with hidden `FAIL_TO_PASS` and `PASS_TO_PASS` tests. Problems: overly specific or unrelated tests, underspecified issues, flaky environments.
- 93 Python developers annotated 1,699 random test samples, 3 independent annotators each, labels 0–3, ensemble = **max severity** (conservative; they accept a higher false-removal rate).
- **38.3%** flagged underspecified problem statements; **61.1%** flagged unit tests that could reject valid solutions; **68.3%** removed for those or other major issues.
- Verified = **500** samples. Difficulty labels: 196 estimated <15 minutes, 45 estimated >1 hour. Most original items were <1 hour (77.8% of the 1,699).
- Dockerized harness to stop environment luck from failing valid patches.
- GPT-4o on the best open scaffold they tried: **33.2%**, more than double its 16% on original SWE-bench. The original benchmark was *underestimating* capability because tasks were unfair — the opposite error from contamination.

Retirement, “Why SWE-bench Verified no longer measures frontier coding capabilities”, https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/ (**publication date UNVERIFIED** in the extract; fetched 2026-10-19):

- After early gains, reported progress slowed from **74.9% to 80.9%** in the six months before that post. They ask whether remaining failures are model limits or dataset defects.
- Audit of **138** problems that o3 did not consistently solve in 64 runs, each reviewed by at least six engineers, re-verified if flagged. **59.4%** had material test or spec issues: **35.5%** narrow tests (implementation details not in the issue, e.g. a required function name), **18.8%** wide tests (tests cover issues the statement never stated), **5.1%** miscellaneous.
- Contamination: frontier models they probed could reproduce gold patches or verbatim problem specifics. Models that had seen the problems were more likely to succeed *because the leaked details were exactly what the underspecified tests required*.
- They stopped reporting Verified and recommend **SWE-bench Pro** (public split; their pipeline still found some contamination, but rarer, and no model produced a complete verbatim gold patch in that check). Longer-term recommendation: privately authored tasks (they cite GDPVal) and canary strings plus careful release hygiene. Public crawl + public solutions is a leaking bucket.

Anthropic’s saturation note (Verified from ~30% to >80%, one-shot evals missing long-task gains) is the same phenomenon from the product side: a high score on a public set stops being a capability signal. Source: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

**Version the eval, not just the agent.** EvalGen’s criteria drift means a rubric edit *is* an intervention. Anthropic: suites are living artifacts and need an owner; product people closest to the user should add tasks. A score is only comparable across runs if task set, grader version, harness, and model snapshot are pinned. Changing the rubric and claiming the workflow improved is not a result.

**Regression vs capability.** Repeated because it is a dataset decision, not just a process one. Capability set: hard, low pass rate, the hill. Regression set: previously solved, near 100%, run on every skill/model change. When capability items saturate, move them to regression and add harder items (longer horizon, stricter grounding, new modality). A suite at 100% only detects backsliding. Sources: Anthropic demystifying evals; OpenAI Verified retirement (saturation + contamination together).

### So for us

Keep three file-versioned sets, and never tune on all three:

1. **Dev / error-analysis set** — the traces you open-code. Skills and rubrics may see these.
2. **Regression set** — briefs the current workflow already completes. Run on every skill or model change. A drop is a backslide, not a research finding.
3. **Sealed capability set** — briefs and rubrics not used to edit prompts. This is the only set that can support “we got better”.

Version `tasks/`, `rubrics/`, and `graders/` the way you version skills. A result line without those hashes is not reproducible. Prefer **private briefs and private reference artifacts**. Public prompt packs and public “golden decks” will enter training data; GSM1k and SWE-bench are the existence proof. If you ever publish a suite, use a canary string and do not publish the gold artifact next to the task (OpenAI’s own lesson). When pass rates on the capability set get high, add harder tasks (multi-stakeholder briefs, conflicting sources, longer video jobs) instead of celebrating the average. Periodically re-grade a sample yourself: if your pass/fail and the judge’s diverge, the judge has become the Goodhart target. When an agent “fails” by producing a better artifact than the rubric allows, fix the rubric — and record the loophole so the next grader cannot be gamed the same way.

---

## 5. Agent and long-horizon practice

### What the sources actually say

**Outcome vs trajectory.** The consistent recommendation across agent benchmarks is: score the **end state**, use the trajectory for diagnosis.

- \(\tau\)-bench compares the **database state** at the end of a user–agent conversation to an annotated goal state, and separately measures reliability with pass^k. The user is itself a model, so the conversation is stochastic; the end state is the contract. https://arxiv.org/abs/2406.12045
- SWE-bench / Verified: the agent sees the issue and the repo, not the tests. A patch passes only if fail-to-pass tests pass **and** pass-to-pass tests still pass. The harness, not the trace, is the judge. Unfair tests and underspecification dominated the original set (68.3% removed). https://openai.com/index/introducing-swe-bench-verified
- WebArena grades browser tasks by URL, page state, and **backend state** (an order counts only if it exists, not if a confirmation page was shown). Best GPT-4 agent in the paper: **14.41%** end-to-end vs human **78.24%**. Those rates are 2023 baselines, not current capability. Shuyan Zhou et al., arXiv:2307.13854, 25 July 2023, https://arxiv.org/abs/2307.13854
- OSWorld: 369 real computer tasks, each with an initial-state setup and a **custom execution-based evaluation script** over files, app state, and UI properties. Humans **>72.36%**, best model in the paper **12.24%**, failures dominated by GUI grounding and operational knowledge. Again, a 2024 baseline; the method is the point. Tianbao Xie et al., arXiv:2404.07972, 11 April 2024, https://arxiv.org/abs/2404.07972
- Anthropic: grade the outcome; trajectory graders for prescribed tool order are brittle; partial credit for multi-component tasks; checkpoints rather than every turn for state-mutating workflows. Research agents are the awkward case: experts disagree, ground truth moves, and long outputs have more room to be wrong. Their pattern — groundedness, coverage of required facts, source quality, exact match only when a fact is objective — is the right pattern for a proposal. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents and the multi-agent post’s appendix on end-state evaluation.

**Process labels are for learning and debugging, not for the headline score.** Lightman et al. found process supervision (feedback on each reasoning step) beat outcome supervision for training a MATH reward model; their process-supervised model solved **78%** of a representative MATH subset, and they released PRM800K (800k step labels). Source: Hunter Lightman et al., “Let’s Verify Step by Step”, arXiv:2305.20050, 31 May 2023, https://arxiv.org/abs/2305.20050 . Use step-level notes to find where a workflow goes wrong (the open-coding “first failure”). Do not require the agent to take those steps. Anthropic’s CORE-Bench and METR threshold bugs are what happens when process-shaped graders punish a valid outcome.

**Long-horizon metric: human time at a fixed success probability.** METR, “Measuring AI Ability to Complete Long Software Tasks”, 19 March 2025, https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/ and arXiv:2503.14499, https://arxiv.org/abs/2503.14499 . Method:

- Collect multi-step tasks and the time skilled humans take.
- Human time strongly predicted model success in that suite: near 100% under about 4 minutes, under 10% beyond about 4 hours (era of that post; Claude 3.7 Sonnet’s fitted 50% horizon was about one hour).
- Fit a logistic of success vs human duration. The **50%-task-completion time horizon** is where the curve crosses 50%. They also report 80%.
- Uncertainty: hierarchical bootstrap over task families, tasks, and attempts.
- The 6-year trend in the original post was roughly exponential, doubling about every **7 months**. The blog now warns that **static figures and the doubling time are out of date**, points to Time Horizon 1.1 (https://metr.org/blog/2026-01-29-time-horizon-1-1/) and https://metr.org/time-horizons/ , and says they are no longer updating TH1.1 with new models. Use the **method**, not the 7-month forecast.
- External validity is the dominant uncertainty. A 10× error in the absolute horizon only shifts an exponential arrival forecast by about 2 years — useful for forecasting, not a reason to treat our own tiny suite as a forecast.
- Replication on SWE-bench Verified with estimated (not timed) human durations showed a faster doubling (<3 months). They suspect the estimate excluded codebase familiarization, which inflates the slope. **How you define “human time” changes the metric.** For us, human time should include gathering context, not just the final edit.

Why this beats pass rate: a suite with a narrow difficulty band saturates or looks flat while real capability (length of job you can hand off) is moving. Anthropic’s Qodo anecdote is the product version of the same point.

**Cost and latency are metrics, not logs.** HELM’s multi-metric design measured accuracy, calibration, robustness, fairness, bias, toxicity, **and efficiency** on the same scenarios so tradeoffs could not be dropped. Percy Liang et al., “Holistic Evaluation of Language Models”, arXiv:2211.09110, 16 Nov 2022, https://arxiv.org/abs/2211.09110 . Anthropic’s agent-eval examples track turns, tool calls, total tokens, time to first token, output tokens/sec, and time to last token, and say that once a suite exists you get latency, token usage, and cost per task “for free” on a static bank. The multi-agent research post quantifies the bill: agents used about **4×** the tokens of chat; multi-agent about **15×**. On BrowseComp, **token use explained 80%** of performance variance, and token use + tool-call count + model choice explained **95%**. Upgrading Sonnet 3.7 → Sonnet 4 beat doubling the token budget. A tool-description rewrite cut later task time **40%**; parallel tool calls cut research time up to **90%**. Multi-agent is only worth it when the task value covers the tokens, and it fits breadth-first work better than tightly dependent coding. https://www.anthropic.com/engineering/multi-agent-research-system

**Harness = part of the system under test.** Anthropic: evaluating “an agent” means model + scaffold. SWE-bench’s Docker harness exists because environment setup was failing valid solutions. Trial isolation is a validity condition (git history leak; shared CPU exhaustion correlating failures). A 0% score after many trials is a spec/grader/harness bug until proven otherwise.

### So for us

Three deliverable types, one grading pattern:

| Workflow | Headline grade | Diagnostic only |
| --- | --- | --- |
| Proposal / PPTX | Files exist, open, required sections present, numbers match the source pack, citations resolve. Binary rubric for the rest, human-calibrated. | Which skill fired, how many revisions, where the first ungrounded claim appeared. |
| Software factory | Clean repo state, fail-to-pass and pass-to-pass checks, lint/type on the diff. Hidden tests. No credit for matching a prescribed edit sequence. | Trajectory, tool errors, retries. |
| Video (later) | Execution script over artifacts: files, durations, captions, shot list coverage. Same idea as OSWorld’s per-task script. | Click/tool path. GUI or editor steps will be gamed and will punish valid paths. |

Pin the harness in the result: OMP version, model id, skill hashes, temperature, retry policy, trial isolation (fresh workspace, no leftover files). Compare versions on the same tasks. Record **dollars, tokens, wall time, and turns per successful artifact** next to pass^k. A workflow that wins on quality and costs 15× is a different decision; Anthropic’s BrowseComp analysis says a lot of “agent quality” is just spending more tokens. For long-horizon progress, tag each task with how long a skilled human takes *including context gathering*, and report the human-time at which pass^1 or pass^3 crosses 50% and 80%. Do not publish a doubling-time forecast from a personal set. When the short briefs all pass, add longer ones; do not squeeze more signal out of a saturated 10-minute suite.

---

## 6. Tooling landscape

### What exists, and the lock-in

| Tool | What it is | Reuse | Lock-in / mismatch |
| --- | --- | --- | --- |
| **Inspect AI** (UK AI Security Institute / Meridian) | Open-source Python framework: Task = dataset + solver/agent + scorer. 200+ built-in evals. Log viewer, VS Code extension, Docker/K8s/Modal sandboxes, bash/python/editor/browser tools, multi-agent primitives, and bridges to **external** agents (Claude Code, Codex CLI, Gemini CLI are named). Local `inspect eval` / `inspect view`. | The best scientific harness if we want real scorers, trial logs, and Miller-correct standard errors. Miller explicitly says Inspect’s `stderr()` implements \(\mathrm{SE}_{\mathrm{C.L.T.}}\) correctly (arXiv:2411.00640). External-agent support matches “OMP is a CLI, not a library”. | Python task format and Inspect log schema. Acceptable if logs stay local and our *contract* (task markdown, rubric, score table) is still plain files. Do not make Inspect the only place results live. Docs: https://inspect.aisi.org.uk/ . Citation: UK AI Security Institute, Inspect AI, May 2024, https://github.com/UKGovernmentBEIS/inspect_ai |
| **promptfoo** | Open-source CLI/library. Declarative YAML cases, many providers, assertions, caching, CI, local-only by default. Red-team features exist; we do not need them for this lab. | Skill and prompt **regression**: “this markdown skill, these briefs, these assertions”, run in CI without a server. Language-agnostic. Fits “files + CLI”. | Weak for multi-hour, multi-agent, environment-state trials (PPTX build, repo sandbox, video render). Easy to slide into generic LLM metrics, which Husain warns against. Docs: https://www.promptfoo.dev/docs/intro/ . Assertions: https://www.promptfoo.dev/docs/configuration/expected-outputs/ . Code: https://github.com/promptfoo/promptfoo |
| **Harbor** | Anthropic’s 2026 agent-eval appendix describes it as the containerized trial runner, with a registry that includes Terminal-Bench 2.0 and a standard task/grader format. | Pattern to copy if software-factory trials need hermetic containers: task spec, clean environment, grader, artifacts out. | Not independently audited here. Treat capabilities beyond Anthropic’s paragraph as **UNVERIFIED**. Mentioned at https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (they link https://harborframework.com/). |
| **Braintrust** | Commercial platform: offline evals + production traces + experiments. `autoevals` scorers (factuality, relevance, …). An experiment is a hosted record of inputs, outputs, scores. | Experiment-comparison UI if we ever want it. Anthropic lists it as one option, not a requirement. | SaaS system of record, SDK-shaped traces, prebuilt scorers that are exactly the generic metrics to avoid until calibrated. Poor fit for “survive OMP upgrades” and for artifacts that must stay on disk (decks, repos, video). Docs: https://www.braintrust.dev/docs/evaluate |
| **LangSmith** | Tracing, datasets, offline/online evals, tight LangChain coupling. https://docs.langchain.com/langsmith/evaluation | Nothing we need if we are not on LangChain. | LangChain/LangSmith trace schema. Parsing OMP into LangSmith spans would couple us to two unstable internals. |
| **Langfuse / Arize Phoenix** | Anthropic lists Langfuse as a self-hosted open-source trace/eval alternative and Phoenix as open-source tracing plus evals. | Self-hosting avoids one vendor. Still a trace-platform schema. | Same mismatch: our stable interface is files from CLI print mode, not an OTEL span tree from OMP. Cited only via Anthropic’s appendix: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents |
| **OpenAI Evals API / platform** | The design guide remains useful. The platform does not. | None as a dependency. | Official page: read-only 31 Oct 2026, shutdown 30 Nov 2026. https://developers.openai.com/api/docs/guides/evaluation-best-practices |

Anthropic’s own closer: frameworks accelerate and standardize, and they are only as good as the tasks you run; many teams use scripts; pick something that fits, then spend the effort on tasks and graders. That matches a personal lab.

### So for us

**System of record: a directory of files**, not a vendor project.

- `tasks/<id>/brief.md` plus inputs (source pack, repo fixture, shot list).
- `rubrics/<id>@<version>.md` — binary checks, which are code vs judge, reference artifact pointer.
- `runs/<experiment>/<task>/<trial>/` — OMP print-mode transcript, stdout/stderr, produced files, token/cost/time sidecar JSON written by *our* wrapper.
- `scores/<experiment>.jsonl` — one row per trial: task id, rubric version, skill hashes, model id, OMP version, pass/fail per check, cost, latency.
- A small script for paired diffs, clustered SEs, and pass^k. Inspect’s `stderr()` is the thing to copy if we do not adopt Inspect itself.

Use **promptfoo** only for fast skill-level regression (a skill file, a few briefs, deterministic assertions) where a full workflow run is wasteful. Use **Inspect** if we want sandboxes and external-agent trials without writing a harness — call OMP as an external agent, export Inspect logs *into* the directory above, and do not let the Inspect log become the only copy. Do not adopt Braintrust, LangSmith, or the OpenAI Evals API as the place results live. Tern is the human inspection surface for traces and artifacts; it is not the grader and it should not be required to compute a score. Do not scrape OMP’s internal event stream. If print mode lacks a field (cost, tool list), record it at the wrapper boundary.

---

## 10 methodological rules for this lab

These are operating rules, not aspirations. Each is implementable with files and a calculator.

1. **Error-analysis before metrics.** No aggregate score until a human has open-coded at least ~30 real traces and axial-coded a failure taxonomy. Generic “helpfulness / coherence” metrics are out until a taxonomy bin requires them. (Husain & Shankar; Anthropic’s “read the transcripts”.)

2. **Version the rubric with the run.** Criteria drift is normal. A result is (task set hash, rubric version, grader version, skill hashes, model id, OMP version). Editing the rubric after seeing scores invalidates the comparison. (EvalGen; Anthropic suite ownership.)

3. **Two suites, different jobs.** Capability set starts hard and stays hard. Regression set is previously solved work and should stay near-perfect. Saturated capability tasks graduate; they are not deleted and not used to claim new headroom. (Anthropic demystifying evals; SWE-bench saturation.)

4. **Grade artifacts and state, not the prescribed path.** Headline pass/fail comes from files and environment checks (deck opens, numbers match sources, tests pass, video script passes). Trajectory tags explain the first failure. They do not decide the winner. A valid artifact that fails a brittle check is a grader bug. (Anthropic; \(\tau\)-bench; SWE-bench; OSWorld; WebArena.)

5. **Paired comparisons only, with an interval, clustered by family.** Same tasks, both versions, difference and 95% CI. Tasks that share a template or brief family are one cluster. A CI that covers zero is a tie. Do not rank on unpaired headline percentages. (Miller 2024.)

6. **Pre-register the decision.** Before the paid run, write the primary metric (usually pass^k or paired pass-rate difference), the minimum effect that would change a skill decision, \(K\), and what you will *not* claim. Other slices are exploratory. With a few dozen tasks you can only detect large effects; do not narrate a 3-point move. (Miller power formula; Dror et al. on misused significance tests.)

7. **pass^k for shipping, pass@k only with a real picker.** If the user would re-run the workflow and expect a good deck, report reliability (all \(k\) trials, or the per-task rate). pass@k is allowed only when a human or a verifier actually selects among \(k\) artifacts. State \(k\). Do not lower temperature to manufacture stability. (Chen et al.; \(\tau\)-bench; Anthropic; Miller §3.3.)

8. **No judge in the score until it is calibrated, and not the generator’s twin.** Human pass/fail plus critiques on a labeled slice; judge prompt frozen; **held-out** TPR and TNR reported (accuracy alone is not enough). Swap positions on pairwise calls. Control length. Prefer a different model family than the one that produced the artifact, or a human audit each experiment. Unknown is an allowed judge output. (Zheng et al.; Panickssery et al.; Husain; OpenAI guide; Anthropic.)

9. **Sealed held-out set. Private tasks for any claim you would repeat.** Dev traces may tune skills. The sealed set may not. Do not treat a public benchmark score as evidence about this workflow; public suites contaminate and go stale (GSM1k, LiveCodeBench, SWE-bench Verified’s retirement). If a suite is ever published, canary it and do not ship gold artifacts beside the tasks.

10. **Cost, latency, tokens, and turns are columns in the score table, and every surprising trial is read.** A quality win that multiplies tokens by an order of magnitude is a different result (Anthropic: multi-agent ~15× chat; BrowseComp variance mostly tokens). Before changing a skill because of a number, read the failing and the unexpectedly passing transcripts. A stubborn 0% after many trials is a broken task until the spec, the grader, and the harness have been checked. (HELM efficiency; Anthropic; METR’s “don’t trust the curve until the tasks are audited”.)

---

## Claims not verified in this pass

- Exact Chen et al. equation number and algebra for the unbiased pass@k estimator (secondary restatement only).
- Landis & Koch numeric kappa bands.
- Gelman & Loken “garden of forking paths” as a fetched source (the multiple-comparisons rule does not depend on that citation).
- Publication date of OpenAI’s SWE-bench Verified retirement post.
- Harbor’s implementation beyond Anthropic’s paragraph.
- Full body of https://www.aievals.co/learn/llm-as-judge/calibration-to-humans (0.90 TPR/TNR target is from the page description; course guidance, not a paper).
- METR’s current numerical horizons (the March 2025 doubling time is explicitly stale on their own page).
- Strauss & Corbin / Glaser & Strauss as primary sources for open and axial coding (operational definition taken from Husain & Shankar).
- GDPVal’s task-construction details (named by OpenAI; page not fetched).
