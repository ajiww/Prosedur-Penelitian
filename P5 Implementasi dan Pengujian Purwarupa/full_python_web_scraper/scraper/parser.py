# scraper/parser.py
from bs4 import BeautifulSoup

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for article in soup.select("div.article"):
        title = article.select_one("h2").get_text(strip=True)
        link = article.select_one("a")["href"]
        items.append({"title": title, "link": link})
    return items

