import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from src.state import StockState


def scrape_news_node(state: StockState) -> Dict[str, Any]:
    """
    Branch C1 Node: Scrapes top 5 Thai financial news articles via Google News RSS
    for the query '{ticker} หุ้น'. Preserves Thai character encoding.
    """
    ticker = state.get("ticker", "").strip()
    if not ticker:
        return {"news_articles": []}

    query = f"{ticker} หุ้น"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=th&gl=TH&ceid=TH:th"

    articles: List[Dict[str, str]] = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Force UTF-8 encoding
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.content, "xml")

            items = soup.find_all("item")
            for item in items[:5]:
                title = item.title.text.strip() if item.title else "No Title"
                link = item.link.text.strip() if item.link else ""
                pub_date = item.pubDate.text.strip() if item.pubDate else ""
                source = item.source.text.strip() if item.source else "Google News"

                articles.append(
                    {
                        "title": title,
                        "link": link,
                        "pub_date": pub_date,
                        "source": source,
                    }
                )
    except Exception as e:
        print(f"Warning: News scraping for {ticker} failed: {e}")

    return {"news_articles": articles}
