// Cloudflare Pages Function: POST /api/subscribe
// Storage: KV namespace bound as SUBSCRIBERS (Pages project → Settings → Bindings). If unbound, returns 503 gracefully.
// Admin removal: DELETE /api/subscribe?email=... with header "Authorization: Bearer <ADMIN_TOKEN>" (env secret; disabled if unset).
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

async function readBody(request) {
  const ct = request.headers.get("content-type") || "";
  if (ct.includes("application/json")) return await request.json().catch(() => ({}));
  if (ct.includes("form")) return Object.fromEntries(await request.formData());
  return {};
}

export async function onRequestPost({ request, env }) {
  const len = Number(request.headers.get("content-length") || 0);
  if (len > 2048) return json({ ok: false, error: "Request too large." }, 413);
  const body = await readBody(request);
  if (body.website) return json({ ok: true }); // honeypot filled → silently accept, store nothing
  const email = String(body.email || "").trim().toLowerCase();
  if (email.length > 254 || !EMAIL_RE.test(email)) return json({ ok: false, error: "Please enter a valid email address." }, 400);
  if (!env.SUBSCRIBERS) return json({ ok: false, error: "Signups open soon — storage not configured yet." }, 503);
  const key = "sub:" + email;
  if (await env.SUBSCRIBERS.get(key)) return json({ ok: true, already: true });
  await env.SUBSCRIBERS.put(key, JSON.stringify({ email, created: new Date().toISOString(), source: String(body.source || "").slice(0, 100) }));
  return json({ ok: true });
}

export async function onRequestDelete({ request, env }) {
  if (!env.ADMIN_TOKEN || request.headers.get("authorization") !== "Bearer " + env.ADMIN_TOKEN) return json({ ok: false, error: "Forbidden" }, 403);
  if (!env.SUBSCRIBERS) return json({ ok: false, error: "storage not configured" }, 503);
  const email = (new URL(request.url).searchParams.get("email") || "").trim().toLowerCase();
  await env.SUBSCRIBERS.delete("sub:" + email);
  return json({ ok: true, removed: email });
}

export const onRequest = () => json({ ok: false, error: "Method not allowed" }, 405);
