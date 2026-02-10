"""
SQLite database operations for Convexity AI
"""
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd

from .config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Stock universe table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            industry TEXT,
            exchange TEXT,
            list_source TEXT,
            added_date DATE,
            is_active BOOLEAN DEFAULT 1,
            current_price REAL,
            market_cap REAL,
            last_updated TIMESTAMP
        )
    """)

    # Daily price cache
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_prices (
            symbol TEXT,
            date DATE,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    """)

    # Calculated metrics (refreshed daily)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_metrics (
            symbol TEXT PRIMARY KEY,
            current_price REAL,
            previous_close REAL,
            fifty_two_week_low REAL,
            fifty_two_week_high REAL,
            fifty_day_avg REAL,
            two_hundred_day_avg REAL,
            volume INTEGER,
            avg_volume INTEGER,
            market_cap REAL,
            pct_from_52wk_low REAL,
            pct_from_52wk_high REAL,
            pct_above_50dma REAL,
            pct_above_200dma REAL,
            volume_ratio REAL,
            price_change_1d REAL,
            price_change_7d REAL,
            price_change_30d REAL,
            consolidation_range_30d REAL,
            days_since_52wk_low INTEGER,
            tier INTEGER,
            last_updated TIMESTAMP
        )
    """)

    # Alert history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            alert_date DATE,
            tier INTEGER,
            price_at_alert REAL,
            pct_from_52wk_low REAL,
            volume_ratio REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User notes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Watchlist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            symbol TEXT PRIMARY KEY,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)

    # Scanner run history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scanner_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TIMESTAMP,
            stocks_scanned INTEGER,
            tier1_count INTEGER,
            tier2_count INTEGER,
            errors TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


# ============================================================================
# Stock Operations
# ============================================================================

def add_stock(symbol: str, name: str = None, sector: str = None,
              industry: str = None, exchange: str = None, list_source: str = None):
    """Add a stock to the universe."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO stocks (symbol, name, sector, industry, exchange, list_source, added_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (symbol.upper(), name, sector, industry, exchange, list_source, date.today()))
    conn.commit()
    conn.close()


def remove_stock(symbol: str):
    """Mark a stock as inactive."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE stocks SET is_active = 0 WHERE symbol = ?", (symbol.upper(),))
    conn.commit()
    conn.close()


def get_all_stocks() -> pd.DataFrame:
    """Get all active stocks."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM stocks WHERE is_active = 1", conn)
    conn.close()
    return df


def get_stock(symbol: str) -> Optional[Dict]:
    """Get a single stock by symbol."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stocks WHERE symbol = ?", (symbol.upper(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def load_stocks_from_csv(csv_path: Path, list_source: str):
    """Load stocks from a CSV file into the database."""
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    conn = get_connection()
    count = 0

    for _, row in df.iterrows():
        try:
            conn.execute("""
                INSERT OR REPLACE INTO stocks (symbol, name, sector, list_source, added_date, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (
                row['symbol'].upper(),
                row.get('name', ''),
                row.get('sector', ''),
                list_source,
                date.today()
            ))
            count += 1
        except Exception as e:
            print(f"Error loading {row.get('symbol', 'unknown')}: {e}")

    conn.commit()
    conn.close()
    print(f"Loaded {count} stocks from {csv_path}")
    return count


# ============================================================================
# Metrics Operations
# ============================================================================

def update_stock_metrics(metrics: Dict):
    """Update calculated metrics for a stock."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO stock_metrics (
            symbol, current_price, previous_close, fifty_two_week_low, fifty_two_week_high,
            fifty_day_avg, two_hundred_day_avg, volume, avg_volume, market_cap,
            pct_from_52wk_low, pct_from_52wk_high, pct_above_50dma, pct_above_200dma,
            volume_ratio, price_change_1d, price_change_7d, price_change_30d,
            consolidation_range_30d, days_since_52wk_low, tier, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        metrics['symbol'],
        metrics.get('current_price'),
        metrics.get('previous_close'),
        metrics.get('fifty_two_week_low'),
        metrics.get('fifty_two_week_high'),
        metrics.get('fifty_day_avg'),
        metrics.get('two_hundred_day_avg'),
        metrics.get('volume'),
        metrics.get('avg_volume'),
        metrics.get('market_cap'),
        metrics.get('pct_from_52wk_low'),
        metrics.get('pct_from_52wk_high'),
        metrics.get('pct_above_50dma'),
        metrics.get('pct_above_200dma'),
        metrics.get('volume_ratio'),
        metrics.get('price_change_1d'),
        metrics.get('price_change_7d'),
        metrics.get('price_change_30d'),
        metrics.get('consolidation_range_30d'),
        metrics.get('days_since_52wk_low'),
        metrics.get('tier'),
        datetime.now()
    ))

    conn.commit()
    conn.close()


def get_stock_metrics(symbol: str) -> Optional[Dict]:
    """Get metrics for a single stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock_metrics WHERE symbol = ?", (symbol.upper(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_metrics() -> pd.DataFrame:
    """Get all stock metrics."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM stock_metrics ORDER BY tier ASC, pct_from_52wk_low DESC", conn)
    conn.close()
    return df


def get_tier_alerts(tier: int) -> pd.DataFrame:
    """Get stocks in a specific tier."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM stock_metrics WHERE tier = ? ORDER BY pct_from_52wk_low DESC",
        conn,
        params=(tier,)
    )
    conn.close()
    return df


