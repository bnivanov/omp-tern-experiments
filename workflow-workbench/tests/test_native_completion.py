"""Consumer-visible acceptance boundaries; no native CLI or model calls."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "run_workflow.py"
SPEC = importlib.util.spec_from_file_location("workbench_completion_runner", SOURCE)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def single_turn_events():
    message = {
        "role": "assistant",
        "content": [{"type": "text", "text": "Synthetic proposal artifact."}],
        "stopReason": "stop",
    }
    return [
        {"type": "session", "id": "synthetic-regression-session"},
        {"type": "agent_start"},
        {"type": "turn_start"},
        {"type": "message_start", "message": {"role": "assistant", "content": []}},
        {"type": "message_end", "message": message},
        {"type": "turn_end"},
        {"type": "agent_end", "messages": [copy.deepcopy(message)]},
    ]


def encode(events):
    return ("\n".join(json.dumps(event) for event in events) + "\n").encode()


class NativeCompletionBoundaryTests(unittest.TestCase):
    def test_tool_retry_and_unknown_events_never_accept_an_artifact(self):
        for event_type in (
            "tool_execution_start",
            "tool_execution_update",
            "tool_execution_end",
            "auto_retry_start",
            "unrecognized_future_event",
        ):
            with self.subTest(event_type=event_type):
                events = single_turn_events()
                events.insert(4, {"type": event_type})
                self.assertFalse(RUNNER.parse_omp(encode(events))["ok"])

    def test_second_turn_cannot_be_hidden_by_a_valid_final_message(self):
        events = single_turn_events()
        events.insert(4, {"type": "turn_start"})
        self.assertFalse(RUNNER.parse_omp(encode(events))["ok"])

    def test_prior_assistant_tool_call_cannot_be_hidden_by_final_text(self):
        events = single_turn_events()
        events.insert(4, {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [{"type": "toolCall", "name": "unapproved-tool"}],
                "stopReason": "toolUse",
            },
        })
        self.assertFalse(RUNNER.parse_omp(encode(events))["ok"])

    def test_tool_result_role_is_not_a_text_only_completion(self):
        events = single_turn_events()
        events.insert(4, {
            "type": "message_end",
            "message": {"role": "toolResult", "content": []},
        })
        self.assertFalse(RUNNER.parse_omp(encode(events))["ok"])

    def test_native_auth_error_cannot_become_an_accepted_claude_artifact(self):
        result = {
            "type": "result",
            "subtype": "success",
            "is_error": True,
            "result": "Failed to authenticate: OAuth session expired and could not be refreshed",
            "terminal_reason": "api_error",
            "stop_reason": "stop_sequence",
            "duration_api_ms": 0,
        }
        self.assertFalse(RUNNER.parse_claude(json.dumps(result).encode())["ok"])


if __name__ == "__main__":
    unittest.main()
