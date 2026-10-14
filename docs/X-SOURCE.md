# X (Twitter) source — "Spotted on X, unverified"

GitHub Actions has **no X access**. The agent runs this daily using the `x` MCP namespace, then pushes; the push deploys.

## Rules (Spencer)
- Keep only **original posts**: no replies, quotes, retweets (queries use `-is:reply -is:quote -is:retweet`; `x_ingest.py` also drops anything with `in_reply_to_user_id` or `referenced_tweets` of type replied_to/quoted/retweeted).
- Author must be on **`config/x_official_accounts.json`** (official product account, or a founder/lead with an evidence URL). Everything else is dropped — discovery hits are only leads for new accounts to verify.
- Two patterns (see `reference_patterns` in `config/x_sources.json`):
  - `promo_time_limited` — e.g. https://x.com/higgsfield_ai/status/2110074247569924489 "Wan 3.0 is now UNLIMITED on Higgsfield for 7 days. 60% OFF…"
  - `engagement_gated` — e.g. https://x.com/FishAudio/status/2110038429199450126 "Comment “DRAMA” within the next 48 hours for 1 month free."
- Items are shown with a **"Spotted on X · unverified"** badge and link to the post; they never enter the verified offers table.

## Daily run (~6–12 X calls; limits 30/min, 1000/day, 25 results/call)
1. For each entry in `config/x_sources.json → queries`: call `x.search_posts_all` with `query`, `start_time` = now − `start_days_ago`, `max_results`, `sort_order`, and the configured `post.fields` / `expansions` / `user.fields`.
2. If a hit is truncated and lacks `note_tweet`, fetch full text with `x.get_posts_by_ids`.
3. Save all responses to `data/x_raw/YYYY-MM-DD.json` as `{"fetched_at":…, "results":[{"name":…, "response":…}]}`.
4. `python3 scripts/x_ingest.py data/x_raw/YYYY-MM-DD.json` → updates `data/x_spotted.json` (dedupe by post id and tool+offer, deadline = post time + stated duration/date, expired and >14-day-old undated items removed) and adds `spotted_on_x` events to `data/changes.json` (Today feed).
5. Read the kept items; delete anything spammy/scammy/crypto-giveaway by hand.
6. Optionally `python3 scripts/draft_posts.py` (adds a "Spotted on X" draft).
7. `git add data/x_raw data/x_spotted.json data/changes.json drafts && git commit -m "x source YYYY-MM-DD" && git push`.

## Adding an official account
Look up the handle (`x.get_users_by_usernames` with `description,url,entities`) and confirm the profile's website is the product's official domain (or the official site links to the X account). Add to `accounts` with `evidence_url`. For people, add to `people` with evidence (official site team page, official account naming them, or bio).
