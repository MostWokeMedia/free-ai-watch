#!/usr/bin/env python3
"""Print sponsor clicks by day (for the weekly sponsor report).
Usage: FAW_ADMIN_TOKEN=... python scripts/click_report.py [--slug S] [--since YYYY-MM-DD] [--delete-slug S]
Needs the ADMIN_TOKEN secret set on the Pages project (see docs/CLICKS.md)."""
import argparse, json, os, sys, urllib.request, urllib.parse
from collections import defaultdict
API = os.environ.get("FAW_CLICKS_API", "https://freeaiwatch.com/api/admin/clicks")
a = argparse.ArgumentParser(); a.add_argument("--slug"); a.add_argument("--since"); a.add_argument("--delete-slug"); o = a.parse_args()
tok = os.environ.get("FAW_ADMIN_TOKEN") or (lambda f: open(f).read().strip() if os.path.exists(f) else None)(os.environ.get("FAW_ADMIN_TOKEN_FILE", os.path.expanduser("~/.secrets/freeaiwatch_admin_token")))
if not tok: sys.exit("FAW_ADMIN_TOKEN not set. Set the ADMIN_TOKEN secret on Pages first (docs/CLICKS.md).")
q = {k: v for k, v in (("slug", o.delete_slug or o.slug), ("since", o.since)) if v}
req = urllib.request.Request(API + ("?" + urllib.parse.urlencode(q) if q else ""), method="DELETE" if o.delete_slug else "GET",
                             headers={"Authorization": "Bearer " + tok, "User-Agent": "faw-click-report"})
try: d = json.load(urllib.request.urlopen(req, timeout=30))
except urllib.error.HTTPError as e: sys.exit(f"HTTP {e.code}: {e.read()[:200]!r}")
if o.delete_slug: print(f"deleted {len(d.get('rows', []))} keys"); sys.exit()
t = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for r in d.get("rows", []): t[r["slug"]][r["day"]][r["medium"]] += r["clicks"]
if not t: print("No clicks recorded."); sys.exit()
for slug, days in sorted(t.items()):
    print(f"\n== {slug} ==  total {sum(sum(m.values()) for m in days.values())}")
    print(f"{'day':<12}{'row':>6}{'banner':>8}{'x':>5}{'digest':>8}{'total':>7}")
    for day, m in sorted(days.items()):
        print(f"{day:<12}{m['row']:>6}{m['banner']:>8}{m['x']:>5}{m['digest']:>8}{sum(m.values()):>7}")
