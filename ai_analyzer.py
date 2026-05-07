import json
import re
import streamlit as st
from groq import Groq


def clean(text):
    if not text:
        return ""
    return text.encode('ascii', 'ignore').decode('ascii')


def analyze_company(company: dict, articles: list[dict], sector_trends: list[dict], stock_data: dict = {}) -> dict:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    company_name = clean(company["name"])
    sector = clean(company["sector"])

    news_text = "\n".join([
        f"- [{clean(a['published_at'])}] {clean(a['title'])}: {clean(a['description'])}"
        for a in articles
    ]) if articles else "No direct company news found — base analysis on sector trends and stock data."

    trends_text = "\n".join([
        f"- {clean(a['title'])}: {clean(a['description'])}"
        for a in sector_trends
    ]) if sector_trends else "No sector trends found."

    stock_text = ""
    if stock_data:
        stock_text = f"""
Stock data ({stock_data.get('ticker', '')}):
- Current price: {stock_data.get('current_price', 'N/A')}
- 30-day price change: {stock_data.get('change_30d_pct', 'N/A')}%
- Trend: {stock_data.get('trend', 'N/A')}
"""

    prompt = f"""You are a portfolio analyst at Genesis Financial Asset Management (GFAM).

You are monitoring: {company_name} ({sector})
Deal type: {clean(company.get('type', 'Watchlist'))}

{stock_text}

Recent news:
{news_text}

Sector trends ({sector}):
{trends_text}

CRITICAL INSTRUCTIONS:
- You MUST give a definitive sentiment — Positive or Negative. NEVER Neutral unless you have absolutely zero data.
- You MUST give a sentiment_score between 1-4 (Negative) or 7-10 (Positive). Never 5 or 6.
- If stock is down >5% = Negative. If up >5% = Positive.
- If there is M&A news = flag as material event, score 8+.
- If there is earnings news = flag and score accordingly.
- If there is leadership change = flag as material event.
- If no direct company news, use sector trends to form a view — do not default to neutral.
- recommendation must be "Follow Up" or "Urgent Review" if anything material was found. Only use "Monitor" if truly nothing noteworthy.

Respond ONLY with this JSON:
{{
  "sentiment": "Positive or Negative",
  "sentiment_score": <integer 1-4 or 7-10, never 5 or 6>,
  "material_events": ["Brief description of material event if found, else empty array"],
  "news_summary": "2-3 sentences summarizing key developments. If no direct news, summarize sector context and what it means for this company specifically.",
  "sector_summary": "2 sentences on sector trends and direct impact on this company.",
  "risks_flagged": ["Specific risk identified"],
  "opportunities_flagged": ["Specific opportunity identified"],
  "recommendation": "Monitor, Follow Up, or Urgent Review",
  "recommendation_reason": "1-2 sentences — be specific about what drove this recommendation."
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    start = raw.find('{')
    end = raw.rfind('}') + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    raw = re.sub(r'[\x00-\x1f\x7f]', ' ', raw)

    try:
        result = json.loads(raw)
        # Force non-neutral score
        score = result.get("sentiment_score", 5)
        if score in [5, 6]:
            result["sentiment_score"] = 4 if result.get("sentiment") == "Negative" else 7
        return result
    except Exception:
        return {
            "sentiment": "Negative",
            "sentiment_score": 4,
            "material_events": [],
            "news_summary": "Unable to retrieve data for this company.",
            "sector_summary": "",
            "risks_flagged": ["Data retrieval failed"],
            "opportunities_flagged": [],
            "recommendation": "Follow Up",
            "recommendation_reason": "Manual review needed — automated data unavailable.",
        }
