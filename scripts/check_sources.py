"""Re-fetch every source page (rendered), save text snapshot, diff vs previous, re-verify each offer's phrase.
Usage: python scripts/check_sources.py [--seed]   (--seed builds data/offers.json from data/candidates.json)"""
import json, re, sys, hashlib, difflib, datetime, pathlib
from playwright.sync_api import sync_playwright
R = pathlib.Path(__file__).resolve().parent.parent
today = datetime.date.today().isoformat()
seed = "--seed" in sys.argv
if seed:
    keys = ["name","provider","offer","value","card_required","resets","source_url","verify","category"]
    items = [dict(zip(keys, c)) for c in json.load(open(R/"data/candidates.json"))]
else:
    items = json.load(open(R/"data/offers.json"))
changes = json.load(open(R/"data/changes.json")) if (R/"data/changes.json").exists() else []
kept = []
BLOCK = re.compile(r"just a moment|attention required|cf-chl|cf_chl|checking your browser|verify you are human|are you a robot|captcha|enable javascript and cookies to continue|ddos protection by|performing security verification", re.I)
VOLATILE = [(re.compile(r"(Cloudflare )?Ray ID:?\s*[0-9a-f]{12,20}", re.I), "Ray ID: <ray>"),
            (re.compile(r"\b(nonce|csrf|token|request[ _-]?id|trace[ _-]?id)([\"'=: ]+)[A-Za-z0-9+/_\-=]{8,}", re.I), r"\1\2<tok>"),
            (re.compile(r"\b[0-9a-f]{32,}\b", re.I), "<hex>"),
            (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<uuid>")]
# Lines that change without the offer changing: cookie/consent banners, keyboard-shortcut glyphs,
# result counters, embedded widget errors (e.g. Jina's key widget failing its human check in CI).
NOISE_LINE = re.compile(r"cookie|privacy|do not sell|manage preferences|consent|accept all|reject (all|optional)|agree to the use of|^settings$|security verification|malicious bots|^(ctrl ?\+? ?[a-z]|⌘ ?[a-z]|ctrl[a-z])$|^displaying \d+-\d+ \(\d+\)$|"
                        r"verify if you are human|refreshing the page multiple times|^(refresh|bug_report|debug info|contact|report_problem.*)$", re.I)
def norm(t):
    for rx, rep in VOLATILE: t = rx.sub(rep, t)
    return "\n".join(l for l in t.splitlines() if l.strip() and not NOISE_LINE.search(l.strip()))
def lh(l): return hashlib.md5(l.strip().lower().encode()).hexdigest()[:12]
def remember(snap, text):
    f = snap.with_suffix(".seen"); seen = set(f.read_text().split()) if f.exists() else set()
    f.write_text("\n".join(sorted(seen | {lh(l) for l in norm(text).splitlines()})))
def add_event(ev):
    """One event per offer/type/day: repeat runs replace instead of stacking."""
    for i, c in enumerate(changes):
        if c["date"] == ev["date"] and c["name"] == ev["name"] and c["type"] == ev["type"]: changes[i] = ev; return
    changes.insert(0, ev)
def blocked(status, text):
    """Bot-block / challenge page: count as 'couldn't verify', never as a change."""
    if status in (403, 429, 503): return True
    return bool(BLOCK.search(text[:5000])) and len(text) < 4000
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(user_agent="Mozilla/5.0 (X11; Linux x86_64) Chrome/130 Safari/537.36")
    for it in items:
        url = it["source_url"]; snap = R/"snapshots"/(hashlib.md5(url.encode()).hexdigest()+".txt")
        status = None
        try:
            resp = pg.goto(url, timeout=30000, wait_until="domcontentloaded"); pg.wait_for_timeout(2500)
            status = resp.status if resp else None
            text = pg.inner_text("body")
            if blocked(status, text + " " + pg.title()):
                print("UNVERIFIABLE TODAY (bot block)", it["name"], status)
                if not seed:
                    it["check_status"] = "unverifiable today"; it["check_status_date"] = today  # last good last_checked/evidence kept
                    kept.append(it)
                continue
        except Exception as e:
            print("FETCH FAIL", it["name"], e.__class__.__name__); text = ""
        if text: it["check_status"] = "verified" if re.search(it["verify"], text) else "phrase missing"; it.pop("check_status_date", None)
        m = re.search(it["verify"], text) if text else None
        ev = re.sub(r"\s+"," ", text[max(0,m.start()-90):m.end()+90]) if m else ""
        if snap.exists() and text:
            old = snap.read_text()
            if norm(old) != norm(text):
                # Only lines never seen before on this page count. A/B copy variants and reordering
                # are remembered in snapshots/<hash>.seen, so a variant only alerts the first time it appears.
                seenf = snap.with_suffix(".seen"); seen = set(seenf.read_text().split()) if seenf.exists() else set()
                seen |= {lh(l) for l in norm(old).splitlines()}
                d = ["+" + l for l in norm(text).splitlines() if lh(l) not in seen]
                if d: add_event({"date":today,"name":it["name"],"type":"page_changed","detail":" | ".join(d[:6])[:400],"source_url":url})
        if text: snap.write_text(text); remember(snap, text)
        if seed:
            if m:
                it.update(last_checked=today, evidence=ev, deadline=None); kept.append(it)
                changes.insert(0, {"date":today,"name":it["name"],"type":"added","detail":"Verified on official page: "+ev[:200],"source_url":url})
            print(("OK  " if m else "SKIP"), it["name"])
        else:
            if m: it.update(last_checked=today, evidence=ev)
            elif text: add_event({"date":today,"name":it["name"],"type":"phrase_missing","detail":"Verification phrase no longer found - review","source_url":url})
            kept.append(it)
    b.close()
json.dump(kept, open(R/"data/offers.json","w"), indent=1)
json.dump(changes[:500], open(R/"data/changes.json","w"), indent=1)
print(len(kept), "offers;", sum(c["date"]==today for c in changes), "change events today")
