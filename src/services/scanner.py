"""
Core stock scanner - detects momentum signals and classifies into tiers
"""
from typing import List, Tuple, Optional
from datetime import datetime
import pandas as pd

from ..utils.config import (
    PENNY_STOCK_MAX_PRICE, PENNY_STOCK_MIN_PRICE, MIN_MARKET_CAP,
    TIER1_PCT_FROM_52WK_LOW, TIER2_PCT_FROM_52WK_LOW,
    TIER1_VOLUME_RATIO, TIER1_CONSOLIDATION_RANGE, TIER1_MIN_DAYS_FROM_LOW,
    NICKS_LIST_PATH, NEW_STOCKS_PATH
)
from ..utils.database import (
    get_all_stocks, load_stocks_from_csv, update_stock_metrics,
    save_alert, log_scanner_run, get_stock
)
from .data_fetcher import data_fetcher


class Scanner:
    """
    Stock scanner that detects momentum signals.

    Tier 1 (Strong Signal):
    - Price up 20%+ from 52-week low
    - 52-week low was 30+ days ago
    - Price above 20-day MA (approximated by 50-day for simplicity)
    - Volume > 1.5x average
    - Prior 30 days had tight range (<20% spread)

    Tier 2 (Watch Signal):
    - Price up 10-20% from 52-week low
    - Price above 20-day MA
    - Volume elevated
    """

    def __init__(self):
        self.errors = []

    def load_stock_universe(self) -> int:
        """Load stocks from CSV files into database."""
        count = 0

        # Load Nick's list
        if NICKS_LIST_PATH.exists():
            count += load_stocks_from_csv(NICKS_LIST_PATH, 'nicks_list')

        # Load 500 new stocks (if available)
        if NEW_STOCKS_PATH.exists():
            count += load_stocks_from_csv(NEW_STOCKS_PATH, '500_new')

        return count

    def classify_tier(self, metrics: dict) -> Optional[int]:
        """
        Classify a stock into Tier 1, Tier 2, or None.

        Args:
            metrics: Dict with calculated metrics

        Returns:
            1 for Tier 1, 2 for Tier 2, None for no alert
        """
        if not metrics:
            return None

        pct_from_low = metrics.get('pct_from_52wk_low', 0)
        volume_ratio = metrics.get('volume_ratio', 0)
        consolidation_range = metrics.get('consolidation_range_30d', 100)
        days_since_low = metrics.get('days_since_52wk_low', 0)
        pct_above_50dma = metrics.get('pct_above_50dma', 0)
        current_price = metrics.get('current_price', 0)
        market_cap = metrics.get('market_cap', 0)

        # Filter out stocks that don't meet basic criteria
        # Skip price filter for all stocks in Nick's universe - they're hand-picked
        # Only filter out extremely low market cap stocks
        if market_cap and market_cap < MIN_MARKET_CAP:
            return None

        # Tier 1: Strong breakout signal
        tier1_conditions = [
            pct_from_low >= TIER1_PCT_FROM_52WK_LOW * 100,  # Up 20%+ from 52wk low
            days_since_low >= TIER1_MIN_DAYS_FROM_LOW,      # Low was 30+ days ago
            pct_above_50dma > 0,                             # Above 50-day MA
            volume_ratio >= TIER1_VOLUME_RATIO,              # Volume 1.5x+ normal
            consolidation_range <= TIER1_CONSOLIDATION_RANGE * 100,  # Tight range before
        ]

        if all(tier1_conditions):
            return 1

        # Tier 2: Emerging signal
        tier2_conditions = [
            pct_from_low >= TIER2_PCT_FROM_52WK_LOW * 100,  # Up 10%+ from 52wk low
            pct_from_low < TIER1_PCT_FROM_52WK_LOW * 100,   # But not yet 20%
            pct_above_50dma > 0,                             # Above 50-day MA
        ]

        if all(tier2_conditions):
            return 2

        return None

    def scan_stock(self, symbol: str) -> Optional[dict]:
        """
        Scan a single stock and return its metrics with tier classification.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with metrics and tier, or None if error
        """
        try:
            metrics = data_fetcher.calculate_metrics(symbol)
            if not metrics:
                self.errors.append(f"No data for {symbol}")
                return None

            tier = self.classify_tier(metrics)
            metrics['tier'] = tier

            # Save to database
            update_stock_metrics(metrics)

            # Save alert if Tier 1 or 2
            if tier in [1, 2]:
                save_alert(
                    symbol=symbol,
                    tier=tier,
                    price=metrics.get('current_price', 0),
                    pct_from_low=metrics.get('pct_from_52wk_low', 0),
                    volume_ratio=metrics.get('volume_ratio', 0)
                )

            return metrics
        except Exception as e:
            self.errors.append(f"Error scanning {symbol}: {e}")
            return None

    def run_full_scan(self, progress_callback=None) -> Tuple[List[dict], List[dict]]:
        """
        Run a full scan of all stocks in the universe.

        Args:
            progress_callback: Optional callback(current, total, symbol) for progress

        Returns:
            Tuple of (tier1_stocks, tier2_stocks)
        """
        self.errors = []
        stocks = get_all_stocks()

        if stocks.empty:
            # Try loading from CSVs first
            self.load_stock_universe()
            stocks = get_all_stocks()

        if stocks.empty:
            print("No stocks in universe. Please add stocks first.")
            return [], []

        symbols = stocks['symbol'].tolist()
        total = len(symbols)

        tier1 = []
        tier2 = []

        print(f"Scanning {total} stocks...")

        for i, symbol in enumerate(symbols):
            metrics = self.scan_stock(symbol)

            if metrics:
                if metrics.get('tier') == 1:
                    tier1.append(metrics)
                elif metrics.get('tier') == 2:
                    tier2.append(metrics)

            if progress_callback:
                progress_callback(i + 1, total, symbol)

        # Log the run
        log_scanner_run(
            stocks_scanned=total,
            tier1_count=len(tier1),
            tier2_count=len(tier2),
            errors="; ".join(self.errors[:10]) if self.errors else None
        )

        print(f"Scan complete: {len(tier1)} Tier 1, {len(tier2)} Tier 2, {len(self.errors)} errors")

        return tier1, tier2

    def scan_single(self, symbol: str) -> Optional[dict]:
        """Quick scan of a single stock."""
        return self.scan_stock(symbol)

    def get_scan_summary(self) -> dict:
        """Get summary of latest scan results."""
        from ..utils.database import get_tier_alerts, get_top_performers

        tier1 = get_tier_alerts(1)
        tier2 = get_tier_alerts(2)
        top_24h = get_top_performers(days=1, limit=10)
        top_7d = get_top_performers(days=7, limit=10)
        top_30d = get_top_performers(days=30, limit=10)

        return {
            'tier1_count': len(tier1),
            'tier2_count': len(tier2),
            'tier1': tier1.to_dict('records') if not tier1.empty else [],
            'tier2': tier2.to_dict('records') if not tier2.empty else [],
            'top_24h': top_24h.to_dict('records') if not top_24h.empty else [],
            'top_7d': top_7d.to_dict('records') if not top_7d.empty else [],
            'top_30d': top_30d.to_dict('records') if not top_30d.empty else [],
        }


# Singleton instance
scanner = Scanner()
