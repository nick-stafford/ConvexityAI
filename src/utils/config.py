"""
Configuration management - loads settings from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Find project root and load .env
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Email Configuration
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECIPIENTS = [e.strip() for e in os.getenv("EMAIL_RECIPIENTS", "").split(",") if e.strip()]

# Scanner Settings
SCANNER_SCHEDULE_TIME = os.getenv("SCANNER_SCHEDULE_TIME", "17:00")
SCANNER_TIMEZONE = os.getenv("SCANNER_TIMEZONE", "US/Eastern")

# Data Paths
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
NICKS_LIST_PATH = DATA_DIR / "stocks_nicks_list.csv"
NEW_STOCKS_PATH = DATA_DIR / "stocks_500_new.csv"

# Database
DB_PATH = DATA_DIR / "convexity.db"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Scanner Parameters
PENNY_STOCK_MAX_PRICE = 5.00
PENNY_STOCK_MIN_PRICE = 0.10
MIN_MARKET_CAP = 5_000_000  # $5M
MIN_AVG_VOLUME = 50_000

# Alert Thresholds
TIER1_PCT_FROM_52WK_LOW = 0.20  # 20%
TIER2_PCT_FROM_52WK_LOW = 0.10  # 10%
TIER1_VOLUME_RATIO = 1.5
TIER1_CONSOLIDATION_RANGE = 0.20  # 20% max range in prior 30 days
TIER1_MIN_DAYS_FROM_LOW = 30

# Historical Data
HISTORY_YEARS = 5

# Groq Settings
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 4096
