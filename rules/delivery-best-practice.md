---
description: Global delivery principles for every agent. Main loads the delivery skill only for substantive, multi-session, or explicit board work.
alwaysApply: true
---

# Delivery principles

Native system and tool instructions win. Project instructions refine inside those constraints. An omitted agent filter is intentional: these principles apply to every agent, including subagents. An ordinary answer, lookup, or small edit needs no skill, board, or workflow scaffolding. A file the user asked for is still created.

## Size

- Quick: answer, look something up, or make one small change, including a file the user asked for. No skill and no workflow scaffolding.
- Substantive: multi-step or multi-file delivery, a material tradeoff, work another session must resume, or explicit board use.

## Who owns what

- The coordinating main owns shared plans/records, integration, and full verification. A top-level session explicitly assigned as an execution worker owns only its bounded slice/checkout, reports to that coordinator, and does not edit shared plans, boards, or the coordinator's handoff—even copied versions. Main loads the whole skill only for substantive, multi-session, or explicit board work; workers follow their brief and named guidance sections.
- Related projects may share one Git root and still keep separate scoped records. Do not fold their plans into that root plan. A folder is not Git, checkout, or runtime isolation. If fit is poor, recommend a sibling repository; do not create, move, split, or nest one unless this conversation authorizes that exact action.
- A subagent follows its brief and path boundaries and reports evidence. It does not load the whole skill to set up or interview, and it does not create a competing plan, board, or other shared delivery state.
- A child may read a named section when the brief names that section. Do not tell every agent to create or update project delivery files.

## How to work

- You may implement. Delegate independent substantial work when that split is safer. Finish the work you keep.
- Do not invent model, cost, token, turn, or read limits. Do not change runtime config, model roles, or isolation knobs unless the user explicitly requests that change. Preserve every unrelated knob.
- Prefer a sensible default. Ask only when a material tradeoff remains uncertain after the request, the repo, and the brief. A clear request authorizes routine reversible work. Explicit approval is for a material scope change, an irreversible action, or an unresolved tradeoff. Main keeps going through approvals already given and does not stop after every wave. Subagents do not interview the user.
- Tag an inference as an inference. Do not promote it to a user decision.
- Accept work only with evidence: the check, the actual path, and the result. A status label, card move, or GUI edit is not acceptance. Smoke the path that will actually be used. Main verifies the integrated result. One passing slice does not prove the whole.
- For a substantive write in an eligible git repo with a valid committed `HEAD`, prefer an isolated checkout when the live task schema offers it, unless the brief assigns a shared-tree write. A repository without a committed `HEAD` fails patch capture on the verified runtime; do not set isolation then. Dirty or untracked files do not by themselves make a committed repository ineligible. An initial local commit needs explicit authorization. Git init is not a commit. Isolation is checkout separation, not a process, network, or auth sandbox. Captured changes are not landed until main reviews the returned patch or branch artifact and integrates it. Read-only work stays shared. Do not set isolation when the field is absent or the tree is ineligible.
- Review in proportion to risk. After a serious fix, recheck that fix against the finding. Do not add unsolicited scope.
- Redact secrets in files, handoffs, and replies. Do not commit, push, archive, rotate, or delete records, and do not take other destructive actions, unless this conversation authorizes that exact action.
- Durable records and handoff are proportional. Main creates them only when tracking or a later session needs them, never by taking over an unowned tracker. Keep one durable task authority; session todos are transient steps, not a mirrored board/backlog. Tern rendering `TODO.md` is not another task store.
- Do not imitate or copy native `/init`, and do not invent a bootstrap command. When the user explicitly asks, run the real native `/init`. Preserve existing `AGENTS.md` and other user guidance unless they asked to update it.

## Conflicts

- A system or tool rule beats this file. A project instruction refines a preference here; it does not waive a safety or tool rule.
- If this file and the skill disagree on whether the skill applies, follow this file. The skill covers how main runs substantive delivery.
