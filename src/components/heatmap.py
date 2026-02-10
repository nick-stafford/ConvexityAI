"""
Sector heatmap component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Callable

from ..utils.database import get_all_metrics, get_stock


def create_sector_treemap(
    metrics_df: pd.DataFrame,
    value_col: str = 'price_change_1d',
    size_col: str = 'market_cap'
) -> go.Figure:
    """
    Create a treemap heatmap showing stocks grouped by sector.

    Args:
        metrics_df: DataFrame with stock metrics
        value_col: Column to use for color (price change)
        size_col: Column to use for tile size (market cap)

    Returns:
        Plotly figure
    """
    if metrics_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    # Need sector information - join with stocks table
    stocks_with_sector = []
    for _, row in metrics_df.iterrows():
        stock_info = get_stock(row['symbol'])
        sector = stock_info.get('sector', 'Unknown') if stock_info else 'Unknown'
        stock_data = row.to_dict()
        stock_data['sector'] = sector if sector else 'Unknown'
        stocks_with_sector.append(stock_data)

    df = pd.DataFrame(stocks_with_sector)

    # Handle missing values
    df[value_col] = df[value_col].fillna(0)
    df[size_col] = df[size_col].fillna(1000000)  # Default 1M market cap

    # Create treemap
    fig = px.treemap(
        df,
        path=['sector', 'symbol'],
        values=size_col,
        color=value_col,
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0,
        hover_data={
            'current_price': ':.2f',
            value_col: ':.2f',
            'volume_ratio': ':.2f'
        }
    )

    fig.update_layout(
        template='plotly_dark',
        height=600,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_colorbar=dict(
            title=dict(text='% Change'),
            tickformat='.1f'
        )
    )

    fig.update_traces(
        textinfo='label+text',
        texttemplate='%{label}<br>%{color:.1f}%',
        hovertemplate='<b>%{label}</b><br>' +
                      'Change: %{color:.2f}%<br>' +
                      'Market Cap: $%{value:,.0f}<extra></extra>'
    )

    return fig


def create_sector_bar_chart(metrics_df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing average sector performance.
    """
    if metrics_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    # Get sector for each stock
    sector_data = []
    for _, row in metrics_df.iterrows():
        stock_info = get_stock(row['symbol'])
        sector = stock_info.get('sector', 'Unknown') if stock_info else 'Unknown'
        sector_data.append({
            'sector': sector if sector else 'Unknown',
            'price_change_1d': row.get('price_change_1d', 0),
            'price_change_7d': row.get('price_change_7d', 0),
            'price_change_30d': row.get('price_change_30d', 0)
        })

    df = pd.DataFrame(sector_data)

    # Group by sector
    sector_avg = df.groupby('sector').agg({
        'price_change_1d': 'mean',
        'price_change_7d': 'mean',
        'price_change_30d': 'mean'
    }).reset_index()

    # Sort by 1-day change
    sector_avg = sector_avg.sort_values('price_change_1d', ascending=True)

    # Create grouped bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='1 Day',
        y=sector_avg['sector'],
        x=sector_avg['price_change_1d'],
        orientation='h',
        marker_color='#26a69a'
    ))

    fig.add_trace(go.Bar(
        name='7 Days',
        y=sector_avg['sector'],
        x=sector_avg['price_change_7d'],
        orientation='h',
        marker_color='#42a5f5'
    ))

    fig.add_trace(go.Bar(
        name='30 Days',
        y=sector_avg['sector'],
        x=sector_avg['price_change_30d'],
        orientation='h',
        marker_color='#ab47bc'
    ))

    fig.update_layout(
        template='plotly_dark',
        barmode='group',
        height=400,
        margin=dict(l=150, r=50, t=30, b=30),
        xaxis=dict(title='% Change', zeroline=True, zerolinecolor='white'),
        legend=dict(orientation='h', y=1.1)
    )

    return fig


