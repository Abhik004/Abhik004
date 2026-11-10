#!/usr/bin/env python3
"""One-time setup: download fonts and subset them to printable ASCII (+ arrows)
as small .woff files in fonts/, which render_readme_cards.py embeds as base64.

  pip install fonttools
  python scripts/make_fonts.py

If a download fails, the cards still render with fallback system fonts.
Tip from the blog: check a font's name table, not its filename, before trusting
which file is italic and which is regular.
"""
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
FONTS.mkdir(exist_ok=True)
BASE = "https://github.com/google/fonts/raw/main/ofl/"
SOURCES = {
    "serif-400":  BASE + "instrumentserif/InstrumentSerif-Regular.ttf",
    "serif-400i": BASE + "instrumentserif/InstrumentSerif-Italic.ttf",
    "sans-400":   BASE + "geist/Geist%5Bwght%5D.ttf",
    "mono-400":   BASE + "geistmono/GeistMono%5Bwght%5D.ttf",
}
TEXT = "".join(chr(c) for c in range(0x20, 0x7F)) + "→↗·"

for name, url in SOURCES.items():
    ttf = FONTS / f"{name}.ttf"
    try:
        print("downloading", url)
        urllib.request.urlretrieve(url, ttf)
        subprocess.run([sys.executable, "-m", "fontTools.subset", str(ttf),
                        f"--text={TEXT}", "--flavor=woff",
                        f"--output-file={FONTS / (name + '.woff')}"], check=True)
        print("  ->", FONTS / (name + ".woff"), (FONTS / (name + ".woff")).stat().st_size // 1024, "KB")
    except Exception as e:
        print("  ! skipped", name, e)
    finally:
        ttf.unlink(missing_ok=True)
