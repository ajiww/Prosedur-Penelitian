# scraper/fetcher.py
import requests
from config import HEADERS

def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

