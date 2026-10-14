"""Builds public HTML into dist/: injects shared header/footer/signup, renders /compare and /blog from posts/*.md (build-time)."""
import re, html, pathlib, json
THEME_HEAD = '<script>(function(){try{var t=localStorage.getItem("theme")}catch(e){}document.documentElement.dataset.theme=(t==="dark"||t==="light")?t:"light"})()</script>'
LOGO = ('<a class="logo" href="/" aria-label="FreeAIWatch home"><svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="17" fill="none" stroke="var(--logo-ring)" stroke-width="5"/>'
        '<circle cx="24" cy="24" r="6.5" fill="var(--logo-dot)"/></svg><span>Free<em>AI</em>Watch</span></a>')
TOGGLE = '<button type="button" class="theme-toggle" aria-label="Switch to dark theme" aria-pressed="false"><span class="moon" aria-hidden="true">🌙</span><span class="sun" aria-hidden="true">☀️</span></button>'

R = pathlib.Path(__file__).resolve().parent.parent; D = R / "dist"
SIGNUP = (R / "partials.html").read_text().split("<!--SIGNUP-->", 1)[1].strip()
FOOT = ('<footer>Not affiliated with, endorsed by, or sponsored by any provider listed. Offers change without notice — always confirm on the official source page. '
        '“Not stated” means the page we checked didn’t say.<br>Follow <a href="https://x.com/freeaiwatch">@freeaiwatch</a> for daily drops · '
        '<a href="https://freeaiwatch.com">freeaiwatch.com</a><br><span class="footer-links"><a href="/submit">Submit a deal</a><a href="/sponsor">Sponsor</a><a href="/compare">Compare</a><a href="/blog">Blog</a></span></footer><script src="/site/signup.js"></script><script src="/site/theme.js"></script></body></html>')
def head(title, desc, path):
    t, d = html.escape(title), html.escape(desc)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'+THEME_HEAD+'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title>'
            f'<meta name="description" content="{d}"><link rel="icon" href="/site/favicon.svg" type="image/svg+xml"><link rel="canonical" href="https://freeaiwatch.com{path}">'
            f'<meta property="og:type" content="website"><meta property="og:url" content="https://freeaiwatch.com{path}"><meta property="og:title" content="{t}"><meta property="og:description" content="{d}">'
            f'<meta property="og:image" content="https://freeaiwatch.com/site/og.png"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@freeaiwatch">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Funnel+Sans:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap"><link rel="stylesheet" href="/site/style.css"></head><body>')
def header(active):
    links = [("/#all", "All offers", "all"), ("/#today", "Today", "today"), ("/#ending", "Ending soon", "ending"), ("/compare", "Compare", "compare"), ("/blog", "Blog", "blog"), ("/submit", "Submit a deal", "submit"), ("/sponsor", "Sponsor", "sponsor")]
    nav = "".join(f'<a href="{h}"{" class=on" if k == active else ""}>{n}</a>' for h, n, k in links)
    return ('<header><h1>'+LOGO+'</h1><p>Every free AI tier, credit and student deal — verified against official pages, re-checked daily.</p>'
            f'<nav>{nav}{TOGGLE}</nav></header>')
def md(t):  # minimal markdown: headings, lists, bold/italic, links, paragraphs; HTML comments stripped
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S); out, ul = [], False
    def inl(s):
        s = html.escape(s)
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s); return re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    for line in t.splitlines():
        l = line.rstrip()
        if l.startswith("- "):
            if not ul: out.append("<ul>"); ul = True
            out.append(f"<li>{inl(l[2:])}</li>"); continue
        if ul: out.append("</ul>"); ul = False
        if not l: continue
        h = re.match(r"(#{1,3}) (.*)", l)
        out.append(f"<h{len(h.group(1))+1}>{inl(h.group(2))}</h{len(h.group(1))+1}>" if h else f"<p>{inl(l)}</p>")
    if ul: out.append("</ul>")
    return "\n".join(out)
def parse(p):
    raw = p.read_text(); m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S); meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":"); meta[k.strip()] = v.split("#")[0].strip().strip('"')
    return meta, m.group(2)
def page(src_text, active):
    m = re.match(r"<!--HEAD:(.*?)\|(.*?)\|(.*?)-->", src_text); body = src_text[m.end():] if m else src_text
    h = head(*m.groups()) if m else ""
    return h + body.replace(f"<!--HEADER:{active}-->", header(active)).replace("<!--SIGNUP-->", SIGNUP).replace("<!--FOOTER-->", FOOT)
# homepage: inject signup + nav already in file; append signup.js
idx = (R / "index.html").read_text().replace('<meta charset="utf-8">', '<meta charset="utf-8">' + THEME_HEAD, 1)
idx = re.sub(r"<h1>.*?</h1>", lambda m: "<h1>" + LOGO + "</h1>", idx, count=1, flags=re.S).replace("</nav></header>", TOGGLE + "</nav></header>", 1)
idx = idx.replace("<!--SIGNUP-->", SIGNUP).replace("<!--SIGNUP-FOOTER-->", "").replace("</body>", '<script src="/site/signup.js"></script><script src="/site/theme.js"></script></body>')
(D / "index.html").write_text(idx)
(D / "compare.html").write_text(page((R / "compare.html").read_text(), "compare"))
(D / "404.html").write_text(page((R / "404.html").read_text(), "none"))
for name in ("submit", "sponsor"): (D / f"{name}.html").write_text(page((R / f"{name}.html").read_text(), name))
posts = sorted([(parse(p), p) for p in (R / "posts").glob("*.md") if p.name != "TEMPLATE.md"], key=lambda x: x[0][0].get("date", ""), reverse=True)
(D / "blog").mkdir(exist_ok=True); items = []
for (meta, body), p in posts:
    slug = p.stem; draft = meta.get("status", "draft") != "published"
    badge = '<span class="badge">Draft · coming soon</span>' if draft else ""
    art = f'<main><article><p class="muted"><a href="/blog">← Blog</a> · {meta.get("date","")} · {html.escape(meta.get("author",""))}</p><h1>{html.escape(meta["title"])}{badge}</h1>{md(body)}</article>{SIGNUP}</main>'
    (D / "blog" / f"{slug}.html").write_text(head(meta["title"] + " — FreeAIWatch", "How I use free AI tools — weekly notes from Spencer.", f"/blog/{slug}") + header("blog") + art + FOOT)
    items.append(f'<li><a href="/blog/{slug}"><b>{html.escape(meta["title"])}</b></a>{badge}<br><small class="muted">{meta.get("date","")}</small></li>')
idxb = (f'<main><h2>How I use this</h2><p class="muted">Weekly notes from Spencer on which free AI offers he actually uses and what he builds with them.</p>'
        f'<ul class="post-list">{"".join(items) or "<li>No posts yet.</li>"}</ul>{SIGNUP}</main>')
(D / "blog.html").write_text(head("Blog — How I use this — FreeAIWatch", "Weekly notes on using free AI tools.", "/blog") + header("blog") + idxb + FOOT)
print("built pages:", 4 + 1 + len(posts))
