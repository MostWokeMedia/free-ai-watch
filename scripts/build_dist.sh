#!/usr/bin/env bash
# Builds dist/ with PUBLIC files only (no scripts, snapshots, drafts, posts source, venv, candidates, og source).
# Pages Functions live in ./functions (repo root) — `wrangler pages deploy dist` run from repo root uploads them automatically.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist/site dist/data
cp _headers dist/
cp site/style.css site/app.js site/compare.js site/signup.js site/logo.svg site/favicon.svg site/og.png dist/site/
cp data/offers.json data/changes.json dist/data/
python3 scripts/build_site.py
echo "dist/ built: $(find dist -type f | wc -l) files"
