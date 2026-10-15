// Owner-only review API. Disabled unless the ADMIN_TOKEN secret is set on the Pages project (it is NOT set by default).
// GET  /api/admin/queue?kind=submission|sponsor&status=pending   → list items
// GET ?kind=sub&status=all lists newsletter subscribers. DELETE ?id=<sub:|submission:|sponsor: key> removes one record (e.g. test entries).
// POST /api/admin/queue  {"id": "...", "action": "approve"|"reject", "note": "..."} → updates status (record kept for audit)
// Auth: header "Authorization: Bearer <ADMIN_TOKEN>". Approving here does NOT publish anything; publishing happens only via
// scripts/review_submissions.py after verification against the official page, committed to the repo by the owner.
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
function authed(req, env) {
  if (!env.ADMIN_TOKEN || env.ADMIN_TOKEN.length < 24) return false;
  const h = req.headers.get("authorization") || ""; const a = new TextEncoder().encode(h), b = new TextEncoder().encode("Bearer " + env.ADMIN_TOKEN);
  if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i]; return d === 0;
}
export async function onRequestGet({ request, env }) {
  if (!authed(request, env)) return json({ ok: false, error: "Forbidden" }, 403);
  const u = new URL(request.url), kind = ["sponsor","sub"].includes(u.searchParams.get("kind")) ? u.searchParams.get("kind") : "submission", status = u.searchParams.get("status") || "pending";
  const items = []; let cursor;
  do { const r = await env.SUBSCRIBERS.list({ prefix: kind + ":", cursor }); for (const k of r.keys) { const raw = await env.SUBSCRIBERS.get(k.name); let v; try { v = JSON.parse(raw || "{}"); } catch { v = { value: raw }; } if (typeof v !== "object" || v === null) v = { value: v }; v.id = v.id || k.name; if (kind === "sub") v.status = v.status || "active"; if (status === "all" || v.status === status) items.push(v); } cursor = r.list_complete ? null : r.cursor; } while (cursor && items.length < 500);
  return json({ ok: true, items });
}
export async function onRequestPost({ request, env }) {
  if (!authed(request, env)) return json({ ok: false, error: "Forbidden" }, 403);
  const b = await request.json().catch(() => ({}));
  if (!/^(submission|sponsor):/.test(b.id || "") || !["approve", "reject"].includes(b.action)) return json({ ok: false, error: "Bad request" }, 400);
  const v = JSON.parse(await env.SUBSCRIBERS.get(b.id) || "null"); if (!v) return json({ ok: false, error: "Not found" }, 404);
  v.status = b.action === "approve" ? "approved" : "rejected"; v.reviewed = new Date().toISOString(); v.review_note = String(b.note || "").slice(0, 500);
  await env.SUBSCRIBERS.put(b.id, JSON.stringify(v)); return json({ ok: true, item: v });
}
export async function onRequestDelete({ request, env }) {
  if (!authed(request, env)) return json({ ok: false, error: "Forbidden" }, 403);
  const id = new URL(request.url).searchParams.get("id") || "";
  if (!/^(sub|submission|sponsor):/.test(id)) return json({ ok: false, error: "Bad request" }, 400);
  if (!(await env.SUBSCRIBERS.get(id))) return json({ ok: false, error: "Not found" }, 404);
  await env.SUBSCRIBERS.delete(id); return json({ ok: true, deleted: id });
}
export const onRequest = () => json({ ok: false, error: "Method not allowed" }, 405);
