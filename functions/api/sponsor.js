// POST /api/sponsor — sponsor inquiries, stored as PENDING in KV (SUBSCRIBERS binding, prefix "sponsor:"). Never published.
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;
const SLOTS = ["featured_row", "homepage_banner", "weekly_digest", "not_sure"];
const BUDGETS = ["under_100", "100_300", "300_1000", "1000_plus", "not_sure"];
const clean = (v, max) => String(v ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim().slice(0, max);
async function body(req) { const ct = req.headers.get("content-type") || ""; if (ct.includes("json")) return req.json().catch(() => ({})); if (ct.includes("form")) return Object.fromEntries(await req.formData()); return {}; }
async function ipHash(req) { const ip = req.headers.get("cf-connecting-ip") || "0"; const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("faw:" + ip)); return [...new Uint8Array(d)].slice(0, 8).map(b => b.toString(16).padStart(2, "0")).join(""); }
async function limited(env, req, route, max = 5) { const k = `rl:${route}:${await ipHash(req)}:${Math.floor(Date.now() / 3600e3)}`; const n = Number(await env.SUBSCRIBERS.get(k) || 0); if (n >= max) return true; await env.SUBSCRIBERS.put(k, String(n + 1), { expirationTtl: 3600 }); return false; }
function httpsUrl(u) { try { const x = new URL(/^https?:\/\//i.test(u) ? u : "https://" + u); return x.hostname.includes(".") ? x.toString() : null; } catch { return null; } }

export async function onRequestPost({ request, env }) {
  if (Number(request.headers.get("content-length") || 0) > 8192) return json({ ok: false, error: "Request too large." }, 413);
  const b = await body(request);
  if (b.website_hp) return json({ ok: true }); // honeypot
  if (!env.SUBSCRIBERS) return json({ ok: false, error: "Sponsor requests are temporarily unavailable." }, 503);
  if (await limited(env, request, "sponsor")) return json({ ok: false, error: "Too many requests — try again in an hour." }, 429);
  const company = clean(b.company, 120), website = httpsUrl(clean(b.website, 300)), email = clean(b.email, 254).toLowerCase();
  const slot = SLOTS.includes(b.slot) ? b.slot : "not_sure", budget = BUDGETS.includes(b.budget) ? b.budget : "not_sure", message = clean(b.message, 2000);
  const errs = [];
  if (company.length < 2) errs.push("Company is required.");
  if (!website) errs.push("Website must be a valid URL.");
  if (!EMAIL_RE.test(email)) errs.push("A valid contact email is required.");
  if (errs.length) return json({ ok: false, error: errs.join(" ") }, 400);
  const id = `sponsor:${new Date().toISOString()}:${crypto.randomUUID().slice(0, 8)}`;
  await env.SUBSCRIBERS.put(id, JSON.stringify({ id, kind: "sponsor", status: "pending", company, website, email, slot, budget, message, created: new Date().toISOString() }));
  return json({ ok: true, message: "Thanks! We'll reply by email. Nothing goes live until we've agreed on details." });
}
export const onRequest = () => json({ ok: false, error: "Method not allowed" }, 405);
