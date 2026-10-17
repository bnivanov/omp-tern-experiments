# OMP / Tern experiments

Portable delivery guidance for OMP, with optional Tern boards and visible interactive sessions.

This is a **Markdown rule and skill package**, not an executable plugin. It contains no extension code, installer, credentials, provider configuration, personal workspace records, or machine-specific paths. Do not use `omp plugin install` or `tern plugin install` for this package.

## What it does

- Loads a concise always-on delivery rule.
- Provides the `delivery-best-practice` skill for substantive delivery, multi-session resume, and explicitly requested boards.
- Keeps one coordinator responsible for shared records, with bounded worker assignments and reviewed integration.
- Includes a board reference and five empty record templates. Records and boards are optional; small tasks need no scaffolding.
- Describes separate interactive OMP conversations in visible Tern tabs when requested and authorized.

It does **not** automatically launch backlog work, schedule agents, collect live session status, or synchronize task queues. Tern displays recorded board state; session todos remain transient execution steps.

## Prerequisites and compatibility

- An installed OMP runtime that supports native rules and skills.
- Tern for board viewing and the visible-tab workflow; the guidance itself can be used without Tern.
- Git for checkout/worktree workflows. Delegated task isolation additionally needs a committed `HEAD` and a runtime schema exposing that capability.

The files are plain Markdown and require no build, package manager, or platform-specific executable. Native discovery and CLI capabilities depend on the installed runtime. Check `omp --help` and `tern --help` rather than assuming commands or isolation fields are identical across versions.

Observed runtime verification: OMP 18.11.3 and Tern 0.9.2 on macOS. This is not a claim that every OMP/Tern version or operating system has been tested. The same resource layout can be copied on other supported systems; verify discovery on the destination machine.

Follow your organization's software, account-access, and data-handling policies. This package does not bypass corporate controls or supply the OMP/Tern applications.

## Download

Use this repository's **Code → Download ZIP**, then extract it, or clone it using your approved Git client. A private repository requires an account with access. No history from the originating workspace is included.

`SHA256SUMS` lists the eight installable resources. From the extracted repository root, macOS can check it with `shasum -a 256 -c SHA256SUMS`; Linux can use `sha256sum -c SHA256SUMS`. On Windows, compare `Get-FileHash -Algorithm SHA256 <file>` with the corresponding entry. Checksums detect changed files; they are not a publisher signature.

The repository's `.gitattributes` preserves LF line endings on checkout, including with Windows Git's `core.autocrlf=true`, so the resource checksums remain stable.

## Install without changing runtime settings

1. **Choose the intended OMP agent directory.** Run `omp config path` with the same profile/override used to start OMP; for a named profile, use `omp --profile <name> config path`. The default installation commonly uses `.omp/agent` under your home directory, but profiles and `PI_CODING_AGENT_DIR` can change the selection. Call the reported directory `<agent-dir>` below. Do not assume that editing this repository installs anything.
2. **Check for existing copies.** If either destination below already exists, stop and review it. Preserve a backup outside this repository and deliberately reconcile or replace only those owned resources; do not blindly overwrite or merge an old skill directory.
3. Using your file manager or approved copy tool, create the destination `rules` and `skills` directories if absent, then copy:

   | From the extracted repository | Destination |
   |---|---|
   | `rules/delivery-best-practice.md` | `<agent-dir>/rules/delivery-best-practice.md` |
   | The complete `skills/delivery-best-practice/` directory | `<agent-dir>/skills/delivery-best-practice/` |

   Preserve the skill's `references` and `templates` subdirectories. The rule filename identifies the rule; do not rename it.
4. Start a **fresh OMP session** using that same profile/override. Existing sessions alone do not prove activation.

Installation copies only these resources. It does not require changing models, authentication, isolation settings, profile settings, or global task behavior. Do not copy the templates into a project until a session actually needs those records, and never overwrite an existing tracker.

## Verify on the destination machine

Check application availability:

```text
omp --version
tern --version
```

Using the intended OMP profile/override, inspect the installed resources:

```text
omp read "<agent-dir>/rules/delivery-best-practice.md"
omp read skill://delivery-best-practice
```

Replace `<agent-dir>` with the directory chosen above. Compare all eight installed files with the download's checksums. The `omp read` commands prove readability, not full activation: also verify in a fresh native session that the rule is active and the skill is discovered. Confirm that the resolved skill is this installed copy; a same-name project or other skill source may take precedence. When skill commands are enabled, `/skill:delivery-best-practice` explicitly loads the skill. Discovery failure means the installation directory, active profile, name collision, or runtime capabilities need checking—not that settings should be changed blindly.

For an optional global-scope check, start another fresh session outside the download/project. A fresh session with `--no-rules` is a negative control for rule injection, not a skill uninstall. Some standalone OMP versions cannot resolve `rule://` URIs; the explicit rule-file read above avoids that dependency.

## Use with Tern

Adopt a board deliberately at the relevant project root; do not create a second authority beside an existing tracker. The skill includes board ownership and handoff rules, scoped project conventions, and isolation/integration guidance.

For concurrent visible work, select only authorized ready items, assign one coordinator, and give each writing session a separate checkout and bounded assignment. Consult the installed Tern CLI help for the target window/session and tab commands. A Tern tab is not checkout isolation, and a quiet tab is not completion evidence. Review worker artifacts and smoke the integrated result before accepting work.

## Package contents

- `rules/delivery-best-practice.md`
- `skills/delivery-best-practice/SKILL.md`
- `skills/delivery-best-practice/references/board.md`
- `skills/delivery-best-practice/templates/`: `TODO.md`, `PLAN.md`, `DECISIONS.md`, `HANDOFF.md`, `BACKLOG.md`
- `SHA256SUMS`

The repository intentionally excludes personal records, local installation history, runtime settings, session logs, and credentials. Before publishing future changes, review both content and commit author/committer metadata for private information.
