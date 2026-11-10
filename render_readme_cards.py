#!/usr/bin/env python3
"""
Renders the animated SVG cards used by README.md into cards/.

  python scripts/render_readme_cards.py            # animated cards
  STATIC=1 python scripts/render_readme_cards.py   # final frame, for screenshots

Inputs
  data/contributions.json   written daily by scripts/fetch_contributions.py
  assets/portrait.jpg       optional photo -> turned into an ASCII portrait
  fonts/*.woff              optional subset fonts (see scripts/make_fonts.py)

Only things that work inside an <img> are used: an inline <style> block with
CSS keyframes, SMIL <animate>/<animateTransform>, and base64 WOFF fonts.
"""
import base64
import datetime as dt
import json
import os
import random
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cards"
OUT.mkdir(exist_ok=True)
STATIC = os.environ.get("STATIC") == "1"

# --------------------------------------------------------------------------
# Content: edit these to change the text on the cards
# --------------------------------------------------------------------------
CFG = {
    "first": "Abhik",
    "last": "Samanta",
    "eyebrow": "M.TECH DATA SCIENCE & ENGINEERING  ·  NIT JAMSHEDPUR",
    "tagline": ["I build machine learning systems and full-stack products.",
                "B.Tech CSE from KIIT (CGPA 9.44), now deep in data science."],
    "link": "github.com/Abhik004",
    "stats": [("9.44", "CGPA, B.Tech CSE at KIIT University"),
              ("M.Tech", "Data Science and Engineering"),
              ("NIT", "Jamshedpur")],
}
TILES = [
    ("AI / ML", "Models that ship",
     "PyTorch, TensorFlow and OpenCV, with NumPy, Pandas and Scikit-learn for the data work.",
     "#2f55ff", "#ffffff"),
    ("WEB", "Full-stack apps",
     "React, Next.js, Node, Express, MongoDB and MySQL, styled with Tailwind and deployed on Vercel.",
     "#f03e2f", "#ffffff"),
    ("CORE", "Languages",
     "Python, C++, C, Java, JavaScript and TypeScript. Git and GitHub every day.",
     "#ffc619", "#111111"),
]

INK, PAPER, BLUE, GREY = "#111111", "#f2f2ef", "#2f55ff", "#6b6b66"
SERIF = "'Instrument Serif', Georgia, 'Times New Roman', serif"
SANS = "'Geist', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace"


# --------------------------------------------------------------------------
# Fonts and shared CSS
# --------------------------------------------------------------------------
def font_css():
    faces = [("serif-400.woff", "Instrument Serif", "normal"),
             ("serif-400i.woff", "Instrument Serif", "italic"),
             ("sans-400.woff", "Geist", "normal"),
             ("mono-400.woff", "Geist Mono", "normal")]
    css = ""
    for fname, family, style in faces:
        p = ROOT / "fonts" / fname
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode()
            css += ("@font-face{font-family:'%s';font-style:%s;font-weight:400;"
                    "src:url(data:font/woff;base64,%s) format('woff')}" % (family, style, b64))
    return css


FONT_CSS = font_css()

