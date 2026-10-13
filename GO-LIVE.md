# FreeAIWatch — go-live checklist (needs Spencer's approval for every account/purchase)
1. [ ] Register freeaiwatch.com (Porkbun ~$11.08/yr seen 2026-10-13) — re-check availability first.
2. [ ] Claim @freeaiwatch on X (bio + link to freeaiwatch.com, header = site/og.png).
3. [ ] Create GitHub repo (private ok), push this folder.
4. [ ] Create Vercel account. NOTE: Hobby (free) is non-commercial only; sponsors/ads = commercial → Pro plan ($20/mo per vercel.com/pricing, 2026-10-13). Can preview on Hobby before any sponsor/affiliate goes live, then upgrade.
5. [ ] Locally: `npx vercel link` (creates project `freeaiwatch`; framework "Other", no build command, output = repo root). Copy orgId/projectId from .vercel/project.json.
6. [ ] Create a Vercel access token → repo secrets VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID.
7. [ ] Run the workflow manually (Actions → daily-check-and-deploy → Run) and confirm the *.vercel.app URL.
8. [ ] Add custom domain freeaiwatch.com in Vercel → set the DNS records Vercel shows at the registrar.
9. [ ] Human review of all offer rows (card/resets/descriptions), fix weak "Free" matches.
10. [ ] Wire email signup to a newsletter tool (e.g. Buttondown/Beehiiv) — currently a placeholder.
11. [ ] Fill sponsor page (pricing + contact email).
12. [ ] Add analytics (e.g. Vercel Web Analytics) for sponsor traffic numbers.
13. [ ] Launch: Spencer posts drafts/<date>.txt from @freeaiwatch (bot never posts).
