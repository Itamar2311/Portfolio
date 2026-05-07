import json
import os

PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portfolio.json')

DEFAULT_PORTFOLIO = [
    {"name": "Algonquin Power and Utilities", "sector": "Infrastructure", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Hydro One", "sector": "Infrastructure", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "TransAlta Corporation", "sector": "Infrastructure", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Gibson Energy", "sector": "Infrastructure", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Enbridge", "sector": "Infrastructure", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Bayshore Healthcare", "sector": "Healthcare Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Extendicare", "sector": "Healthcare Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Lifemark Health Group", "sector": "Healthcare Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "CBI Health", "sector": "Healthcare Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Manulife Financial", "sector": "Financial Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Rogers Communications", "sector": "Financial Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Fairfax Financial", "sector": "Financial Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Element Fleet Management", "sector": "Financial Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Propel Holdings", "sector": "Financial Services", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Chobani", "sector": "Special Situations", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Clearwater Seafoods", "sector": "Special Situations", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Yellow Pages", "sector": "Special Situations", "type": "Watchlist", "entry_date": "2025-01"},
    {"name": "Torstar Corporation", "sector": "Special Situations", "type": "Watchlist", "entry_date": "2025-01"},
]


def load_portfolio() -> list[dict]:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_PORTFOLIO.copy()


def save_portfolio(portfolio: list[dict]):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)


def add_company(portfolio: list[dict], name: str, sector: str, deal_type: str, entry_date: str) -> list[dict]:
    portfolio.append({
        "name": name,
        "sector": sector,
        "type": deal_type,
        "entry_date": entry_date,
    })
    save_portfolio(portfolio)
    return portfolio


def remove_company(portfolio: list[dict], name: str) -> list[dict]:
    portfolio = [c for c in portfolio if c["name"] != name]
    save_portfolio(portfolio)
    return portfolio