def get_top_performers(days: int = 1, limit: int = 10) -> pd.DataFrame:
    """Get top performing stocks over a time period."""
    conn = get_connection()

    if days == 1:
        order_col = "price_change_1d"
    elif days <= 7:
        order_col = "price_change_7d"
    else:
        order_col = "price_change_30d"

    df = pd.read_sql_query(
        f"SELECT * FROM stock_metrics WHERE {order_col} IS NOT NULL ORDER BY {order_col} DESC LIMIT ?",
        conn,
        params=(limit,)
    )
    conn.close()
    return df


def get_flat_stocks_breaking_out(limit: int = 40) -> pd.DataFrame:
    """
    Get stocks that were flat/down but are now showing upward momentum.

    Criteria:
    - Still relatively close to 52-week low (less than 30% above)
    - Showing positive recent momentum (7d or 30d change positive)
    - Had tight consolidation (low 30d range) OR were trending down
    """
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT * FROM stock_metrics
        WHERE
            pct_from_52wk_low IS NOT NULL
            AND pct_from_52wk_low < 30
            AND pct_from_52wk_low > 0
            AND (
                (price_change_7d > 3 AND price_change_30d > 0)
                OR (price_change_30d > 10 AND consolidation_range_30d < 25)
            )
        ORDER BY price_change_7d DESC
        LIMIT ?
        """,
        conn,
        params=(limit,)
    )
    conn.close()
    return df


def get_consolidating_stocks(limit: int = 40) -> pd.DataFrame:
    """
    Get stocks in tight consolidation (potential breakout candidates).

    Criteria:
    - Tight 30-day range (under 15%)
    - Near 52-week low (under 25% above)
    - Some recent positive movement
    """
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT * FROM stock_metrics
        WHERE
            consolidation_range_30d IS NOT NULL
            AND consolidation_range_30d < 15
            AND pct_from_52wk_low < 25
            AND pct_from_52wk_low > 0
            AND price_change_1d > -5
        ORDER BY consolidation_range_30d ASC
        LIMIT ?
        """,
        conn,
        params=(limit,)
    )
    conn.close()
    return df


# ============================================================================
# Alert History
# ============================================================================

def save_alert(symbol: str, tier: int, price: float, pct_from_low: float,
               volume_ratio: float, notes: str = None):
    """Save an alert to history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (symbol, alert_date, tier, price_at_alert, pct_from_52wk_low, volume_ratio, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (symbol.upper(), date.today(), tier, price, pct_from_low, volume_ratio, notes))
    conn.commit()
    conn.close()


def get_alert_history(symbol: str = None, days: int = 30) -> pd.DataFrame:
    """Get alert history, optionally filtered by symbol."""
    conn = get_connection()

    if symbol:
        df = pd.read_sql_query(
            """SELECT * FROM alerts WHERE symbol = ? AND alert_date >= date('now', ?)
               ORDER BY alert_date DESC""",
            conn,
            params=(symbol.upper(), f'-{days} days')
        )
    else:
        df = pd.read_sql_query(
            """SELECT * FROM alerts WHERE alert_date >= date('now', ?)
               ORDER BY alert_date DESC""",
            conn,
            params=(f'-{days} days',)
        )

    conn.close()
    return df


# ============================================================================
# User Notes & Watchlist
# ============================================================================

def add_user_note(symbol: str, note: str):
    """Add a user note for a stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_notes (symbol, note) VALUES (?, ?)",
        (symbol.upper(), note)
    )
    conn.commit()
    conn.close()


def get_user_notes(symbol: str) -> List[Dict]:
    """Get all notes for a stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM user_notes WHERE symbol = ? ORDER BY created_at DESC",
        (symbol.upper(),)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_to_watchlist(symbol: str, notes: str = None):
    """Add a stock to the watchlist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO watchlist (symbol, notes) VALUES (?, ?)",
        (symbol.upper(), notes)
    )
    conn.commit()
    conn.close()


def remove_from_watchlist(symbol: str):
    """Remove a stock from the watchlist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))
    conn.commit()
    conn.close()


def get_watchlist() -> pd.DataFrame:
    """Get all watchlist stocks."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM watchlist ORDER BY added_at DESC", conn)
    conn.close()
    return df


# ============================================================================
# Scanner Run Logging
# ============================================================================

def log_scanner_run(stocks_scanned: int, tier1_count: int, tier2_count: int, errors: str = None):
    """Log a scanner run."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scanner_runs (run_date, stocks_scanned, tier1_count, tier2_count, errors)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.now(), stocks_scanned, tier1_count, tier2_count, errors))
    conn.commit()
    conn.close()


# Initialize database on import
init_database()
