# Convexity AI - Architecture Document

> Personal penny stock scanner with AI-powered research capabilities.
> Built for finding high-convexity opportunities in energy, materials, tech, biotech, and emerging sectors.

---

## Table of Contents
1. [Overview](#overview)
2. [Design Decisions](#design-decisions)
3. [Tech Stack](#tech-stack)
4. [Data Architecture](#data-architecture)
5. [Feature Specifications](#feature-specifications)
6. [UI Structure](#ui-structure)
7. [File Structure](#file-structure)

---

## Overview

**Convexity AI** is a penny stock screening and research platform that:
- Monitors 850+ stocks across energy, materials, tech, biotech, defense, and emerging sectors
- Detects momentum signals (Tier 1 = strong, Tier 2 = watch)
- Provides AI-powered deep research via Groq (Llama 3 70B)
- Stores research in a searchable knowledge base (LanceDB)
- Runs daily EOD scans at 5:00 PM ET

### Why "Convexity"?
The name reflects the investment thesis: finding asymmetric bets where downside is limited but upside potential is massive (high convexity).

---

## Design Decisions

### Stock Universe
| List | Count | Description |
|------|-------|-------------|
| Nick's List | 349 | Personal watchlist from Yahoo Finance |
| 500 New Stocks | 500 | Curated list following sector criteria |
| **Total** | ~850 | Combined scanning universe |

### Penny Stock Definition
- **Price Range:** $0.10 - $5.00
- **Min Market Cap:** $5M
- **Manual Override:** Can add any stock at any price

### Sector Distribution (500 New Stocks)
| Category | % | Count |
|----------|---|-------|
| Materials/Mining | 30% | 150 |
| Energy (Nuclear, Solar) | 15% | 75 |
| Tech - AI/Software | 15% | 75 |
| Tech - Semiconductors | 10% | 50 |
| Biotech | 10% | 50 |
| Defense/Space/Drones | 10% | 50 |
| Quantum/Cyber/Robotics | 10% | 50 |

### Alert Tiers

**Tier 1 (Strong Signal):**
- Price up 20%+ from 52-week low
- 52-week low was 30+ days ago
- Price above 20-day MA
- Volume > 1.5x average
- Prior 30 days had tight range (<20% spread)

**Tier 2 (Watch Signal):**
- Price up 10-20% from 52-week low
- Price above 20-day MA
- Volume elevated

### Data Refresh Strategy
- **Schedule:** Daily at 5:00 PM ET (after market close)
- **Method:** Windows Task Scheduler
- **Caching:** Tiered lazy loading

#### Cache Tiers
| Tier | Data | When Loaded |
|------|------|-------------|
| 1 | Basic price/volume for all stocks | App startup |
| 2 | Full 5-year history | For alert stocks only |
| 3 | News, SEC filings, research | On-demand |

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **UI** | Streamlit | Dashboard and interface |
| **Charts** | Plotly | Interactive line charts |
| **Stock Data** | yfinance | Price, volume, fundamentals |
| **AI (Primary)** | Groq API (Llama 3 70B) | Research and analysis |
| **AI (Backup)** | Ollama (local) | Offline capability |
| **Vector DB** | LanceDB | Knowledge base, semantic search |
| **Structured DB** | SQLite | Stock metadata, alert history |
| **Embeddings** | Sentence-Transformers | Embed research for search |

### Python Dependencies
- streamlit
- plotly
- yfinance
- pandas
- numpy
- lancedb
- sentence-transformers
- groq
- python-dotenv
- schedule
- requests
- beautifulsoup4

---

## Data Architecture

### SQLite Tables

```sql
-- Stock universe
CREATE TABLE stocks (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    industry TEXT,
    exchange TEXT,
    list_source TEXT,  -- 'nicks_list' or '500_new'
    added_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Daily price cache
CREATE TABLE daily_prices (
    symbol TEXT,
    date DATE,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    PRIMARY KEY (symbol, date)
);

-- Alert history
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    alert_date DATE,
    tier INTEGER,  -- 1 or 2
    price_at_alert REAL,
    pct_from_52wk_low REAL,
    volume_ratio REAL,
    notes TEXT
);

-- User notes
CREATE TABLE user_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### LanceDB Collections

```python
# Knowledge base schema
{
    "id": str,           # unique ID
    "symbol": str,       # stock ticker
    "content": str,      # research text
    "source": str,       # 'groq_research', 'news', 'sec_filing', 'user_note'
    "created_at": str,   # ISO timestamp
    "embedding": list    # 384-dim vector from sentence-transformers
}
```

---

## Feature Specifications

### Core Scanner
- [x] Load stock universe (Nick's List + 500 New)
- [x] Fetch EOD data via yfinance
- [x] Calculate signals (52wk low %, MAs, volume ratio)
- [x] Classify into Tier 1 / Tier 2
- [x] Store alert history

### Dashboard
- [x] Top performers (24H, 1W, 1M)
- [x] Tier 1 alerts summary
- [x] Tier 2 alerts summary
- [x] Industry heatmap

### Stock Detail View
Expandable sections when clicking a stock:
- [x] Price chart (line, with MA overlays)
- [x] News feed
- [x] Groq research (deep dive)
- [x] Sentiment analysis
- [x] Insider trading
- [x] SEC filings
- [x] Compare to similar stocks
- [x] Backtest this signal
- [x] My notes

### Knowledge Base
- [x] Save all research to LanceDB
- [x] Semantic search across research
- [x] Browse by stock or date
- [x] Never lose insights

### Comparison Tool
- [x] Side-by-side compare 2-3 stocks
- [x] Same industry peers
- [x] Key metrics table

### Backtesting
- [x] Test Tier 1/2 signals historically (5 years)
- [x] Calculate win rate
- [x] Average return at 30/60/90 days

### Email Digest (Optional)
- [ ] Daily email with Tier 1 alerts
- [ ] Configurable recipient list
- [ ] Gmail SMTP integration

---

## UI Structure

### Tabs
| Tab | Purpose |
|-----|---------|
| Dashboard | Top performers, alerts summary, heatmap |
| Tier 1 Alerts | Strong signals with expandable details |
| Tier 2 Alerts | Watch signals |
| Full Scanner | All 850 stocks, sortable table |
| Research | Groq deep dive + knowledge base |
| My Knowledge Base | Browse/search saved research |
| Watchlist | Manually tracked stocks |
| Settings | Add/remove stocks, configure alerts |

### Stock Detail Expandable Sections
```
┌─────────────────────────────────────────────────────────────┐
│  UUUU - Energy Fuels                              $4.82     │
├─────────────────────────────────────────────────────────────┤
│  📈 Chart                                          [−]      │
│  📰 News                                           [+]      │
│  🔬 Groq Research                                  [+]      │
│  📊 Sentiment Analysis                             [+]      │
│  👔 Insider Trading                                [+]      │
│  📄 SEC Filings                                    [+]      │
│  ⚖️ Compare to Similar Stocks                      [+]      │
│  🧪 Backtest This Signal                           [+]      │
│  📝 My Notes                                       [+]      │
└─────────────────────────────────────────────────────────────┘
```

### Chart Specifications
- **Type:** Line chart (default)
- **Time toggles:** 24H, 1W, 1M, 3M, 6M, 1Y, 5Y
- **Overlays:** 20 DMA, 50 DMA, 200 DMA
- **Volume:** Bar chart below price

---

## File Structure

```
ConvexityAI/
├── .env                     # API keys (not in git)
├── .gitignore
├── ARCHITECTURE.md          # This file
├── README.md
├── requirements.txt
├── app.py                   # Streamlit entry point
│
├── src/
│   ├── __init__.py
│   │
│   ├── components/          # UI components
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── stock_detail.py
│   │   ├── charts.py
│   │   ├── alerts_table.py
│   │   └── heatmap.py
│   │
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── scanner.py       # Core scanning logic
│   │   ├── data_fetcher.py  # yfinance wrapper
│   │   ├── ai_research.py   # Groq integration
│   │   ├── sentiment.py     # Reddit, StockTwits, news
│   │   ├── insider.py       # Insider trading data
│   │   ├── sec_filings.py   # SEC EDGAR integration
│   │   ├── backtest.py      # Historical signal testing
│   │   └── email_digest.py  # Email notifications
│   │
│   └── utils/               # Helpers
│       ├── __init__.py
│       ├── database.py      # SQLite operations
│       ├── knowledge_base.py # LanceDB operations
│       ├── cache.py         # Caching logic
│       └── config.py        # Load .env settings
│
├── data/
│   ├── stocks_nicks_list.csv
│   ├── stocks_500_new.csv
│   ├── cache/               # Cached price data
│   └── knowledge_base/      # LanceDB files
│
└── docs/
    ├── decisions.md         # Why we made each choice
    └── api_reference.md     # Internal API docs
```

---

## Future Enhancements (Not in V1)
- Mobile deployment
- Portfolio tracking (actual positions, P&L)
- PDF report generation
- Multi-user support
- Options flow integration

---

*Document created: March 2026*
*Last updated: March 2026*
