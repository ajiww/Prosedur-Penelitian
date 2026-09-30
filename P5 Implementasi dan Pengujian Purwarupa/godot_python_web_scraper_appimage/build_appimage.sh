#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

APP_NAME="GodotPythonWebScraper"
APP_DIR="$ROOT/build/AppDir"
GODOT_BIN="$ROOT/build/godot/${APP_NAME}.x86_64"

if ! command -v godot >/dev/null 2>&1; then
  echo "ERROR: godot tidak ditemukan di PATH. Install Godot 4.x terlebih dahulu."
  exit 1
fi

if ! command -v appimagetool >/dev/null 2>&1; then
  echo "ERROR: appimagetool tidak ditemukan di PATH."
  echo "Download AppImage tooling dari AppImageKit/linuxdeploy project atau install appimagetool."
  exit 1
fi

"$ROOT/build_python.sh"

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/bin" "$APP_DIR/output"

echo "[1/3] Export Godot..."
godot --headless --path "$ROOT" --export-release "Linux" "$GODOT_BIN"

if [[ ! -f "$GODOT_BIN" ]]; then
  echo "ERROR: export Godot gagal: $GODOT_BIN tidak ditemukan."
  exit 1
fi

echo "[2/3] Menyusun AppDir..."
cp "$GODOT_BIN" "$APP_DIR/$APP_NAME.x86_64"
cp "$ROOT/build/python/scraper" "$APP_DIR/bin/scraper"
chmod +x "$APP_DIR/$APP_NAME.x86_64" "$APP_DIR/bin/scraper"

cat > "$APP_DIR/AppRun" <<'APPRUN'
#!/usr/bin/env bash
set -e
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/GodotPythonWebScraper.x86_64" "$@"
APPRUN
chmod +x "$APP_DIR/AppRun"

cat > "$APP_DIR/GodotPythonWebScraper.desktop" <<'DESKTOP'
[Desktop Entry]
Name=Godot Python Web Scraper
Exec=GodotPythonWebScraper
Type=Application
Categories=Network;Utility;
Terminal=false
Comment=GUI web scraper powered by Godot and Python
DESKTOP

# Optional icon. AppImage can still be built without one.
echo "[3/3] Membuat AppImage..."
appimagetool "$APP_DIR" "$ROOT/build/${APP_NAME}.AppImage"
chmod +x "$ROOT/build/${APP_NAME}.AppImage"

echo "SELESAI: $ROOT/build/${APP_NAME}.AppImage"
