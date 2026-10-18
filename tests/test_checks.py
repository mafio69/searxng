import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_project import main


class ProjectCheckTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".local/tmp").mkdir(parents=True, exist_ok=True)

    def test_lint_failure_stops_the_gate(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local/tmp") as directory:
            with patch("check_project.subprocess.run", return_value=Mock(returncode=1, stdout="synthetic lint error")) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(Path(directory)), 1)
                self.assertEqual(run.call_count, 1)
                self.assertIn("ruff", run.call_args.args[0])
                self.assertNotIn("--fix", run.call_args.args[0])

    def test_success_runs_every_required_check(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local/tmp") as directory:
            with patch("check_project.subprocess.run", return_value=Mock(returncode=0, stdout="synthetic success")) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(Path(directory)), 0)
                commands = [call.args[0] for call in run.call_args_list]
                self.assertEqual(len(commands), 6)
                self.assertEqual(commands[-1], ["git", "diff", "--cached", "--check"])

    def test_missing_tool_blocks_the_gate(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local/tmp") as directory:
            with patch("check_project.subprocess.run", side_effect=FileNotFoundError) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(Path(directory)), 1)
                self.assertEqual(run.call_count, 1)
