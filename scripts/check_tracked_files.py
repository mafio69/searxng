"""Scan Git-tracked files for forbidden filenames and leaked credentials."""

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ENV_TEMPLATES = {
    ".env.example",
    ".env.dist",
    ".env.test.example",
    ".env.testing.example",
}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".geany"}
FORBIDDEN_NAME_PARTS = ("secret", "token", "credential", "id_rsa", "id_ed25519")
SKIP_CONTENT_PATHS = {"opencode.json"}
CREDENTIAL_PATTERNS = (
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("perplexity_key", re.compile(r"\bpplx-[A-Za-z0-9]{16,}\b")),
    (
        "api_key_token",
        re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    ),
    (
        "populated_env_secret",
        re.compile(r"^(?:SEARXNG_SECRET|PPLX_API_KEY|MCP_AUTH_TOKEN)\s*=\s*(?!\$\{)[^\s#]+"),
    ),
    (
        "populated_searxng_secret_key",
        re.compile(r'^\s*secret_key:\s*(?!""\s*$|\'\'\s*$)\S+'),
    ),
)


def list_tracked_files(root):
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return [entry for entry in result.stdout.split("\0") if entry]


def is_forbidden_env_file(name):
    if name in ALLOWED_ENV_TEMPLATES:
        return False
    return name == ".env" or name.startswith(".env.") or name.endswith(".env.keys")


def has_forbidden_filename(relative_path):
    path = Path(relative_path)
    name = path.name.lower()
    if relative_path == "searxng-settings.yml":
        return True
    if is_forbidden_env_file(name):
        return True
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return True
    return any(part in name for part in FORBIDDEN_NAME_PARTS)


def is_skipped_policy_file(relative_path):
    return relative_path in SKIP_CONTENT_PATHS or relative_path.startswith(".opencode/")


def is_populated_template_line(relative_path, line):
    if relative_path not in ALLOWED_ENV_TEMPLATES:
        return False
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    return not stripped.endswith("=")


def scan_line(relative_path, line):
    if is_populated_template_line(relative_path, line):
        return "non_empty_env_template"
    for code, pattern in CREDENTIAL_PATTERNS:
        if pattern.search(line):
            return code
    return None


def scan_tracked_files(root=ROOT, tracked_files=None):
    files = list_tracked_files(root) if tracked_files is None else tracked_files
    findings = []
    for relative_path in files:
        if has_forbidden_filename(relative_path):
            findings.append(f"{relative_path}: forbidden_tracked_file")
            continue
        if is_skipped_policy_file(relative_path):
            continue
        file_path = root / relative_path
        if not file_path.is_file():
            continue
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            reason = scan_line(relative_path, line)
            if reason:
                findings.append(f"{relative_path}:{number}: {reason}")
    return findings


def main(root=ROOT):
    findings = scan_tracked_files(root)
    for finding in findings:
        print(finding, flush=True)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
