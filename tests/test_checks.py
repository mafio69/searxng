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
from check_tracked_files import scan_tracked_files


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
                self.assertEqual(len(commands), 7)
                self.assertIn("scripts/check_tracked_files.py", commands[1])
                self.assertEqual(commands[-1], ["git", "diff", "--cached", "--check"])

    def test_missing_tool_blocks_the_gate(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local/tmp") as directory:
            with patch("check_project.subprocess.run", side_effect=FileNotFoundError) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(Path(directory)), 1)
                self.assertEqual(run.call_count, 1)

    def test_repository_tracked_files_are_clean(self):
        self.assertEqual(scan_tracked_files(ROOT), [])

    def test_scanner_detects_forbidden_files_and_synthetic_credentials_without_leaking_values(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local/tmp") as directory:
            root = Path(directory)
            (root / ".env.example").write_text("SEARXNG_SECRET=synthetic_value\n", encoding="utf-8")
            (root / ".env.dist").write_text("SERVICE_PASSWORD=c3ludGhldGlj==\n", encoding="utf-8")
            (root / "searxng-settings.example.yml").write_text("  secret_key: synthetic_hex_value\n", encoding="utf-8")
            (root / "sample.txt").write_text("pplx-" + "1234567890abcdef1234\n", encoding="utf-8")
            (root / "opencode.json").write_text("pplx-ignored-in-policy-file\n", encoding="utf-8")
            findings = scan_tracked_files(
                root,
                [
                    ".env",
                    "searxng-settings.yml",
                    "project.geany",
                    "certs/server.pem",
                    ".env.example",
                    ".env.dist",
                    "searxng-settings.example.yml",
                    "sample.txt",
                    "opencode.json",
                ],
            )
            self.assertEqual(
                findings,
                [
                    ".env: forbidden_tracked_file",
                    "searxng-settings.yml: forbidden_tracked_file",
                    "project.geany: forbidden_tracked_file",
                    "certs/server.pem: forbidden_tracked_file",
                    ".env.example:1: non_empty_env_template",
                    ".env.dist:1: non_empty_env_template",
                    "searxng-settings.example.yml:1: populated_searxng_secret_key",
                    "sample.txt:1: perplexity_key",
                ],
            )
            self.assertNotIn("synthetic_value", "\n".join(findings))
            self.assertNotIn("c3ludGhldGlj==", "\n".join(findings))
            self.assertNotIn("1234567890abcdef1234", "\n".join(findings))

    def test_scanner_inspects_git_index_when_working_copy_is_cleaned_or_deleted(self):
        import subprocess

        with tempfile.TemporaryDirectory(dir=ROOT / ".local/tmp") as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            key = "pplx-" + "1234567890abcdef1234"
            (root / "cleaned.txt").write_text(key + "\n", encoding="utf-8")
            (root / "deleted.txt").write_text(key + "\n", encoding="utf-8")
            (root / "opencode.json").write_text(key + "\n", encoding="utf-8")
            (root / ".opencode").mkdir()
            (root / ".opencode" / "local.json").write_text(key + "\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "cleaned.txt", "deleted.txt", "opencode.json", ".opencode/local.json"],
                cwd=root,
                check=True,
            )
            (root / "cleaned.txt").write_text("safe working tree content\n", encoding="utf-8")
            (root / "deleted.txt").unlink()
            findings = scan_tracked_files(root)
            self.assertEqual(
                findings,
                [
                    "cleaned.txt:1: perplexity_key",
                    "deleted.txt:1: perplexity_key",
                ],
            )
