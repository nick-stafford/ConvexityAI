"""
Data fetching service - yfinance wrapper with caching
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import time
import pickle
from pathlib import Path

from ..utils.config import CACHE_DIR, HISTORY_YEARS


class DataFetcher:
    """Fetches and caches stock data from Yahoo Finance."""

    def __init__(self):
        self.cache_dir = CACHE_DIR
        self._rate_limit_delay = 0.1  # seconds between requests
        self._last_request_time = 0

    def _rate_limit(self):
        """Apply rate limiting to avoid hammering Yahoo."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get basic stock info (current price, 52wk high/low, volume, etc.)
        """
        self._rate_limit()
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or 'regularMarketPrice' not in info:
                return None

            return {
                'symbol': symbol.upper(),
                'name': info.get('longName') or info.get('shortName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'exchange': info.get('exchange', ''),
                'current_price': info.get('regularMarketPrice') or info.get('currentPrice'),
                'previous_close': info.get('previousClose'),
                'open': info.get('regularMarketOpen'),
                'day_low': info.get('dayLow'),
                'day_high': info.get('dayHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_day_avg': info.get('fiftyDayAverage'),
                'two_hundred_day_avg': info.get('twoHundredDayAverage'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'avg_volume_10d': info.get('averageVolume10days'),
                'market_cap': info.get('marketCap'),
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol: str, years: int = None,
                            use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Get historical price data for a stock.

        Args:
            symbol: Stock ticker symbol
            years: Number of years of history (default from config)
            use_cache: Whether to use cached data

        Returns:
            DataFrame with OHLCV data
        """
        if years is None:
            years = HISTORY_YEARS

        cache_file = self.cache_dir / f"{symbol.upper()}_history.pkl"

        # Check cache
        if use_cache and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=20):  # Cache valid for ~1 day
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except:
                    pass  # Cache corrupted, fetch fresh

        # Fetch from Yahoo
        self._rate_limit()
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=f"{years}y")

            if df.empty:
                return None

            # Clean up the dataframe
            df = df.reset_index()
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]

            # Save to cache
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)

            return df
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return None

    def get_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get recent news for a stock."""
        self._rate_limit()
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return []

            return [
                {
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                    'type': item.get('type', ''),
                }
                for item in news[:limit]
            ]
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    def get_insider_trades(self, symbol: str) -> pd.DataFrame:
        """Get insider trading data."""
        self._rate_limit()
        try:
            ticker = yf.Ticker(symbol)
            insiders = ticker.insider_transactions

            if insiders is None or insiders.empty:
                return pd.DataFrame()

            return insiders
        except Exception as e:
            print(f"Error fetching insider trades for {symbol}: {e}")
            return pd.DataFrame()

    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """Get analyst recommendations."""
        self._rate_limit()
        try:
            ticker = yf.Ticker(symbol)
            recs = ticker.recommendations

            if recs is None or recs.empty:
                return pd.DataFrame()

            return recs
        except Exception as e:
            print(f"Error fetching recommendations for {symbol}: {e}")
            return pd.DataFrame()

    def batch_fetch_info(self, symbols: List[str],
                          progress_callback=None) -> Dict[str, Dict]:
        """
        Fetch info for multiple stocks.

        Args:
            symbols: List of ticker symbols
            progress_callback: Optional callback(current, total) for progress updates

        Returns:
            Dict mapping symbol to info dict
        """
        results = {}
        total = len(symbols)

        for i, symbol in enumerate(symbols):
            info = self.get_stock_info(symbol)
            if info:
                results[symbol] = info

            if progress_callback:
                progress_callback(i + 1, total)

        return results

    def calculate_metrics(self, symbol: str) -> Optional[Dict]:
        """
        Calculate all metrics for a stock needed for scanning.
        """
        info = self.get_stock_info(symbol)
        if not info:
            return None

        history = self.get_historical_data(symbol, years=1)
        if history is None or len(history) < 20:
            return None

        try:
            current_price = info['current_price']

            # Calculate price changes
            if len(history) >= 2:
                price_1d = ((current_price - history['close'].iloc[-2]) / history['close'].iloc[-2]) * 100
            else:
                price_1d = 0

            if len(history) >= 7:
                price_7d = ((current_price - history['close'].iloc[-7]) / history['close'].iloc[-7]) * 100
            else:
                price_7d = 0

            if len(history) >= 30:
                price_30d = ((current_price - history['close'].iloc[-30]) / history['close'].iloc[-30]) * 100
            else:
                price_30d = 0

            # Calculate 52-week metrics
            fifty_two_week_low = info.get('fifty_two_week_low')
            fifty_two_week_high = info.get('fifty_two_week_high')

            if fifty_two_week_low and fifty_two_week_low > 0:
                pct_from_52wk_low = ((current_price - fifty_two_week_low) / fifty_two_week_low) * 100
            else:
                pct_from_52wk_low = 0

            if fifty_two_week_high and fifty_two_week_high > 0:
                pct_from_52wk_high = ((current_price - fifty_two_week_high) / fifty_two_week_high) * 100
            else:
                pct_from_52wk_high = 0

            # Moving average calculations
            fifty_day_avg = info.get('fifty_day_avg')
            two_hundred_day_avg = info.get('two_hundred_day_avg')

            if fifty_day_avg and fifty_day_avg > 0:
                pct_above_50dma = ((current_price - fifty_day_avg) / fifty_day_avg) * 100
            else:
                pct_above_50dma = 0

            if two_hundred_day_avg and two_hundred_day_avg > 0:
                pct_above_200dma = ((current_price - two_hundred_day_avg) / two_hundred_day_avg) * 100
            else:
                pct_above_200dma = 0

            # Volume ratio
            volume = info.get('volume', 0)
            avg_volume = info.get('avg_volume', 1)
            volume_ratio = volume / avg_volume if avg_volume > 0 else 0

            # Consolidation range (last 30 days)
            if len(history) >= 30:
                last_30 = history.tail(30)
                range_30d = (last_30['high'].max() - last_30['low'].min()) / last_30['low'].min() if last_30['low'].min() > 0 else 0
            else:
                range_30d = 1  # Assume high volatility if not enough data

            # Days since 52-week low
            if fifty_two_week_low and len(history) > 0:
                # Find the date of the 52-week low
                low_date = history[history['low'] == history['low'].min()]['date'].iloc[0]
                # Handle timezone-aware dates from yfinance
                low_date_dt = pd.to_datetime(low_date)
                if low_date_dt.tzinfo is not None:
                    low_date_dt = low_date_dt.tz_localize(None)
                days_since_low = (datetime.now() - low_date_dt).days
            else:
                days_since_low = 365  # Default to a year

            return {
                'symbol': symbol.upper(),
                'current_price': current_price,
                'previous_close': info.get('previous_close'),
                'fifty_two_week_low': fifty_two_week_low,
                'fifty_two_week_high': fifty_two_week_high,
                'fifty_day_avg': fifty_day_avg,
                'two_hundred_day_avg': two_hundred_day_avg,
                'volume': volume,
                'avg_volume': avg_volume,
                'market_cap': info.get('market_cap'),
                'pct_from_52wk_low': pct_from_52wk_low,
                'pct_from_52wk_high': pct_from_52wk_high,
                'pct_above_50dma': pct_above_50dma,
                'pct_above_200dma': pct_above_200dma,
                'volume_ratio': volume_ratio,
                'price_change_1d': price_1d,
                'price_change_7d': price_7d,
                'price_change_30d': price_30d,
                'consolidation_range_30d': range_30d * 100,  # As percentage
                'days_since_52wk_low': days_since_low,
                'tier': None,  # Will be set by scanner
            }
        except Exception as e:
            print(f"Error calculating metrics for {symbol}: {e}")
            return None


# Singleton instance
data_fetcher = DataFetcher()
