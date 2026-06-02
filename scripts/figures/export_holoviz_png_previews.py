#!/usr/bin/env python3
"""Export HoloViz HTML previews to cropped PNG screenshots with headless Chrome.

This is a pragmatic local preview path: Bokeh's native PNG export needs a
webdriver, but Chrome itself is installed on this machine. These PNGs are for
review; canonical paper PNG/PDF generation remains in the static figure scripts.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
HTML_DIR = ROOT / "paper" / "figures" / "holoviz"
PNG_DIR = HTML_DIR / "png"
CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
]


def find_chrome() -> Path:
    for c in CHROME_CANDIDATES:
        if c.exists():
            return c
    raise SystemExit("missing Chrome/Chromium for local HoloViz screenshot export")


def crop_white(path: Path) -> None:
    im = Image.open(path).convert("RGB")
    diff = ImageChops.difference(im, Image.new("RGB", im.size, "white"))
    bbox = diff.getbbox()
    if not bbox:
        return
    left, top, right, bottom = bbox
    pad = 18
    cropped = im.crop((max(left - pad, 0), max(top - pad, 0), min(right + pad, im.width), min(bottom + pad, im.height)))
    # Drop a tiny Bokeh logo strip when toolbar is disabled but the logo remains
    # in the far top-right whitespace. Keep this conservative to avoid clipping
    # chart axes or legends.
    if cropped.width > 900:
        cropped = cropped.crop((0, 0, max(cropped.width - 28, 1), cropped.height))
    cropped.save(path)


def main() -> int:
    chrome = find_chrome()
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    for html in sorted(HTML_DIR.glob("*_holoviz.html")):
        out = PNG_DIR / f"{html.stem}.png"
        subprocess.run([
            str(chrome),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--window-size=1550,620",
            f"--screenshot={out}",
            html.resolve().as_uri(),
        ], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        crop_white(out)
        print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
