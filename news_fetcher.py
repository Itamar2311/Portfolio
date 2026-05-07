import requests
from datetime import datetime, timedelta
import streamlit as st

SECTOR_TREND_QUERIES = {
    "Infrastructure": "infrastructure investment Canada acquisition deal 2026",
    "Healthcare Services": "healthcare services Canada acquisition private equity 2026",
    "Financial Services": "financial services fintech Canada M&A deal 2026",
    "Special Situations": "distressed debt restructuring Canada private credit 2026",
}

COMPANY_SEARCH_TERMS = {
    "Algonquin Power and Utilities": ["Algonquin Power", "AQN stock", "Algonquin utilities acquisition"],
    "Hydro One": ["Hydro One", "Hydro One acquisition", "Hydro One earnings"],
    "TransAlta Corporation": ["TransAlta", "TransAlta energy deal"],
    "Gibson Energy": ["Gibson Energy", "Gibson midstream"],
    "Enbridge": ["Enbridge", "Enbridge pipeline deal"],
    "Bayshore Healthcare": ["Bayshore Healthcare", "Bayshore home care"],
    "Extendicare": ["Extendicare", "Extendicare long-term care"],
    "Lifemark Health Group": ["Lifemark Health", "Lifemark physiotherapy"],
    "CBI Health": ["CBI Health", "CBI rehabilitation Canada"],
    "Manulife Financial": ["Manulife", "Manulife acquisition", "Manulife earnings"],
    "Rogers Communications": ["Rogers Communications", "Rogers telecom deal"],
    "Fairfax Financial": ["Fairfax Financial", "Prem Watsa investment"],
    "Element Fleet Management": ["Element Fleet", "Element Fleet earnings"],
    "Propel Holdings": ["Propel Holdings", "Propel fintech Canada"],
    "Chobani": ["Chobani", "Chobani IPO acquisition"],
    "Clearwater Seafoods": ["Clearwater Seafoods", "Clearwater acquisition"],
    "Yellow Pages": ["Yellow Pages Canada", "YP Canada restructuring"],
    "Torstar Corporation": ["Torstar", "Toronto Star ownership"],
}

STOCK_TICKERS = {
    "Algonquin Power and Utilities": "AQN.TO",
    "Hydro One": "H.TO",
    "TransAlta Corporation": "TA.TO",
    "Gibson Energy": "GEI.TO",
    "Enbridge": "ENB.TO",
    "Extendicare": "EXE.TO",
    "Manulife Financial": "MFC.TO",
    "Rogers Communications": "RCI-B.TO",
    "Fairfax Financial": "FFH.TO",
    "Element Fleet Management": "EFN.TO",
    "Propel Holdings": "PRL.TO",
}


def fetch_stock_data(company_name: str) -> dict:
    ticker = STOCK_TICKERS.get(company_name)
    if not ticker:
        return {}
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1mo"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        chart = data["chart"]["result"][0]
        closes = [c for c in chart["indicators"]["quote"][0]["close"] if c is not None]
        if len(closes) >= 2:
            first, last = closes[0], closes[-1]
            change_pct = round(((last - first) / first) * 100, 2)
            return {
                "ticker": ticker,
                "current_price": round(last, 2),
                "change_30d_pct": change_pct,
                "trend": "up" if change_pct > 2 else "down" if change_pct < -2 else "flat",
            }
    except Exception:
        pass
    return {}


def fetch_company_news(company_name: str, days_back: int = 30) -> list[dict]:
    api_key = st.secrets["NEWSAPI_KEY"]
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    search_terms = COMPANY_SEARCH_TERMS.get(company_name, [company_name])

    seen_urls = set()
    all_articles = []

    for term in search_terms[:2]:
        params = {
            "q": term,
            "from": from_date,
            "sortBy": "relevancy",
            "language": "en",
            "pageSize": 8,
            "apiKey": api_key,
        }
        try:
            r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=5)
            data = r.json()
            if data.get("status") != "ok":
                continue
            for a in data.get("articles", []):
                if not a.get("title") or not a.get("description"):
                    continue
                if a["url"] in seen_urls:
                    continue
                seen_urls.add(a["url"])
                all_articles.append({
                    "title": a["title"],
                    "description": a.get("description", "")[:250],
                    "source": a["source"]["name"],
                    "url": a["url"],
                    "published_at": a["publishedAt"][:10],
                })
        except Exception:
            continue

    return all_articles


def fetch_sector_trends(sector: str, days_back: int = 30) -> list[dict]:
    api_key = st.secrets["NEWSAPI_KEY"]
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    query = SECTOR_TREND_QUERIES.get(sector, f"{sector} Canada investment 2026")

    params = {
        "q": query,
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 5,
        "apiKey": api_key,
    }
    try:
        r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=5)
        data = r.json()
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
    except Exception:
        return []
