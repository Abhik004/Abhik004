#!/usr/bin/env python3
"""Generate animated SVG cards for Abhik004's GitHub profile. Stdlib only."""
import html, json, os, sys, urllib.request
from datetime import date, timedelta
from pathlib import Path

USER = "Abhik004"
OUT = Path(__file__).resolve().parent
BLUE, RED, YELLOW = "#3155F5", "#EF3934", "#FFC21B"
INK, MUTED, PAPER = "#171717", "#777777", "#F5F4F0"
QUERY = '''query($login:String!){user(login:$login){name login contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}} months{name totalContributions}}} pinnedItems(first:3,types:[REPOSITORY]){nodes{... on Repository{name description url stargazerCount forkCount primaryLanguage{name color}}}}}}'''


def fetch():
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise RuntimeError("Set GITHUB_TOKEN (the GitHub Actions workflow supplies it).")
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json",
        "User-Agent": "Abhik004-profile-svg-renderer"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read().decode())
    if result.get("errors") or not result.get("data", {}).get("user"):
        raise RuntimeError("GitHub GraphQL request failed: " + json.dumps(result.get("errors", result)))
    return result["data"]["user"]


def e(v):
    return html.escape(str(v or ""), quote=True)


def start(w, h, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{e(title)}"><title>{e(title)}</title>
<defs><style>
text{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}.mono{{font-family:"SFMono-Regular",Consolas,monospace}}.serif{{font-family:Georgia,"Times New Roman",serif}}
@keyframes rise{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
.rise{{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}}.bar{{transform-box:fill-box;transform-origin:bottom;animation:grow .9s ease both}}.pulse{{animation:pulse 2.4s ease-in-out infinite}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}
</style></defs>'''


def save(name, svg):
    (OUT / name).write_text(svg + "</svg>\n", encoding="utf-8")


def days_from(cal):
    return sorted([d for w in cal["weeks"] for d in w["contributionDays"]], key=lambda x: x["date"])


def streaks(days):
    active = {date.fromisoformat(d["date"]) for d in days if d["contributionCount"] > 0}
    today = date.today()
    cursor = today if today in active else today - timedelta(days=1)
    current = 0
    while cursor in active:
        current += 1
        cursor -= timedelta(days=1)
    longest, run, previous = 0, 0, None
    for day in sorted(active):
        run = run + 1 if previous and day == previous + timedelta(days=1) else 1
        longest, previous = max(longest, run), day
    busiest = max((d["contributionCount"] for d in days), default=0)
    return current, longest, busiest


def hero(user):
    name = user.get("name") or USER
    first, rest = (name.split()[0], " ".join(name.split()[1:])) if len(name.split()) > 1 else (name, "Samanta")
    s = start(1200, 360, f"{name} — Data Science and Engineering")
    s += f'<rect width="1200" height="360" rx="20" fill="{PAPER}"/><rect width="10" height="360" fill="{BLUE}"/>'
    s += '<text x="66" y="62" class="mono" font-size="14" letter-spacing="3" fill="#666">DATA SCIENCE &amp; ENGINEERING  /  NIT JAMSHEDPUR</text>'
    s += f'<circle cx="73" cy="104" r="5" fill="{BLUE}" class="pulse"/><text x="92" y="109" font-size="14" fill="#555">OPEN TO IDEAS, COLLABORATION &amp; BUILDING</text>'
    s += f'<text x="64" y="204" class="serif rise" font-size="88" letter-spacing="-4" fill="{INK}">{e(first)}</text>'
    s += f'<text x="64" y="282" class="serif rise" font-size="88" font-style="italic" letter-spacing="-4" fill="{INK}" style="animation-delay:.12s">{e(rest)}</text>'
    s += '<text x="68" y="322" font-size="17" fill="#555">I build with data, explore intelligent systems, and turn ideas into software.</text>'
    # Abstract line-art terminal motif, not represented as a likeness of the user.
    s += f'<g transform="translate(845 72)" fill="none" stroke="{INK}" stroke-width="2" opacity=".78"><path d="M20 170Q18 65 112 36Q202 8 248 91Q270 135 248 209L225 229H42Z"/><path d="M63 129Q84 104 108 125M158 125Q184 104 207 128M91 151Q112 164 132 151M164 151Q184 164 205 151M145 146L135 184L154 187M113 207Q145 224 180 205M55 92Q125 5 217 76M72 70L48 48M205 68L232 42"/><path d="M28 246H252M50 258H230" stroke-dasharray="4 8"/></g>'
    s += f'<text x="855" y="340" class="mono" font-size="11" fill="{MUTED}">[ SYSTEMS / DATA / CURIOSITY ]</text>'
    save("hero.svg", s)


def world(filename, label, title, lines, color, dark=False, number=1):
    fg = INK if dark else "#FFFFFF"
    s = start(390, 250, f"{label}: {title}") + f'<rect width="390" height="250" rx="18" fill="{color}"/>'
    s += f'<text x="28" y="42" class="mono" font-size="12" letter-spacing="2" fill="{fg}">{label}</text><text x="28" y="100" class="serif" font-size="42" fill="{fg}">{title}</text>'
    for i, line in enumerate(lines):
        s += f'<text x="30" y="{145+i*25}" font-size="15" fill="{fg}">{e(line)}</text>'
    s += f'<circle cx="344" cy="42" r="9" fill="none" stroke="{fg}" class="pulse"/><path d="M28 220H362" stroke="{fg}" opacity=".35"/><text x="28" y="239" class="mono" font-size="10" fill="{fg}">0{number} / ABHIK SAMANTA</text>'
    save(filename, s)


def activity(cal, days):
    months = cal["months"][-12:] or [{"name": "—", "totalContributions": 0}]
    vals = [m["totalContributions"] for m in months]
    best, maxv = max(range(len(vals)), key=lambda i: vals[i]), max(vals or [1])
    current, longest, busiest = streaks(days)
    s = start(1200, 430, "GitHub activity over the last 12 months") + f'<rect width="1200" height="430" rx="18" fill="{PAPER}"/>'
    s += '<text x="54" y="54" class="mono" font-size="13" letter-spacing="2" fill="#777">THE LAST 12 MONTHS ON GITHUB</text>'
    s += f'<text x="52" y="126" class="serif" font-size="64" fill="{INK}">{cal["totalContributions"]:,} <tspan font-style="italic" fill="{BLUE}">contributions</tspan></text><text x="55" y="158" font-size="14" fill="#777">A year of showing up, learning and building.</text>'
    for i, m in enumerate(months):
        h = max(5, m["totalContributions"] / max(1, maxv) * 150)
        x, y = 55 + i * 68, 340 - h
        color = BLUE if i == best else INK
        s += f'<rect x="{x}" y="{y:.1f}" width="48" height="{h:.1f}" rx="6" fill="{color}" class="bar" style="animation-delay:{i*.045:.2f}s"/>'
        s += f'<text x="{x+24}" y="365" text-anchor="middle" class="mono" font-size="12" fill="#777">{e(m["name"][:3])}</text>'
        if i == best:
            s += f'<text x="{x+24}" y="{max(188,y-13):.1f}" text-anchor="middle" class="mono" font-size="12" fill="{BLUE}">{m["totalContributions"]:,}</text>'
    s += '<path d="M900 58V366" stroke="#D7D5CF"/>'
    for i, (v, label) in enumerate([(f"{current} days", "CURRENT STREAK"), (f"{longest} days", "LONGEST STREAK"), (str(busiest), "BUSIEST DAY")]):
        y = 110 + i * 100
        s += f'<text x="940" y="{y}" class="serif" font-size="43" fill="{INK}">{v}</text><text x="944" y="{y+25}" class="mono" font-size="11" letter-spacing="1.5" fill="#777">{label}</text>'
    s += '<text x="56" y="405" class="mono" font-size="10" fill="#888">SOURCE: GITHUB CONTRIBUTION CALENDAR · UPDATED DAILY</text>'
    save("activity.svg", s)


def heatmap(days):
    recent = days[-371:]
    if not recent:
        recent = [{"date": date.today().isoformat(), "contributionCount": 0}]
    while len(recent) < 371:
        d = date.fromisoformat(recent[0]["date"]) - timedelta(days=1)
        recent.insert(0, {"date": d.isoformat(), "contributionCount": 0})
    palette = ["#E8E9F0", "#C8D2FF", "#91A6FF", "#5E7BFF", BLUE]
    maximum = max(1, max(d["contributionCount"] for d in recent))
    s = start(1200, 205, "GitHub contribution heatmap") + f'<rect width="1200" height="205" rx="18" fill="{PAPER}"/>'
    s += '<text x="42" y="38" class="serif" font-size="31" fill="#171717">Every day, <tspan font-style="italic" fill="#3155F5">in blue.</tspan></text><text x="1155" y="35" text-anchor="end" class="mono" font-size="10" fill="#888">ROLLING 12 MONTHS</text>'
    for i, d in enumerate(recent):
        col, row = divmod(i, 7)
        count = d["contributionCount"]
        level = 0 if count == 0 else min(4, max(1, int(count / maximum * 4) + 1))
        x, y = 42 + col * 19, 65 + row * 19
        s += f'<rect x="{x}" y="{y}" width="14" height="14" rx="3" fill="{palette[level]}"><title>{e(d["date"])}: {count} contributions</title></rect>'
    for col, label in [(0,"12 MONTHS AGO"),(13,"9M"),(26,"6M"),(39,"3M"),(51,"NOW")]:
        s += f'<text x="{42+col*19}" y="190" class="mono" font-size="9" fill="#888">{label}</text>'
    save("contributions.svg", s)


def repo_card(i, repo):
    name = repo.get("name") or "Pin a repository"
    desc = repo.get("description") or "Pin a project on your GitHub profile and this card will update automatically."
    lang = repo.get("primaryLanguage") or {"name":"GitHub", "color":BLUE}
    lines, line = [], ""
    for word in desc.split():
        if len(line + " " + word) > 39:
            lines.append(line); line = word
        else:
            line = (line + " " + word).strip()
        if len(lines) == 2: break
    if line and len(lines) < 2: lines.append(line)
    s = start(390, 250, f"Featured repository: {name}") + f'<rect width="390" height="250" rx="18" fill="{PAPER}" stroke="#E1DFD8"/><rect width="7" height="250" rx="3" fill="{BLUE}"/>'
    shown = name if len(name) <= 25 else name[:22] + "…"
    s += f'<text x="26" y="38" class="mono" font-size="11" letter-spacing="2" fill="#777">FEATURED REPOSITORY / 0{i}</text><text x="26" y="91" class="serif" font-size="29" fill="{INK}">{e(shown)}</text>'
    for j, line in enumerate(lines[:2]): s += f'<text x="28" y="{132+j*22}" font-size="13" fill="#666">{e(line)}</text>'
    s += f'<circle cx="31" cy="204" r="5" fill="{e(lang.get("color") or BLUE)}"/><text x="44" y="209" font-size="12" fill="#555">{e(lang.get("name") or "Open source")}</text>'
    s += f'<text x="205" y="209" class="mono" font-size="11" fill="#555">★ {repo.get("stargazerCount",0)}  ⑂ {repo.get("forkCount",0)}</text><text x="28" y="237" class="mono" font-size="9" fill="#999">OPEN REPOSITORY ON GITHUB ↗</text>'
    save(f"repo-{i}.svg", s)


def main():
    user = fetch()
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = days_from(cal)
    hero(user)
    world("build.svg", "BUILD", "Make it real", ["AI / ML · Data Science", "Full-stack applications", "Python · TypeScript · C++"], BLUE, number=1)
    world("brand.svg", "BRAND", "Show the work", ["Projects with purpose", "Engineering in public", "Connect · Collaborate · Create"], RED, number=2)
    world("learn.svg", "LEARN", "Stay curious", ["DSA · CS fundamentals", "Research & experimentation", "Learn something every day"], YELLOW, dark=True, number=3)
    activity(cal, days)
    heatmap(days)
    repos = user.get("pinnedItems", {}).get("nodes", [])
    for i in range(1, 4):
        fallback = {"name":"Pin a repository", "description":"Pin a project on your GitHub profile and this card will update automatically.", "primaryLanguage":{"name":"GitHub","color":BLUE}, "stargazerCount":0,"forkCount":0}
        repo_card(i, repos[i-1] if len(repos) >= i else fallback)
    print("Rendered hero, three world cards, activity, heatmap and three pinned-repository cards.")


if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print(f"Card generation failed: {exc}", file=sys.stderr)
        raise
