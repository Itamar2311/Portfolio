import json
import re
import streamlit as st
from groq import Groq


def clean(text):
    if not text:
        return ""
    return text.encode('ascii', 'ignore').decode('ascii')


def analyze_company(company: dict, articles: list[dict], sector_trends: list[dict]) -> dict:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    company_name = clean(company["name"])
    sector = clean(company["sector"])

    news_text = "\n".join([
        f"- {clean(a['title'])} ({clean(a['published_at'])}): {clean(a['description'])}"
        for a in articles
    ]) or "No recent news found."

    trends_text = "\n".join([
        f"- {clean(a['title'])}: {clean(a['description'])}"
        for a in sector_trends
    ]) or "No sector trends found."

    prompt = f"""You are a portfolio monitoring analyst at Genesis Financial Asset Management (GFAM).

You are reviewing updates for one of GFAM's portfolio companies.

Company: {company_name}
Sector: {sector}
Deal Type: {clean(company.get('type', ''))}
Entry Date: {clean(company.get('entry_date', ''))}

Recent news about this company:
{news_text}

Recent sector trends ({sector}):
{trends_text}

Analyze the above and respond ONLY with this JSON:

{{
  "sentiment": "Positive, Neutral, or Negative",
  "sentiment_score": <integer 1-10 where 10 is very positive>,
  "material_events": ["Brief description of any material event e.g. leadership change, new contract, legal issue"],
  "news_summary": "2-3 sentences summarizing the key developments for this company over the past 30 days",
  "sector_summary": "2 sentences summarizing the key sector trends and how they affect this company",
  "risks_flagged": ["Any new risk identified from the news"],
  "opportunities_flagged": ["Any new opportunity identified from the news"],
  "recommendation": "Monitor, Follow Up, or Urgent Review",
  "recommendation_reason": "1-2 sentences explaining the recommendation"
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
    except Exception:
        result = {
            "sentiment": "Neutral",
            "sentiment_score": 5,
            "material_events": [],
            "news_summary": "Could not parse AI response.",
            "sector_summary": "",
            "risks_flagged": [],
            "opportunities_flagged": [],
            "recommendation": "Monitor",
            "recommendation_reason": "Unable to analyze at this time.",
        }

    return result
