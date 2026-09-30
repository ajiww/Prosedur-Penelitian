# scraper/__init__.py
from .fetcher import fetch_page
from .parser import parse_html
from .storage import save_data

__all__ = ["fetch_page", "parse_html", "save_data"]

