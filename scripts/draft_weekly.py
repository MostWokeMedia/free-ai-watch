"""Drafts the weekly email roundup into drafts/weekly-YYYY-MM-DD.md (draft only; sends nothing)."""
import json, datetime, pathlib, re
R = pathlib.Path(__file__).resolve().parent.parent; t = datetime.date.today(); since = (t - datetime.timedelta(days=7)).isoformat()
o = json.load(open(R / "data/offers.json")); c = json.load(open(R / "data/changes.json"))
wk = [x for x in c if x["date"] >= since]
def usd(v):
    m = re.search(r"\$\s?([\d,]+(?:\.\d+)?)", v); return float(m.group(1).replace(",", "")) * (12 if re.search(r"/\s?mo|month", v) else 1) if m else -1
top = sorted(o, key=lambda x: (-usd(x["value"]), x["card_required"] != "no"))[:5]
nocard = [x for x in o if x["card_required"] == "no"]
dl = sorted([x for x in o if x.get("deadline") and x["deadline"] >= t.isoformat()], key=lambda x: x["deadline"])
L = [f"# FreeAIWatch weekly — {t:%B %-d, %Y}", "", "_DRAFT — review before sending. Every item links to its official page._", "",
     f"Tracking **{len(o)}** free AI offers, re-checked daily. Full list: https://freeaiwatch.com · Compare: https://freeaiwatch.com/compare", "",
     "## Top offers by stated dollar value"]
L += [f"- **{x['name']}** ({x['provider']}): {x['value']} · card: {x['card_required']} — {x['source_url']}" for x in top]
for typ, title in [("added", "New this week"), ("page_changed", "Pages that changed (review)"), ("phrase_missing", "Possibly ended or changed")]:
    items = [x for x in wk if x["type"] == typ]
    L += ["", f"## {title} ({len(items)})"] + ([f"- {x['name']} — {x['source_url']}" for x in items[:10]] or ["- None"])
L += ["", "## No credit card required"] + [f"- {x['name']}: {x['value']}" for x in nocard[:6]]
L += ["", "## Deadlines"] + ([f"- {x['name']}: ends {x['deadline']}" for x in dl] or ["- No verified deadlines"])
L += ["", "## How I use this", "- Link this week's post: https://freeaiwatch.com/blog", "", "---", "Not affiliated with any provider listed. You're getting this because you subscribed at freeaiwatch.com. Unsubscribe: {{unsubscribe_link}}"]
(R / "drafts").mkdir(exist_ok=True); f = R / "drafts" / f"weekly-{t}.md"; f.write_text("\n".join(L) + "\n"); print("wrote", f)
