"""Lokalny skaner sekretów i plików wrażliwych w repozytorium FlowKit.
Uruchom: python scripts/validate_secrets.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SENSITIVE_FILE = re.compile(
    r"(^|/)(\.env(\.(?!example$)[^/]+)?|id_rsa|id_ed25519|credentials(\.[^/]+)?|secrets?\.[^/]+"
    r"|[^/]+\.(pem|key|pfx|p12))$",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub/OpenAI/Slack token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[abprs]-[A-Za-z0-9-]{10,})\b")),
    ("URL with credentials", re.compile(r"(?i)\bhttps?://[^\s:/@]+:[^\s/@]+@")),
)
EXCLUDED_DIRS = (".git/", "tests/fixtures/", ".pytest_cache/", "__pycache__/")
EXCLUDED_FILES = {"runtime/flowkit_exec.py", "scripts/validate_secrets.py", "tests/test_runtime.py", "tests/test_flowkit.py"}


def tracked_or_repo_files() -> list[Path]:
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False)
    if res.returncode == 0 and res.stdout.strip():
        return [ROOT / line.strip() for line in res.stdout.splitlines() if line.strip()]
    return [p for p in ROOT.rglob("*") if p.is_file()]


def scan() -> list[str]:
    findings: list[str] = []
    for path in tracked_or_repo_files():
        rel = path.relative_to(ROOT).as_posix()
        if any(rel.startswith(prefix) for prefix in EXCLUDED_DIRS) or rel in EXCLUDED_FILES:
            continue
        if SENSITIVE_FILE.search(rel):
            findings.append(f"Sensitive file tracked in repo: {rel}")
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text[:match.start()].count("\n") + 1
                findings.append(f"{rel}:{line_no} — possible {label}")
    return findings


def main() -> int:
    print("Scanning repository for secrets and sensitive files...")
    findings = scan()
    if findings:
        print(f"Secret scan failed with {len(findings)} finding(s):")
        for item in findings:
            print(f"  - {item}")
        return 1
    print("Secret scan passed (0 findings)!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
