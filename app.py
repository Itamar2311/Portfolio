import streamlit as st
from datetime import datetime
from portfolio import load_portfolio, save_portfolio, add_company, remove_company
from news_fetcher import fetch_company_news, fetch_sector_trends
from ai_analyzer import analyze_company
from report_generator import generate_report

st.set_page_config(page_title="GFAM Portfolio Monitor", page_icon="📡", layout="wide")

st.title("📡 GFAM Market Watchlist")
st.caption("AI-powered company monitoring across GFAM's target sectors")
st.divider()

# ── Load portfolio ────────────────────────────────────────────
if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_portfolio()

portfolio = st.session_state.portfolio

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Watchlist")

    for company in portfolio:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{company['name']}**")
        col1.caption(f"{company['sector']} · {company.get('entry_date','')}")
        if col2.button("✕", key=f"remove_{company['name']}"):
            st.session_state.portfolio = remove_company(portfolio, company['name'])
            st.rerun()

    st.divider()
    st.subheader("➕ Add Company")
    new_name = st.text_input("Company name")
    new_sector = st.selectbox("Sector", ["Infrastructure", "Healthcare Services", "Financial Services", "Special Situations"])
    new_type = st.selectbox("Deal type", ["Acquisition", "Growth Equity", "Acquisition Financing", "Growth Capital", "Special Situations"])
    new_date = st.text_input("Entry date (YYYY-MM)", value=datetime.now().strftime("%Y-%m"))

    if st.button("Add to Portfolio", use_container_width=True):
        if new_name:
            st.session_state.portfolio = add_company(portfolio, new_name, new_sector, new_type, new_date)
            st.success(f"Added {new_name}")
            st.rerun()

    st.divider()
    days_back = st.slider("Lookback period (days)", 7, 90, 30)
    run = st.button("🔄 Run Watchlist Update", use_container_width=True)

REC_COLORS = {
    "Monitor": "success",
    "Follow Up": "warning",
    "Urgent Review": "error",
}

SENTIMENT_ICONS = {
    "Positive": "🟢",
    "Neutral": "🟡",
    "Negative": "🔴",
}

if run:
    if not portfolio:
        st.warning("No companies in portfolio. Add some in the sidebar.")
        st.stop()

    portfolio_results = []
    progress = st.progress(0)
    status = st.empty()

    for i, company in enumerate(portfolio):
        status.write(f"Analyzing {company['name']}...")

        with st.spinner(f"Fetching news for {company['name']}..."):
            articles = fetch_company_news(company['name'], days_back)
            sector_trends = fetch_sector_trends(company['sector'], days_back)

        with st.spinner(f"Running AI analysis for {company['name']}..."):
            analysis = analyze_company(company, articles, sector_trends)

        portfolio_results.append({
            "company": company,
            "articles": articles,
            "sector_trends": sector_trends,
            "analysis": analysis,
        })

        progress.progress((i + 1) / len(portfolio))

    status.empty()
    progress.empty()
    st.success(f"Watchlist update complete — {len(portfolio)} companies analyzed")
    st.divider()

    # ── Summary metrics ───────────────────────────────────────
    urgent = sum(1 for r in portfolio_results if r["analysis"].get("recommendation") == "Urgent Review")
    follow_up = sum(1 for r in portfolio_results if r["analysis"].get("recommendation") == "Follow Up")
    positive = sum(1 for r in portfolio_results if r["analysis"].get("sentiment") == "Positive")
    avg_score = sum(r["analysis"].get("sentiment_score", 5) for r in portfolio_results) / len(portfolio_results)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Companies monitored", len(portfolio_results))
    col2.metric("Avg sentiment", f"{avg_score:.1f}/10")
    col3.metric("Follow up needed", follow_up)
    col4.metric("Urgent reviews", urgent, delta=None if urgent == 0 else f"{urgent} flagged")

    # ── Download report ───────────────────────────────────────
    try:
        report_bytes = generate_report(portfolio_results)
        st.download_button(
            label="📄 Download Watchlist Report (.docx)",
            data=report_bytes,
            file_name=f"GFAM_Portfolio_Update_{datetime.now().strftime('%Y-%m')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Report generation failed: {e}")

    st.divider()

    # ── Per company cards ─────────────────────────────────────
    st.subheader("Company Updates")

    for pr in portfolio_results:
        company = pr["company"]
        analysis = pr["analysis"]
        articles = pr["articles"]
        sector_trends = pr["sector_trends"]

        rec = analysis.get("recommendation", "Monitor")
        sentiment = analysis.get("sentiment", "Neutral")
        score = analysis.get("sentiment_score", 5)
        icon = SENTIMENT_ICONS.get(sentiment, "🟡")

        with st.expander(f"{icon} **{company['name']}** — {rec}  |  {sentiment} ({score}/10)"):
            left, right = st.columns([3, 2])

            with left:
                st.markdown("**News Summary**")
                st.write(analysis.get("news_summary", "No summary available."))

                st.markdown("**Sector Trends**")
                st.write(analysis.get("sector_summary", "No sector data available."))

                material = analysis.get("material_events", [])
                if material:
                    st.markdown("**⚡ Material Events**")
                    for event in material:
                        st.warning(event)

            with right:
                getattr(st, REC_COLORS.get(rec, "info"))(f"**{rec}** — {analysis.get('recommendation_reason','')}")

                risks = analysis.get("risks_flagged", [])
                if risks:
                    st.markdown("**🔴 Risks**")
                    for r in risks:
                        st.write(f"• {r}")

                opps = analysis.get("opportunities_flagged", [])
                if opps:
                    st.markdown("**🟢 Opportunities**")
                    for o in opps:
                        st.write(f"• {o}")

                if articles:
                    st.markdown("**Recent Articles**")
                    for a in articles[:3]:
                        st.markdown(f"[{a['title'][:60]}...]({a['url']}) — *{a['published_at']}*")

else:
    st.info("👈 Add companies to your watchlist in the sidebar and click **Run Update**.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📰 News Monitoring**")
        st.write("Real-time news for each portfolio company flagging material events")
    with col2:
        st.markdown("**📊 Sector Trends**")
        st.write("Broader market context and sector-level developments")
    with col3:
        st.markdown("**📄 Monthly Memo**")
        st.write("One-click report ready to send to partners and LPs")
