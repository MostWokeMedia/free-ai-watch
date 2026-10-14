"""WCAG contrast check for theme token pairs parsed from site/style.css (AA: 4.5 normal text, 3.0 large/UI)."""
import re, pathlib, sys
css = (pathlib.Path(__file__).resolve().parent.parent / "site/style.css").read_text()
def theme(sel): return dict(re.findall(r"--([\w-]+):(#[0-9A-Fa-f]{6})", re.search(sel + r"\{(.*?)\}", css).group(1)))
def lum(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]; c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def ratio(a, b): A, B = sorted([lum(a), lum(b)], reverse=True); return (A + .05) / (B + .05)
pairs = [("text","bg",4.5),("text","surface",4.5),("text","surface-2",4.5),("muted","bg",4.5),("muted","surface",4.5),("muted","surface-2",4.5),
         ("link","bg",4.5),("link","surface",4.5),("link","sponsor-bg",4.5),("text","sponsor-bg",4.5),("success","surface",4.5),("success","surface-2",4.5),
         ("on-primary","primary",4.5),("badge-text","badge-bg",4.5),("primary","surface",3.0),("logo-ring","bg",3.0),("logo-dot","bg",3.0)]
bad = 0
for name, sel in [("light", r":root,\[data-theme=light\]"), ("dark", r"\[data-theme=dark\]")]:
    t = theme(sel)
    for f, b, need in pairs:
        r = ratio(t[f], t[b]); ok = r >= need; bad += not ok
        print(f"{name:5} {f:>10} on {b:<10} {t[f]} / {t[b]}  {r:5.2f}  {'PASS' if ok else 'FAIL'} (≥{need})")
sys.exit(1 if bad else 0)
