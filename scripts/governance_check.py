#!/usr/bin/env python3
"""Governance checks for the standalone repository.

Fails if:
- the retired product name appears, except on a line that says it was formerly used
- a likely secret is committed
- LICENSE is missing or is not the MIT licence
- a hub-relative ../../.. path has been copied in
- .sync-ignore no longer protects the standalone files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETIRED_BRAND = "Azure AI" + " Foundry"
TEXT_SUFFIXES = {
    ".py", ".md", ".yml", ".yaml", ".json", ".txt", ".cff",
    ".html", ".toml", ".ini", ".cfg", ".gitignore",
}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache"}

SECRET_PATTERNS = (
    (re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "GitHub personal access token"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "GitHub token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{20,}\b"), "API key"),
    (re.compile(r"AccountKey=[A-Za-z0-9+/=]{20,}"), "storage account key"),
    (
        re.compile(
            r"(?i)(?:api[_-]?key|client[_-]?secret|password|secret)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
        "assigned secret",
    ),
)
PLACEHOLDER = re.compile(
    r"(?i)your[-_ ]|example|placeholder|changeme|todo|redacted|<[^>]+>"
)

REQUIRED_SYNC_IGNORE = (
    "README.md",
    "llms.txt",
    "llms-full.txt",
    "CITATION.cff",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".github/",
    "site/",
    "scripts/",
)


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in {".sync-ignore", ".gitignore"} or path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def find_brand_violations(root: Path) -> list[str]:
    violations: list[str] = []
    needle = RETIRED_BRAND.lower()
    for path in iter_text_files(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if needle in line.lower() and "formerly" not in line.lower():
                rel = path.relative_to(root)
                violations.append(f"{rel}:{number}: retired product name without a formerly note")
    return violations


def find_secrets(root: Path) -> list[str]:
    findings: list[str] = []
    for path in iter_text_files(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern, label in SECRET_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                if PLACEHOLDER.search(match.group(0)):
                    continue
                rel = path.relative_to(root)
                findings.append(f"{rel}:{number}: possible {label}")
    return findings


def check_licence(root: Path) -> list[str]:
    path = root / "LICENSE"
    if not path.is_file():
        return ["LICENSE is missing"]
    text = path.read_text(encoding="utf-8")
    errors = []
    if "MIT License" not in text:
        errors.append("LICENSE does not contain the MIT licence grant")
    if "Rahul Bachina" not in text:
        errors.append("LICENSE does not name Rahul Bachina")
    return errors


def check_hub_paths(root: Path) -> list[str]:
    """Flag hub-relative paths copied into the experiment. The sync script keeps the old path so it can rewrite it."""
    errors = []
    marker = "../" * 3
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        if rel.startswith("scripts/"):
            continue
        if marker in path.read_text(encoding="utf-8"):
            errors.append(f"{rel}: hub-relative path")
    return errors


def check_sync_ignore(root: Path) -> list[str]:
    path = root / ".sync-ignore"
    if not path.is_file():
        return [".sync-ignore is missing"]
    text = path.read_text(encoding="utf-8")
    return [f".sync-ignore does not list {item}" for item in REQUIRED_SYNC_IGNORE if item not in text]


def main() -> int:
    errors = [
        *check_licence(ROOT),
        *check_sync_ignore(ROOT),
        *check_hub_paths(ROOT),
        *find_brand_violations(ROOT),
        *find_secrets(ROOT),
    ]
    if errors:
        print("Governance checks failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Governance checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
