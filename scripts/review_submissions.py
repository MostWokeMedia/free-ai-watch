"""Owner review tool for community deal submissions and sponsor requests (stored as PENDING in Cloudflare KV).
Nothing is published until you approve AND the offer is verified on its official page AND you commit + push.

Requires the ADMIN_TOKEN secret to be set on the Pages project (see docs/SUBMISSIONS.md) and exported locally:
  export FAW_ADMIN_TOKEN=...            # same value as the Pages secret
Commands:
  python3 scripts/review_submissions.py list [--kind submission|sponsor] [--status pending|approved|rejected|all]
  python3 scripts/review_submissions.py approve <id> --phrase "<text that must appear on the source page>" \
        --name "Tool free tier" --provider "Company" --value "as stated" --category API [--card no|yes|"not stated"] [--resets monthly]
  python3 scripts/review_submissions.py reject <id> [--note "reason"]
  python3 scripts/review_submissions.py sponsor-done <id> [--note "replied"]   # marks a sponsor request handled
"""
import argparse, datetime, json, os, pathlib, re, sys, urllib.request
R = pathlib.Path(__file__).resolve().parent.parent
API = os.environ.get("FAW_API", "https://freeaiwatch.com/api/admin/queue")

def call(method, query="", body=None):
    tok = os.environ.get("FAW_ADMIN_TOKEN")
    if not tok: sys.exit("FAW_ADMIN_TOKEN is not set. See docs/SUBMISSIONS.md (ADMIN_TOKEN must be set on the Pages project first).")
    req = urllib.request.Request(API + query, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json", "User-Agent": "faw-review/1"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def show(v):  # repr() keeps any hostile text inert in the terminal
    for k in ("id", "status", "tool", "offer", "source_url", "deadline", "email", "company", "website", "slot", "budget", "message", "created"):
        if v.get(k) is not None: print(f"  {k:10}: {v[k]!r}")
    print()

def fetch_text(url):
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(); pg.goto(url, timeout=30000, wait_until="domcontentloaded"); pg.wait_for_timeout(2500)
            t = pg.inner_text("body"); final = pg.url; b.close(); return t, final
    except ImportError:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r: return re.sub(r"<[^>]+>", " ", r.read().decode("utf-8", "ignore")), r.url

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("list"); l.add_argument("--kind", default="submission", choices=["submission", "sponsor"]); l.add_argument("--status", default="pending")
    a = sp.add_parser("approve"); a.add_argument("id"); a.add_argument("--phrase", required=True); a.add_argument("--name", required=True); a.add_argument("--provider", required=True)
    a.add_argument("--value", required=True); a.add_argument("--category", required=True); a.add_argument("--card", default="not stated"); a.add_argument("--resets", default="not stated"); a.add_argument("--offer")
    rj = sp.add_parser("reject"); rj.add_argument("id"); rj.add_argument("--note", default="")
    sd = sp.add_parser("sponsor-done"); sd.add_argument("id"); sd.add_argument("--note", default="")
    x = ap.parse_args()
    if x.cmd == "list":
        items = call("GET", f"?kind={x.kind}&status={x.status}")["items"]; print(f"{len(items)} {x.kind} item(s), status={x.status}\n"); [show(v) for v in items]; return
    if x.cmd in ("reject", "sponsor-done"):
        print(call("POST", body={"id": x.id, "action": "reject" if x.cmd == "reject" else "approve", "note": x.note})["item"]["status"]); return
    items = {v["id"]: v for v in call("GET", "?kind=submission&status=all")["items"]}
    v = items.get(x.id) or sys.exit("Submission not found")
    text, final = fetch_text(v["source_url"])
    m = re.search(re.escape(x.phrase), text, re.I)
    if not m: sys.exit(f"NOT VERIFIED: phrase {x.phrase!r} not found on {final}. Nothing changed.")
    ev = re.sub(r"\s+", " ", text[max(0, m.start() - 90):m.end() + 90])
    today = datetime.date.today().isoformat(); offers_p = R / "data/offers.json"; offers = json.load(open(offers_p))
    if any(o["source_url"] == v["source_url"] and o["name"].lower() == x.name.lower() for o in offers): sys.exit("Already listed.")
    offers.append({"name": x.name, "provider": x.provider, "offer": x.offer or v["offer"][:200], "value": x.value, "card_required": x.card, "resets": x.resets,
                   "source_url": v["source_url"], "verify": re.escape(x.phrase), "category": x.category, "last_checked": today, "evidence": ev,
                   "deadline": v.get("deadline"), "note": "community-submitted", "submission_id": v["id"]})
    json.dump(offers, open(offers_p, "w"), indent=1)
    ch_p = R / "data/changes.json"; ch = json.load(open(ch_p))
    ch.insert(0, {"date": today, "name": x.name, "type": "added", "detail": "Community-submitted, verified on official page: " + ev[:200], "source_url": v["source_url"]})
    json.dump(ch[:500], open(ch_p, "w"), indent=1)
    call("POST", body={"id": v["id"], "action": "approve", "note": "verified: " + x.phrase})
    print(f"VERIFIED and added to data/offers.json: {x.name}\nEvidence: {ev}\nNext: review the diff, then git commit && git push to publish.")

if __name__ == "__main__": main()
