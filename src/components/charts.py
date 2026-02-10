"""
Chart components using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional


def create_price_chart(
    history: pd.DataFrame,
    metrics: Dict = None,
    show_ma: bool = True,
    show_volume: bool = True
) -> go.Figure:
    """
    Create an interactive candlestick chart with optional MA lines and volume.

    Args:
        history: DataFrame with date, open, high, low, close, volume columns
        metrics: Optional dict with fifty_day_avg, two_hundred_day_avg
        show_ma: Whether to show moving average lines
        show_volume: Whether to show volume subplot

    Returns:
        Plotly figure
    """
    if history.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    # Create subplots
    rows = 2 if show_volume else 1
    row_heights = [0.7, 0.3] if show_volume else [1]

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=history['date'],
            open=history['open'],
            high=history['high'],
            low=history['low'],
            close=history['close'],
            name='Price',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )

    # Add moving averages if available
    if show_ma and metrics:
        if metrics.get('fifty_day_avg'):
            fig.add_hline(
                y=metrics['fifty_day_avg'],
                line_dash="dash",
                line_color="orange",
                annotation_text="50 DMA",
                row=1, col=1
            )
        if metrics.get('two_hundred_day_avg'):
            fig.add_hline(
                y=metrics['two_hundred_day_avg'],
                line_dash="dash",
                line_color="purple",
                annotation_text="200 DMA",
                row=1, col=1
            )

    # Add 52-week levels if available
    if metrics:
        if metrics.get('fifty_two_week_low'):
            fig.add_hline(
                y=metrics['fifty_two_week_low'],
                line_dash="dot",
                line_color="red",
                annotation_text="52wk Low",
                row=1, col=1
            )
        if metrics.get('fifty_two_week_high'):
            fig.add_hline(
                y=metrics['fifty_two_week_high'],
                line_dash="dot",
                line_color="green",
                annotation_text="52wk High",
                row=1, col=1
            )

    # Volume bars
    if show_volume:
        colors = ['#26a69a' if history['close'].iloc[i] >= history['open'].iloc[i]
                  else '#ef5350' for i in range(len(history))]

        fig.add_trace(
            go.Bar(
                x=history['date'],
                y=history['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )

    # Layout
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        showlegend=False,
        height=500,
        margin=dict(l=50, r=50, t=30, b=30)
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def create_mini_chart(history: pd.DataFrame, days: int = 30) -> go.Figure:
    """Create a small sparkline-style chart for tables/cards."""
    if history.empty:
        fig = go.Figure()
        return fig

    recent = history.tail(days)

    # Determine color based on trend
    start_price = recent['close'].iloc[0]
    end_price = recent['close'].iloc[-1]
    color = '#26a69a' if end_price >= start_price else '#ef5350'

    fig = go.Figure(
        go.Scatter(
            x=recent['date'],
            y=recent['close'],
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)"
        )
    )

    fig.update_layout(
        template='plotly_dark',
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=60,
        width=150
    )

    return fig


def create_performance_bars(metrics: Dict) -> go.Figure:
    """Create horizontal bar chart showing performance metrics."""
    labels = ['1 Day', '7 Days', '30 Days', 'From 52wk Low']
    values = [
        metrics.get('price_change_1d', 0),
        metrics.get('price_change_7d', 0),
        metrics.get('price_change_30d', 0),
        metrics.get('pct_from_52wk_low', 0)
    ]

    colors = ['#26a69a' if v >= 0 else '#ef5350' for v in values]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker_color=colors,
            text=[f"{v:.1f}%" for v in values],
            textposition='outside'
        )
    )

    fig.update_layout(
        template='plotly_dark',
        showlegend=False,
        height=200,
        margin=dict(l=100, r=50, t=20, b=20),
        xaxis=dict(title='% Change', zeroline=True, zerolinecolor='white')
    )

    return fig


def create_volume_comparison(current_vol: int, avg_vol: int) -> go.Figure:
    """Create a gauge showing volume vs average."""
    ratio = current_vol / avg_vol if avg_vol > 0 else 0

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=ratio,
            title={'text': "Volume Ratio"},
            number={'suffix': 'x'},
            gauge={
                'axis': {'range': [0, 3]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.5], 'color': "#ef5350"},
                    {'range': [0.5, 1], 'color': "#ffc107"},
                    {'range': [1, 1.5], 'color': "#26a69a"},
                    {'range': [1.5, 3], 'color': "#00e676"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 2},
                    'thickness': 0.75,
                    'value': 1.5
                }
            }
        )
    )

    fig.update_layout(
        template='plotly_dark',
        height=200,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def create_sector_heatmap(stocks_df: pd.DataFrame) -> go.Figure:
    """
    Create a treemap heatmap showing sector performance.

    Args:
        stocks_df: DataFrame with symbol, sector, price_change_1d columns
    """
    if stocks_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    # Check if sector column exists
    if 'sector' not in stocks_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Run a scan to see sector data", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(template='plotly_dark', height=300)
        return fig

    # Group by sector
    sector_data = stocks_df.groupby('sector').agg({
        'price_change_1d': 'mean',
        'symbol': 'count'
    }).reset_index()
    sector_data.columns = ['sector', 'avg_change', 'count']

    fig = go.Figure(
        go.Treemap(
            labels=sector_data['sector'],
            parents=[''] * len(sector_data),
            values=sector_data['count'],
            marker=dict(
                colors=sector_data['avg_change'],
                colorscale='RdYlGn',
                cmid=0
            ),
            textinfo='label+value',
            hovertemplate='<b>%{label}</b><br>Stocks: %{value}<br>Avg Change: %{color:.1f}%<extra></extra>'
        )
    )

    fig.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    return fig


def create_alert_distribution(tier1_count: int, tier2_count: int, no_alert_count: int) -> go.Figure:
    """Create a pie chart showing alert distribution."""
    labels = ['Tier 1', 'Tier 2', 'No Alert']
    values = [tier1_count, tier2_count, no_alert_count]
    colors = ['#26a69a', '#ffc107', '#666666']

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.4,
            textinfo='label+percent',
            textposition='outside'
        )
    )

    fig.update_layout(
        template='plotly_dark',
        showlegend=True,
        height=300,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    return fig


def create_backtest_equity_curve(trades: List[Dict]) -> go.Figure:
    """Create an equity curve from backtest results."""
    if not trades:
        fig = go.Figure()
        fig.add_annotation(text="No trades to display", x=0.5, y=0.5, showarrow=False)
        return fig

    # Calculate cumulative returns
    sorted_trades = sorted(trades, key=lambda x: x.exit_date)
    dates = [t.exit_date for t in sorted_trades]
    returns = [t.return_pct for t in sorted_trades]
    cumulative = [sum(returns[:i+1]) for i in range(len(returns))]

    # Calculate drawdown
    running_max = []
    for i, c in enumerate(cumulative):
        running_max.append(max(cumulative[:i+1]))
    drawdown = [c - m for c, m in zip(cumulative, running_max)]

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Equity curve
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[c * 100 for c in cumulative],
            name='Cumulative Return',
            line=dict(color='#26a69a', width=2)
        ),
        secondary_y=False
    )

    # Drawdown
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[d * 100 for d in drawdown],
            name='Drawdown',
            fill='tozeroy',
            line=dict(color='#ef5350', width=1),
            fillcolor='rgba(239, 83, 80, 0.3)'
        ),
        secondary_y=True
    )

    fig.update_layout(
        template='plotly_dark',
        height=350,
        margin=dict(l=50, r=50, t=30, b=30),
        legend=dict(x=0, y=1, orientation='h')
    )

    fig.update_yaxes(title_text="Cumulative Return %", secondary_y=False)
    fig.update_yaxes(title_text="Drawdown %", secondary_y=True)

    return fig
