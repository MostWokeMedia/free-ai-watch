// Owner-only click counts. Disabled (403) unless the ADMIN_TOKEN secret is set. See docs/CLICKS.md.
// GET /api/admin/clicks?slug=<optional>&since=YYYY-MM-DD  → {ok, rows:[{day,slug,medium,clicks}]}
// DELETE /api/admin/clicks?slug=<slug>  → removes that sponsor's count keys (e.g. the test slug)
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
function authed(req, env) {
  if (!env.ADMIN_TOKEN || env.ADMIN_TOKEN.length < 24) return false;
  const a = new TextEncoder().encode(req.headers.get("authorization") || ""), b = new TextEncoder().encode("Bearer " + env.ADMIN_TOKEN);
  if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i]; return d === 0;
}
async function keys(env) { const out = []; let cursor; do { const r = await env.SUBSCRIBERS.list({ prefix: "click:count:", cursor }); out.push(...r.keys.map((k) => k.name)); cursor = r.list_complete ? null : r.cursor; } while (cursor); return out; }
export async function onRequest({ request, env }) {
  if (!authed(request, env)) return json({ ok: false, error: "Forbidden" }, 403);
  if (!env.SUBSCRIBERS) return json({ ok: false, error: "KV not bound" }, 503);
  const u = new URL(request.url), slug = u.searchParams.get("slug"), since = u.searchParams.get("since") || "0000";
  const rows = [];
  for (const k of await keys(env)) {
    const [, , day, s, medium] = k.split(":");
    if ((slug && s !== slug) || day < since) continue;
    if (request.method === "DELETE") { if (slug) { await env.SUBSCRIBERS.delete(k); rows.push({ deleted: k }); } continue; }
    rows.push({ day, slug: s, medium, clicks: parseInt(await env.SUBSCRIBERS.get(k) || "0", 10) });
  }
  if (request.method === "DELETE" && !slug) return json({ ok: false, error: "slug required" }, 400);
  if (!["GET", "DELETE"].includes(request.method)) return json({ ok: false, error: "Method not allowed" }, 405);
  rows.sort((a, b) => (a.day || "").localeCompare(b.day || "")); return json({ ok: true, rows });
}
