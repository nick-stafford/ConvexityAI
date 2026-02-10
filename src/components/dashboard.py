"""
Main dashboard component
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Callable

from .charts import create_alert_distribution, create_sector_heatmap
from .alerts_table import render_alerts_table, render_alert_summary, render_top_movers
from .spline_3d import render_3d_header, render_spline_scene, DEMO_SCENES
from .advanced_visuals import render_wave_divider, render_animated_counter
from ..utils.database import (
    get_tier_alerts, get_top_performers, get_all_metrics,
    get_all_stocks, get_watchlist, get_flat_stocks_breaking_out,
    get_consolidating_stocks
)
from ..services.scanner import scanner


def render_scan_controls():
    """Render scanner controls."""
    st.markdown("### 🔍 Scanner Controls")

    col1, col2, col3 = st.columns([2, 2, 4])

    with col1:
        if st.button("🚀 Run Full Scan", type="primary", use_container_width=True):
            return "full_scan"

    with col2:
        if st.button("📊 Quick Refresh", use_container_width=True):
            return "refresh"

    return None


def render_scan_progress(progress_placeholder, current, total, symbol):
    """Update scan progress display."""
    progress = current / total
    progress_placeholder.progress(progress, text=f"Scanning {symbol} ({current}/{total})")


def run_scanner_with_progress():
    """Run the scanner with an animated progress indicator."""
    # Create placeholder for animated status
    header_placeholder = st.empty()
    progress_placeholder = st.empty()
    stats_placeholder = st.empty()

    tier1_count = 0
    tier2_count = 0

    def progress_callback(current, total, symbol):
        nonlocal tier1_count, tier2_count
        progress = current / total

        # Animated header
        header_placeholder.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2 style="margin: 0;">
                    <span class="scanning-indicator">🔍</span> Scanning Stocks...
                </h2>
                <p style="color: #888;">Analyzing {symbol}</p>
            </div>
        """, unsafe_allow_html=True)

        progress_placeholder.progress(progress, text=f"{current} of {total} stocks ({progress*100:.0f}%)")

        # Live stats
        stats_placeholder.markdown(f"""
            <div style="display: flex; justify-content: center; gap: 40px; padding: 10px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; color: #26a69a;">🟢 {tier1_count}</div>
                    <div style="color: #888;">Tier 1</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; color: #ffc107;">🟡 {tier2_count}</div>
                    <div style="color: #888;">Tier 2</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    header_placeholder.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h2><span class="scanning-indicator">⏳</span> Initializing Scanner...</h2>
        </div>
    """, unsafe_allow_html=True)

    scanner.load_stock_universe()

    tier1, tier2 = scanner.run_full_scan(progress_callback=progress_callback)

    # Clear progress indicators
    header_placeholder.empty()
    progress_placeholder.empty()
    stats_placeholder.empty()

    # Show completion message with animation
    st.balloons()
    st.success(f"✅ Scan complete! Found **{len(tier1)} Tier 1** and **{len(tier2)} Tier 2** alerts.")

    return tier1, tier2


def render_dashboard_summary():
    """Render the dashboard summary section."""
    # Get counts
    tier1 = get_tier_alerts(1)
    tier2 = get_tier_alerts(2)
    all_stocks = get_all_stocks()

    tier1_count = len(tier1) if not tier1.empty else 0
    tier2_count = len(tier2) if not tier2.empty else 0
    total_stocks = len(all_stocks) if not all_stocks.empty else 0

    # Render summary cards
    render_alert_summary(tier1_count, tier2_count, total_stocks)

    return tier1, tier2


def render_quick_stats():
    """Render quick statistics."""
    col1, col2, col3, col4 = st.columns(4)

    top_1d = get_top_performers(days=1, limit=1)
    top_7d = get_top_performers(days=7, limit=1)
    metrics = get_all_metrics()

    with col1:
        if not top_1d.empty:
            best_1d = top_1d.iloc[0]
            st.metric(
                "📈 Top Mover (1D)",
                best_1d['symbol'],
                f"{best_1d['price_change_1d']:.1f}%"
            )
        else:
            st.metric("📈 Top Mover (1D)", "N/A")

    with col2:
        if not top_7d.empty:
            best_7d = top_7d.iloc[0]
            st.metric(
                "🔥 Top Mover (7D)",
                best_7d['symbol'],
                f"{best_7d['price_change_7d']:.1f}%"
            )
        else:
            st.metric("🔥 Top Mover (7D)", "N/A")

    with col3:
        if not metrics.empty:
            avg_change = metrics['price_change_1d'].mean()
            st.metric(
                "📊 Avg Change (1D)",
                f"{avg_change:.2f}%"
            )
        else:
            st.metric("📊 Avg Change (1D)", "N/A")

    with col4:
        watchlist = get_watchlist()
        st.metric(
            "👁️ Watchlist",
            len(watchlist) if not watchlist.empty else 0
        )


