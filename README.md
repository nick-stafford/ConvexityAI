# ConvexityAI

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-00D4AA?style=flat)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**AI-powered stock momentum scanner with intelligent research capabilities.**

ConvexityAI identifies high-convexity opportunities—stocks with limited downside but massive upside potential—using technical signals, AI-driven research, and real-time market data.

![Dashboard Preview](docs/screenshots/dashboard.png)

---

## Features

### Core Scanner
- **Tier 1/2 Alert System** — Classifies stocks by signal strength based on 52-week positioning, volume, and momentum
- **850+ Stock Universe** — Covers energy, materials, tech, biotech, defense, and emerging sectors
- **Real-time Scanning** — Daily EOD analysis with configurable refresh

### AI Research
- **Deep Dive Analysis** — Powered by Groq's Llama 3.3 70B for instant company research
- **Sentiment Analysis** — Aggregates news, social, and market sentiment
- **Knowledge Base** — Vector search over all past research (LanceDB)

### Visualization
- **Interactive Charts** — 5Y price history with MA overlays (Plotly)
- **Sector Heatmap** — Visual breakdown of performance by industry
- **Sector Rotation Dashboard** — Track momentum across sectors

### Additional Tools
- **Backtesting Engine** — Test signal performance over historical data
- **Earnings Calendar** — Upcoming and recent earnings events
- **Insider Activity** — Track insider buying/selling signals
- **Watchlist & Notes** — Personal tracking with annotations

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Charts** | Plotly |
| **Market Data** | yfinance |
| **AI Engine** | Groq API (Llama 3.3 70B) |
| **Vector DB** | LanceDB |
| **Database** | SQLite |
| **Embeddings** | Sentence-Transformers |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Groq API key ([free tier available](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/nickstafford/convexityai.git
cd convexityai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Run

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## Alert Tiers

### Tier 1 (Strong Signal)
- Price up **20%+** from 52-week low
- 52-week low was **30+ days** ago
- Price **above 20-day MA**
- Volume **>1.5x** average
- Prior 30 days had **tight range** (<20% spread)

### Tier 2 (Watch Signal)
- Price up **10-20%** from 52-week low
- Price above 20-day MA
- Elevated volume

---

## Project Structure

```
ConvexityAI/
├── app.py                 # Streamlit entry point
├── src/
│   ├── components/        # UI components
│   │   ├── dashboard.py
│   │   ├── stock_detail.py
│   │   ├── charts.py
│   │   └── heatmap.py
│   ├── services/          # Business logic
│   │   ├── scanner.py     # Core scanning engine
│   │   ├── ai_research.py # Groq integration
│   │   ├── backtest.py    # Historical testing
│   │   └── data_fetcher.py
│   └── utils/
│       ├── database.py    # SQLite operations
│       └── knowledge_base.py
├── data/
│   └── stocks_*.csv       # Stock universe
└── docs/
    └── ARCHITECTURE.md    # Detailed architecture
```

---

## Screenshots

| Dashboard | Stock Detail | AI Research |
|-----------|--------------|-------------|
| ![Dashboard](docs/screenshots/dashboard-thumb.png) | ![Detail](docs/screenshots/detail-thumb.png) | ![Research](docs/screenshots/research-thumb.png) |

---

## Roadmap

- [ ] Email digest for Tier 1 alerts
- [ ] Mobile-responsive layout
- [ ] Options flow integration
- [ ] Portfolio tracking with P&L

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built by <a href="https://nickstafford.dev">Nick Stafford</a>
</p>
