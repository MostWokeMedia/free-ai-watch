# Community submissions & sponsor requests: review flow

**Nothing submitted is ever published automatically.** Forms only write *pending* records to private KV storage. No public endpoint reads them.

## Where things go
| Form | Page | Endpoint | KV key prefix |
|---|---|---|---|
| Submit a deal | /submit | POST /api/submit | `submission:` |
| Sponsor request | /sponsor | POST /api/sponsor | `sponsor:` |

- Both reuse the existing **SUBSCRIBERS** KV binding. Prefixes keep them apart from `sub:` (newsletter emails) and `rl:` (rate-limit counters). The deploy token is Pages-Edit only, so a separate SUBMISSIONS namespace wasn't created. To split later: create a KV namespace, bind it as `SUBMISSIONS`, and switch `env.SUBSCRIBERS` → `env.SUBMISSIONS` in the two functions and the admin API.
- **Protections:** a honeypot field, a 5 per hour per IP rate limit (hashed IP, 1-hour TTL), length caps, control characters stripped, and source URLs that must be https. All text is shown escaped: the site escapes when rendering, and the review script prints with `repr()`.

## Enable the owner review API (one-time)
The admin API `/api/admin/queue` stays **disabled (403) until `ADMIN_TOKEN` is set**.
1. Generate a long random token locally: `python3 -c "import secrets;print(secrets.token_urlsafe(32))"` (24+ characters required).
2. Cloudflare dashboard → Workers & Pages → **freeaiwatch** → Settings → Variables and Secrets → Add → Type **Secret**, name `ADMIN_TOKEN`, Production. (CLI alternative: `npx wrangler pages secret put ADMIN_TOKEN --project-name=freeaiwatch` with an account-level token.)
3. Redeploy: push, or re-run the workflow.
4. Locally: `export FAW_ADMIN_TOKEN=<same value>`. Never commit it.

## Review
```bash
python3 scripts/review_submissions.py list                          # pending deal submissions
python3 scripts/review_submissions.py list --kind sponsor           # pending sponsor requests
python3 scripts/review_submissions.py approve <id> --phrase "1,000 free credits" \
   --name "Example free tier" --provider "Example" --value "1,000 credits/month" --category API --card no --resets monthly
python3 scripts/review_submissions.py reject <id> --note "not an official source"
python3 scripts/review_submissions.py sponsor-done <id> --note "replied 2026-10-15"
```
- `approve` opens the **submitted official source URL**, requires your `--phrase` to appear on it, and only then appends the offer to `data/offers.json` with `"note": "community-submitted"` plus evidence. It adds a Today-feed event and marks the KV record approved.
- If the phrase isn't found, nothing changes.
- **Publishing happens only when you `git commit && git push`.** Review the diff first.
- Reply to sponsor requests by email. Nothing on /sponsor goes live without a manual change to the site.
