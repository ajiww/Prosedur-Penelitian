#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

python3 -m venv .venv-build
source .venv-build/bin/activate
python -m pip install --upgrade pip
python -m pip install -r python/requirements.txt

rm -rf build/python dist
mkdir -p build/python

pyinstaller \
  --clean \
  --noconfirm \
  --onefile \
  --name scraper \
  --distpath build/python \
  python/scraper.py

chmod +x build/python/scraper

echo "Python scraper: $ROOT/build/python/scraper"
