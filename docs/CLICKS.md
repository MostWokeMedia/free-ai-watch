# Sponsor click tracking

**Tracked link:** `https://freeaiwatch.com/go/<slug>?m=row|banner|x|digest`
- The slug is looked up in `config/sponsors.json` (`sponsors.<slug>.url`, which must be https, and `active`). Unknown or inactive slugs return 404.
- Redirect: 302 to the URL with `utm_source=freeaiwatch&utm_medium=<m>&utm_campaign=founding-<slug>`. An unknown or missing `m` defaults to `row`.
- Adding a sponsor: add an entry under `sponsors`, then commit and push. The config is bundled into the function at deploy time.

## Counting rules (these are the "counted clicks" behind the click floor)
- At most one click per visitor, per sponsor, per UTC day. The visitor ID is SHA-256(daily random salt + IP + user agent), truncated. The salt is random per day and expires after 48h, so IDs can't be linked across days. Raw IPs and user agents are never stored.
- Skipped: requests with an empty user agent or an obvious bot/tool user agent (bot, crawl, spider, preview, curl, wget, python, headless, …).
- KV keys (SUBSCRIBERS namespace): `click:count:<day>:<slug>:<medium>` holds the count; `click:seen:…` and `click:salt:…` expire after 48h.
- A counting failure never blocks the redirect.

## Reading counts
The endpoint is `/api/admin/clicks` (GET, or DELETE with `?slug=`). It returns **403 until `ADMIN_TOKEN` is set**.
1. Set the token: Cloudflare dashboard → Workers & Pages → freeaiwatch → Settings → Variables and Secrets → Add → type *Secret*, name `ADMIN_TOKEN`, value: a random string of 24+ characters (e.g. `python3 -c "import secrets;print(secrets.token_urlsafe(32))"`). Then redeploy (push or re-run the workflow). Or use `npx wrangler pages secret put ADMIN_TOKEN --project-name=freeaiwatch`.
2. `python scripts/click_report.py [--slug acme] [--since 2026-11-01]`
3. To remove a sponsor's counts: `python scripts/click_report.py --delete-slug <slug>`.

## Test slug
`test-sponsor` (→ https://example.com/) was added to prove the redirect live and then removed from the config. The live tests used a `curl` user agent, which is on the bot list, so no counts should exist for it. If any do, run `--delete-slug test-sponsor` once the token is set.

**Status (Oct 14, 2026):** ADMIN_TOKEN is set on the production Pages project. The owner copy is at `/home/box/.secrets/freeaiwatch_admin_token` on the box, and the same value is in the `FAW_ADMIN_TOKEN` GitHub secret. To rotate it, write a new value to that file, then run `gh secret set FAW_ADMIN_TOKEN < file` and `wrangler pages secret put ADMIN_TOKEN --project-name=freeaiwatch` (or use a one-off Actions workflow, since the deploy token has Pages Edit), then redeploy.
