# Godot Python Web Scraper — Linux AppImage

Project Godot 4 + Python scraper yang ditujukan untuk distribusi Linux melalui AppImage.

## Arsitektur

Godot GUI memanggil executable `bin/scraper` yang dibangun dengan PyInstaller. Aplikasi tidak lagi bergantung pada Python sistem saat sudah dipaketkan sebagai AppImage.

## Build di Ubuntu

Persyaratan:

- Godot 4.x + Linux export templates
- Python 3
- `venv` Python
- `appimagetool`

Langkah:

```bash
chmod +x build_python.sh build_appimage.sh tools/setup_dev.sh
./build_appimage.sh
```

Output:

```text
build/GodotPythonWebScraper.AppImage
```

Jalankan:

```bash
chmod +x build/GodotPythonWebScraper.AppImage
./build/GodotPythonWebScraper.AppImage
```

## Mode development

Sebelum membuka project di editor Godot, buat executable scraper:

```bash
./tools/setup_dev.sh
```

Ini menghasilkan:

```text
bin/scraper
```

## Data hasil scraping

AppImage dipasang pada filesystem read-only. Karena itu CSV tidak ditulis ke `res://`. Aplikasi menyimpan hasil di:

```text
<Godot user data>/scraper_output/result.csv
```

Tombol **Buka Folder Output** membuka lokasi tersebut.

## Catatan kompatibilitas

AppImage bersifat portable tetapi tetap dipengaruhi kompatibilitas glibc/library pada distribusi Linux target. Untuk distribusi luas, build sebaiknya dilakukan pada Ubuntu yang cukup tua dibanding target minimum.

Scraper hanya melakukan HTTP request + parsing HTML statis. Situs yang membutuhkan JavaScript penuh, login, CAPTCHA, atau anti-bot dapat memerlukan Playwright/Selenium dan mekanisme yang berbeda.

Gunakan scraper hanya pada situs yang mengizinkan akses otomatis dan hormati robots.txt, terms of service, rate limit, serta privasi data.
