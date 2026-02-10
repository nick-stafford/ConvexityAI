"""
Earnings calendar service
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from ..utils.database import get_all_stocks


def get_earnings_date(symbol: str) -> Optional[Dict]:
    """
    Get next earnings date for a stock.

    Returns dict with earnings info or None.
    """
    try:
        ticker = yf.Ticker(symbol)
        calendar = ticker.calendar

        if calendar is None or (isinstance(calendar, pd.DataFrame) and calendar.empty):
            return None

        # Handle different return formats from yfinance
        if isinstance(calendar, dict):
            earnings_date = calendar.get('Earnings Date')
            if earnings_date:
                if isinstance(earnings_date, list) and len(earnings_date) > 0:
                    earnings_date = earnings_date[0]
                return {
                    'symbol': symbol,
                    'earnings_date': earnings_date,
                    'earnings_estimate': calendar.get('Earnings Average'),
                    'revenue_estimate': calendar.get('Revenue Average')
                }
        elif isinstance(calendar, pd.DataFrame):
            if 'Earnings Date' in calendar.columns:
                return {
                    'symbol': symbol,
                    'earnings_date': calendar['Earnings Date'].iloc[0] if len(calendar) > 0 else None,
                    'earnings_estimate': calendar.get('Earnings Average', [None])[0] if 'Earnings Average' in calendar.columns else None,
                    'revenue_estimate': calendar.get('Revenue Average', [None])[0] if 'Revenue Average' in calendar.columns else None
                }

        return None
    except Exception as e:
        return None


def get_upcoming_earnings(days: int = 14) -> List[Dict]:
    """
    Get stocks with earnings coming up in the next N days.

    Args:
        days: Number of days to look ahead

    Returns:
        List of stocks with upcoming earnings, sorted by date
    """
    stocks = get_all_stocks()
    if stocks.empty:
        return []

    upcoming = []
    now = datetime.now()
    cutoff = now + timedelta(days=days)

    for symbol in stocks['symbol'].tolist():
        try:
            earnings = get_earnings_date(symbol)

            if earnings and earnings.get('earnings_date'):
                earnings_date = earnings['earnings_date']

                # Convert to datetime if needed
                if isinstance(earnings_date, str):
                    try:
                        earnings_date = pd.to_datetime(earnings_date)
                    except:
                        continue

                # Handle timezone
                if hasattr(earnings_date, 'tzinfo') and earnings_date.tzinfo is not None:
                    earnings_date = earnings_date.tz_localize(None)

                # Check if within range
                if now <= earnings_date <= cutoff:
                    days_until = (earnings_date - now).days
                    upcoming.append({
                        'symbol': symbol,
                        'earnings_date': earnings_date.strftime('%Y-%m-%d'),
                        'days_until': days_until,
                        'earnings_estimate': earnings.get('earnings_estimate'),
                        'revenue_estimate': earnings.get('revenue_estimate')
                    })

        except Exception as e:
            continue

    # Sort by date
    upcoming.sort(key=lambda x: x['days_until'])

    return upcoming


def get_recent_earnings(days: int = 7) -> List[Dict]:
    """
    Get stocks that reported earnings in the last N days.

    Useful for finding post-earnings momentum plays.
    """
    stocks = get_all_stocks()
    if stocks.empty:
        return []

    recent = []
    now = datetime.now()
    cutoff = now - timedelta(days=days)

    for symbol in stocks['symbol'].tolist():
        try:
            ticker = yf.Ticker(symbol)

            # Get earnings history
            earnings_hist = ticker.earnings_dates

            if earnings_hist is None or earnings_hist.empty:
                continue

            # Find most recent past earnings
            for date_idx in earnings_hist.index:
                earnings_date = pd.to_datetime(date_idx)

                if hasattr(earnings_date, 'tzinfo') and earnings_date.tzinfo is not None:
                    earnings_date = earnings_date.tz_localize(None)

                if cutoff <= earnings_date <= now:
                    row = earnings_hist.loc[date_idx]
                    recent.append({
                        'symbol': symbol,
                        'earnings_date': earnings_date.strftime('%Y-%m-%d'),
                        'days_ago': (now - earnings_date).days,
                        'eps_estimate': row.get('EPS Estimate'),
                        'eps_actual': row.get('Reported EPS'),
                        'surprise': row.get('Surprise(%)')
                    })
                    break  # Only get most recent

        except Exception as e:
            continue

    # Sort by most recent first
    recent.sort(key=lambda x: x['days_ago'])

    return recent
