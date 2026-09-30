# main.py
from scraper.fetcher import fetch_page
from scraper.parser import parse_html
from scraper.storage import save_data
from utils.logger import logger
from config import BASE_URL

def run_scraper():
    logger.info("Fetching page...")
    html = fetch_page(BASE_URL)

    logger.info("Parsing content...")
    data = parse_html(html)

    logger.info("Saving data...")
    save_data(data)

    logger.info("Scraping completed!")

if __name__ == "__main__":
    run_scraper()

