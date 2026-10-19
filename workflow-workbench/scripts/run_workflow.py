#!/usr/bin/env python3
"""Run a saved sequential workflow through the OMP or Claude Code CLI.

Canonical representation: the workflow manifest and its prompt files. This
script is the only interpreter. It does not generate workflow code or wrap a
native workflow engine.

validate  Check the manifest and print stage order. No model call and no files.
plan      Check the manifest and brief, resolve the selected CLI, and print
          stage order, handoffs, argv, hashes, and provenance gaps. The full
          prompt is not printed. No model call and no files.
run       Explicit cost authorization. POSIX only; SIGKILL cannot be handled.
          Launch the selected CLI once per stage.
          Write only to a new output directory outside the repository and project.

CLI completion is not business acceptance. Semantic quality is not verified.
Flags are requested configuration, not observed effective configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 1_048_576
MAX_PROMPT_BYTES = 8_000_000
VERSION_TIMEOUT_SECONDS = 30
KILL_WAIT_SECONDS = 5
TERM_GRACE_SECONDS = 1
FLUSH_BACKSTOP_SECONDS = 15
CLAUDE_MCP_BYTES = b'{"mcpServers":{}}\n'

MARKER_BRIEF = "<<<WORKFLOW_BRIEF_JSON>>>"
MARKER_BRIEF_END = "<<<END_WORKFLOW_BRIEF_JSON>>>"
MARKER_PRIOR = "<<<PRIOR_STAGE_OUTPUTS>>>"
MARKER_PRIOR_END = "<<<END_PRIOR_STAGE>>>"
MARKER_END = "<<<END_OF_INPUT>>>"
MARKERS = (
    MARKER_BRIEF,
    MARKER_BRIEF_END,
    MARKER_PRIOR,
    MARKER_PRIOR_END,
    MARKER_END,
)

ID_RE = re.compile(r"^[a-z](?:[a-z0-9]|-(?=[a-z0-9])){0,62}$")
SOURCE_ID_RE = re.compile(r"^SRC-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
SUCCESS_STOPS = (None, "end_turn", "stop")
THINKING_TYPES = {"thinking", "redactedThinking"}
OMP_LIFECYCLE_EVENTS = frozenset(
    {
        "session",
        "agent_start",
        "turn_start",
        "message_start",
        "message_update",
        "message_end",
        "turn_end",
        "agent_end",
    }
)
OMP_MESSAGE_ROLES = frozenset({"user", "assistant"})
TOOL_CONTENT_TYPES = frozenset({"toolCall", "tool_use", "tool_result", "toolResult"})


class ValidationError(Exception):
    pass


class PreflightError(Exception):
    pass


class DuplicateKeyError(ValueError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run{stamp}{secrets.token_hex(3)}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def project_root() -> Path:
    script = Path(__file__).resolve()
    root = script.parent.parent
    if script.parent.name != "scripts" or script.name != "run_workflow.py":
        raise PreflightError(
            "runner must stay at projects/workflow-workbench/scripts/run_workflow.py"
        )
    return root


def script_path() -> Path:
    return Path(__file__).resolve()


def reject_constant(value: str) -> None:
    raise json.JSONDecodeError("nonstandard number", value, 0)


def load_json_text(text: str, label: str) -> object:
    duplicates: list[str] = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        seen: set[str] = set()
        for key, _value in pairs:
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        if duplicates:
            raise DuplicateKeyError(f"{label} has duplicate keys: {', '.join(duplicates)}")
        return dict(pairs)

    try:
        return json.loads(text, object_pairs_hook=hook, parse_constant=reject_constant)
    except DuplicateKeyError:
        raise
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} is not valid JSON: {exc.msg}") from exc


def load_json_bytes(data: bytes, label: str) -> object:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{label} is not UTF-8") from exc
    return load_json_text(text, label)


def parse_native_json(text: str) -> object:
    duplicates: list[str] = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        seen: set[str] = set()
        for key, _value in pairs:
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        if duplicates:
            raise DuplicateKeyError("duplicate keys")
        return dict(pairs)

    return json.loads(text, object_pairs_hook=hook, parse_constant=reject_constant)


def decode_json_value(text: str) -> tuple[object, int]:
    duplicates: list[str] = []

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        seen: set[str] = set()
        for key, _value in pairs:
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        if duplicates:
            raise DuplicateKeyError("duplicate keys")
        return dict(pairs)

    decoder = json.JSONDecoder(object_pairs_hook=hook, parse_constant=reject_constant)
    return decoder.raw_decode(text)


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def write_text(path: Path, text: str) -> None:
    write_bytes(path, text.encode("utf-8"))


def write_json(path: Path, payload: object) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    write_text(path, text)


def contains_marker(text: str) -> str | None:
    for marker in MARKERS:
        if marker in text:
            return marker
    if "<<<PRIOR_STAGE " in text:
        return "<<<PRIOR_STAGE "
    return None


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return f"{path.name} (path omitted)"


def require_id(value: object, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or ID_RE.fullmatch(value) is None:
        errors.append(f"{label} must be a lowercase safe id")
        return ""
    return value


def resolve_workflow(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    resolved = path.resolve()
    root = project_root()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValidationError("workflow must stay inside the project") from exc
    if len(relative.parts) < 2 or relative.parts[0] != "workflows" or resolved.suffix != ".json":
        raise ValidationError("workflow must be a JSON file under workflows/")
    if not resolved.is_file():
        raise ValidationError("workflow file does not exist")
    return resolved


def resolve_prompt(workflow_path: Path, raw: str, errors: list[str]) -> Path | None:
    if not isinstance(raw, str) or not raw or raw.startswith(("/", "\\")) or "\\" in raw:
        errors.append("prompt must be a relative path")
        return None
    parts = Path(raw).parts
    if not parts or ".." in parts or "." in parts or any(part == "" for part in parts):
        errors.append("prompt must stay inside the project and must not contain ..")
        return None
    candidate = (workflow_path.parent / raw).resolve()
    try:
        candidate.relative_to(project_root())
    except ValueError:
        errors.append("prompt resolves outside the project")
        return None
    if candidate.suffix != ".md" or not candidate.is_file():
        errors.append(f"prompt file is missing: {raw}")
        return None
    return candidate


def validate_workflow(workflow_path: Path, payload: object) -> dict[str, object]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        raise ValidationError("workflow must be a JSON object")
    allowed = {"schema_version", "id", "description", "stages"}
    extra = sorted(set(payload) - allowed)
    if extra:
        errors.append("unsupported workflow fields: " + ", ".join(extra))
    version = payload.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        errors.append("schema_version must be integer 1")
    workflow_id = require_id(payload.get("id"), "id", errors)
    description = payload.get("description")
    if (
        not isinstance(description, str)
        or not description.strip()
        or len(description) > 500
        or any(ord(char) < 32 for char in description)
    ):
        errors.append("description must be one line of at most 500 characters")
    stages = payload.get("stages")
    parsed_stages: list[dict[str, object]] = []
    if not isinstance(stages, list) or not stages:
        errors.append("stages must be a non-empty list")
    else:
        seen: set[str] = set()
        for index, stage in enumerate(stages, 1):
            if not isinstance(stage, dict):
                errors.append(f"stage {index} must be an object")
                continue
            stage_extra = sorted(set(stage) - {"id", "role", "prompt", "handoffs"})
            if stage_extra:
                errors.append(
                    f"stage {index} has unsupported fields: " + ", ".join(stage_extra)
                )
            stage_id = require_id(stage.get("id"), f"stage {index} id", errors)
            role = require_id(stage.get("role"), f"stage {index} role", errors)
            if stage_id and stage_id in seen:
                errors.append(f"duplicate stage id: {stage_id}")
            if stage_id:
                seen.add(stage_id)
            prompt_path = resolve_prompt(workflow_path, stage.get("prompt"), errors)
            handoffs = stage.get("handoffs")
            parsed_handoffs: list[dict[str, str]] = []
            if not isinstance(handoffs, list):
                errors.append(f"stage {stage_id or index} handoffs must be a list")
            else:
                prior = [item["id"] for item in parsed_stages]
                used: set[str] = set()
                for handoff in handoffs:
                    if not isinstance(handoff, dict) or set(handoff) != {"from"}:
                        errors.append(
                            f"stage {stage_id or index} handoff must be an object with only from"
                        )
                        continue
                    source = handoff.get("from")
                    if not isinstance(source, str) or source not in prior:
                        errors.append(
                            f"stage {stage_id or index} handoff references an unavailable stage"
                        )
                        continue
                    if source in used:
                        errors.append(f"stage {stage_id or index} repeats handoff {source}")
                    used.add(source)
                    parsed_handoffs.append({"from": source})
            if stage_id and prompt_path is not None and isinstance(stage.get("prompt"), str):
                parsed_stages.append(
                    {
                        "id": stage_id,
                        "role": role,
                        "prompt": stage["prompt"],
                        "prompt_path": prompt_path,
                        "handoffs": parsed_handoffs,
                    }
                )
    if errors:
        raise ValidationError("\n".join(errors))
    return {
        "schema_version": SCHEMA_VERSION,
        "id": workflow_id,
        "description": description,
        "stages": parsed_stages,
        "path": workflow_path,
    }


def validate_brief(data: bytes, label: str) -> dict[str, object]:
    if len(data) > MAX_INPUT_BYTES:
        raise ValidationError(f"{label} exceeds {MAX_INPUT_BYTES} bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{label} is not UTF-8") from exc
    marker = contains_marker(text)
    if marker:
        raise ValidationError(f"{label} contains a reserved marker")
    try:
        payload = load_json_text(text, label)
    except DuplicateKeyError as exc:
        raise ValidationError(str(exc)) from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"{label} must be a JSON object")
    errors: list[str] = []
    if payload.get("fictional") is not True:
        errors.append(f"{label} fictional must be true; this proof refuses non-synthetic briefs")
    require_id(payload.get("id"), f"{label} id", errors)
    sources = payload.get("sources")
    seen: set[str] = set()
    if not isinstance(sources, list) or not sources:
        errors.append(f"{label} sources must be a non-empty list")
    else:
        for index, source in enumerate(sources, 1):
            if not isinstance(source, dict):
                errors.append(f"{label} source {index} must be an object")
                continue
            source_id = source.get("id")
            if (
                not isinstance(source_id, str)
                or SOURCE_ID_RE.fullmatch(source_id) is None
                or len(source_id) > 40
            ):
                errors.append(f"{label} source {index} id must be a stable SRC- id")
            elif source_id in seen:
                errors.append(f"{label} duplicate source id {source_id}")
            else:
                seen.add(source_id)
            body = source.get("text")
            if not isinstance(body, str) or not body.strip():
                errors.append(f"{label} source {index} text must be non-empty")
            elif contains_marker(body):
                errors.append(f"{label} source {index} contains a reserved marker")
    gaps = payload.get("known_gaps")
    if not isinstance(gaps, list) or not gaps:
        errors.append(f"{label} known_gaps must be a non-empty list")
    else:
        for index, gap in enumerate(gaps, 1):
            if not isinstance(gap, str) or not gap.strip():
                errors.append(f"{label} known_gaps item {index} must be a non-empty string")
    if errors:
        raise ValidationError("\n".join(errors))
    return payload


def load_workflow(raw: str) -> tuple[dict[str, object], bytes]:
    path = resolve_workflow(raw)
    data = path.read_bytes()
    try:
        payload = load_json_bytes(data, "workflow")
    except DuplicateKeyError as exc:
        raise ValidationError(str(exc)) from exc
    return validate_workflow(path, payload), data


def read_prompt_bytes(workflow: dict[str, object]) -> dict[str, bytes]:
    found: dict[str, bytes] = {}
    for stage in workflow["stages"]:
        data = stage["prompt_path"].read_bytes()
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"{stage['prompt']} is not UTF-8") from exc
        # Author-controlled prompts may name delimiters. Brief bytes and prior
        # artifacts are the untrusted inserts, and those are checked separately.
        found[stage["id"]] = data
    return found


def load_input(raw: str) -> tuple[Path, bytes]:
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    resolved = path.resolve()
    if not resolved.is_file():
        raise ValidationError("input file does not exist")
    data = resolved.read_bytes()
    validate_brief(data, "input")
    return resolved, data


def compose_prompt(prompt_text: str, brief_text: str, handoffs: list[tuple[str, str]]) -> str:
    parts = [
        prompt_text.rstrip() + "\n\n",
        MARKER_BRIEF + "\n",
        brief_text.rstrip() + "\n",
        MARKER_BRIEF_END + "\n",
        MARKER_PRIOR + "\n",
    ]
    if not handoffs:
        parts.append("(none)\n")
    for stage_id, artifact in handoffs:
        parts.append(f"<<<PRIOR_STAGE id={stage_id}>>>\n")
        parts.append(artifact.rstrip() + "\n")
        parts.append(MARKER_PRIOR_END + "\n")
    parts.append(MARKER_END + "\n")
    return "".join(parts)


def handoff_text(stage: dict[str, object]) -> str:
    names = [item["from"] for item in stage["handoffs"]]
    return ",".join(names) if names else "none"


def format_validate(workflow: dict[str, object]) -> str:
    lines = [
        "status: valid",
        "model_invoked: false",
        "files_created: none",
        f"workflow_id: {workflow['id']}",
        f"schema_version: {workflow['schema_version']}",
        f"description: {workflow['description']}",
        f"stage_count: {len(workflow['stages'])}",
        "canonical_representation: manifest+prompts interpreted by scripts/run_workflow.py",
        "generated_workflow_code: false",
        "native_workflow_wrapper: false",
    ]
    for index, stage in enumerate(workflow["stages"], 1):
        lines.extend(
            [
                f"stage: {index}",
                f"id: {stage['id']}",
                f"role: {stage['role']}",
                f"prompt: {stage['prompt']}",
                f"handoffs: {handoff_text(stage)}",
            ]
        )
    lines.append("input: not checked")
    return "\n".join(lines) + "\n"


def executable_for(runtime: str) -> str:
    found = shutil.which(runtime)
    if not found:
        raise PreflightError(f"{runtime} executable not found; no runtime fallback")
    return found


def cli_version(executable: str) -> str:
    try:
        completed = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            timeout=VERSION_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PreflightError(f"CLI version check failed: {type(exc).__name__}") from exc
    text = completed.stdout.decode("utf-8", errors="replace").strip()
    if not text:
        text = completed.stderr.decode("utf-8", errors="replace").strip()
    if completed.returncode != 0 or not text:
        raise PreflightError(f"CLI version check failed with exit {completed.returncode}")
    return text.splitlines()[0].strip()


def adapter_argv(
    runtime: str,
    executable: str,
    cwd_display: str,
    mcp_display: str | None,
    timeout: int | None,
) -> list[str]:
    if runtime == "omp":
        argv = [
            executable,
            "-p",
            "--mode=json",
            f"--cwd={cwd_display}",
            "--no-session",
            "--no-title",
            "--no-tools",
            "--no-lsp",
            "--no-extensions",
            "--no-skills",
            "--no-rules",
        ]
        if timeout is not None:
            argv.append(f"--max-time={timeout}")
        return argv
    if runtime != "claude":
        raise PreflightError(f"unsupported runtime: {runtime}")
    if mcp_display is None:
        raise PreflightError("claude adapter requires an MCP config path")
    return [
        executable,
        "-p",
        "--output-format",
        "json",
        "--safe-mode",
        "--disable-slash-commands",
        "--permission-prompts",
        "none",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--mcp-config",
        mcp_display,
        "--tools",
        "",
    ]


def capability_notes(runtime: str) -> list[str]:
    shared = [
        "hermetic: false",
        "sandbox: false",
        "full_isolation: false",
        "full_accounting: false",
        "controlled_ambient_config: false",
        "flags_are_effective_config: false",
        "effective_model_controlled: false",
        "hidden_workflow_tool_disabled: unknown",
        "requested_model: configured-default",
        "observed_model: recorded per stage from native output when present; absence is unknown, not the configured default",
        "semantic_verification: not performed",
        "human_approval: not performed and not bypassed",
        "business_acceptance: false",
        "remote_cancellation: not guaranteed by a local process-group signal",
        "missing_usage: unknown, never zero; native scopes are not added together",
    ]
    if runtime == "omp":
        shared.extend(
            [
                "omp_flags_disable_builtin_tools_skills_rules_extensions_and_lsp_only_as_requested",
                "omp_usage_scope: terminal assistant message only; auxiliary calls unknown",
                "omp_has_no_safe_mode_flag_in_this_adapter",
            ]
        )
    else:
        shared.extend(
            [
                "claude_safe_mode_requested: true; help says customizations are disabled and CLAUDE_CODE_SAFE_MODE=1",
                "claude_managed_settings: help says admin-managed policy settings still apply",
                "claude_safe_mode_tools: help says built-in tools, plugins, auth, model selection, and permissions work normally",
                "claude_tools_empty_is_not_proof_a_hidden_Workflow_tool_is_off",
                "claude_bare_not_used: bare changes subscription auth",
                "claude_safe_mode_with_explicit_mcp_config: unverified",
                "claude_print_without_bare_can_load_user_hooks_and_settings",
                "claude_usage_and_modelUsage_are_different_scopes_and_are_not_summed",
            ]
        )
    return shared


def check_timeout(value: int | None) -> int | None:
    if value is None:
        return None
    if type(value) is not int or isinstance(value, bool) or value < 1:
        raise PreflightError("timeout-seconds must be a positive integer")
    return value


def format_plan(
    workflow: dict[str, object],
    runtime: str,
    version: str,
    input_display: str,
    input_hash: str,
    workflow_hash: str,
    script_hash: str,
    prompt_hashes: dict[str, str],
    timeout: int | None,
    argv: list[str],
    brief_text: str,
    prompt_texts: dict[str, str],
) -> str:
    lines = [
        "status: planned",
        "model_invoked: false",
        "files_created: none",
        f"workflow_id: {workflow['id']}",
        f"schema_version: {workflow['schema_version']}",
        f"runtime: {runtime}",
        f"executable: {runtime}",
        f"cli_version: {version}",
        f"input: {input_display}",
        f"input_sha256: {input_hash}",
        f"workflow_sha256: {workflow_hash}",
        f"script_sha256: {script_hash}",
        f"timeout_seconds: {timeout if timeout is not None else 'none'}",
        "canonical_representation: manifest+prompts interpreted by scripts/run_workflow.py",
        "generated_workflow_code: false",
        "native_workflow_wrapper: false",
        f"stage_count: {len(workflow['stages'])}",
    ]
    for index, stage in enumerate(workflow["stages"], 1):
        lines.extend(
            [
                f"stage: {index}",
                f"id: {stage['id']}",
                f"role: {stage['role']}",
                f"prompt: {stage['prompt']}",
                f"prompt_sha256: {prompt_hashes[stage['id']]}",
                f"handoffs: {handoff_text(stage)}",
            ]
        )
        if stage["handoffs"]:
            lines.extend(
                [
                    "stdin: not composed; prior stage artifacts are collected at run time",
                    "stdin_sha256: unknown",
                ]
            )
        else:
            composed = compose_prompt(prompt_texts[stage["id"]], brief_text, [])
            encoded = composed.encode("utf-8")
            lines.extend(
                [
                    "stdin: composed from prompt file, brief bytes, and empty handoffs",
                    f"stdin_sha256: {sha256_bytes(encoded)}",
                    f"stdin_bytes: {len(encoded)}",
                ]
            )
        lines.append("stdin_text: omitted")
    lines.extend(
        [
            "argv: " + json.dumps(argv),
            "prompt_transport: stdin",
            "same_argv_each_stage: true",
            "requested_model: configured-default",
            "observed_model: unknown",
            "observed_provider: unknown",
            "provenance_gaps:",
        ]
    )
    lines.extend(f"- {note}" for note in capability_notes(runtime))
    if timeout is None:
        lines.append("- workbench_deadline: none requested")
    else:
        lines.append(
            f"- workbench_backstop_seconds: {timeout + FLUSH_BACKSTOP_SECONDS}; native omp --max-time is {timeout} when runtime is omp"
        )
    return "\n".join(lines) + "\n"


def git_boundary(start: Path, flag: str) -> Path:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", flag],
            cwd=start,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PreflightError("cannot prove output directory is outside the repository") from exc
    if completed.returncode != 0 or not completed.stdout.strip():
        raise PreflightError("cannot prove output directory is outside the repository")
    raw = Path(completed.stdout.strip())
    if not raw.is_absolute():
        raw = start / raw
    resolved = raw.resolve()
    if resolved == Path("/"):
        raise PreflightError("refusing a repository boundary of /")
    return resolved


def assert_output_outside(output_dir: Path) -> None:
    if os.path.lexists(output_dir):
        raise PreflightError("output directory already exists and will not be overwritten")
    parent = output_dir.parent
    if not parent.is_dir():
        raise PreflightError("output directory parent must already exist")
    candidate = parent.resolve() / output_dir.name
    root = project_root()
    boundaries = [root.resolve()]
    # A permitted standalone source copy has no repository boundary. Keep Git
    # optional there; inside a checkout, retain worktree/common-dir protection.
    if any(os.path.lexists(parent / ".git") for parent in (root, *root.parents)):
        boundaries.extend(
            [
                git_boundary(root, "--show-toplevel"),
                git_boundary(root, "--git-dir"),
                git_boundary(root, "--git-common-dir"),
            ]
        )
        boundaries.append(boundaries[-1].parent)
    for boundary in boundaries:
        if candidate == boundary or boundary in candidate.parents:
            raise PreflightError("output directory must be outside the repository and project")


def redact_home(value: str) -> str:
    home = str(Path.home())
    if home and home not in {"/", ""} and home in value:
        return value.replace(home, "<home>")
    return value


def redact(value: str, output_dir: Path) -> str:
    redacted = value.replace(str(output_dir.resolve()), "<output-dir>").replace(
        str(output_dir), "<output-dir>"
    )
    return redact_home(redacted)


def display_argv(argv: list[str], runtime: str, executable: str, output_dir: Path) -> list[str]:
    shown: list[str] = []
    for arg in argv:
        if arg == executable:
            shown.append(runtime)
        else:
            shown.append(redact(arg, output_dir))
    return shown


def raise_cancel(_signum: int, _frame: object) -> None:
    # SIGKILL cannot be handled. SIGTERM and SIGHUP use the same cancel path as SIGINT.
    ignore_cancel_signals()
    raise KeyboardInterrupt


def ignore_cancel_signals() -> None:
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        while True:
            try:
                signal.signal(sig, signal.SIG_IGN)
            except KeyboardInterrupt:
                # A cancel at entry must not skip process cleanup or terminal writes.
                continue
            except (OSError, ValueError):
                break
            else:
                break


def restore_signals(saved: list[tuple[int, object]]) -> None:
    for sig, previous in saved:
        signal.signal(sig, previous)


def stop_group(proc: subprocess.Popen[bytes]) -> list[str]:
    notes = [
        "local process-group signal only; remote requests and descendants that left the group are not guaranteed cancelled"
    ]
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        notes.append("SIGTERM sent to local process group")
    except ProcessLookupError:
        notes.append("process group already gone before SIGTERM")
    except OSError as exc:
        notes.append(f"SIGTERM failed: {type(exc).__name__}")
    else:
        try:
            proc.wait(timeout=TERM_GRACE_SECONDS)
            notes.append("child exited during SIGTERM grace")
        except subprocess.TimeoutExpired:
            notes.append("child still present after SIGTERM grace")
    # The session leader may exit before descendants in its process group.
    try:
        os.killpg(proc.pid, signal.SIGKILL)
        notes.append("SIGKILL sent to remaining local process group")
    except ProcessLookupError:
        notes.append("process group already gone before SIGKILL")
    except OSError as exc:
        notes.append(f"SIGKILL failed: {type(exc).__name__}")
    try:
        proc.wait(timeout=KILL_WAIT_SECONDS)
    except subprocess.TimeoutExpired:
        notes.append("child not reaped within kill wait")
    return notes


def launch_cli(argv: list[str], prompt: bytes, cwd: Path, timeout: int | None) -> dict[str, object]:
    # Anonymous files avoid pipe-buffer races when a signal interrupts process startup.
    # command_run owns restoration; failed launches keep cancel signals ignored until
    # their streams and terminal receipts have been persisted.
    proc: subprocess.Popen[bytes] | None = None
    pending_cancel = False
    timed_out = False
    cancelled = False
    notes: list[str] = []
    backstop = None if timeout is None else timeout + FLUSH_BACKSTOP_SECONDS

    def remember_cancel(_signum: int, _frame: object) -> None:
        nonlocal pending_cancel
        pending_cancel = True

    with (
        tempfile.TemporaryFile(dir=cwd) as native_input,
        tempfile.TemporaryFile(dir=cwd) as native_stdout,
        tempfile.TemporaryFile(dir=cwd) as native_stderr,
    ):
        native_input.write(prompt)
        native_input.seek(0)
        spawning_signals: list[tuple[int, object]] = []
        try:
            try:
                for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                    previous = signal.getsignal(sig)
                    if previous != signal.SIG_IGN:
                        spawning_signals.append((sig, signal.signal(sig, remember_cancel)))
                proc = subprocess.Popen(
                    argv,
                    stdin=native_input,
                    stdout=native_stdout,
                    stderr=native_stderr,
                    cwd=cwd,
                    start_new_session=True,
                )
            finally:
                restore_signals(spawning_signals)
            if pending_cancel:
                raise KeyboardInterrupt
            proc.wait(timeout=backstop)
        except subprocess.TimeoutExpired:
            timed_out = True
        except KeyboardInterrupt:
            cancelled = True
        finally:
            if timed_out or cancelled or (proc is not None and proc.poll() is None):
                ignore_cancel_signals()
                if proc is not None:
                    notes = stop_group(proc)
        native_stdout.seek(0)
        native_stderr.seek(0)
        return {
            "timed_out": timed_out,
            "cancelled": cancelled,
            "exit_code": proc.returncode if proc is not None else None,
            "stdout": native_stdout.read(),
            "stderr": native_stderr.read(),
            "termination": notes,
        }


def assistant_text(message: dict[str, object]) -> tuple[str | None, str | None]:
    content = message.get("content")
    if not isinstance(content, list):
        return None, "assistant content is not a list"
    texts: list[str] = []
    for block in content:
        if not isinstance(block, dict) or not isinstance(block.get("type"), str):
            return None, "assistant content block is not an object"
        kind = block["type"]
        if kind == "text":
            text = block.get("text")
            if not isinstance(text, str):
                return None, "text block has no string text"
            if text.strip():
                texts.append(text.strip())
        elif kind in THINKING_TYPES:
            continue
        elif kind in {"toolCall", "tool_use"}:
            name = block.get("name", kind)
            return None, f"assistant attempted a tool call ({name})"
        else:
            return None, f"unrecognized assistant content type: {kind}"
    if not texts:
        return None, "assistant text is empty"
    return "\n".join(texts), None


def observed_model_fields(message: dict[str, object]) -> dict[str, object]:
    model = message.get("model") if isinstance(message.get("model"), str) and message.get("model") else None
    provider = message.get("provider") if isinstance(message.get("provider"), str) and message.get("provider") else None
    upstream_model = (
        message.get("upstreamModel")
        if isinstance(message.get("upstreamModel"), str) and message.get("upstreamModel")
        else None
    )
    upstream_provider = (
        message.get("upstreamProvider")
        if isinstance(message.get("upstreamProvider"), str) and message.get("upstreamProvider")
        else None
    )
    usage = message.get("usage") if isinstance(message.get("usage"), dict) else None
    native_cost = usage.get("cost") if usage is not None else None
    cost = number_or_none(native_cost.get("total")) if isinstance(native_cost, dict) else None
    return {
        "requested_model": None,
        "model_selection": "configured-default",
        "observed_model": model,
        "observed_model_status": "reported" if model else "unknown",
        "observed_model_source": "message_end.model" if model else "absent",
        "observed_provider": provider,
        "observed_provider_status": "reported" if provider else "unknown",
        "upstream_model": upstream_model,
        "upstream_model_status": "reported" if upstream_model else "unknown",
        "upstream_provider": upstream_provider,
        "upstream_provider_status": "reported" if upstream_provider else "unknown",
        "usage": usage,
        "usage_status": "reported" if usage else "unknown",
        "usage_scope": "omp_terminal_assistant_message",
        "cost": cost,
        "cost_status": "reported" if cost is not None else "unknown",
        "cost_scope": "omp_terminal_assistant_message_usage_cost_client_estimate_not_billing",
        "effective_model_controlled": False,
    }


def parse_failure(reason: str, detail: str = "", text: str | None = None, **fields: object) -> dict[str, object]:
    payload: dict[str, object] = {"ok": False, "reason": reason, "detail": detail, "text": text}
    payload.update(fields)
    return payload


def assistant_tool_detail(message: object) -> str | None:
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if not isinstance(content, list):
        return None
    for block in content:
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        if kind in TOOL_CONTENT_TYPES:
            name = block.get("name", kind)
            return f"assistant attempted a tool call ({name})"
    return None


def reject_omp(detail: str, session_id: str | None) -> dict[str, object]:
    return parse_failure("omp_disallowed_event", detail, session_id=session_id)


def parse_omp(stdout: bytes) -> dict[str, object]:
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError:
        return parse_failure("stdout_not_utf8")
    if not text.endswith("\n"):
        return parse_failure("stdout_truncated", "missing trailing newline")
    events: list[dict[str, object]] = []
    for index, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = parse_native_json(line)
        except (json.JSONDecodeError, DuplicateKeyError) as exc:
            return parse_failure("stdout_truncated", f"line {index}: {exc}")
        if not isinstance(item, dict):
            return parse_failure("unknown_output_format", f"line {index} is not an object")
        events.append(item)
    if not events:
        return parse_failure("empty_output")
    session_id = None
    if events[0].get("type") == "session" and isinstance(events[0].get("id"), str):
        session_id = events[0]["id"]
    message_end = None
    agent_end = None
    turn_starts = 0
    for event in events:
        kind = event.get("type")
        if kind not in OMP_LIFECYCLE_EVENTS:
            return reject_omp(str(kind), session_id)
        if kind == "turn_start":
            turn_starts += 1
            if turn_starts > 1:
                return reject_omp("multiple turn_start", session_id)
            continue
        if kind == "message_end":
            message = event.get("message")
            role = message.get("role") if isinstance(message, dict) else None
            if role not in OMP_MESSAGE_ROLES:
                return reject_omp(f"message_end role {role!r}", session_id)
            if role == "assistant":
                tool_error = assistant_tool_detail(message)
                if tool_error:
                    return reject_omp(tool_error, session_id)
                message_end = message
            continue
        if kind == "message_update":
            update = event.get("assistantMessageEvent")
            update_type = update.get("type") if isinstance(update, dict) else None
            if isinstance(update_type, str) and "tool" in update_type.lower():
                return reject_omp(update_type, session_id)
            continue
        if kind == "turn_end":
            results = event.get("toolResults")
            if isinstance(results, list) and results:
                return reject_omp("turn_end toolResults", session_id)
            turn_message = event.get("message")
            if isinstance(turn_message, dict) and turn_message.get("role") == "assistant":
                tool_error = assistant_tool_detail(turn_message)
                if tool_error:
                    return reject_omp(tool_error, session_id)
            continue
        if kind == "agent_end" and isinstance(event.get("messages"), list):
            for message in event["messages"]:
                if not isinstance(message, dict) or message.get("role") != "assistant":
                    continue
                tool_error = assistant_tool_detail(message)
                if tool_error:
                    return reject_omp(tool_error, session_id)
                agent_end = message
    if turn_starts != 1:
        return reject_omp("turn_start missing", session_id)
    if not isinstance(message_end, dict):
        return parse_failure("omp_message_end_missing", session_id=session_id)
    observed = observed_model_fields(message_end)
    observed["session_id"] = session_id
    observed["session_status"] = "reported" if session_id else "unknown"
    if isinstance(agent_end, dict):
        if message_end.get("stopReason") != agent_end.get("stopReason"):
            return parse_failure(
                "omp_terminal_message_mismatch",
                "stopReason differs",
                **observed,
            )
        end_text, end_error = assistant_text(message_end)
        agent_text, agent_error = assistant_text(agent_end)
        if end_error or agent_error or end_text != agent_text:
            return parse_failure(
                "omp_terminal_message_mismatch",
                end_error or agent_error or "text differs",
                **observed,
            )
    extracted, extract_error = assistant_text(message_end)
    stop = message_end.get("stopReason")
    observed["stop_reason"] = stop if isinstance(stop, str) else None
    if stop != "stop":
        return parse_failure("omp_stop_reason", f"stopReason={stop!r}", extracted, **observed)
    if extract_error:
        return parse_failure("missing_artifact", extract_error, **observed)
    return {
        "ok": True,
        "reason": None,
        "detail": "",
        "text": extracted,
        **observed,
    }


def number_or_none(value: object) -> float | int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def parse_claude(stdout: bytes) -> dict[str, object]:
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError:
        return parse_failure("stdout_not_utf8")
    stripped = text.strip()
    if not stripped:
        return parse_failure("empty_output")
    try:
        raw, end = decode_json_value(stripped)
    except DuplicateKeyError:
        return parse_failure("unknown_output_format", "duplicate keys")
    except json.JSONDecodeError as exc:
        return parse_failure("stdout_truncated", exc.msg)
    if stripped[end:].strip():
        return parse_failure("unknown_output_format", "extra data after JSON value")
    if not isinstance(raw, dict):
        return parse_failure("unknown_output_format", "result is not an object")
    obj = raw
    if obj.get("type") != "result":
        return parse_failure("unknown_output_format", "type is not result")
    subtype = obj.get("subtype")
    if not isinstance(subtype, str):
        return parse_failure("unknown_output_format", "subtype missing")
    if "is_error" not in obj or not isinstance(obj.get("is_error"), bool):
        return parse_failure("unknown_output_format", "is_error missing or not boolean")
    if "stop_reason" not in obj:
        return parse_failure("unknown_output_format", "stop_reason missing")
    stop = obj.get("stop_reason")
    if stop is not None and not isinstance(stop, str):
        return parse_failure("unknown_output_format", "stop_reason is not a string or null")
    session_id = obj.get("session_id")
    if "session_id" in obj and not isinstance(session_id, str):
        return parse_failure("unknown_output_format", "session_id is not a string")
    result = obj.get("result")
    extracted = result if isinstance(result, str) else None
    if "permission_denials" in obj and not isinstance(obj.get("permission_denials"), list):
        return parse_failure("unknown_output_format", "permission_denials is not a list")
    if "usage" in obj and not isinstance(obj.get("usage"), dict):
        return parse_failure("unknown_output_format", "usage is not an object")
    if "modelUsage" in obj and not isinstance(obj.get("modelUsage"), dict):
        return parse_failure("unknown_output_format", "modelUsage is not an object")
    if "total_cost_usd" in obj and number_or_none(obj.get("total_cost_usd")) is None:
        return parse_failure("unknown_output_format", "total_cost_usd is not a number")
    terminal = obj.get("terminal_reason") if "terminal_reason" in obj else None
    if "terminal_reason" in obj and terminal not in SUCCESS_STOPS and terminal not in {
        "success",
        "completed",
    }:
        bad_terminal = True
    else:
        bad_terminal = False
    usage = obj.get("usage") if isinstance(obj.get("usage"), dict) else None
    top_model = obj.get("model") if isinstance(obj.get("model"), str) and obj.get("model") else None
    model_usage = obj.get("modelUsage") if isinstance(obj.get("modelUsage"), dict) else None
    keys_reported = sorted(model_usage) if isinstance(model_usage, dict) else None
    observed: dict[str, object] = {
        "requested_model": None,
        "model_selection": "configured-default",
        "observed_model": top_model,
        "observed_model_status": "reported" if top_model else "unknown",
        "observed_model_source": "result.model" if top_model else "absent",
        "observed_model_keys": keys_reported,
        "observed_model_keys_status": "reported" if keys_reported is not None else "unknown",
        "observed_provider": None,
        "observed_provider_status": "unknown",
        "session_id": session_id if isinstance(session_id, str) else None,
        "session_status": "reported" if isinstance(session_id, str) and session_id else "unknown",
        "stop_reason": stop,
        "subtype": subtype,
        "is_error": obj["is_error"],
        "usage": usage,
        "usage_status": "reported" if usage is not None else "unknown",
        "usage_scope": "claude_result_usage_main_loop",
        "model_usage": model_usage,
        "model_usage_status": "reported" if model_usage is not None else "unknown",
        "model_usage_scope": "claude_result_model_usage_query_pipeline",
        "cost": number_or_none(obj.get("total_cost_usd")) if "total_cost_usd" in obj else None,
        "cost_status": "reported" if "total_cost_usd" in obj else "unknown",
        "cost_scope": "claude_cli_result_client_estimate_not_billing",
        "effective_model_controlled": False,
    }
    if subtype != "success" or obj["is_error"] is not False:
        reason = "claude_is_error" if obj["is_error"] else "claude_subtype"
        return parse_failure(reason, f"subtype={subtype!r} is_error={obj['is_error']!r}", extracted, **observed)
    if stop not in (None, "end_turn", "stop"):
        return parse_failure("claude_stop_reason", f"stop_reason={stop!r}", extracted, **observed)
    if bad_terminal:
        return parse_failure("claude_stop_reason", f"terminal_reason={terminal!r}", extracted, **observed)
    denials = obj.get("permission_denials")
    if isinstance(denials, list) and denials:
        return parse_failure("claude_permission_denial", f"{len(denials)} denial(s)", extracted, **observed)
    if not isinstance(session_id, str) or not session_id:
        return parse_failure("unknown_output_format", "session_id missing", extracted, **observed)
    if not isinstance(result, str) or not result.strip():
        return parse_failure("missing_artifact", "result text empty", **observed)
    return {"ok": True, "reason": None, "detail": "", "text": result, **observed}


def model_receipt(parsed: dict[str, object]) -> dict[str, object]:
    return {
        "requested": None,
        "selection": "configured-default",
        "observed": parsed.get("observed_model"),
        "observed_status": parsed.get("observed_model_status", "unknown"),
        "observed_provider": parsed.get("observed_provider"),
        "observed_provider_status": parsed.get("observed_provider_status", "unknown"),
        "observed_model_keys": parsed.get("observed_model_keys"),
        "observed_model_keys_status": parsed.get("observed_model_keys_status", "unknown"),
        "observed_source": parsed.get("observed_model_source", "unknown"),
        "upstream_model": parsed.get("upstream_model"),
        "upstream_model_status": parsed.get("upstream_model_status", "unknown"),
        "upstream_provider": parsed.get("upstream_provider"),
        "upstream_provider_status": parsed.get("upstream_provider_status", "unknown"),
        "effective_model_controlled": False,
        "note": (
            "Requested model is the CLI configured default, not an observed effective model. "
            "OMP model and provider are taken only from the terminal assistant message. "
            "Claude observed model is result.model when that field is present. "
            "Claude modelUsage keys are recorded separately and are not collapsed into one model."
        ),
    }


def usage_receipt(parsed: dict[str, object]) -> dict[str, object]:
    return {
        "summed": False,
        "missing_is_zero": False,
        "usage": {
            "status": parsed.get("usage_status", "unknown"),
            "scope": parsed.get("usage_scope"),
            "reported": parsed.get("usage"),
        },
        "model_usage": {
            "status": parsed.get("model_usage_status", "unknown"),
            "scope": parsed.get("model_usage_scope"),
            "reported": parsed.get("model_usage"),
            "keys": parsed.get("observed_model_keys"),
        },
        "cost": {
            "status": parsed.get("cost_status", "unknown"),
            "scope": parsed.get("cost_scope"),
            "amount": parsed.get("cost"),
            "kind": "client_estimate_not_billing" if parsed.get("cost_status") == "reported" else "unknown",
        },
        "note": "Do not add usage to modelUsage. Auxiliary and hidden calls outside the recorded native scope remain unknown.",
    }


def initial_state(run_id: str, runtime: str, workflow_id: str, stages: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": "started",
        "business_acceptance": False,
        "started_at": now_iso(),
        "updated_at": now_iso(),
        "finished_at": None,
        "runtime": runtime,
        "workflow_id": workflow_id,
        "current_stage": None,
        "stages": {stage["id"]: {"status": "pending"} for stage in stages},
        "error": None,
    }


def summary_text(state: dict[str, object], stage_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Run summary",
        "",
        f"- status: {state['status']}",
        f"- run_id: {state['run_id']}",
        f"- workflow_id: {state['workflow_id']}",
        f"- runtime: {state['runtime']}",
        "- business_acceptance: false",
        "- semantic_verification: not performed",
        "- human_approval: not performed and not bypassed",
        "",
        "CLI completion is not business acceptance, storyline approval, or a quality judgment.",
        "The canonical representation is the manifest and prompt files interpreted by this runner.",
        "",
        "## Stages",
        "",
    ]
    for row in stage_rows:
        lines.append(f"### {row['id']}")
        lines.append(f"- status: {row['status']}")
        lines.append(f"- handoffs: {row['handoffs']}")
        if row.get("artifact"):
            lines.append(f"- artifact: {row['artifact']}")
            lines.append(f"- artifact_sha256: {row['artifact_sha256']}")
        else:
            lines.append("- artifact: none")
        if row.get("reason"):
            lines.append(f"- reason: {row['reason']}")
        lines.append("")
    lines.extend(
        [
            "## Provenance",
            "",
            "- receipt: receipt.json",
            "- state: state.json",
            "- snapshots: snapshots/",
            "- raw native stdout and stderr remain under stages/",
            "",
        ]
    )
    return "\n".join(lines)


def finalize_declared_stages(
    workflow: dict[str, object],
    state: dict[str, object],
    output_dir: Path,
    stage_rows: list[dict[str, object]],
    receipt_stages: list[dict[str, object]],
) -> None:
    if state.get("status") == "completed":
        return
    recorded = {row["id"] for row in stage_rows}
    run_status = state.get("status")
    interrupted = state.get("current_stage")
    error = state.get("error") if isinstance(state.get("error"), dict) else {}
    for stage in workflow["stages"]:
        stage_id = stage["id"]
        current = state["stages"][stage_id]
        status = current.get("status") if isinstance(current, dict) else None
        reason = current.get("reason") if isinstance(current, dict) else None
        if status == "running":
            if run_status == "cancelled":
                status = "cancelled"
                reason = "cancelled"
            else:
                status = "failed"
                reason = error.get("reason") or "unexpected_error"
            state["stages"][stage_id] = {"status": status, "reason": reason}
        elif status == "pending":
            status = "not_started"
            reason = "prior_stage_failed" if run_status == "failed" else "not_started"
            state["stages"][stage_id] = {"status": "not_started"}
        if status in {"running", "pending"}:
            status = "failed"
            reason = "unexpected_error"
            state["stages"][stage_id] = {"status": status, "reason": reason}
        if stage_id in recorded or status == "completed":
            continue
        row: dict[str, object] = {
            "id": stage_id,
            "status": status,
            "handoffs": handoff_text(stage),
            "reason": reason,
        }
        if stage_id == interrupted and status in {"cancelled", "failed"} and error.get("detail"):
            row["detail"] = error.get("detail")
        stage_rows.append(row)
        receipt_stages.append(row)
        stage_dir = output_dir / "stages" / stage_id
        stage_dir.mkdir(parents=True, exist_ok=True)
        stage_path = stage_dir / "stage.json"
        if not stage_path.exists():
            write_json(stage_path, row)


def execute_run(
    workflow: dict[str, object],
    workflow_bytes: bytes,
    runtime: str,
    executable: str,
    version: str,
    input_path: Path,
    input_bytes: bytes,
    prompt_bytes: dict[str, bytes],
    output_dir: Path,
    timeout: int | None,
) -> int:
    try:
        output_dir.mkdir()
    except FileExistsError as exc:
        raise PreflightError("output directory already exists and will not be overwritten") from exc
    run_id = new_run_id()
    state = initial_state(run_id, runtime, str(workflow["id"]), workflow["stages"])
    state_path = output_dir / "state.json"
    write_json(state_path, state)
    task_cwd = output_dir / "task-cwd"
    snapshots = output_dir / "snapshots"
    code = 1
    stage_rows: list[dict[str, object]] = []
    receipt_stages: list[dict[str, object]] = []
    script_sha256: str | None = None
    try:
        script_sha256 = sha256_bytes(script_path().read_bytes())
        task_cwd.mkdir()
        snapshots.mkdir()
        write_bytes(snapshots / "workflow.json", workflow_bytes)
        write_bytes(snapshots / "input.json", input_bytes)
        prompt_dir = snapshots / "prompts"
        prompt_dir.mkdir()
        for stage in workflow["stages"]:
            write_bytes(prompt_dir / f"{stage['id']}.md", prompt_bytes[stage["id"]])
        mcp_path = snapshots / "claude-mcp.json"
        if runtime == "claude":
            write_bytes(mcp_path, CLAUDE_MCP_BYTES)
        hash_payload = {
            "script_sha256": script_sha256,
            "workflow_sha256": sha256_bytes(workflow_bytes),
            "input_sha256": sha256_bytes(input_bytes),
            "prompt_sha256": {
                stage["id"]: sha256_bytes(prompt_bytes[stage["id"]]) for stage in workflow["stages"]
            },
            "claude_mcp_sha256": sha256_bytes(CLAUDE_MCP_BYTES) if runtime == "claude" else None,
        }
        write_json(snapshots / "hashes.json", hash_payload)
        state["updated_at"] = now_iso()
        write_json(state_path, state)
        brief_text = input_bytes.decode("utf-8")
        prompt_texts = {
            stage["id"]: prompt_bytes[stage["id"]].decode("utf-8") for stage in workflow["stages"]
        }
        accepted: dict[str, str] = {}
        real_argv = adapter_argv(
            runtime,
            executable,
            str(task_cwd),
            str(mcp_path) if runtime == "claude" else None,
            timeout,
        )
        for stage in workflow["stages"]:
            stage_id = stage["id"]
            state["current_stage"] = stage_id
            state["stages"][stage_id] = {"status": "running", "started_at": now_iso()}
            state["updated_at"] = now_iso()
            write_json(state_path, state)
            stage_dir = output_dir / "stages" / stage_id
            stage_dir.mkdir(parents=True)
            handoff_pairs: list[tuple[str, str]] = []
            blocked = None
            for item in stage["handoffs"]:
                source_id = item["from"]
                artifact = accepted.get(source_id)
                if artifact is None:
                    blocked = "prior stage artifact missing"
                    break
                marker = contains_marker(artifact)
                if marker:
                    blocked = "prior stage artifact contains a reserved marker"
                    break
                handoff_pairs.append((source_id, artifact))
            if blocked:
                row = {
                    "id": stage_id,
                    "status": "failed",
                    "handoffs": handoff_text(stage),
                    "reason": "handoff_unavailable",
                    "detail": blocked,
                }
                stage_rows.append(row)
                receipt_stages.append(row)
                state["stages"][stage_id] = {"status": "failed", "reason": "handoff_unavailable"}
                state["status"] = "failed"
                state["error"] = {"reason": "handoff_unavailable", "detail": blocked}
                write_json(stage_dir / "stage.json", row)
                break
            composed = compose_prompt(prompt_texts[stage_id], brief_text, handoff_pairs)
            composed_bytes = composed.encode("utf-8")
            if len(composed_bytes) > MAX_PROMPT_BYTES:
                row = {
                    "id": stage_id,
                    "status": "failed",
                    "handoffs": handoff_text(stage),
                    "reason": "prompt_too_large",
                    "detail": f"{len(composed_bytes)} bytes",
                }
                stage_rows.append(row)
                receipt_stages.append(row)
                state["stages"][stage_id] = {"status": "failed", "reason": "prompt_too_large"}
                state["status"] = "failed"
                state["error"] = {"reason": "prompt_too_large", "detail": row["detail"]}
                write_json(stage_dir / "stage.json", row)
                break
            write_bytes(stage_dir / "prompt.txt", composed_bytes)
            request = {
                "runtime": runtime,
                "argv": display_argv(real_argv, runtime, executable, output_dir),
                "prompt_transport": "stdin",
                "prompt_sha256": sha256_bytes(composed_bytes),
                "prompt_bytes": len(composed_bytes),
                "cwd": "task-cwd",
                "timeout_seconds": timeout,
                "native_max_time_seconds": timeout if runtime == "omp" else None,
                "safe_mode_requested": runtime == "claude",
            }
            write_json(stage_dir / "request.json", request)
            launched = launch_cli(real_argv, composed_bytes, task_cwd, timeout)
            write_bytes(stage_dir / "stdout.txt", launched["stdout"])
            write_bytes(stage_dir / "stderr.txt", launched["stderr"])
            if launched["cancelled"]:
                parsed = parse_failure(
                    "cancelled",
                    "local process group signaled; remote cancellation not guaranteed",
                )
            elif launched["timed_out"]:
                parsed = parse_failure(
                    "timeout",
                    "local process group signaled; remote cancellation not guaranteed",
                )
            else:
                parsed = parse_omp(launched["stdout"]) if runtime == "omp" else parse_claude(launched["stdout"])
                if launched["exit_code"] != 0 and parsed["ok"]:
                    parsed = parse_failure(
                        "nonzero_exit",
                        f"exit {launched['exit_code']}",
                        parsed.get("text") if isinstance(parsed.get("text"), str) else None,
                    )
            stage_status = "cancelled" if launched["cancelled"] else ("completed" if parsed["ok"] else "failed")
            stage_record: dict[str, object] = {
                "id": stage_id,
                "status": stage_status,
                "handoffs": handoff_text(stage),
                "reason": parsed.get("reason"),
                "detail": parsed.get("detail"),
                "exit_code": launched["exit_code"],
                "timed_out": launched["timed_out"],
                "cancelled": launched["cancelled"],
                "termination": launched["termination"],
                "stdout_sha256": sha256_bytes(launched["stdout"]),
                "stderr_sha256": sha256_bytes(launched["stderr"]),
                "prompt_sha256": sha256_bytes(composed_bytes),
                "model": model_receipt(parsed),
                "accounting": usage_receipt(parsed),
                "native_session": {
                    "id": parsed.get("session_id"),
                    "status": parsed.get("session_status", "unknown"),
                    "persistence_disabled_requested": True,
                    "persistence_disabled_observed": "unknown",
                },
                "stop_reason": parsed.get("stop_reason"),
            }
            if isinstance(parsed.get("text"), str) and parsed["text"].strip() and not launched["cancelled"]:
                extracted_name = "output.md" if parsed["ok"] else "extracted.md"
                write_text(stage_dir / extracted_name, parsed["text"].rstrip() + "\n")
                stage_record["extracted"] = extracted_name
                stage_record["extracted_sha256"] = sha256_bytes(
                    (stage_dir / extracted_name).read_bytes()
                )
                if parsed["ok"]:
                    accepted[stage_id] = parsed["text"]
                    stage_record["artifact"] = f"stages/{stage_id}/output.md"
                    stage_record["artifact_sha256"] = stage_record["extracted_sha256"]
            write_json(stage_dir / "stage.json", stage_record)
            stage_rows.append(
                {
                    "id": stage_id,
                    "status": stage_record["status"],
                    "handoffs": handoff_text(stage),
                    "artifact": stage_record.get("artifact"),
                    "artifact_sha256": stage_record.get("artifact_sha256"),
                    "reason": parsed.get("reason"),
                }
            )
            receipt_stages.append(stage_record)
            state["stages"][stage_id] = {
                "status": stage_status,
                "reason": parsed.get("reason"),
            }
            if launched["cancelled"]:
                state["status"] = "cancelled"
                state["error"] = {"reason": "cancelled", "detail": parsed.get("detail")}
                code = 130
                break
            if not parsed["ok"]:
                state["status"] = "failed"
                state["error"] = {"reason": parsed.get("reason"), "detail": parsed.get("detail")}
                break
        else:
            state["status"] = "completed"
            state["error"] = None
            code = 0
        if state["status"] == "cancelled":
            code = 130
        elif state["status"] != "completed":
            code = 1
    except KeyboardInterrupt:
        state["status"] = "cancelled"
        state["error"] = {"reason": "cancelled", "detail": "KeyboardInterrupt"}
        code = 130
    except Exception as exc:
        state["status"] = "failed"
        detail = type(exc).__name__
        if isinstance(exc, OSError) and exc.errno is not None:
            detail += f" (errno {exc.errno})"
        state["error"] = {"reason": "unexpected_error", "detail": detail}
        code = 1
    # Terminal persistence is a short non-interruptible section. command_run restores
    # the caller's settings even if a storage write fails.
    ignore_cancel_signals()
    finalize_declared_stages(workflow, state, output_dir, stage_rows, receipt_stages)
    state["finished_at"] = now_iso()
    state["updated_at"] = state["finished_at"]
    state["current_stage"] = None
    write_json(state_path, state)
    write_text(output_dir / "summary.md", summary_text(state, stage_rows))
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "workflow_id": workflow["id"],
        "status": state["status"],
        "business_acceptance": False,
        "semantic_verification": False,
        "human_approval": {"performed": False, "bypassed": False},
        "canonical_representation": "manifest+prompts interpreted by scripts/run_workflow.py",
        "generated_workflow_code": False,
        "native_workflow_wrapper": False,
        "runtime": {
            "requested": runtime,
            "executable": runtime,
            "version": redact_home(version),
            "fallback": False,
        },
        "hashes": {
            "script_sha256": script_sha256,
            "workflow_sha256": sha256_bytes(workflow_bytes),
            "input_sha256": sha256_bytes(input_bytes),
            "input": display_path(input_path, project_root()),
            "prompt_sha256": {
                stage["id"]: sha256_bytes(prompt_bytes[stage["id"]]) for stage in workflow["stages"]
            },
        },
        "isolation": {
            "hermetic": False,
            "sandbox": False,
            "full_isolation": False,
            "full_accounting": False,
            "controlled_ambient_config": False,
            "notes": capability_notes(runtime),
        },
        "command": {
            "argv": display_argv(
                adapter_argv(
                    runtime,
                    executable,
                    "<output-dir>/task-cwd",
                    "<output-dir>/snapshots/claude-mcp.json" if runtime == "claude" else None,
                    timeout,
                ),
                runtime,
                executable,
                output_dir,
            ),
            "resolved_executable_recorded": False,
            "prompt_transport": "stdin",
            "prompt_text_included": False,
            "environment_recorded": False,
        },
        "stages": receipt_stages,
        "usage": {
            "summed": False,
            "missing_is_zero": False,
            "note": "Per-stage native figures are not added. Missing is unknown, not zero.",
        },
    }
    write_json(output_dir / "receipt.json", receipt)
    print(f"status: {state['status']}")
    print(f"output_dir: {output_dir}")
    print("summary: summary.md")
    print("receipt: receipt.json")
    print("business_acceptance: false")
    if state.get("error"):
        print(f"reason: {state['error'].get('reason')}", file=sys.stderr)
    return code


def command_validate(args: argparse.Namespace) -> int:
    workflow, _data = load_workflow(args.workflow)
    sys.stdout.write(format_validate(workflow))
    return 0


def command_plan(args: argparse.Namespace) -> int:
    timeout = check_timeout(args.timeout_seconds)
    workflow, workflow_bytes = load_workflow(args.workflow)
    input_path, input_bytes = load_input(args.input)
    prompt_bytes = read_prompt_bytes(workflow)
    executable = executable_for(args.runtime)
    version = redact_home(cli_version(executable))
    mcp_display = "<output-dir>/snapshots/claude-mcp.json" if args.runtime == "claude" else None
    argv = adapter_argv(args.runtime, args.runtime, "<output-dir>/task-cwd", mcp_display, timeout)
    prompt_texts = {stage["id"]: prompt_bytes[stage["id"]].decode("utf-8") for stage in workflow["stages"]}
    sys.stdout.write(
        format_plan(
            workflow,
            args.runtime,
            version,
            display_path(input_path, project_root()),
            sha256_bytes(input_bytes),
            sha256_bytes(workflow_bytes),
            sha256_bytes(script_path().read_bytes()),
            {stage["id"]: sha256_bytes(prompt_bytes[stage["id"]]) for stage in workflow["stages"]},
            timeout,
            argv,
            input_bytes.decode("utf-8"),
            prompt_texts,
        )
    )
    return 0


def command_run(args: argparse.Namespace) -> int:
    if os.name != "posix":
        raise PreflightError(
            "run requires a POSIX system; Windows is not supported, and SIGKILL cannot be handled"
        )
    timeout = check_timeout(args.timeout_seconds)
    workflow, workflow_bytes = load_workflow(args.workflow)
    input_path, input_bytes = load_input(args.input)
    prompt_bytes = read_prompt_bytes(workflow)
    executable = executable_for(args.runtime)
    version = cli_version(executable)
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir
    assert_output_outside(output_dir)
    installed: list[tuple[int, object]] = []
    try:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            previous = signal.getsignal(sig)
            installed.append((sig, previous))
            if previous != signal.SIG_IGN:
                signal.signal(sig, raise_cancel)
        return execute_run(
            workflow,
            workflow_bytes,
            args.runtime,
            executable,
            version,
            input_path,
            input_bytes,
            prompt_bytes,
            output_dir,
            timeout,
        )
    finally:
        for sig, previous in installed:
            signal.signal(sig, previous)



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="run_workflow.py")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="check a workflow without a model call or file writes")
    validate.add_argument("workflow")
    plan = sub.add_parser("plan", help="print the selected command and provenance gaps without writing")
    plan.add_argument("workflow")
    plan.add_argument("--runtime", required=True, choices=("omp", "claude"))
    plan.add_argument("--input", required=True)
    plan.add_argument("--timeout-seconds", type=int)
    run = sub.add_parser("run", help="launch the selected CLI; explicit cost authorization")
    run.add_argument("workflow")
    run.add_argument("--runtime", required=True, choices=("omp", "claude"))
    run.add_argument("--input", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--timeout-seconds", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            return command_validate(args)
        if args.command == "plan":
            return command_plan(args)
        if args.command == "run":
            return command_run(args)
    except (ValidationError, PreflightError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        return 130
    print(f"unsupported command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
