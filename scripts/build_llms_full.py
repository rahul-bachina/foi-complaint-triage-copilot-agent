#!/usr/bin/env python3
"""Concatenate the README and key docs into llms-full.txt.

Run with --check in CI so the committed file cannot drift.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "llms-full.txt"
PARTS = (
    "README.md",
    "docs/security-and-permissions.md",
    "docs/harness-comparison.md",
    "docs/github-copilot-harness.md",
    "docs/autonomy-levels.md",
    "copilot-studio/README.md",
    "copilot-studio/system-prompt.md",
    "foundry/README.md",
)


def build() -> str:
    chunks = [
        "# FOI and Complaint Triage AI Agent for UK Public Sector\n",
        "\n",
        "This file concatenates the README and the key documents so a language model\n",
        "can read them in one fetch. The permissions manifest is `agent-manifest.yaml`.\n",
        "The output schema is `schema/triage_output.schema.json`. Evaluation data in\n",
        "`eval/synthetic_dataset.json` is synthetic. This file is not a substitute\n",
        "for the manifest when the two disagree.\n",
    ]
    for rel in PARTS:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"Missing document for llms-full.txt: {rel}")
        chunks.append(f"\n\n----- BEGIN {rel} -----\n\n")
        chunks.append(path.read_text(encoding="utf-8").rstrip())
        chunks.append(f"\n\n----- END {rel} -----\n")
    return "".join(chunks).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit 1 if llms-full.txt is stale")
    args = parser.parse_args()
    text = build()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
            print("llms-full.txt is out of date. Run: python scripts/build_llms_full.py", file=sys.stderr)
            return 1
        print("llms-full.txt is up to date")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
