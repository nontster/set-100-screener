import sys
import os

# Add project root to sys.path so 'src' module can be imported cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from typing import List, Dict, Any

from src.set100_tickers import SET100_TICKERS
from src.graph import run_single_stock_screening
from src.cache import Config

# Configure Streamlit page
st.set_page_config(
    page_title="SET100 AI Stock Screener & Anti-Fraud Suite",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern dark UI aesthetics
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    .badge-pass {
        background-color: #00C853;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-watchlist {
        background-color: #FFB300;
        color: black;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-reject {
        background-color: #FF1744;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_csv_mtime(csv_path: str = "SET100_AI_Screening_Report.csv") -> float:
    """Return modification timestamp of CSV file, or 0.0 if missing."""
    if os.path.exists(csv_path):
        return os.path.getmtime(csv_path)
    return 0.0


@st.cache_data(ttl=60)
def load_cached_reports(mtime: float) -> pd.DataFrame:
    """Load latest screening report from CSV if available, or initialize default mock data."""
    csv_path = "SET100_AI_Screening_Report.csv"
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path, encoding="utf-8-sig")
        except Exception:
            pass

    # Default initial dataframe
    default_data = [
        {
            "Ticker": "CPALL",
            "Recommendation": "PASS",
            "Total Score": 78.5,
            "Value Score": 80,
            "Fraud Risk": "LOW",
            "Sentiment Score": 45,
            "Executive Summary": "Solid retail business with consistent cash flows and low fraud risk.",
        },
        {
            "Ticker": "PTT",
            "Recommendation": "WATCHLIST",
            "Total Score": 64.0,
            "Value Score": 70,
            "Fraud Risk": "LOW",
            "Sentiment Score": -10,
            "Executive Summary": "Fairly valued energy giant; short-term sentiment headwinds.",
        },
        {
            "Ticker": "DELTA",
            "Recommendation": "WATCHLIST",
            "Total Score": 58.0,
            "Value Score": 45,
            "Fraud Risk": "MEDIUM",
            "Sentiment Score": 30,
            "Executive Summary": "High valuation multiplier with moderate accounting volatility.",
        },
        {
            "Ticker": "HIGH_RISK_MOCK",
            "Recommendation": "REJECT",
            "Total Score": 25.0,
            "Value Score": 85,
            "Fraud Risk": "HIGH",
            "Sentiment Score": -60,
            "Executive Summary": "REJECT override triggered: Severe operating cash flow divergence.",
        },
    ]
    return pd.DataFrame(default_data)


def main():
    st.title("📈 SET100 AI Stock Screener & Anti-Fraud Suite")
    st.caption("Parallel Multi-Agent Financial Quality, Accounting Audit, and News Sentiment Analysis")

    # Load data dynamically based on CSV modification timestamp
    mtime = get_csv_mtime()
    df = load_cached_reports(mtime)

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filter Options")

    # Clear cache action button
    if st.sidebar.button("🔄 Refresh Data", key="btn_clear_cache"):
        st.cache_data.clear()
        st.rerun()

    # Multi-select recommendation status
    recommendations = ["PASS", "WATCHLIST", "REJECT"]
    selected_recs = st.sidebar.multiselect(
        "Recommendation Status",
        options=recommendations,
        default=recommendations,
        key="ms_rec_filter",
    )

    # Multi-select stock category
    categories = ["DIVIDEND", "GROWTH", "HYBRID", "NEUTRAL", "REJECTED"]
    selected_categories = st.sidebar.multiselect(
        "Stock Category",
        options=categories,
        default=categories,
        key="ms_category_filter",
    )

    # Multi-select Mega Trends
    mega_trends_opts = [
        "AI & Data Center Infrastructure",
        "EV & Renewable Energy",
        "Healthcare & Aging Society",
        "Digital Commerce & Smart Logistics",
    ]
    selected_mega_trends = st.sidebar.multiselect(
        "World Mega Trends",
        options=mega_trends_opts,
        default=[],
        key="ms_megatrend_filter",
    )

    # Multi-select fraud risk levels
    fraud_risks = ["LOW", "MEDIUM", "HIGH"]
    selected_fraud = st.sidebar.multiselect(
        "Fraud Risk Level",
        options=fraud_risks,
        default=fraud_risks,
        key="ms_fraud_filter",
    )

    # Minimum score slider
    min_score = st.sidebar.slider(
        "Minimum Total Score",
        min_value=0,
        max_value=100,
        value=0,
        key="slider_min_score",
    )

    # Single stock manual screen section
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Run Single Stock Screen")
    manual_ticker = st.sidebar.selectbox("Select Ticker", options=SET100_TICKERS, key="sb_manual_ticker")
    if st.sidebar.button("Analyze Ticker", key="btn_run_single"):
        with st.spinner(f"Evaluating {manual_ticker} across multi-agent graph..."):
            res = run_single_stock_screening(manual_ticker)
            st.sidebar.success(f"Analysis Complete! Recommendation: {res['recommendation']}")
            classification = res.get("classification_report") or {}
            mega_trends_list = classification.get("mega_trends") or []
            # Append/update dataframe
            new_row = {
                "Ticker": res["ticker"],
                "Recommendation": res["recommendation"],
                "Total Score": res["total_score"],
                "Stock Category": classification.get("category", "NEUTRAL"),
                "Payout Safety": classification.get("payout_safety", "N/A"),
                "Mega Trend Tags": ", ".join(mega_trends_list) if mega_trends_list else "None",
                "Value Score": res["value_score"],
                "Fraud Risk": res["fraud_risk_level"],
                "Sentiment Score": res["sentiment_score"],
                "Executive Summary": res["executive_summary"],
                "Classification Rationale": classification.get("rationale", ""),
            }
            # Update df in session
            df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True).drop_duplicates(
                subset=["Ticker"], keep="first"
            )

    # Filter logic
    cat_col = "Stock Category" if "Stock Category" in df.columns else None
    mt_col = "Mega Trend Tags" if "Mega Trend Tags" in df.columns else None

    filter_mask = (
        (df["Recommendation"].isin(selected_recs))
        & (df["Fraud Risk"].isin(selected_fraud))
        & (df["Total Score"] >= min_score)
    )

    if cat_col and selected_categories:
        filter_mask = filter_mask & (df[cat_col].isin(selected_categories))

    if mt_col and selected_mega_trends:
        mt_mask = df[mt_col].astype(str).apply(
            lambda val: any(trend in val for trend in selected_mega_trends)
        )
        filter_mask = filter_mask & mt_mask

    filtered_df = df[filter_mask]

    # --- TOP SUMMARY ROW ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Scanned", len(df))
    with col2:
        pass_count = len(df[df["Recommendation"] == "PASS"])
        st.metric("PASS (Top Pick)", pass_count)
    with col3:
        watchlist_count = len(df[df["Recommendation"] == "WATCHLIST"])
        st.metric("WATCHLIST", watchlist_count)
    with col4:
        reject_count = len(df[df["Recommendation"] == "REJECT"])
        st.metric("REJECT (High Risk)", reject_count)

    st.markdown("---")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(
        ["📊 Interactive Screening Table", "📉 Visual Analytics", "🔎 Stock Deep-Dive"]
    )

    # --- TAB 1: SCREENING TABLE ---
    with tab1:
        st.subheader("SET100 Stock Screening Results")
        if filtered_df.empty:
            st.info("No stocks match the selected filter criteria.")
        else:
            st.dataframe(
                filtered_df,
                column_config={
                    "Total Score": st.column_config.ProgressColumn(
                        "Total Score",
                        help="Calculated score (0-100)",
                        format="%.1f",
                        min_value=0,
                        max_value=100,
                    ),
                    "Value Score": st.column_config.ProgressColumn(
                        "Value Score",
                        help="Value score (0-100)",
                        format="%d",
                        min_value=0,
                        max_value=100,
                    ),
                },
                width="stretch",
                height=400,
            )

    # --- TAB 2: VISUAL ANALYTICS ---
    with tab2:
        st.subheader("Distribution & Risk Analytics")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("##### Recommendation Distribution")
            if not df.empty:
                pie_fig = px.pie(
                    df,
                    names="Recommendation",
                    color="Recommendation",
                    color_discrete_map={
                        "PASS": "#00C853",
                        "WATCHLIST": "#FFB300",
                        "REJECT": "#FF1744",
                    },
                    hole=0.4,
                )
                st.plotly_chart(pie_fig, width="stretch")

        with c2:
            st.markdown("##### Value Score vs Total Score (by Fraud Risk)")
            if not df.empty:
                scatter_fig = px.scatter(
                    df,
                    x="Value Score",
                    y="Total Score",
                    color="Fraud Risk",
                    hover_name="Ticker",
                    color_discrete_map={
                        "LOW": "#00C853",
                        "MEDIUM": "#FFB300",
                        "HIGH": "#FF1744",
                    },
                    size_max=15,
                )
                st.plotly_chart(scatter_fig, width="stretch")

    # --- TAB 3: STOCK DEEP-DIVE ---
    with tab3:
        st.subheader("Stock Deep-Dive Analysis")
        selected_ticker = st.selectbox(
            "Select Ticker for Detailed Inspection",
            options=df["Ticker"].unique() if not df.empty else ["CPALL"],
            key="sb_deepdive_ticker",
        )

        stock_info = df[df["Ticker"] == selected_ticker]
        if not stock_info.empty:
            row = stock_info.iloc[0]
            st.markdown(f"### {row['Ticker']} — Recommendation: **{row['Recommendation']}**")

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Score", f"{row['Total Score']:.1f}/100")
            k2.metric("Value Score", f"{row['Value Score']}/100")
            k3.metric("Fraud Risk Level", row["Fraud Risk"])
            k4.metric("Sentiment Score", row["Sentiment Score"])

            st.markdown("#### AI Executive Summary")
            st.info(row["Executive Summary"])

            # --- CLASSIFICATION BREAKDOWN CARD (T010) ---
            with st.expander("🏷️ Stock Classification & Mega Trend Breakdown", expanded=True):
                c_cat = row.get("Stock Category", "NEUTRAL")
                c_payout = row.get("Payout Safety", "N/A")
                c_trends = row.get("Mega Trend Tags", "None")
                c_rationale = row.get("Classification Rationale", "N/A")

                st.markdown(f"**Stock Category**: `{c_cat}` | **Payout Safety**: `{c_payout}`")
                st.markdown(f"**World Mega Trend Exposure**: `{c_trends}`")

                if c_rationale and c_rationale != "N/A":
                    st.success(f"**Classification Rationale**: {c_rationale}")

        # Live 1-Year Candlestick Chart via yfinance
        st.markdown(f"#### 1-Year Price History ({selected_ticker}.BK)")
        with st.spinner("Fetching 1-year candlestick price data..."):
            try:
                stock_data = yf.Ticker(f"{selected_ticker}.BK").history(period="1y")
                if not stock_data.empty:
                    candle_fig = go.Figure(
                        data=[
                            go.Candlestick(
                                x=stock_data.index,
                                open=stock_data["Open"],
                                high=stock_data["High"],
                                low=stock_data["Low"],
                                close=stock_data["Close"],
                                name=selected_ticker,
                            )
                        ]
                    )
                    candle_fig.update_layout(
                        title=f"{selected_ticker}.BK 1-Year Candlestick Chart",
                        yaxis_title="Price (THB)",
                        template="plotly_dark",
                        xaxis_rangeslider_visible=False,
                    )
                    st.plotly_chart(candle_fig, width="stretch")
                else:
                    st.warning("Historical price data unavailable for this ticker.")
            except Exception as e:
                st.error(f"Failed to load price chart: {e}")


if __name__ == "__main__":
    main()
