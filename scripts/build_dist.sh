#!/usr/bin/env bash
# Builds dist/ with PUBLIC files only (no scripts, snapshots, drafts, venv, candidates, og source).
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist/site dist/data
cp index.html _headers dist/
cp site/style.css site/app.js site/logo.svg site/favicon.svg site/og.png dist/site/
cp data/offers.json data/changes.json dist/data/
echo "dist/ built: $(find dist -type f | wc -l) files"
