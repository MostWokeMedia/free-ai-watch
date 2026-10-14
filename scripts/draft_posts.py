"""FreeAIWatch (@freeaiwatch): writes 3 draft X posts for today to drafts/YYYY-MM-DD.txt (drafts only; never posts)."""
import json,datetime,pathlib,random
R=pathlib.Path(__file__).resolve().parent.parent;t=datetime.date.today()
o=json.load(open(R/"data/offers.json"));c=json.load(open(R/"data/changes.json"))
nocard=[x for x in o if x["card_required"]=="no"];dl=sorted([x for x in o if x.get("deadline")],key=lambda x:x["deadline"])
real=[x for x in c if x["date"]==t.isoformat() and x["type"]!="added"]
p=[f"{len(o)} free AI tiers, credits & student deals — every one checked against the official page today.\n\nSearch them all, no signup: https://freeaiwatch.com"]
if dl: d=dl[0];p.append(f"⏳ {(datetime.date.fromisoformat(d['deadline'])-t).days} days left: {d['name']} ({d['value']}). Redeem by {d['deadline']}.\n\nSource + every other deadline: https://freeaiwatch.com")
p.append("Free AI with NO credit card required:\n\n"+"\n".join(f"• {x['name']}: {x['value']}" for x in nocard[:4])+"\n\nFull list: https://freeaiwatch.com")
if real: p[0]=f"🔔 {len(real)} free AI offers changed today, incl. {real[0]['name']}. What moved: https://freeaiwatch.com"
xp=R/"data/x_spotted.json";xs=json.load(open(xp)) if xp.exists() else []
xd=sorted([x for x in xs if x.get("deadline")],key=lambda x:x["deadline"])
if xd:
    x=xd[0];hrs=(datetime.datetime.fromisoformat(x["deadline"].replace("Z","+00:00"))-datetime.datetime.now(datetime.timezone.utc)).total_seconds()/3600
    when=f"~{int(hrs)}h left" if hrs<48 else f"~{int(hrs//24)} days left"
    p.insert(1,f"👀 Spotted on X (unverified): {x['tool']} — {x['offer']}\n\n{when}, per {x['author']}'s post: {x['url']}\n\nMore: https://freeaiwatch.com/#ending")
(R/"drafts").mkdir(exist_ok=True);f=R/"drafts"/f"{t}.txt"
f.write_text("\n\n----- DRAFT (not posted) -----\n\n".join(p[:3]));print(f.read_text())
