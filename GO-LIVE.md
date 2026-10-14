# FreeAIWatch — go-live checklist (needs Spencer's approval for every account/purchase)
1. [ ] Register freeaiwatch.com (Porkbun ~$11.08/yr seen 2026-10-13) — re-check availability first.
2. [ ] Claim @freeaiwatch on X (bio + link to freeaiwatch.com, header = site/og.png).
3. [ ] Create GitHub repo (private ok), push this folder.
4. [ ] Create Cloudflare account (Free plan OK for a sponsor-funded site — no commercial-use restriction in the Self-Serve Subscription Agreement; Pages has unlimited bandwidth/requests, 500 builds/mo).
5. [ ] Create Pages project `freeaiwatch` (Direct Upload; production branch `main`). Or let the first `wrangler pages deploy` create it.
6. [ ] Create Cloudflare API token with "Cloudflare Pages: Edit" → repo secrets CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID.
7. [ ] Run the workflow manually (Actions → daily-check-and-deploy → Run) and confirm the freeaiwatch.pages.dev URL. Local test: `bash scripts/build_dist.sh` (only public files go in dist/).
8. [ ] Add custom domain freeaiwatch.com in Pages → Custom domains; easiest if the domain's DNS is on Cloudflare.
9. [ ] Human review of all offer rows (card/resets/descriptions), fix weak "Free" matches.
10. [ ] Wire email signup to a newsletter tool (e.g. Buttondown/Beehiiv) — currently a placeholder.
11. [ ] Fill sponsor page (pricing + contact email).
12. [ ] Add analytics (e.g. Cloudflare Web Analytics) for sponsor traffic numbers.
13. [ ] Launch: Spencer posts drafts/<date>.txt from @freeaiwatch (bot never posts).

## Email digest (added 2026-10-14)
- Signup form → `functions/api/subscribe.js` (Cloudflare Pages Function). Stores to KV binding **SUBSCRIBERS**; without it, returns 503 "Signups open soon".
- [ ] Cloudflare dashboard → Storage & Databases → KV → Create namespace `freeaiwatch-subscribers`.
- [ ] Workers & Pages → freeaiwatch → Settings → Bindings → Add → KV namespace → Variable name `SUBSCRIBERS` → that namespace (Production). Redeploy (push or re-run workflow).
- [ ] Optional: Settings → Variables and Secrets → add secret `ADMIN_TOKEN` (enables DELETE /api/subscribe?email=… for removals).
- [ ] To actually send: pick a sender (e.g. Buttondown or Resend), verify freeaiwatch.com sending domain (SPF/DKIM), add a real unsubscribe link, export/sync emails from KV. Weekly draft: `drafts/weekly-YYYY-MM-DD.md` (auto on Mondays).
## Blog
- New post: copy `posts/TEMPLATE.md` → `posts/YYYY-MM-DD-slug.md`, write real content, set `status: published`, push.
