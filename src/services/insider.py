"""
Insider trading data service
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from .data_fetcher import data_fetcher
from ..utils.database import get_all_stocks


def get_insider_buying(symbol: str) -> pd.DataFrame:
    """
    Get recent insider buying activity for a stock.

    Returns DataFrame with insider transactions.
    """
    return data_fetcher.get_insider_trades(symbol)


def get_recent_insider_buys(days: int = 30, min_value: float = 10000) -> List[Dict]:
    """
    Scan all stocks for recent insider buying activity.

    Args:
        days: Look back period in days
        min_value: Minimum transaction value to include

    Returns:
        List of stocks with insider buying
    """
    stocks = get_all_stocks()
    if stocks.empty:
        return []

    insider_buys = []
    cutoff_date = datetime.now() - timedelta(days=days)

    for symbol in stocks['symbol'].tolist()[:100]:  # Limit to avoid rate limits
        try:
            trades = data_fetcher.get_insider_trades(symbol)

            if trades is None or trades.empty:
                continue

            # Filter for purchases
            if 'Transaction' in trades.columns:
                buys = trades[trades['Transaction'].str.contains('Purchase|Buy', case=False, na=False)]
            elif 'transaction' in trades.columns:
                buys = trades[trades['transaction'].str.contains('Purchase|Buy', case=False, na=False)]
            else:
                continue

            if buys.empty:
                continue

            # Get the most recent buy
            recent_buy = buys.iloc[0]

            insider_buys.append({
                'symbol': symbol,
                'insider': recent_buy.get('Insider Trading', recent_buy.get('insider', 'Unknown')),
                'position': recent_buy.get('Position', recent_buy.get('position', 'Unknown')),
                'shares': recent_buy.get('Shares', recent_buy.get('shares', 0)),
                'value': recent_buy.get('Value', recent_buy.get('value', 0)),
                'date': recent_buy.get('Start Date', recent_buy.get('date', 'Unknown'))
            })

        except Exception as e:
            continue

    return insider_buys


def format_insider_data(trades: pd.DataFrame) -> List[Dict]:
    """Format insider trades for display."""
    if trades is None or trades.empty:
        return []

    result = []
    for _, row in trades.head(10).iterrows():
        result.append({
            'insider': row.get('Insider Trading', row.get('insider', 'Unknown')),
            'position': row.get('Position', row.get('position', '')),
            'transaction': row.get('Transaction', row.get('transaction', '')),
            'shares': row.get('Shares', row.get('shares', 0)),
            'value': row.get('Value', row.get('value', 0)),
            'date': str(row.get('Start Date', row.get('date', '')))
        })

    return result
