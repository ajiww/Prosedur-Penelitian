#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
./build_python.sh
cp build/python/scraper bin/scraper
chmod +x bin/scraper
printf '\nScraper development siap: %s\n' "$ROOT/bin/scraper"
