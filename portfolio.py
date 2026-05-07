import json
import os

PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portfolio.json')

DEFAULT_PORTFOLIO = [
    {"name": "Northgate Healthcare Services", "sector": "Healthcare Services", "type": "Acquisition", "entry_date": "2024-03"},
    {"name": "PulseGrid Infrastructure", "sector": "Infrastructure", "type": "Growth Equity", "entry_date": "2024-09"},
    {"name": "Maple Financial Group", "sector": "Financial Services", "type": "Acquisition Financing", "entry_date": "2023-11"},
    {"name": "Ridgeline Utilities", "sector": "Infrastructure", "type": "Growth Capital", "entry_date": "2024-01"},
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
