#!/usr/bin/env python3
"""Copy experiment 01 from a local hub clone and keep standalone paths working.

The hub repository is https://github.com/rahul-bachina/copilot-agent-experiments.
This script copies experiments/01-foi-complaint-triage/ onto the repository root,
refreshes the shared manifest schema and the catalogue page, then rewrites
hub-relative paths. Paths listed in .sync-ignore are left untouched.
"""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path

HUB_EXPERIMENT = "experiments/01-foi-complaint-triage"
REPO_URL = "https://github.com/rahul-bachina/foi-complaint-triage-copilot-agent"
SCHEMA_ID = (
    f"{REPO_URL}/blob/main/schema/triage_output.schema.json"
)
BANNER_MARK = "<!-- standalone-copy -->"

EXTRA_FILES = (
    ("LICENSE", "LICENSE"),
    ("schemas/agent-manifest.schema.json", "schemas/agent-manifest.schema.json"),
    ("docs/autonomy-levels.md", "docs/autonomy-levels.md"),
    (
        "docs-site/docs/experiments/01-foi-complaint-triage.md",
        "docs/catalogue-page.md",
    ),
)

UPSTREAM_README = "UPSTREAM.md"


def load_ignore(path: Path) -> list[str]:
    patterns: list[str] = []
    if not path.exists():
        return patterns
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _normalise(rel: str) -> str:
    """Normalise a repo-relative path without stripping meaningful leading dots."""
    rel = rel.replace("\\", "/").lstrip("/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def is_ignored(rel: str, patterns: list[str]) -> bool:
    """Return True when a repo-relative path is standalone-only."""
    rel = _normalise(rel)
    name = rel.rsplit("/", 1)[-1]
    for pattern in patterns:
        if pattern.endswith("/"):
            prefix = pattern[:-1]
            if rel == prefix or rel.startswith(pattern):
                return True
            continue
        if any(token in pattern for token in "*?["):
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(name, pattern):
                return True
            continue
        if rel == pattern:
            return True
    return False


def _copy_file(source: Path, target: Path, dry_run: bool) -> None:
    if dry_run:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_from_hub(hub: Path, dest: Path, patterns: list[str], dry_run: bool) -> list[str]:
    experiment = hub / HUB_EXPERIMENT
    if not experiment.is_dir():
        raise SystemExit(f"Hub experiment folder not found: {experiment}")

    copied: list[str] = []
    for source in sorted(experiment.rglob("*")):
        if not source.is_file():
            continue
        rel = source.relative_to(experiment).as_posix()
        if rel == "README.md" or is_ignored(rel, patterns):
            continue
        _copy_file(source, dest / rel, dry_run)
        copied.append(rel)

    readme = experiment / "README.md"
    if readme.is_file() and not is_ignored(UPSTREAM_README, patterns):
        _copy_file(readme, dest / UPSTREAM_README, dry_run)
        copied.append(UPSTREAM_README)

    for src_rel, dest_rel in EXTRA_FILES:
        if is_ignored(dest_rel, patterns):
            continue
        source = hub / src_rel
        if not source.is_file():
            raise SystemExit(f"Required hub file missing: {src_rel}")
        _copy_file(source, dest / dest_rel, dry_run)
        copied.append(dest_rel)
    return copied


def _replace_once_block(text: str, old: str, new: str, label: str) -> str:
    if new in text and old not in text:
        return text
    if old not in text:
        raise SystemExit(f"Standalone rewrite could not find the expected block in {label}")
    return text.replace(old, new, 1)


def apply_standalone_fixes(dest: Path, dry_run: bool = False) -> list[str]:
    """Rewrite hub-relative imports and paths. Idempotent."""
    changed: list[str] = []

    def rewrite(rel: str, mutator) -> None:
        path = dest / rel
        if not path.is_file():
            raise SystemExit(f"Expected file missing after copy: {rel}")
        original = path.read_text(encoding="utf-8")
        updated = mutator(original)
        if updated != original:
            changed.append(rel)
            if not dry_run:
                path.write_text(updated, encoding="utf-8")

    def manifest(text: str) -> str:
        text = text.replace(
            '$schema: "../../../schemas/agent-manifest.schema.json"',
            '$schema: "schemas/agent-manifest.schema.json"',
        )
        text = text.replace(
            'repository: "https://github.com/rahul-bachina/copilot-agent-experiments"',
            f'repository: "{REPO_URL}"',
        )
        text = text.replace(
            'experiment_path: "experiments/01-foi-complaint-triage"',
            'experiment_path: "."',
        )
        if 'schemas/agent-manifest.schema.json"' not in text:
            raise SystemExit("Manifest schema path was not rewritten")
        if "../../../" in text:
            raise SystemExit("Manifest still contains a hub-relative path")
        return text

    def output_schema(text: str) -> str:
        for old in (
            "https://github.com/rahulbachina/copilot-agent-experiments/experiments/01-foi-complaint-triage/schema/triage_output.schema.json",
            "https://github.com/rahul-bachina/copilot-agent-experiments/experiments/01-foi-complaint-triage/schema/triage_output.schema.json",
        ):
            text = text.replace(old, SCHEMA_ID)
        return text

    def triage_agent(text: str) -> str:
        old = (
            "from models import TriageOutput\n"
            "from prompts import SYSTEM_PROMPT, get_user_prompt\n"
            "from mock_responses import generate_mock_response\n"
        )
        new = (
            "try:\n"
            "    from .models import TriageOutput\n"
            "    from .prompts import SYSTEM_PROMPT, get_user_prompt\n"
            "    from .mock_responses import generate_mock_response\n"
            "except ImportError:  # python src/triage_agent.py\n"
            "    from models import TriageOutput\n"
            "    from prompts import SYSTEM_PROMPT, get_user_prompt\n"
            "    from mock_responses import generate_mock_response\n"
        )
        return _replace_once_block(text, old, new, "src/triage_agent.py")

    def tests(text: str) -> str:
        old = (
            "import json\n"
            "import sys\n"
            "from pathlib import Path\n"
            "\n"
            "import pytest\n"
            "\n"
            "sys.path.insert(0, str(Path(__file__).parent.parent / \"src\"))\n"
            "\n"
            "from models import TriageOutput, Classification, Flags, ExtractedAsk\n"
            "from mock_responses import (\n"
        )
        new = (
            "import json\n"
            "\n"
            "import pytest\n"
            "\n"
            "from src.models import TriageOutput, Classification, Flags, ExtractedAsk\n"
            "from src.mock_responses import (\n"
        )
        text = _replace_once_block(text, old, new, "tests/test_triage_agent.py")
        return text.replace(
            "from triage_agent import triage, validate_output\n",
            "from src.triage_agent import triage, validate_output\n",
        )

    def evaluate(text: str) -> str:
        old = (
            'sys.path.insert(0, str(Path(__file__).parent.parent / "src"))\n'
            "from triage_agent import triage\n"
        )
        new = (
            "ROOT = Path(__file__).resolve().parents[1]\n"
            "if str(ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(ROOT))\n"
            "from src.triage_agent import triage\n"
        )
        text = _replace_once_block(text, old, new, "eval/evaluate.py")
        text = text.replace(
            "Run with Azure AI (requires credentials)",
            "Run with Microsoft Foundry (requires credentials)",
        )
        text = text.replace(
            "Use live Azure AI instead of mock mode",
            "Use live Microsoft Foundry instead of mock mode",
        )
        return text

    def diagram(text: str) -> str:
        text = text.replace(
            "ax.text(11, 7.1, 'AZURE'",
            "ax.text(11, 7.1, 'MICROSOFT'",
        )
        text = text.replace(
            "ax.text(11, 6.5, 'AI Foundry'",
            "ax.text(11, 6.5, 'Foundry'",
        )
        return text

    def upstream(text: str) -> str:
        text = text.replace("[LICENSE](../../LICENSE)", "[LICENSE](LICENSE)")
        text = text.replace(
            "cd experiments/01-foi-complaint-triage\n",
            "# In this standalone repository, run commands from the repository root.\n",
        )
        text = text.replace(
            "experiments/01-foi-complaint-triage/\n",
            "./\n",
        )
        text = text.replace(
            "`.github/workflows/experiment-01-tests.yml`",
            "`.github/workflows/ci.yml`",
        )
        banner = (
            f"{BANNER_MARK}\n"
            "> Standalone copy of the hub experiment README. "
            "Commands run from the repository root. "
            "The published overview is [README.md](README.md).\n\n"
        )
        if BANNER_MARK not in text:
            text = banner + text
        return text

    def catalogue(text: str) -> str:
        banner = (
            f"{BANNER_MARK}\n"
            "> Catalogue page copied from the experiments hub. "
            "In this repository the same files live at the root, "
            "so ignore any instruction to `cd experiments/01-foi-complaint-triage`.\n\n"
        )
        if BANNER_MARK not in text:
            text = banner + text
        return text

    def requirements(text: str) -> str:
        if "pyyaml" in text.lower():
            return text
        return text.rstrip() + (
            "\n\n# Manifest validation in this standalone repository\npyyaml>=6.0\n"
        )

    rewrite("requirements.txt", requirements)
    rewrite("agent-manifest.yaml", manifest)
    rewrite("schema/triage_output.schema.json", output_schema)
    rewrite("src/triage_agent.py", triage_agent)
    rewrite("tests/test_triage_agent.py", tests)
    rewrite("eval/evaluate.py", evaluate)
    rewrite("docs/generate_diagram.py", diagram)
    rewrite(UPSTREAM_README, upstream)
    rewrite("docs/catalogue-page.md", catalogue)
    return changed


def regenerate_diagram(dest: Path) -> None:
    script = dest / "docs" / "generate_diagram.py"
    subprocess.run([sys.executable, str(script)], cwd=dest, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hub", type=Path, help="Path to a clone of the public hub")
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Standalone repository root (default: this repo)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--regenerate-diagram",
        action="store_true",
        help="Redraw docs/architecture_diagram.png after the label fix",
    )
    args = parser.parse_args(argv)
    hub = args.hub.resolve()
    dest = args.dest.resolve()
    patterns = load_ignore(dest / ".sync-ignore")
    copied = copy_from_hub(hub, dest, patterns, args.dry_run)
    changed = apply_standalone_fixes(dest, dry_run=args.dry_run)
    print(f"Copied {len(copied)} file(s); rewrote {len(changed)} file(s).")
    if args.dry_run:
        return 0
    if args.regenerate_diagram:
        regenerate_diagram(dest)
        print("Regenerated docs/architecture_diagram.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