def render_alerts_section(on_stock_select: Callable = None):
    """Render the alerts section with Tier 1 and Tier 2 tables."""
    tier1 = get_tier_alerts(1)
    tier2 = get_tier_alerts(2)

    tab1, tab2 = st.tabs(["🟢 Tier 1 - Strong Signals", "🟡 Tier 2 - Watch List"])

    with tab1:
        render_alerts_table(tier1, tier=1, on_select=on_stock_select, key_prefix="dash")

    with tab2:
        render_alerts_table(tier2, tier=2, on_select=on_stock_select, key_prefix="dash")


def render_movers_section(on_stock_select=None):
    """Render top movers in multiple timeframes."""
    st.markdown("### 📊 Top Performers")

    col1, col2, col3 = st.columns(3)

    with col1:
        top_1d = get_top_performers(days=1, limit=40)
        render_top_movers(top_1d, "Last 24 Hours", "price_change_1d", on_select=on_stock_select)

    with col2:
        top_7d = get_top_performers(days=7, limit=40)
        render_top_movers(top_7d, "Last 7 Days", "price_change_7d", on_select=on_stock_select)

    with col3:
        top_30d = get_top_performers(days=30, limit=40)
        render_top_movers(top_30d, "Last 30 Days", "price_change_30d", on_select=on_stock_select)


def render_flat_stocks_section(on_stock_select=None):
    """Render flat stocks that are starting to break out."""
    st.markdown("### 📊 Flat Stocks Breaking Out")
    st.caption("Stocks that were flat/down but showing recent upward momentum")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🚀 Breaking Out** (recent momentum)")
        breaking_out = get_flat_stocks_breaking_out(limit=40)

        if breaking_out.empty:
            st.info("No breakout candidates found. Run a scan first.")
        else:
            with st.container(height=400):
                for idx, row in breaking_out.iterrows():
                    symbol = row.get('symbol', 'N/A')
                    price = row.get('current_price', 0)
                    from_low = row.get('pct_from_52wk_low', 0)
                    change_7d = row.get('price_change_7d', 0)
                    change_30d = row.get('price_change_30d', 0)

                    c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1.5, 1])

                    with c1:
                        st.markdown(f"**{symbol}**")
                    with c2:
                        st.markdown(f"${price:.2f}")
                    with c3:
                        color = "#26a69a" if change_7d >= 0 else "#ef5350"
                        st.markdown(f"<span style='color:{color}'>7d: {change_7d:.1f}%</span>", unsafe_allow_html=True)
                    with c4:
                        color = "#26a69a" if change_30d >= 0 else "#ef5350"
                        st.markdown(f"<span style='color:{color}'>30d: {change_30d:.1f}%</span>", unsafe_allow_html=True)
                    with c5:
                        if on_stock_select and st.button("→", key=f"flat_break_{symbol}_{idx}"):
                            on_stock_select(symbol)

    with col2:
        st.markdown("**⏳ Tight Consolidation** (potential breakouts)")
        consolidating = get_consolidating_stocks(limit=40)

        if consolidating.empty:
            st.info("No consolidating stocks found. Run a scan first.")
        else:
            with st.container(height=400):
                for idx, row in consolidating.iterrows():
                    symbol = row.get('symbol', 'N/A')
                    price = row.get('current_price', 0)
                    from_low = row.get('pct_from_52wk_low', 0)
                    range_30d = row.get('consolidation_range_30d', 0)

                    c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1.5, 1])

                    with c1:
                        st.markdown(f"**{symbol}**")
                    with c2:
                        st.markdown(f"${price:.2f}")
                    with c3:
                        st.markdown(f"Low+{from_low:.0f}%")
                    with c4:
                        st.markdown(f"Range: {range_30d:.1f}%")
                    with c5:
                        if on_stock_select and st.button("→", key=f"flat_cons_{symbol}_{idx}"):
                            on_stock_select(symbol)


def render_overview_charts():
    """Render overview charts."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Alert Distribution")
        tier1 = get_tier_alerts(1)
        tier2 = get_tier_alerts(2)
        all_metrics = get_all_metrics()

        tier1_count = len(tier1) if not tier1.empty else 0
        tier2_count = len(tier2) if not tier2.empty else 0
        total = len(all_metrics) if not all_metrics.empty else 0
        no_alert = total - tier1_count - tier2_count

        fig = create_alert_distribution(tier1_count, tier2_count, no_alert)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Sector Overview")
        metrics = get_all_metrics()
        if not metrics.empty:
            fig = create_sector_heatmap(metrics)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sector data available")


def render_dashboard(on_stock_select: Callable = None):
    """
    Render the full dashboard page.

    Args:
        on_stock_select: Callback when a stock is selected
    """
    # 3D Animated Header
    render_3d_header("CONVEXITY AI", "Momentum Stock Scanner")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.divider()

    # Scanner controls
    scan_action = render_scan_controls()

    if scan_action == "full_scan":
        run_scanner_with_progress()
        st.rerun()

    st.divider()

    # Summary
    render_dashboard_summary()

    st.divider()

    # Quick stats
    render_quick_stats()

    st.divider()

    # Alerts
    render_alerts_section(on_stock_select)

    st.divider()

    # Flat stocks breaking out
    render_flat_stocks_section(on_stock_select)

    st.divider()

    # Top movers
    render_movers_section(on_stock_select)

    st.divider()

    # Overview charts
    render_overview_charts()
