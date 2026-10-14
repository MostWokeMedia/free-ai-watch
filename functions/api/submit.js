// POST /api/submit — community deal submissions. Stored as PENDING in KV; nothing is ever published automatically.
// Storage: reuses the SUBSCRIBERS KV binding with key prefix "submission:" (no separate namespace could be created
// with the Pages-only deploy token). Rate limit: 5 per IP per hour via "rl:submit:<iphash>:<hour>" keys (TTL 1h).
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;
const clean = (v, max) => String(v ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim().slice(0, max);
async function body(req) { const ct = req.headers.get("content-type") || ""; if (ct.includes("json")) return req.json().catch(() => ({})); if (ct.includes("form")) return Object.fromEntries(await req.formData()); return {}; }
async function ipHash(req) { const ip = req.headers.get("cf-connecting-ip") || "0"; const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("faw:" + ip)); return [...new Uint8Array(d)].slice(0, 8).map(b => b.toString(16).padStart(2, "0")).join(""); }
async function limited(env, req, route, max = 5) { const k = `rl:${route}:${await ipHash(req)}:${Math.floor(Date.now() / 3600e3)}`; const n = Number(await env.SUBSCRIBERS.get(k) || 0); if (n >= max) return true; await env.SUBSCRIBERS.put(k, String(n + 1), { expirationTtl: 3600 }); return false; }
function httpsUrl(u) { try { const x = new URL(u); return x.protocol === "https:" && x.hostname.includes(".") ? x.toString() : null; } catch { return null; } }

export async function onRequestPost({ request, env }) {
  if (Number(request.headers.get("content-length") || 0) > 8192) return json({ ok: false, error: "Request too large." }, 413);
  const b = await body(request);
  if (b.website) return json({ ok: true }); // honeypot
  if (!env.SUBSCRIBERS) return json({ ok: false, error: "Submissions are temporarily unavailable." }, 503);
  if (await limited(env, request, "submit")) return json({ ok: false, error: "Too many submissions — try again in an hour." }, 429);
  const tool = clean(b.tool, 100), offer = clean(b.offer, 1000), source = httpsUrl(clean(b.source_url, 500));
  const deadline = clean(b.deadline, 10), email = clean(b.email, 254).toLowerCase();
  const errs = [];
  if (tool.length < 2) errs.push("Tool name is required.");
  if (offer.length < 10) errs.push("Describe the offer (at least 10 characters).");
  if (!source) errs.push("Link to the official source must be a valid https:// URL.");
  if (deadline && !/^\d{4}-\d{2}-\d{2}$/.test(deadline)) errs.push("Deadline must be a date (YYYY-MM-DD).");
  if (email && !EMAIL_RE.test(email)) errs.push("Email looks invalid (it is optional).");
  if (errs.length) return json({ ok: false, error: errs.join(" ") }, 400);
  const id = `submission:${new Date().toISOString()}:${crypto.randomUUID().slice(0, 8)}`;
  await env.SUBSCRIBERS.put(id, JSON.stringify({ id, kind: "submission", status: "pending", tool, offer, source_url: source, deadline: deadline || null, email: email || null, created: new Date().toISOString() }));
  return json({ ok: true, message: "Thanks! Your deal is queued for review. We verify every offer on its official page before listing it." });
}
export const onRequest = () => json({ ok: false, error: "Method not allowed" }, 405);
