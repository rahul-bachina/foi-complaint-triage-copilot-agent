#!/usr/bin/env python3
"""Draw the 1280x640 GitHub social preview card."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".github" / "social-preview.png"
WIDTH, HEIGHT = 1280, 640

FONT = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"
FONT_MEDIUM = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0B1F33")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 18, HEIGHT), fill="#1F6F6A")
    draw.rectangle((0, HEIGHT - 8, WIDTH, HEIGHT), fill="#1F6F6A")

    title = ImageFont.truetype(FONT, 64)
    subtitle = ImageFont.truetype(FONT, 40)
    body = ImageFont.truetype(FONT_REGULAR, 28)
    footer = ImageFont.truetype(FONT_MEDIUM, 26)

    draw.text((72, 150), "FOI and Complaint Triage", font=title, fill="#F4F7FB")
    draw.text((72, 240), "AI Agent for UK Public Sector", font=subtitle, fill="#D5E4F2")
    draw.rectangle((72, 320, 280, 326), fill="#C4A35A")
    draw.text(
        (72, 360),
        "An officer decides. The agent never sends or rejects.",
        font=body,
        fill="#E7EEF5",
    )
    draw.text(
        (72, 520),
        "Copilot Studio   ·   Microsoft Foundry   ·   Autonomy A1",
        font=footer,
        fill="#9FB4C8",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG")
    if image.size != (WIDTH, HEIGHT):
        raise SystemExit(f"Unexpected size {image.size}")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
