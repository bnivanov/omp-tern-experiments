"""Real local subprocess/signal boundaries; no installed agent CLI or model calls."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("workbench_lifecycle_runner", ROOT / "scripts/run_workflow.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


@unittest.skipUnless(os.name == "posix", "runner execution supports POSIX only")
class SubprocessLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="workbench-lifecycle-test-")
        self.addCleanup(self.scratch.cleanup)
        self.output = Path(self.scratch.name) / "run"
        self.args = argparse.Namespace(
            workflow=str(ROOT / "workflows/proposal-storyline.workflow.json"),
            input=str(ROOT / "examples/synthetic-brief.json"),
            runtime="omp",
            output_dir=str(self.output),
            timeout_seconds=30,
        )
        self.handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        self.addCleanup(self.restore_handlers)

    def restore_handlers(self):
        for sig, handler in self.handlers.items():
            signal.signal(sig, handler)

    def run_local(self, argv):
        # Substitute only the native command boundary; the child and signals are real.
        with (
            patch.object(RUNNER, "executable_for", return_value=sys.executable),
            patch.object(RUNNER, "cli_version", return_value="local Python subprocess fixture"),
            patch.object(RUNNER, "adapter_argv", return_value=argv),
        ):
            return RUNNER.command_run(self.args)

    def read_receipt(self):
        return json.loads((self.output / "receipt.json").read_text())

    def test_cancel_during_spawn_reaps_child_and_finalizes_all_stages(self):
        original_popen = subprocess.Popen
        original_signal = signal.signal
        interrupted_ignore = False
        children = []

        def cancel_after_spawn(*args, **kwargs):
            child = original_popen(*args, **kwargs)
            if kwargs.get("start_new_session"):
                children.append(child)
                os.kill(os.getpid(), signal.SIGTERM)
            return child

        def cancel_as_cleanup_defers_signals(sig, handler):
            nonlocal interrupted_ignore
            if handler == signal.SIG_IGN and not interrupted_ignore:
                interrupted_ignore = True
                os.kill(os.getpid(), signal.SIGTERM)
            return original_signal(sig, handler)

        try:
            with (
                patch.object(RUNNER.subprocess, "Popen", side_effect=cancel_after_spawn),
                patch.object(RUNNER.signal, "signal", side_effect=cancel_as_cleanup_defers_signals),
            ):
                code = self.run_local([sys.executable, "-c", "import time; time.sleep(60)"])
            self.assertEqual(code, 130)
            receipt = self.read_receipt()
            self.assertEqual(receipt["status"], "cancelled")
            self.assertEqual({row["id"]: row["status"] for row in receipt["stages"]}, {"storyline": "cancelled", "critique": "not_started"})
            for stage in ("storyline", "critique"):
                self.assertTrue((self.output / "stages" / stage / "stage.json").exists())
                self.assertFalse((self.output / "stages" / stage / "output.md").exists())
            self.assertEqual(len(children), 1)
            self.assertIsNotNone(children[0].returncode)
            self.assertLess(children[0].returncode, 0)
            self.assertEqual({sig: signal.getsignal(sig) for sig in self.handlers}, self.handlers)
        finally:
            for child in children:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=5)

    def test_repeated_signal_cannot_interrupt_terminal_receipt(self):
        original_write = RUNNER.write_json

        def interrupt_receipt(path, value):
            if path.name == "receipt.json":
                os.kill(os.getpid(), signal.SIGTERM)
                os.kill(os.getpid(), signal.SIGTERM)
            return original_write(path, value)

        with patch.object(RUNNER, "write_json", side_effect=interrupt_receipt):
            code = self.run_local([str(self.output.parent / "missing-executable")])
        self.assertEqual(code, 1)
        receipt = self.read_receipt()
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual({row["id"]: row["status"] for row in receipt["stages"]}, {"storyline": "failed", "critique": "not_started"})
        self.assertTrue((self.output / "summary.md").exists())
        self.assertEqual({sig: signal.getsignal(sig) for sig in self.handlers}, self.handlers)

    def test_inherited_ignored_hangup_does_not_cancel_the_child(self):
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        original_popen = subprocess.Popen

        def hangup_after_spawn(*args, **kwargs):
            child = original_popen(*args, **kwargs)
            if kwargs.get("start_new_session"):
                os.kill(os.getpid(), signal.SIGHUP)
            return child

        with patch.object(RUNNER.subprocess, "Popen", side_effect=hangup_after_spawn):
            code = self.run_local([sys.executable, "-c", "raise SystemExit(7)"])
        self.assertEqual(code, 1)
        self.assertEqual(self.read_receipt()["status"], "failed")
        self.assertEqual(signal.getsignal(signal.SIGHUP), signal.SIG_IGN)

    def test_spawn_error_does_not_publish_resolved_home_path(self):
        missing = Path.home() / "workbench-regression-missing" / "omp"
        code = self.run_local([str(missing)])
        self.assertEqual(code, 1)
        for relative in ("state.json", "receipt.json", "stages/storyline/stage.json"):
            self.assertNotIn(str(Path.home()), (self.output / relative).read_text())
        self.assertEqual(self.read_receipt()["stages"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
