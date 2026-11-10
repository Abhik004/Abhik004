#!/usr/bin/env python3
"""Fetch the last year of contributions via the GitHub GraphQL API
and write data/contributions.json  ->  {"days": [{"date": "...", "count": n}, ...]}

Needs GH_TOKEN (the Action's GITHUB_TOKEN is enough) and USERNAME (default Abhik004).
"""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

USER = os.environ.get("USERNAME_GH", "Abhik004")
TOKEN = os.environ["GH_TOKEN"]
now = dt.datetime.now(dt.timezone.utc)
frm = (now - dt.timedelta(days=364)).strftime("%Y-%m-%dT00:00:00Z")
to = now.strftime("%Y-%m-%dT%H:%M:%SZ")

query = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      contributionCalendar{ weeks{ contributionDays{ date contributionCount } } }
    }
  }
}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"login": USER, "from": frm, "to": to}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
             "User-Agent": "readme-cards"},
)
data = json.load(urllib.request.urlopen(req))
if "errors" in data:
    raise SystemExit(data["errors"])
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
days = [{"date": d["date"], "count": d["contributionCount"]}
        for w in weeks for d in w["contributionDays"]]

out = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"days": days}))
print(f"wrote {out} ({len(days)} days)")
