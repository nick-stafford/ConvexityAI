"""
Stock detail component - comprehensive single stock view
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

from .charts import (
    create_price_chart, create_performance_bars,
    create_volume_comparison
)
from ..services.data_fetcher import data_fetcher
from ..services.ai_research import ai_researcher
from ..services.ai_memory import ai_memory
from ..services.image_gen import image_generator
from ..utils.database import (
    get_stock_metrics, get_user_notes, add_user_note,
    add_to_watchlist, remove_from_watchlist, get_watchlist
)


def render_stock_header(symbol: str, info: Dict, metrics: Dict):
    """Render the stock header with key info."""
    name = info.get('name', symbol) if info else symbol
    price = metrics.get('current_price', 0) if metrics else 0
    change_1d = metrics.get('price_change_1d', 0) if metrics else 0

    # Price color
    color = "#26a69a" if change_1d >= 0 else "#ef5350"
    arrow = "▲" if change_1d >= 0 else "▼"

    # Tier badge
    tier = metrics.get('tier') if metrics else None
    tier_badge = ""
    if tier == 1:
        tier_badge = '<span style="background: #26a69a; padding: 2px 8px; border-radius: 12px; margin-left: 10px;">Tier 1</span>'
    elif tier == 2:
        tier_badge = '<span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 12px; margin-left: 10px;">Tier 2</span>'

    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h1 style="margin-bottom: 5px;">
                {symbol} {tier_badge}
            </h1>
            <p style="color: #888; margin-bottom: 10px;">{name}</p>
            <div style="display: flex; align-items: baseline; gap: 15px;">
                <span style="font-size: 32px; font-weight: bold;">${price:.2f}</span>
                <span style="color: {color}; font-size: 18px;">
                    {arrow} {abs(change_1d):.2f}%
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_key_metrics(metrics: Dict):
    """Render key metrics in a grid."""
    if not metrics:
        st.warning("No metrics available")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("52-Week Low", f"${metrics.get('fifty_two_week_low', 0):.2f}")
        st.metric("From Low", f"{metrics.get('pct_from_52wk_low', 0):.1f}%")

    with col2:
        st.metric("52-Week High", f"${metrics.get('fifty_two_week_high', 0):.2f}")
        st.metric("From High", f"{metrics.get('pct_from_52wk_high', 0):.1f}%")

    with col3:
        st.metric("50-Day MA", f"${metrics.get('fifty_day_avg', 0):.2f}")
        st.metric("Above 50 DMA", f"{metrics.get('pct_above_50dma', 0):.1f}%")

    with col4:
        st.metric("200-Day MA", f"${metrics.get('two_hundred_day_avg', 0):.2f}")
        st.metric("Above 200 DMA", f"{metrics.get('pct_above_200dma', 0):.1f}%")


def render_volume_metrics(metrics: Dict):
    """Render volume-related metrics."""
    if not metrics:
        return

    col1, col2 = st.columns(2)

    with col1:
        volume = metrics.get('volume', 0)
        avg_volume = metrics.get('avg_volume', 0)

        st.markdown("**Volume Analysis**")
        st.markdown(f"Current Volume: **{volume:,}**")
        st.markdown(f"Average Volume: **{avg_volume:,}**")
        st.markdown(f"Volume Ratio: **{metrics.get('volume_ratio', 0):.2f}x**")

    with col2:
        fig = create_volume_comparison(
            metrics.get('volume', 0),
            metrics.get('avg_volume', 1)
        )
        st.plotly_chart(fig, use_container_width=True)


def render_price_chart_section(symbol: str, metrics: Dict):
    """Render the price chart with controls."""
    st.markdown("### Price Chart")

    # Controls
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        period = st.selectbox(
            "Period",
            options=["1M", "3M", "6M", "1Y", "5Y"],
            index=2,
            key=f"period_{symbol}"
        )
    with col2:
        show_volume = st.checkbox("Show Volume", value=True, key=f"vol_{symbol}")

    # Get historical data - fetch 5 years to support all periods
    years = 5
    history = data_fetcher.get_historical_data(symbol, years=years)

    if history is None or history.empty:
        st.warning("No historical data available")
        return

    # Filter by period
    period_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825}
    history = history.tail(period_days.get(period, 180))

    # Create chart
    fig = create_price_chart(
        history,
        metrics=metrics,
        show_ma=True,
        show_volume=show_volume
    )
    st.plotly_chart(fig, use_container_width=True)


def render_performance_section(metrics: Dict):
    """Render performance metrics."""
    st.markdown("### Performance")

    col1, col2 = st.columns(2)

    with col1:
        fig = create_performance_bars(metrics)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**30-Day Consolidation**")
        range_30d = metrics.get('consolidation_range_30d', 0)

        # Determine consolidation quality
        if range_30d < 15:
            quality = "Tight (Good)"
            color = "#26a69a"
        elif range_30d < 25:
            quality = "Moderate"
            color = "#ffc107"
        else:
            quality = "Wide (Volatile)"
            color = "#ef5350"

        st.markdown(f"Range: **{range_30d:.1f}%**")
        st.markdown(f"<span style='color: {color};'>{quality}</span>", unsafe_allow_html=True)

        st.markdown("**Days Since 52-Week Low**")
        days = metrics.get('days_since_52wk_low', 0)
        st.markdown(f"**{days}** days")


def render_ai_research_section(symbol: str, metrics: Dict):
    """Render AI-powered research section with memory and image generation."""
    st.markdown("### 🤖 AI Research")

    # Show previous research from memory
    memories = ai_memory.recall_stock_memories(symbol, limit=3)
    if memories:
        with st.expander(f"📚 Previous Research ({len(memories)} insights)", expanded=False):
            for mem in memories:
                st.markdown(f"""
                <div class="stock-card">
                    <strong>{mem['memory_type'].upper()}</strong> - {mem['created_at'][:10]}<br>
                    <small>{mem['content'][:200]}...</small>
                </div>
                """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Signal Analysis", "News Sentiment", "Trade Thesis", "🎨 Visuals"])

    with tab1:
        if st.button("Generate Company Overview", key=f"overview_{symbol}"):
            with st.spinner("Analyzing company (with memory context)..."):
                overview = ai_researcher.get_company_overview(symbol)
                st.markdown(overview)
                st.success("✅ Saved to AI memory for future reference")

    with tab2:
        if st.button("Analyze Signal Quality", key=f"signal_{symbol}"):
            with st.spinner("Analyzing signal..."):
                analysis = ai_researcher.analyze_momentum_signal(metrics)
                st.markdown(analysis)
                # Save to memory
                ai_memory.remember_stock_insight(symbol, "signal_analysis", analysis[:300], 0.7, "AI Analysis")

    with tab3:
        if st.button("Analyze News Sentiment", key=f"news_{symbol}"):
            with st.spinner("Analyzing news..."):
                sentiment = ai_researcher.analyze_news_sentiment(symbol)
                st.markdown(sentiment)
                ai_memory.remember_stock_insight(symbol, "sentiment", sentiment[:300], 0.6, "News Analysis")

    with tab4:
        if st.button("Generate Trade Thesis", key=f"thesis_{symbol}"):
            with st.spinner("Generating thesis..."):
                thesis = ai_researcher.generate_trade_thesis(symbol, metrics)
                st.markdown(thesis)
                ai_memory.remember_stock_insight(symbol, "trade_thesis", thesis[:400], 0.8, "AI Thesis")

    with tab5:
        st.markdown("**AI-Generated Visuals** (requires Gemini API key)")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🖼️ Generate Infographic", key=f"infographic_{symbol}"):
                with st.spinner("Creating infographic..."):
                    image_path = image_generator.generate_stock_infographic(symbol, metrics)
                    if image_path and Path(image_path).exists():
                        st.image(image_path, caption=f"{symbol} Infographic")
                        st.success(f"Saved to {image_path}")
                    else:
                        st.warning("Image generation requires GEMINI_API_KEY in .env")

        with col2:
            if st.button("🚨 Generate Alert Banner", key=f"banner_{symbol}"):
                tier = metrics.get('tier', 0)
                if tier:
                    with st.spinner("Creating alert banner..."):
                        image_path = image_generator.generate_alert_banner(symbol, tier, metrics)
                        if image_path and Path(image_path).exists():
                            st.image(image_path, caption=f"Tier {tier} Alert")
                        else:
                            st.warning("Image generation requires GEMINI_API_KEY in .env")
                else:
                    st.info("No active alert tier for this stock")


def render_insider_section(symbol: str):
    """Render insider trading activity."""
    st.markdown("### 👔 Insider Activity")

    insider_trades = data_fetcher.get_insider_trades(symbol)

    if insider_trades is None or insider_trades.empty:
        st.info("No insider trading data available for this stock.")
        return

    # Show recent transactions
    st.dataframe(
        insider_trades.head(10),
        use_container_width=True,
        hide_index=True
    )

    # Highlight buys
    if 'Transaction' in insider_trades.columns:
        buys = insider_trades[insider_trades['Transaction'].str.contains('Purchase|Buy', case=False, na=False)]
        sells = insider_trades[insider_trades['Transaction'].str.contains('Sale|Sell', case=False, na=False)]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Recent Buys", len(buys))
        with col2:
            st.metric("Recent Sells", len(sells))

        if len(buys) > len(sells):
            st.success("📈 More insider buying than selling - bullish signal")
        elif len(sells) > len(buys):
            st.warning("📉 More insider selling than buying")


def render_user_notes_section(symbol: str):
    """Render user notes and watchlist section."""
    st.markdown("### 📝 Notes & Watchlist")

    col1, col2 = st.columns(2)

    with col1:
        # Check if on watchlist
        watchlist = get_watchlist()
        on_watchlist = symbol in watchlist['symbol'].values if not watchlist.empty else False

        if on_watchlist:
            if st.button("❌ Remove from Watchlist", key=f"remove_wl_{symbol}"):
                remove_from_watchlist(symbol)
                st.success(f"Removed {symbol} from watchlist")
                st.rerun()
        else:
            if st.button("⭐ Add to Watchlist", key=f"add_wl_{symbol}"):
                add_to_watchlist(symbol)
                st.success(f"Added {symbol} to watchlist")
                st.rerun()

    with col2:
        # Quick note
        note = st.text_input("Add a note:", key=f"note_input_{symbol}")
        if st.button("Save Note", key=f"save_note_{symbol}"):
            if note:
                add_user_note(symbol, note)
                st.success("Note saved!")
                st.rerun()

    # Display existing notes
    notes = get_user_notes(symbol)
    if notes:
        st.markdown("**Previous Notes:**")
        for n in notes[:5]:
            st.markdown(f"- {n['note']} *(saved at {n['created_at']})*")


def render_stock_detail(symbol: str):
    """
    Main function to render the complete stock detail page.

    Args:
        symbol: Stock ticker symbol
    """
    # Fetch data
    info = data_fetcher.get_stock_info(symbol)
    metrics = get_stock_metrics(symbol)

    if not metrics:
        # Try to calculate fresh metrics
        with st.spinner(f"Fetching data for {symbol}..."):
            metrics = data_fetcher.calculate_metrics(symbol)

    if not metrics:
        st.error(f"Could not load data for {symbol}")
        return

    # Header
    render_stock_header(symbol, info, metrics)

    # Quick actions
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh Data", key=f"refresh_{symbol}"):
            with st.spinner("Refreshing..."):
                metrics = data_fetcher.calculate_metrics(symbol)
                st.rerun()

    st.divider()

    # Key Metrics
    render_key_metrics(metrics)

    st.divider()

    # Price Chart
    render_price_chart_section(symbol, metrics)

    st.divider()

    # Two column layout for performance and volume
    col1, col2 = st.columns(2)
    with col1:
        render_performance_section(metrics)
    with col2:
        render_volume_metrics(metrics)

    st.divider()

    # AI Research
    render_ai_research_section(symbol, metrics)

    st.divider()

    # Insider Activity
    render_insider_section(symbol)

    st.divider()

    # User Notes
    render_user_notes_section(symbol)
