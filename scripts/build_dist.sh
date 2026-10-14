#!/usr/bin/env bash
# Builds dist/ with PUBLIC files only (no scripts, snapshots, drafts, posts source, venv, candidates, og source).
# Pages Functions live in ./functions (repo root) — `wrangler pages deploy dist` run from repo root uploads them automatically.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist/site dist/data
cp _headers dist/
cp site/style.css site/app.js site/compare.js site/signup.js site/theme.js site/logo.svg site/favicon.svg site/og.png dist/site/
cp data/offers.json data/changes.json dist/data/
[ -f data/x_spotted.json ] && cp data/x_spotted.json dist/data/ || echo "[]" > dist/data/x_spotted.json
python3 scripts/build_site.py
# Cache-bust /site assets (they are cached 1 day): append ?v=<content hash> in every HTML file
for f in site/style.css site/app.js site/compare.js site/signup.js site/theme.js; do
  h=$(sha256sum "$f" | cut -c1-10); find dist -name '*.html' -exec sed -i "s#/$f\"#/$f?v=$h\"#g" {} +
done
echo "dist/ built: $(find dist -type f | wc -l) files"