def create_tier_heatmap(metrics_df: pd.DataFrame) -> go.Figure:
    """
    Create a heatmap showing tier distribution by sector.
    """
    if metrics_df.empty:
        fig = go.Figure()
        return fig

    # Get sector for each stock
    data = []
    for _, row in metrics_df.iterrows():
        stock_info = get_stock(row['symbol'])
        sector = stock_info.get('sector', 'Unknown') if stock_info else 'Unknown'
        data.append({
            'sector': sector if sector else 'Unknown',
            'tier': row.get('tier')
        })

    df = pd.DataFrame(data)

    # Create pivot table
    pivot = pd.crosstab(df['sector'], df['tier'].fillna('No Alert'))

    # Ensure all tier columns exist
    for tier in ['No Alert', 2, 1]:
        if tier not in pivot.columns:
            pivot[tier] = 0

    pivot = pivot[['No Alert', 2, 1]]  # Reorder columns
    pivot.columns = ['No Alert', 'Tier 2', 'Tier 1']

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[
            [0, '#333333'],
            [0.5, '#ffc107'],
            [1, '#26a69a']
        ],
        text=pivot.values,
        texttemplate='%{text}',
        textfont=dict(size=12, color='white'),
        hovertemplate='%{y}<br>%{x}: %{z} stocks<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=150, r=50, t=30, b=50),
        xaxis=dict(title='Alert Tier'),
        yaxis=dict(title='Sector')
    )

    return fig


def render_heatmap_page(on_stock_select: Callable = None):
    """
    Render the full heatmap page.

    Args:
        on_stock_select: Callback when a stock is selected
    """
    st.markdown("## 🗺️ Sector Heatmap")

    # Get all metrics
    metrics_df = get_all_metrics()

    if metrics_df.empty:
        st.warning("No stock data available. Run a scan first.")
        return

    # Controls
    col1, col2, col3 = st.columns([2, 2, 6])

    with col1:
        color_by = st.selectbox(
            "Color by",
            options=['price_change_1d', 'price_change_7d', 'price_change_30d', 'pct_from_52wk_low'],
            format_func=lambda x: {
                'price_change_1d': '1 Day Change',
                'price_change_7d': '7 Day Change',
                'price_change_30d': '30 Day Change',
                'pct_from_52wk_low': '% From 52wk Low'
            }.get(x, x)
        )

    with col2:
        size_by = st.selectbox(
            "Size by",
            options=['market_cap', 'volume'],
            format_func=lambda x: {
                'market_cap': 'Market Cap',
                'volume': 'Volume'
            }.get(x, x)
        )

    # Main treemap
    st.markdown("### Interactive Treemap")
    fig = create_sector_treemap(metrics_df, value_col=color_by, size_col=size_by)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Two column layout
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Sector Performance")
        fig = create_sector_bar_chart(metrics_df)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Alert Distribution by Sector")
        fig = create_tier_heatmap(metrics_df)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Sector breakdown table
    st.markdown("### Sector Breakdown")

    # Calculate sector stats
    sector_stats = []
    for _, row in metrics_df.iterrows():
        stock_info = get_stock(row['symbol'])
        sector = stock_info.get('sector', 'Unknown') if stock_info else 'Unknown'
        sector_stats.append({
            'sector': sector if sector else 'Unknown',
            'symbol': row['symbol'],
            'current_price': row.get('current_price', 0),
            'price_change_1d': row.get('price_change_1d', 0),
            'tier': row.get('tier')
        })

    df = pd.DataFrame(sector_stats)

    # Group by sector
    sector_summary = df.groupby('sector').agg({
        'symbol': 'count',
        'price_change_1d': 'mean',
        'tier': lambda x: (x == 1).sum()
    }).reset_index()

    sector_summary.columns = ['Sector', 'Stocks', 'Avg 1D Change %', 'Tier 1 Count']
    sector_summary = sector_summary.sort_values('Avg 1D Change %', ascending=False)

    st.dataframe(sector_summary, use_container_width=True, hide_index=True)

    # Select sector to drill down
    selected_sector = st.selectbox(
        "Select sector to view stocks:",
        options=['All'] + sorted(df['sector'].unique().tolist())
    )

    if selected_sector != 'All':
        sector_stocks = df[df['sector'] == selected_sector].sort_values('price_change_1d', ascending=False)
        st.dataframe(sector_stocks[['symbol', 'current_price', 'price_change_1d', 'tier']], hide_index=True)

        if on_stock_select:
            selected_stock = st.selectbox(
                "Select stock for details:",
                options=sector_stocks['symbol'].tolist()
            )
            if selected_stock:
                on_stock_select(selected_stock)
