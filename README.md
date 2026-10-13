# FreeAIWatch (preview) — freeaiwatch.com · @freeaiwatch
- Serve: python3 -m http.server 8787 --bind 127.0.0.1  -> http://127.0.0.1:8787/
- Daily check: . .venv/bin/activate && python scripts/check_sources.py   (re-fetches sources, diffs snapshots/, logs to data/changes.json)
- Drafts: python3 scripts/draft_posts.py  -> drafts/YYYY-MM-DD.txt (never posts)
- Seed from data/candidates.json: python scripts/check_sources.py --seed (keeps only offers whose phrase is found on the official page)
