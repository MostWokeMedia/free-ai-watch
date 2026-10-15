// Sponsor click redirect: /go/<slug>?m=row|banner|x|digest → sponsor URL + UTMs (302).
// Counts at most one click per visitor per day per sponsor. Visitor = SHA-256(daily random salt + IP + UA); raw IP never stored.
import cfg from "../../config/sponsors.json";
const MEDIA = ["row", "banner", "x", "digest"];
const BOT = /bot|crawl|spider|slurp|preview|facebookexternalhit|embedly|curl|wget|python|httpclient|headless|monitor|lighthouse|scan|fetch/i;
const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
export async function onRequestGet({ request, env, params }) {
  const slug = String(params.slug || "").toLowerCase();
  const s = /^[a-z0-9-]{1,60}$/.test(slug) && (cfg.sponsors || {})[slug];
  if (!s || s.active === false || !/^https:\/\//.test(s.url || "")) return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
  const u = new URL(request.url); const m = MEDIA.includes(u.searchParams.get("m")) ? u.searchParams.get("m") : "row";
  const dest = new URL(s.url);
  dest.searchParams.set("utm_source", "freeaiwatch"); dest.searchParams.set("utm_medium", m); dest.searchParams.set("utm_campaign", "founding-" + slug);
  const ua = request.headers.get("user-agent") || "";
  if (env.SUBSCRIBERS && ua && !BOT.test(ua) && request.method === "GET") {
    try {
      const day = new Date().toISOString().slice(0, 10), KV = env.SUBSCRIBERS;
      let salt = await KV.get("click:salt:" + day);
      if (!salt) { salt = hex(crypto.getRandomValues(new Uint8Array(16))); await KV.put("click:salt:" + day, salt, { expirationTtl: 172800 }); }
      const ip = request.headers.get("cf-connecting-ip") || "";
      const vid = hex(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(salt + "|" + ip + "|" + ua))).slice(0, 32);
      const seen = `click:seen:${day}:${slug}:${vid}`;
      if (!(await KV.get(seen))) {
        await KV.put(seen, "1", { expirationTtl: 172800 });
        const ck = `click:count:${day}:${slug}:${m}`;
        await KV.put(ck, String((parseInt(await KV.get(ck) || "0", 10) || 0) + 1));
      }
    } catch (e) { /* counting must never block the redirect */ }
  }
  return new Response(null, { status: 302, headers: { Location: dest.toString(), "Cache-Control": "no-store", "Referrer-Policy": "no-referrer-when-downgrade" } });
}
export const onRequest = () => new Response("Method not allowed", { status: 405 });