ANIM_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(18px)}}
@keyframes fade{from{opacity:0}}
@keyframes grow{from{transform:scaleY(0)}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{transform:scale(1.25)}}
@keyframes swing{from{opacity:0;transform:translateY(46px) rotate(5deg)}60%{opacity:1;transform:translateY(-8px) rotate(-1.2deg)}}
@keyframes ring{0%{opacity:.8;transform:scale(.15)}100%{opacity:0;transform:scale(1.7)}}
@keyframes nudge{50%{transform:translateX(5px)}}
@keyframes pulse{50%{opacity:.3}}
.rise{animation:rise .9s cubic-bezier(.2,.8,.2,1) both}
.fade{animation:fade .5s ease-out both}
.grow{transform-box:fill-box;transform-origin:50% 100%;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}
.pop{transform-box:fill-box;transform-origin:center;animation:pop .5s ease-out both}
.swing{transform-box:fill-box;transform-origin:50% 100%;animation:swing 1.1s cubic-bezier(.2,.8,.2,1) both}
.ring{transform-box:fill-box;transform-origin:center;animation:ring 3.2s ease-out 2.2s infinite}
.nudge{animation:nudge 2.4s ease-in-out 2.6s infinite}
.pulse{animation:pulse 2s ease-in-out infinite}
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
"""
STATIC_CSS = "*{animation:none!important}"


def svg(w, h, body, defs=""):
    css = FONT_CSS + (STATIC_CSS if STATIC else ANIM_CSS)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">\n<defs><style>{css}</style>{defs}</defs>\n'
            f'{body}\n</svg>\n')


def dly(s):
    return f'style="animation-delay:{s:.2f}s"'


def smil(markup):
    """SMIL element, dropped in STATIC mode."""
    return "" if STATIC else markup


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", OUT / name, f"({len(content) // 1024} KB)")


# --------------------------------------------------------------------------
# Contribution data
# --------------------------------------------------------------------------
def load_counts():
    p = ROOT / "data" / "contributions.json"
    if not p.exists():
        print("! data/contributions.json missing, drawing demo data")
        rnd = random.Random(7)
        today = dt.date.today()
        return {today - dt.timedelta(days=i): (0 if rnd.random() < .15 else rnd.randint(1, 14))
                for i in range(400)}
    raw = json.loads(p.read_text())
    if isinstance(raw, dict) and "days" in raw:
        raw = raw["days"]
    if isinstance(raw, dict):
        items = raw.items()
    else:
        items = [(d["date"], d.get("count", d.get("contributionCount", 0))) for d in raw]
    return {dt.date.fromisoformat(str(k)[:10]): int(v) for k, v in items}


COUNTS = load_counts()
TODAY = dt.date.today()


def stats():
    window = [TODAY - dt.timedelta(days=i) for i in range(366)]
    total = sum(COUNTS.get(d, 0) for d in window[:365])
    active = sum(1 for d in window if COUNTS.get(d, 0) > 0)
    busiest = max((COUNTS.get(d, 0) for d in window), default=0)
    d, streak = TODAY, 0
    if COUNTS.get(d, 0) == 0:
        d -= dt.timedelta(days=1)
    while COUNTS.get(d, 0) > 0:
        streak += 1
        d -= dt.timedelta(days=1)
    months = []
    y, m = TODAY.year, TODAY.month
    for _ in range(12):
        months.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    months.reverse()
    monthly = [sum(v for k, v in COUNTS.items() if (k.year, k.month) == ym and k <= TODAY)
               for ym in months]
    return dict(total=total, active=active, days=len(window), busiest=busiest,
                streak=streak, months=months, monthly=monthly)


S = stats()
fmt = lambda n: f"{n:,}"


# --------------------------------------------------------------------------
# Card 1: hero
# --------------------------------------------------------------------------
def ascii_rows(path, cols=100):
    from PIL import Image, ImageOps  # optional dependency
    im = ImageOps.autocontrast(Image.open(path).convert("L"))
    w, h = im.size
    rows = int(cols * h / w * 0.5)
    if rows > 64:
        rows = 64
        cols = int(rows * w / h * 2)
    im = im.resize((cols, rows))
    ramp = "@%#*+=-:. "
    if os.environ.get("INVERT") == "1":
        ramp = ramp[::-1]
    px = list(im.getdata())
    return [("".join(ramp[min(len(ramp) - 1, int(px[r * cols + c] / 256 * len(ramp)))]
                     for c in range(cols))) for r in range(rows)], cols


def hero():
    W, H = 1000, 420
    b = [f'<rect width="{W}" height="{H}" rx="22" fill="{PAPER}"/>']
    b.append(f'<rect x="56" y="52" width="9" height="9" rx="2" fill="{BLUE}" class="pulse"/>')
    b.append(f'<text x="76" y="61" font-family="{MONO}" font-size="12" letter-spacing="1.4" '
             f'fill="{GREY}" class="fade">{escape(CFG["eyebrow"])}</text>')
    b.append(f'<text x="52" y="172" font-family="{SERIF}" font-size="124" fill="{INK}" '
             f'letter-spacing="-3" class="rise" {dly(.1)}>{escape(CFG["first"])}</text>')
    b.append(f'<text x="52" y="282" font-family="{SERIF}" font-style="italic" font-size="124" '
             f'fill="url(#shine)" letter-spacing="-3" class="rise" {dly(.3)}>{escape(CFG["last"])}</text>')
    for i, line in enumerate(CFG["tagline"]):
        b.append(f'<text x="58" y="{328 + i * 28}" font-family="{SANS}" font-size="18" '
                 f'fill="#3d3d3a" class="rise" {dly(.6 + i * .15)}>{escape(line)}</text>')
    b.append(f'<text x="58" y="394" font-family="{MONO}" font-size="13" fill="{INK}" '
             f'class="fade" {dly(1)}>{escape(CFG["link"])}</text>')
    b.append(f'<text x="{58 + len(CFG["link"]) * 7.9 + 10}" y="394" font-family="{MONO}" '
             f'font-size="13" fill="{BLUE}" class="nudge">↗</text>')

    portrait = ROOT / "assets" / "portrait.jpg"
    if portrait.exists():
        try:
            rows, cols = ascii_rows(portrait)
            cw = min(3.8, 380 / cols)
            pitch = cw * 1.45
            fs = cw / 0.6
            x0 = 940 - cols * cw
            y0 = 36 + (340 - rows * pitch) / 2
            for i, row in enumerate(rows):
                b.append(f'<text x="{x0:.1f}" y="{y0 + i * pitch:.1f}" font-family="{MONO}" '
                         f'font-size="{fs:.2f}" fill="{INK}" textLength="{cols * cw:.1f}" '
                         f'xml:space="preserve" class="fade" {dly(.4 + i * .018)}>{escape(row)}</text>')
        except Exception as e:  # Pillow missing or bad image
            print("! portrait skipped:", e)
            portrait = None
    if not portrait or not portrait.exists():
        for i, (big, small) in enumerate(CFG["stats"]):
            y = 110 + i * 100
            b.append(f'<line x1="640" y1="{y - 54}" x2="944" y2="{y - 54}" stroke="#d6d6d0" '
                     f'class="fade" {dly(.5 + i * .15)}/>')
            b.append(f'<text x="640" y="{y + 10}" font-family="{SERIF}" font-size="56" fill="{INK}" '
                     f'class="rise" {dly(.5 + i * .15)}>{escape(big)}</text>')
            b.append(f'<text x="640" y="{y + 34}" font-family="{SANS}" font-size="14" fill="{GREY}" '
                     f'class="rise" {dly(.6 + i * .15)}>{escape(small)}</text>')

    defs = ('<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="52" y1="0" x2="472" y2="0">'
            f'<stop offset="0" stop-color="{INK}"/><stop offset=".40" stop-color="{INK}"/>'
            f'<stop offset=".5" stop-color="{BLUE}"/><stop offset=".60" stop-color="{INK}"/>'
            f'<stop offset="1" stop-color="{INK}"/>'
            + smil('<animateTransform attributeName="gradientTransform" type="translate" '
                   'from="-440 0" to="440 0" dur="5s" begin="1.6s" repeatCount="indefinite"/>')
            + '</linearGradient>')
    write("hero.svg", svg(W, H, "\n".join(b), defs))


# --------------------------------------------------------------------------
# Cards 2-4: tiles
# --------------------------------------------------------------------------
def tile(idx, label, title, body, color, fg):
    W, H = 400, 290
    cid = f"c{idx}"
    base = 3.3 + idx * .18
    lines = textwrap.wrap(body, 34)[:4]
    t = [f'<clipPath id="{cid}"><rect width="{W}" height="{H}" rx="22"/></clipPath>']
    g = [f'<g class="swing" {dly(base)}>',
         f'<rect width="{W}" height="{H}" rx="22" fill="{color}"/>',
         f'<g clip-path="url(#{cid})">',
         f'<circle cx="{W - 32}" cy="38" r="46" fill="none" stroke="{fg}" stroke-width="2" '
         f'class="ring" {dly(0)}/>']
    if not STATIC:
        g.append(f'<polygon points="0,0 70,0 20,{H} -50,{H}" fill="#fff" opacity=".2">'
                 f'<animateTransform attributeName="transform" type="translate" from="-120 0" '
                 f'to="560 0" dur="6s" begin="{base + 2:.1f}s" repeatCount="indefinite"/></polygon>')
    g.append('</g>')
    g.append(f'<text x="28" y="44" font-family="{MONO}" font-size="12" letter-spacing="1.6" '
             f'fill="{fg}">{escape(label)}</text>')
    g.append(f'<text x="{W - 40}" y="46" font-family="{MONO}" font-size="16" fill="{fg}" '
             f'class="nudge">→</text>')
    g.append(f'<text x="26" y="132" font-family="{SERIF}" font-size="52" fill="{fg}" '
             f'letter-spacing="-1">{escape(title)}</text>')
    for i, ln in enumerate(lines):
        g.append(f'<text x="28" y="{190 + i * 24}" font-family="{SANS}" font-size="15" '
                 f'fill="{fg}">{escape(ln)}</text>')
    g.append('</g>')
    write(f"tile-{idx + 1}.svg", svg(W, H, "\n".join(g), "".join(t)))


# --------------------------------------------------------------------------
# Card 5: last 12 months
# --------------------------------------------------------------------------
def activity():
    W, H = 1000, 360
    MN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    b = [f'<rect width="{W}" height="{H}" rx="22" fill="{PAPER}"/>',
         f'<text x="40" y="50" font-family="{MONO}" font-size="12" letter-spacing="1.4" '
         f'fill="{GREY}">THE LAST 12 MONTHS ON GITHUB</text>',
         f'<text x="38" y="122" font-family="{SERIF}" font-size="68" fill="{INK}" class="rise" '
         f'{dly(2.2)}>{fmt(S["total"])} <tspan font-style="italic">contributions</tspan></text>']
    mx = max(S["monthly"]) or 1
    best = S["monthly"].index(max(S["monthly"]))
    base_y, max_h, bw, gap, x0 = 292, 120, 38, 14, 40
    for i, (v, (y, m)) in enumerate(zip(S["monthly"], S["months"])):
        h = max(8, v / mx * max_h)
        x = x0 + i * (bw + gap)
        current = i == len(S["months"]) - 1
        col = BLUE if i == best else ("#c9c9c3" if current else INK)
        d = 2.5 + i * .06
        b.append(f'<rect x="{x}" y="{base_y - h:.1f}" width="{bw}" height="{h:.1f}" rx="5" '
                 f'fill="{col}" class="grow" {dly(d)}/>')
        b.append(f'<text x="{x + bw / 2}" y="{base_y + 24}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="12" fill="{GREY}">{MN[m - 1]}</text>')
        if i == best:
            b.append(f'<text x="{x + bw / 2}" y="{base_y - h - 10:.1f}" text-anchor="middle" '
                     f'font-family="{MONO}" font-size="12" fill="{BLUE}" class="fade" '
                     f'{dly(3.5)}>{fmt(v)}</text>')
    rows = [(f'{S["streak"]}', " days", "current streak"),
            (f'{S["active"]}', f' / {S["days"]}', "days with a commit"),
            (f'{S["busiest"]}', "", "on the busiest day")]
    for i, (num, suf, label) in enumerate(rows):
        y = 100 + i * 78
        if i:
            b.append(f'<line x1="720" y1="{y - 44}" x2="960" y2="{y - 44}" stroke="#d6d6d0"/>')
        suf_el = (f'<tspan font-style="{"italic" if i == 0 else "normal"}" fill="{GREY if i else INK}">'
                  f'{escape(suf)}</tspan>') if suf else ""
        b.append(f'<text x="720" y="{y}" font-family="{SERIF}" font-size="46" fill="{INK}" '
                 f'class="rise" {dly(2.6 + i * .15)}>{num}{suf_el}</text>')
        b.append(f'<text x="720" y="{y + 22}" font-family="{SANS}" font-size="13" fill="{GREY}" '
                 f'class="fade" {dly(3 + i * .15)}>{escape(label)}</text>')
    write("activity.svg", svg(W, H, "\n".join(b)))


# --------------------------------------------------------------------------
# Card 6: contribution graph in blue
# --------------------------------------------------------------------------
def graph():
    W, H = 1000, 262
    LEVELS = ["#e6e6e1", "#c9d4ff", "#93aaff", "#5a7bff", "#2f55ff"]
    start = TODAY - dt.timedelta(days=(TODAY.weekday() + 1) % 7) - dt.timedelta(weeks=52)
    vals = sorted(v for v in COUNTS.values() if v > 0)
    q = (lambda p: vals[int(len(vals) * p)] if vals else 1)
    cuts = [q(.25), q(.5), q(.75)]

    def level(v):
        if v == 0:
            return 0
        return 1 + sum(v > c for c in cuts)

    b = [f'<rect width="{W}" height="{H}" rx="22" fill="{PAPER}"/>',
         f'<text x="40" y="64" font-family="{SERIF}" font-size="38" fill="{INK}">Every day, '
         f'<tspan font-style="italic" fill="{BLUE}">in blue</tspan></text>',
         f'<text x="960" y="58" text-anchor="end" font-family="{MONO}" font-size="12" '
         f'letter-spacing="1.4" fill="{GREY}">REFRESHED DAILY  ·  {TODAY.isoformat()}</text>']
    gx, gy, cell, pitch = 40, 92, 13, 17
    last_month = None
    for w in range(53):
        for d in range(7):
            day = start + dt.timedelta(weeks=w, days=d)
            if day > TODAY:
                continue
            x, y = gx + w * pitch, gy + d * pitch
            b.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                     f'fill="{LEVELS[level(COUNTS.get(day, 0))]}" class="pop" '
                     f'{dly(1.0 + w * .018 + d * .004)}/>')
        first = start + dt.timedelta(weeks=w)
        if first.month != last_month and first.day <= 7:
            b.append(f'<text x="{gx + w * pitch}" y="{gy + 7 * pitch + 16}" '
                     f'font-family="{MONO}" font-size="12" fill="{GREY}">{first.strftime("%b")}</text>')
            last_month = first.month
    lx = 790
    b.append(f'<text x="{lx - 12}" y="{H - 18}" text-anchor="end" font-family="{MONO}" '
             f'font-size="12" fill="{GREY}">less</text>')
    for i, c in enumerate(LEVELS):
        b.append(f'<rect x="{lx + i * 17}" y="{H - 29}" width="{cell}" height="{cell}" rx="3" fill="{c}"/>')
    b.append(f'<text x="{lx + 5 * 17 + 6}" y="{H - 18}" font-family="{MONO}" font-size="12" '
             f'fill="{GREY}">more</text>')
    write("graph.svg", svg(W, H, "\n".join(b)))


if __name__ == "__main__":
    hero()
    for i, t in enumerate(TILES):
        tile(i, *t)
    activity()
    graph()
    print("done" + (" (STATIC)" if STATIC else ""))
