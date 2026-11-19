"""The hub sync must leave standalone files alone."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sync():
    spec = importlib.util.spec_from_file_location(
        "sync_from_hub", ROOT / "scripts" / "sync_from_hub.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standalone_files_are_ignored():
    sync = _sync()
    patterns = sync.load_ignore(ROOT / ".sync-ignore")
    protected = [
        "README.md",
        "llms.txt",
        "llms-full.txt",
        "CITATION.cff",
        "SECURITY.md",
        "CONTRIBUTING.md",
        ".github/workflows/ci.yml",
        ".github/workflows/sync-from-hub.yml",
        ".github/ISSUE_TEMPLATE/request-an-adaptation.yml",
        ".github/social-preview.png",
        "site/index.html",
        "scripts/sync_from_hub.py",
        "foundry/README.md",
    ]
    for rel in protected:
        assert sync.is_ignored(rel, patterns), rel


def test_experiment_files_are_not_ignored():
    sync = _sync()
    patterns = sync.load_ignore(ROOT / ".sync-ignore")
    shipped = [
        "src/triage_agent.py",
        "tests/test_triage_agent.py",
        "agent-manifest.yaml",
        "schema/triage_output.schema.json",
        "eval/synthetic_dataset.json",
        "copilot-studio/README.md",
        "docs/security-and-permissions.md",
        "UPSTREAM.md",
    ]
    for rel in shipped:
        assert not sync.is_ignored(rel, patterns), rel
