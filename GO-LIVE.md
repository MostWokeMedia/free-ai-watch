# FreeAIWatch — go-live checklist (needs Spencer's approval for every account/purchase)
1. [ ] Register freeaiwatch.com (Porkbun ~$11.08/yr seen 2026-10-13) — re-check availability first.
2. [ ] Claim @freeaiwatch on X (bio + link to freeaiwatch.com, header = site/og.png).
3. [ ] Create GitHub repo (private ok), push this folder.
4. [ ] Create Cloudflare account + Pages project named `freeaiwatch` (direct upload).
5. [ ] Create Cloudflare API token (Pages: Edit) → repo secrets CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID.
6. [ ] Run the workflow manually (Actions → daily-check-and-deploy → Run) and confirm the *.pages.dev URL.
7. [ ] Add custom domain freeaiwatch.com in Pages; point registrar nameservers/DNS to Cloudflare.
8. [ ] Human review of all offer rows (card/resets/descriptions), fix weak "Free" matches.
9. [ ] Wire email signup to a newsletter tool (e.g. Buttondown/Beehiiv) — currently a placeholder.
10. [ ] Fill sponsor page (pricing + contact email).
11. [ ] Add privacy-friendly analytics (e.g. Cloudflare Web Analytics) for sponsor traffic numbers.
12. [ ] Launch: Spencer posts drafts/<date>.txt from @freeaiwatch (bot never posts).
