"""The public summary, landing page, and social card stay aligned."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    "FOI and complaint triage for UK public sector staff on Copilot Studio and "
    "Microsoft Foundry. An officer approves every output. The agent never sends or rejects."
)


def test_readme_opens_with_the_standalone_summary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    body = readme.split("\n", 2)[2].lstrip("\n")
    paragraph = body.split("\n\n", 1)[0].replace("\n", " ")
    assert paragraph.startswith(SUMMARY)
    assert len(SUMMARY) == 160
    assert SUMMARY.endswith(".")


def test_landing_page_quotes_the_same_summary():
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    assert html.count(SUMMARY) >= 3
    assert "SoftwareSourceCode" in html
    assert 'property="og:description"' in html
    assert "Azure AI" + " Foundry" not in html


def test_llms_txt_has_a_title_and_blockquote():
    text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith("# ")
    assert any(line.startswith("> ") for line in lines)
    assert "agent-manifest.yaml" in text
    assert "llms-full.txt" in text


def test_social_preview_is_1280_by_640():
    image = Image.open(ROOT / ".github" / "social-preview.png")
    assert image.size == (1280, 640)
