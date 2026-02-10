"""
Alerts table component - displays tier 1 and tier 2 stocks
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Callable


def create_sparkline(prices: list, width: int = 120, height: int = 40) -> go.Figure:
    """Create a minimal sparkline chart."""
    if not prices or len(prices) < 2:
        return None

    # Determine color based on trend
    color = "#26a69a" if prices[-1] >= prices[0] else "#ef5350"

    fig = go.Figure(
        go.Scatter(
            y=prices,
            mode='lines',
            line=dict(color=color, width=1.5),
            fill='tozeroy',
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)"
        )
    )

    fig.update_layout(
        width=width,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False
    )

    return fig


def format_price(value):
    """Format price values."""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"${value:.2f}"


def format_percent(value):
    """Format percentage values with color."""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"{value:.1f}%"


def format_volume(value):
    """Format volume with K/M suffix."""
    if pd.isna(value) or value is None:
        return "N/A"
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(value)


def render_alerts_table(
    df: pd.DataFrame,
    tier: int,
    on_select: Callable = None,
    key_prefix: str = ""
):
    """
    Render an interactive alerts table.

    Args:
        df: DataFrame with stock metrics
        tier: Tier number (1 or 2) for styling
        on_select: Callback function when row is clicked
        key_prefix: Prefix for Streamlit widget keys
    """
    if df.empty:
        st.info(f"No Tier {tier} alerts found.")
        return

    # Style based on tier
    tier_color = "#26a69a" if tier == 1 else "#ffc107"
    tier_icon = "🟢" if tier == 1 else "🟡"

    st.markdown(f"""
        <div style="background: linear-gradient(90deg, {tier_color}20, transparent);
                    padding: 10px; border-radius: 5px; border-left: 4px solid {tier_color};">
            <h3 style="margin: 0;">{tier_icon} Tier {tier} Alerts ({len(df)} stocks)</h3>
        </div>
    """, unsafe_allow_html=True)

    # Prepare display columns
    display_cols = {
        'symbol': 'Symbol',
        'current_price': 'Price',
        'pct_from_52wk_low': 'From Low',
        'price_change_1d': '1D Chg',
        'price_change_7d': '7D Chg',
        'volume_ratio': 'Vol Ratio',
        'consolidation_range_30d': '30D Range'
    }

    # Filter to available columns
    available_cols = [c for c in display_cols.keys() if c in df.columns]

    if not available_cols:
        st.error("No displayable columns found")
        return

    display_df = df[available_cols].copy()

    # Format values
    for col in display_df.columns:
        if col == 'current_price':
            display_df[col] = display_df[col].apply(format_price)
        elif col in ['pct_from_52wk_low', 'price_change_1d', 'price_change_7d', 'consolidation_range_30d']:
            display_df[col] = display_df[col].apply(format_percent)
        elif col == 'volume_ratio':
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else "N/A")
        elif col == 'volume':
            display_df[col] = display_df[col].apply(format_volume)

    # Rename columns
    display_df.columns = [display_cols.get(c, c) for c in display_df.columns]

    # Create clickable table
    st.markdown("""
        <style>
        .stDataFrame tbody tr:hover {
            background-color: rgba(255,255,255,0.1);
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # Column headers
    col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1])
    with col1:
        st.markdown("**Symbol**")
    with col2:
        st.markdown("**Price**")
    with col3:
        st.markdown("**From Low**")
    with col4:
        st.markdown("**1D Chg**")
    with col5:
        st.markdown("**Vol Ratio**")
    with col6:
        st.markdown("**Action**")

    # Create clickable list with view buttons
    with st.container(height=400):
        for idx, row in df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1])

            symbol = row.get('symbol', 'N/A')
            price = row.get('current_price', 0)
            from_low = row.get('pct_from_52wk_low', 0)
            change_1d = row.get('price_change_1d', 0)
            vol_ratio = row.get('volume_ratio', 0)

            with col1:
                st.markdown(f"**{symbol}**")
            with col2:
                st.markdown(f"${price:.2f}")
            with col3:
                color = "#26a69a" if from_low >= 0 else "#ef5350"
                st.markdown(f"<span style='color:{color}'>{from_low:.1f}%</span>", unsafe_allow_html=True)
            with col4:
                color = "#26a69a" if change_1d >= 0 else "#ef5350"
                st.markdown(f"<span style='color:{color}'>{change_1d:.1f}%</span>", unsafe_allow_html=True)
            with col5:
                st.markdown(f"{vol_ratio:.2f}x")
            with col6:
                if on_select and st.button("View", key=f"{key_prefix}_view_{tier}_{symbol}_{idx}"):
                    on_select(symbol)


def render_top_movers(
    df: pd.DataFrame,
    title: str = "Top Movers",
    change_col: str = "price_change_1d",
    on_select: callable = None
):
    """Render a scrollable top movers list with clickable stocks."""
    if df.empty:
        st.info("No data available")
        return

    st.markdown(f"**{title}** ({len(df)} stocks)")

    # Create scrollable container for all stocks
    with st.container(height=400):
        for idx, row in df.iterrows():
            symbol = row.get('symbol', 'N/A')
            price = row.get('current_price', 0)
            change = row.get(change_col, 0)

            # Color based on change
            color = "#26a69a" if change >= 0 else "#ef5350"
            arrow = "▲" if change >= 0 else "▼"

            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                st.markdown(f"**{symbol}**")
            with col2:
                st.markdown(f"${price:.2f}")
            with col3:
                st.markdown(f"<span style='color: {color};'>{arrow} {abs(change):.1f}%</span>", unsafe_allow_html=True)
            with col4:
                if st.button("→", key=f"view_{title}_{symbol}_{idx}", help=f"View {symbol}"):
                    if on_select:
                        on_select(symbol)


def render_alert_summary(tier1_count: int, tier2_count: int, total_stocks: int):
    """Render an alert summary card."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="🟢 Tier 1 Alerts",
            value=tier1_count,
            delta=f"{tier1_count/total_stocks*100:.1f}% of universe" if total_stocks > 0 else None
        )

    with col2:
        st.metric(
            label="🟡 Tier 2 Alerts",
            value=tier2_count,
            delta=f"{tier2_count/total_stocks*100:.1f}% of universe" if total_stocks > 0 else None
        )

    with col3:
        st.metric(
            label="📊 Total Stocks",
            value=total_stocks
        )


def render_watchlist(df: pd.DataFrame, on_remove: Callable = None):
    """Render the user's watchlist."""
    if df.empty:
        st.info("Your watchlist is empty. Add stocks from the scanner results.")
        return

    st.markdown("### 👁️ Watchlist")

    for _, row in df.iterrows():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"**{row['symbol']}** - Added {row.get('added_at', 'N/A')}")
            if row.get('notes'):
                st.caption(row['notes'])

        with col2:
            if on_remove and st.button("❌", key=f"remove_{row['symbol']}"):
                on_remove(row['symbol'])
                st.rerun()
