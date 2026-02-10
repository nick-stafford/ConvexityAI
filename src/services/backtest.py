"""
Backtesting service - tests alert strategies against historical data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .data_fetcher import data_fetcher
from ..utils.database import get_alert_history


@dataclass
class TradeResult:
    """Result of a single simulated trade."""
    symbol: str
    entry_date: datetime
    entry_price: float
    exit_date: datetime
    exit_price: float
    return_pct: float
    holding_days: int
    exit_reason: str  # 'target', 'stop_loss', 'time_exit'


@dataclass
class BacktestResult:
    """Overall backtest results."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_return: float
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    avg_holding_days: float
    trades: List[TradeResult]


class Backtester:
    """
    Backtest tier alerts against historical price data.
    """

    def __init__(self):
        self.default_target = 0.20  # 20% profit target
        self.default_stop = -0.10   # 10% stop loss
        self.max_holding_days = 30  # Max days to hold

    def backtest_alert(
        self,
        symbol: str,
        entry_date: datetime,
        entry_price: float,
        target_pct: float = None,
        stop_loss_pct: float = None,
        max_days: int = None
    ) -> Optional[TradeResult]:
        """
        Backtest a single alert by simulating the trade forward.

        Args:
            symbol: Stock ticker
            entry_date: Date alert was triggered
            entry_price: Price at alert
            target_pct: Profit target (default 20%)
            stop_loss_pct: Stop loss (default -10%)
            max_days: Max holding period (default 30)

        Returns:
            TradeResult or None if insufficient data
        """
        target = target_pct or self.default_target
        stop = stop_loss_pct or self.default_stop
        max_hold = max_days or self.max_holding_days

        # Get historical data
        history = data_fetcher.get_historical_data(symbol, years=1)
        if history is None or history.empty:
            return None

        # Filter to dates after entry
        history['date'] = pd.to_datetime(history['date'])
        future_prices = history[history['date'] > entry_date].copy()

        if future_prices.empty:
            return None

        # Simulate trade
        target_price = entry_price * (1 + target)
        stop_price = entry_price * (1 + stop)

        for i, row in future_prices.iterrows():
            days_held = (row['date'] - entry_date).days

            # Check for stop loss hit (using low price)
            if row['low'] <= stop_price:
                return TradeResult(
                    symbol=symbol,
                    entry_date=entry_date,
                    entry_price=entry_price,
                    exit_date=row['date'],
                    exit_price=stop_price,
                    return_pct=stop,
                    holding_days=days_held,
                    exit_reason='stop_loss'
                )

            # Check for target hit (using high price)
            if row['high'] >= target_price:
                return TradeResult(
                    symbol=symbol,
                    entry_date=entry_date,
                    entry_price=entry_price,
                    exit_date=row['date'],
                    exit_price=target_price,
                    return_pct=target,
                    holding_days=days_held,
                    exit_reason='target'
                )

            # Check for time exit
            if days_held >= max_hold:
                exit_price = row['close']
                return_pct = (exit_price - entry_price) / entry_price
                return TradeResult(
                    symbol=symbol,
                    entry_date=entry_date,
                    entry_price=entry_price,
                    exit_date=row['date'],
                    exit_price=exit_price,
                    return_pct=return_pct,
                    holding_days=days_held,
                    exit_reason='time_exit'
                )

        # If we get here, use the last available price
        last_row = future_prices.iloc[-1]
        exit_price = last_row['close']
        return_pct = (exit_price - entry_price) / entry_price

        return TradeResult(
            symbol=symbol,
            entry_date=entry_date,
            entry_price=entry_price,
            exit_date=last_row['date'],
            exit_price=exit_price,
            return_pct=return_pct,
            holding_days=(last_row['date'] - entry_date).days,
            exit_reason='time_exit'
        )

    def backtest_tier_alerts(
        self,
        tier: int,
        days_back: int = 90,
        target_pct: float = None,
        stop_loss_pct: float = None
    ) -> BacktestResult:
        """
        Backtest all alerts of a specific tier from the past N days.

        Args:
            tier: Alert tier (1 or 2)
            days_back: How many days of alerts to test
            target_pct: Profit target percentage
            stop_loss_pct: Stop loss percentage

        Returns:
            BacktestResult with aggregate statistics
        """
        alerts = get_alert_history(days=days_back)

        if alerts.empty:
            return BacktestResult(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                avg_return=0,
                total_return=0,
                max_drawdown=0,
                sharpe_ratio=0,
                avg_holding_days=0,
                trades=[]
            )

        # Filter by tier
        tier_alerts = alerts[alerts['tier'] == tier]
        trades = []

        for _, alert in tier_alerts.iterrows():
            result = self.backtest_alert(
                symbol=alert['symbol'],
                entry_date=pd.to_datetime(alert['alert_date']),
                entry_price=alert['price_at_alert'],
                target_pct=target_pct,
                stop_loss_pct=stop_loss_pct
            )
            if result:
                trades.append(result)

        if not trades:
            return BacktestResult(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                avg_return=0,
                total_return=0,
                max_drawdown=0,
                sharpe_ratio=0,
                avg_holding_days=0,
                trades=[]
            )

        # Calculate statistics
        returns = [t.return_pct for t in trades]
        winning = [r for r in returns if r > 0]
        losing = [r for r in returns if r <= 0]

        # Calculate max drawdown
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = running_max - cumulative
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

        # Calculate Sharpe ratio (simplified)
        if len(returns) > 1:
            sharpe = np.mean(returns) / (np.std(returns) + 0.0001) * np.sqrt(252 / 30)
        else:
            sharpe = 0

        return BacktestResult(
            total_trades=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=len(winning) / len(trades) if trades else 0,
            avg_return=np.mean(returns) if returns else 0,
            total_return=np.sum(returns) if returns else 0,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            avg_holding_days=np.mean([t.holding_days for t in trades]),
            trades=trades
        )

    def optimize_parameters(
        self,
        tier: int,
        days_back: int = 180
    ) -> Dict:
        """
        Test different target/stop combinations to find optimal parameters.

        Returns best parameters and results.
        """
        targets = [0.10, 0.15, 0.20, 0.25, 0.30]
        stops = [-0.05, -0.07, -0.10, -0.15, -0.20]

        best_result = None
        best_params = None
        all_results = []

        for target in targets:
            for stop in stops:
                result = self.backtest_tier_alerts(
                    tier=tier,
                    days_back=days_back,
                    target_pct=target,
                    stop_loss_pct=stop
                )

                param_result = {
                    'target': target,
                    'stop': stop,
                    'win_rate': result.win_rate,
                    'avg_return': result.avg_return,
                    'total_return': result.total_return,
                    'sharpe': result.sharpe_ratio,
                    'trades': result.total_trades
                }
                all_results.append(param_result)

                # Optimize for risk-adjusted returns (Sharpe)
                if best_result is None or result.sharpe_ratio > best_result.sharpe_ratio:
                    best_result = result
                    best_params = {'target': target, 'stop': stop}

        return {
            'best_params': best_params,
            'best_result': best_result,
            'all_results': all_results
        }

    def get_performance_by_sector(
        self,
        tier: int,
        days_back: int = 90
    ) -> Dict[str, Dict]:
        """
        Break down backtest performance by sector.
        """
        from ..utils.database import get_stock

        alerts = get_alert_history(days=days_back)
        if alerts.empty:
            return {}

        tier_alerts = alerts[alerts['tier'] == tier]
        sector_results = {}

        for _, alert in tier_alerts.iterrows():
            stock = get_stock(alert['symbol'])
            sector = stock.get('sector', 'Unknown') if stock else 'Unknown'

            result = self.backtest_alert(
                symbol=alert['symbol'],
                entry_date=pd.to_datetime(alert['alert_date']),
                entry_price=alert['price_at_alert']
            )

            if result:
                if sector not in sector_results:
                    sector_results[sector] = []
                sector_results[sector].append(result.return_pct)

        # Aggregate by sector
        summary = {}
        for sector, returns in sector_results.items():
            summary[sector] = {
                'trades': len(returns),
                'win_rate': len([r for r in returns if r > 0]) / len(returns),
                'avg_return': np.mean(returns),
                'total_return': np.sum(returns)
            }

        return summary


# Singleton instance
backtester = Backtester()
