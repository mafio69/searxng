"""Mandatory offline checks before commit; never load environment files."""

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main(root=ROOT):
    local = root / ".local"
    logs = local / "logs" / "checks"
    logs.mkdir(parents=True, exist_ok=True)
    child_environment = os.environ.copy()
    child_environment["PYTHONPATH"] = os.pathsep.join([
        str(local / "tools" / "ruff"), str(local / "python"),
    ])
    python = [sys.executable, "-X", "pycache_prefix=.local/cache/pycache"]
    checks = [
        ("ruff", python + ["-m", "ruff", "check", "--config", "ruff.toml", "mcp", "scripts", "tests"]),
        ("tracked-files", python + ["scripts/check_tracked_files.py"]),
        ("backend", python + ["-c", (
            "import logging,sys,unittest;logging.disable(logging.CRITICAL);"
            "suite=unittest.defaultTestLoader.discover('tests');"
            "result=unittest.TextTestRunner(verbosity=1).run(suite);"
            "sys.exit(not result.wasSuccessful())"
        )]),
        ("frontend", ["npm", "--prefix", "web", "test"]),
        ("build", ["npm", "--prefix", "web", "run", "build"]),
        ("diff", ["git", "diff", "--check"]),
        ("staged-diff", ["git", "diff", "--cached", "--check"]),
    ]
    for name, command in checks:
        try:
            result = subprocess.run(command, cwd=root, env=child_environment,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except OSError:
            print(f"{name}: FAIL (required tool unavailable)", flush=True)
            return 1
        report = logs / f"{name}.log"
        report.write_text(result.stdout, encoding="utf-8")
        print(f"{name}: {'PASS' if result.returncode == 0 else 'FAIL'}", flush=True)
        if result.returncode:
            print(f"Details: {report.relative_to(root)}", flush=True)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
