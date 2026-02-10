"""
Sector Rotation Dashboard Component
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from ..utils.database import get_all_metrics, get_stock


def get_sector_performance() -> pd.DataFrame:
    """Calculate performance metrics by sector."""
    metrics = get_all_metrics()

    if metrics.empty:
        return pd.DataFrame()

    # Add sector to metrics
    sector_data = []
    for _, row in metrics.iterrows():
        stock_info = get_stock(row['symbol'])
        sector = stock_info.get('sector', 'Unknown') if stock_info else 'Unknown'
        sector_data.append({
            'symbol': row['symbol'],
            'sector': sector if sector else 'Unknown',
            'price_change_1d': row.get('price_change_1d', 0),
            'price_change_7d': row.get('price_change_7d', 0),
            'price_change_30d': row.get('price_change_30d', 0),
            'pct_from_52wk_low': row.get('pct_from_52wk_low', 0),
            'volume_ratio': row.get('volume_ratio', 0),
            'tier': row.get('tier')
        })

    df = pd.DataFrame(sector_data)

    # Aggregate by sector
    sector_agg = df.groupby('sector').agg({
        'symbol': 'count',
        'price_change_1d': 'mean',
        'price_change_7d': 'mean',
        'price_change_30d': 'mean',
        'pct_from_52wk_low': 'mean',
        'volume_ratio': 'mean',
        'tier': lambda x: (x == 1).sum()
    }).reset_index()

    sector_agg.columns = ['Sector', 'Stock Count', 'Avg 1D %', 'Avg 7D %', 'Avg 30D %',
                          'Avg From Low %', 'Avg Vol Ratio', 'Tier 1 Count']

    return sector_agg


def create_sector_momentum_chart(sector_df: pd.DataFrame) -> go.Figure:
    """Create a momentum scatter plot (7d vs 30d performance)."""
    if sector_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    # Size based on stock count
    max_count = sector_df['Stock Count'].max()
    sizes = (sector_df['Stock Count'] / max_count * 50) + 10

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sector_df['Avg 30D %'],
        y=sector_df['Avg 7D %'],
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=sector_df['Avg 1D %'],
            colorscale='RdYlGn',
            colorbar=dict(title='1D Change %'),
            showscale=True,
            line=dict(width=1, color='white')
        ),
        text=sector_df['Sector'],
        textposition='top center',
        hovertemplate=(
            '<b>%{text}</b><br>' +
            '30D: %{x:.1f}%<br>' +
            '7D: %{y:.1f}%<br>' +
            '1D: %{marker.color:.1f}%<extra></extra>'
        )
    ))

    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Quadrant labels
    fig.add_annotation(x=sector_df['Avg 30D %'].max() * 0.7, y=sector_df['Avg 7D %'].max() * 0.8,
                       text="🔥 HOT", showarrow=False, font=dict(size=14, color='green'))
    fig.add_annotation(x=sector_df['Avg 30D %'].min() * 0.7, y=sector_df['Avg 7D %'].min() * 0.8,
                       text="❄️ COLD", showarrow=False, font=dict(size=14, color='red'))
    fig.add_annotation(x=sector_df['Avg 30D %'].min() * 0.7, y=sector_df['Avg 7D %'].max() * 0.8,
                       text="🚀 RECOVERING", showarrow=False, font=dict(size=12, color='orange'))
    fig.add_annotation(x=sector_df['Avg 30D %'].max() * 0.7, y=sector_df['Avg 7D %'].min() * 0.8,
                       text="⚠️ COOLING", showarrow=False, font=dict(size=12, color='orange'))

    fig.update_layout(
        template='plotly_dark',
        title='Sector Momentum Map',
        xaxis_title='30-Day Performance %',
        yaxis_title='7-Day Performance %',
        height=500,
        showlegend=False
    )

    return fig


def create_sector_ranking_chart(sector_df: pd.DataFrame, metric: str = 'Avg 7D %') -> go.Figure:
    """Create a horizontal bar chart ranking sectors."""
    if sector_df.empty:
        fig = go.Figure()
        return fig

    # Sort by metric
    sorted_df = sector_df.sort_values(metric, ascending=True)

    colors = ['#ef5350' if x < 0 else '#26a69a' for x in sorted_df[metric]]

    fig = go.Figure(go.Bar(
        x=sorted_df[metric],
        y=sorted_df['Sector'],
        orientation='h',
        marker_color=colors,
        text=[f"{x:.1f}%" for x in sorted_df[metric]],
        textposition='outside'
    ))

    fig.update_layout(
        template='plotly_dark',
        title=f'Sector Ranking by {metric}',
        xaxis_title=metric,
        height=400,
        margin=dict(l=150)
    )

    return fig


def create_sector_flow_chart(sector_df: pd.DataFrame) -> go.Figure:
    """Create a flow chart showing momentum direction."""
    if sector_df.empty:
        fig = go.Figure()
        return fig

    # Calculate momentum direction
    sector_df = sector_df.copy()
    sector_df['momentum'] = sector_df.apply(
        lambda x: 'Accelerating' if x['Avg 7D %'] > x['Avg 30D %'] / 4 and x['Avg 7D %'] > 0
        else ('Decelerating' if x['Avg 7D %'] < x['Avg 30D %'] / 4 and x['Avg 30D %'] > 0
              else ('Recovering' if x['Avg 7D %'] > 0 and x['Avg 30D %'] < 0
                    else 'Declining')),
        axis=1
    )

    # Color map
    color_map = {
        'Accelerating': '#26a69a',
        'Decelerating': '#ffc107',
        'Recovering': '#42a5f5',
        'Declining': '#ef5350'
    }

    fig = go.Figure()

    for momentum_type in ['Accelerating', 'Recovering', 'Decelerating', 'Declining']:
        subset = sector_df[sector_df['momentum'] == momentum_type]
        if not subset.empty:
            fig.add_trace(go.Bar(
                name=momentum_type,
                x=subset['Sector'],
                y=subset['Avg 7D %'],
                marker_color=color_map[momentum_type],
                text=[f"{x:.1f}%" for x in subset['Avg 7D %']],
                textposition='outside'
            ))

    fig.update_layout(
        template='plotly_dark',
        title='Sector Momentum Direction',
        barmode='group',
        height=400,
        legend=dict(orientation='h', y=1.1)
    )

    return fig


def render_sector_rotation_page(on_stock_select=None):
    """Render the full sector rotation dashboard."""
    st.markdown("# 🔄 Sector Rotation Dashboard")
    st.caption("Identify which sectors are heating up and which are cooling down")

    # Get data
    sector_df = get_sector_performance()

    if sector_df.empty:
        st.warning("No sector data available. Run a scan first.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    hottest = sector_df.loc[sector_df['Avg 7D %'].idxmax()]
    coldest = sector_df.loc[sector_df['Avg 7D %'].idxmin()]
    most_volume = sector_df.loc[sector_df['Avg Vol Ratio'].idxmax()]
    most_alerts = sector_df.loc[sector_df['Tier 1 Count'].idxmax()]

    with col1:
        st.metric("🔥 Hottest Sector", hottest['Sector'], f"{hottest['Avg 7D %']:.1f}%")
    with col2:
        st.metric("❄️ Coldest Sector", coldest['Sector'], f"{coldest['Avg 7D %']:.1f}%")
    with col3:
        st.metric("📊 Most Volume", most_volume['Sector'], f"{most_volume['Avg Vol Ratio']:.2f}x")
    with col4:
        st.metric("🎯 Most Tier 1s", most_alerts['Sector'], f"{int(most_alerts['Tier 1 Count'])} alerts")

    st.divider()

    # Momentum Map
    st.markdown("### Momentum Map")
    st.caption("Position shows performance, color shows 1-day change, size shows stock count")
    fig = create_sector_momentum_chart(sector_df)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Rankings
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 7-Day Performance Ranking")
        fig = create_sector_ranking_chart(sector_df, 'Avg 7D %')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 30-Day Performance Ranking")
        fig = create_sector_ranking_chart(sector_df, 'Avg 30D %')
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Momentum Direction
    st.markdown("### Momentum Direction")
    fig = create_sector_flow_chart(sector_df)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Detailed Table
    st.markdown("### Sector Details")
    st.dataframe(
        sector_df.style.format({
            'Avg 1D %': '{:.2f}%',
            'Avg 7D %': '{:.2f}%',
            'Avg 30D %': '{:.2f}%',
            'Avg From Low %': '{:.1f}%',
            'Avg Vol Ratio': '{:.2f}x'
        }).background_gradient(subset=['Avg 7D %'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )

    # Drill down
    st.divider()
    st.markdown("### Drill Down by Sector")

    selected_sector = st.selectbox("Select a sector:", options=sector_df['Sector'].tolist())

    if selected_sector:
        metrics = get_all_metrics()
        sector_stocks = []

        for _, row in metrics.iterrows():
            stock_info = get_stock(row['symbol'])
            sector = stock_info.get('sector', 'Unknown') if stock_info else 'Unknown'
            if sector == selected_sector:
                sector_stocks.append(row)

        if sector_stocks:
            sector_df_detail = pd.DataFrame(sector_stocks)
            sector_df_detail = sector_df_detail.sort_values('price_change_7d', ascending=False)

            st.dataframe(
                sector_df_detail[['symbol', 'current_price', 'price_change_1d', 'price_change_7d',
                                  'price_change_30d', 'volume_ratio', 'tier']].head(20),
                use_container_width=True,
                hide_index=True
            )

            if on_stock_select:
                selected_stock = st.selectbox(
                    "View stock details:",
                    options=sector_df_detail['symbol'].tolist(),
                    key='sector_stock_select'
                )
                if st.button("Go to Stock →"):
                    on_stock_select(selected_stock)
