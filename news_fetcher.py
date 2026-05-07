import requests
from datetime import datetime, timedelta
import streamlit as st

SECTOR_TREND_QUERIES = {
    "Healthcare Services": "healthcare services M&A private equity Canada trends",
    "Infrastructure": "infrastructure investment Canada private equity deals",
    "Financial Services": "financial services fintech Canada M&A investment",
    "Special Situations": "distressed debt restructuring Canada private credit",
}


def fetch_company_news(company_name: str, days_back: int = 30) -> list[dict]:
    api_key = st.secrets["NEWSAPI_KEY"]
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    params = {
        "q": f'"{company_name}"',
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 10,
        "apiKey": api_key,
    }

    response = requests.get("https://newsapi.org/v2/everything", params=params)
    data = response.json()

    if data.get("status") != "ok":
        return []

    articles = []
    for a in data.get("articles", []):
        if not a.get("title") or not a.get("description"):
            continue
        articles.append({
            "title": a["title"],
            "description": a.get("description", "")[:200],
            "source": a["source"]["name"],
            "url": a["url"],
            "published_at": a["publishedAt"][:10],
        })

    return articles


def fetch_sector_trends(sector: str, days_back: int = 30) -> list[dict]:
    api_key = st.secrets["NEWSAPI_KEY"]
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    query = SECTOR_TREND_QUERIES.get(sector, f"{sector} investment Canada")

    params = {
        "q": query,
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 5,
        "apiKey": api_key,
    }

    response = requests.get("https://newsapi.org/v2/everything", params=params)
    data = response.json()

    if data.get("status") != "ok":
        return []

    articles = []
    for a in data.get("articles", []):
        if not a.get("title") or not a.get("description"):
            continue
        articles.append({
            "title": a["title"],
            "description": a.get("description", "")[:200],
            "source": a["source"]["name"],
            "url": a["url"],
            "published_at": a["publishedAt"][:10],
        })

    return articles
