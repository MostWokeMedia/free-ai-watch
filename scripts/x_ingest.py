"""Ingest a raw X search dump into data/x_spotted.json.
Usage: python scripts/x_ingest.py data/x_raw/YYYY-MM-DD.json
Raw format: {"results":[{"name":..., "response": <x API response with data/includes.users>}]} or a single x API response.
Rules: ORIGINAL posts only (no replies/quotes/retweets), author must be on config/x_official_accounts.json,
must match a reference pattern (promo_time_limited / engagement_gated), spam blocklist, dedupe by post id and tool+offer,
deadline computed from post time + stated duration or stated date; expired / stale items are removed."""
import json, re, sys, pathlib, datetime as dt
R = pathlib.Path(__file__).resolve().parent.parent
cfg = json.load(open(R / "config/x_sources.json")); allow = json.load(open(R / "config/x_official_accounts.json"))
OFF = {a["handle"].lower(): a for a in allow["accounts"] + allow.get("people", [])}
NUM = {"one": 1, "two": 2, "three": 3, "seven": 7}
UNIT = {"hour": "hours", "day": "days", "week": "weeks"}
now = dt.datetime.now(dt.timezone.utc)

def posts(raw):
    resps = [r["response"] for r in raw["results"]] if "results" in raw else [raw]
    for j in resps:
        users = {u["id"]: u for u in j.get("includes", {}).get("users", [])}
        for p in j.get("data", []) or []:
            yield p, users.get(p.get("author_id"), {})

def is_original(p):
    if p.get("in_reply_to_user_id"): return False
    return not any(r.get("type") in ("replied_to", "quoted", "retweeted") for r in p.get("referenced_tweets") or [])

def deadline(text, created):
    m = re.search(cfg["extract"]["duration"], text, re.I)
    if m:
        n = NUM.get(m.group(1).lower()) or int(m.group(1)); u = UNIT[m.group(2).lower().rstrip("s")]
        return (created + dt.timedelta(**{u: n})).isoformat().replace("+00:00", "Z"), m.group(0)
    m = re.search(cfg["extract"]["until_date"], text, re.I)
    if m:
        d = dt.datetime.strptime(f"{m.group(1)} {created.year}", "%B %d %Y").replace(hour=23, minute=59, tzinfo=dt.timezone.utc)
        if d < created - dt.timedelta(days=1): d = d.replace(year=d.year + 1)
        return d.isoformat().replace("+00:00", "Z"), m.group(0)
    return None, None

def offer_line(text, label):
    pats = cfg["classify"][label]
    for line in re.split(r"\n+|(?<=[.!])\s+", text):
        if any(re.search(p, line, re.I) for p in pats): return line.strip()[:200]
    return text.strip()[:200]

def main(path):
    raw = json.load(open(path)); out_p = R / "data/x_spotted.json"
    cur = json.load(open(out_p)) if out_p.exists() else []
    seen = {x["post_id"] for x in cur}; keys = {(x["tool"].lower(), x["offer"].lower()) for x in cur}
    stats = dict(seen_posts=0, not_original=0, not_official=0, no_pattern=0, spam=0, dup=0, kept=0)
    for p, u in posts(raw):
        stats["seen_posts"] += 1
        text = (p.get("note_tweet") or {}).get("text") or p.get("text", ""); text = text.replace("&gt;", ">").replace("&amp;", "&")
        if not is_original(p): stats["not_original"] += 1; continue
        h = (u.get("username") or "").lower()
        if h not in OFF: stats["not_official"] += 1; continue
        if any(re.search(s, text, re.I) for s in cfg["spam_block"]): stats["spam"] += 1; continue
        label = next((l for l in ("engagement_gated", "promo_time_limited") if any(re.search(r, text, re.I | re.S) for r in cfg["classify"][l])), None)
        if not label: stats["no_pattern"] += 1; continue
        created = dt.datetime.fromisoformat(p["created_at"].replace("Z", "+00:00"))
        dl, basis = deadline(text, created); offer = offer_line(text, label); tool = OFF[h]["tool"]
        if p["id"] in seen or (tool.lower(), offer.lower()) in keys: stats["dup"] += 1; continue
        disc = re.search(cfg["extract"]["discount"], text, re.I); kw = re.search(cfg["extract"]["keyword"], text, re.I)
        cur.append({"post_id": p["id"], "url": f"https://x.com/{u['username']}/status/{p['id']}", "author": "@" + u["username"],
                    "author_evidence": OFF[h]["evidence_url"], "tool": tool, "type": label, "offer": offer,
                    "discount_pct": int(disc.group(1)) if disc else None, "comment_keyword": kw.group(1) if kw else None,
                    "posted_at": p["created_at"], "deadline": dl, "deadline_basis": basis,
                    "metrics": {k: p.get("public_metrics", {}).get(k) for k in ("like_count", "reply_count", "retweet_count", "impression_count")},
                    "status": "unverified", "first_seen": now.date().isoformat()})
        seen.add(p["id"]); keys.add((tool.lower(), offer.lower())); stats["kept"] += 1
    maxage = dt.timedelta(days=cfg["rules"]["max_age_days_without_deadline"]); before = len(cur)
    def live(x):
        if x.get("deadline"): return dt.datetime.fromisoformat(x["deadline"].replace("Z", "+00:00")) > now
        return dt.datetime.fromisoformat(x["posted_at"].replace("Z", "+00:00")) > now - maxage
    cur = sorted([x for x in cur if live(x)], key=lambda x: x["posted_at"], reverse=True)
    stats["expired_removed"] = before - len(cur)
    json.dump(cur, open(out_p, "w"), indent=1, ensure_ascii=False)
    # Today feed events for newly kept items
    ch_p = R / "data/changes.json"; ch = json.load(open(ch_p))
    have = {(c.get("post_id")) for c in ch if c.get("post_id")}
    for x in cur:
        if x["post_id"] not in have and x["first_seen"] == now.date().isoformat():
            ch.insert(0, {"date": x["first_seen"], "name": x["tool"], "type": "spotted_on_x", "post_id": x["post_id"],
                          "detail": f"Spotted on X, unverified: {x['offer']}" + (f" (ends ~{x['deadline'][:10]})" if x["deadline"] else ""), "source_url": x["url"]})
    json.dump(ch[:500], open(ch_p, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(stats), "| live items:", len(cur))

if __name__ == "__main__": main(sys.argv[1])
