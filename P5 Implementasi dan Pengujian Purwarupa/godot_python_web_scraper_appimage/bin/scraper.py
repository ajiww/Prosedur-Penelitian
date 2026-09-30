#!/usr/bin/env python3
"""
Simple web scraper called by the Godot GUI.

Install:
    python -m pip install requests beautifulsoup4

Usage example:
    python scraper.py --url https://example.com --selector "h1" --output output/result.csv
"""

import argparse
import csv
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL tidak valid; gunakan http:// atau https://")


def scrape(url: str, selector: str | None, output: str) -> int:
    validate_url(url)

    headers = {
        "User-Agent": "GodotPythonWebScraper/1.0 (+educational project)"
    }

    print(f"Mengambil: {url}", flush=True)
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = []
    if selector:
        elements = soup.select(selector)
        print(f"Ditemukan {len(elements)} elemen.", flush=True)
        for i, element in enumerate(elements, start=1):
            rows.append({
                "index": i,
                "text": " ".join(element.stripped_strings),
                "tag": element.name,
                "url": url,
            })
    else:
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        rows.append({
            "index": 1,
            "text": title,
            "tag": "title",
            "url": url,
        })

    with open(output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "text", "tag", "url"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Hasil disimpan: {output}", flush=True)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--selector", default=None)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        count = scrape(args.url, args.selector, args.output)
        print(f"SELESAI: {count} baris.", flush=True)
        return 0
    except requests.HTTPError as exc:
        print(f"ERROR HTTP: {exc}", file=sys.stderr, flush=True)
        return 2
    except requests.RequestException as exc:
        print(f"ERROR jaringan: {exc}", file=sys.stderr, flush=True)
        return 3
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
