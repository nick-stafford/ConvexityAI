"""
AI-powered stock research using Groq API with persistent memory
"""
import json
from typing import Dict, Optional, List
from datetime import datetime
from groq import Groq

from ..utils.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS
from .data_fetcher import data_fetcher
from .ai_memory import ai_memory


class AIResearcher:
    """
    AI-powered deep research on stocks using Groq's Llama 3 70B model.
    Now with persistent memory for better context across sessions.
    """

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.model = GROQ_MODEL
        self.memory = ai_memory

    def _call_groq(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Make a call to Groq API."""
        if not self.client:
            return "Error: Groq API key not configured"

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.3,  # Lower for more factual responses
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Groq API: {e}"

    def get_company_overview(self, symbol: str, save_to_memory: bool = True) -> str:
        """
        Generate a comprehensive company overview.
        Includes previous research from memory for context.
        """
        info = data_fetcher.get_stock_info(symbol)
        if not info:
            return f"Could not fetch data for {symbol}"

        # Get previous research from memory
        previous_research = self.memory.get_all_stock_insights(symbol)

        system_prompt = """You are a professional equity research analyst specializing in
        small-cap and penny stocks. Provide concise, factual analysis focused on:
        - Business model and revenue drivers
        - Operating leverage potential
        - Key risks and catalysts
        - Industry positioning
        Keep responses clear and actionable for traders.
        If previous research is provided, build upon it rather than repeating."""

        prompt = f"""Analyze {symbol} ({info.get('name', 'Unknown')}).

Company Info:
- Sector: {info.get('sector', 'N/A')}
- Industry: {info.get('industry', 'N/A')}
- Market Cap: ${info.get('market_cap', 0):,.0f}
- Current Price: ${info.get('current_price', 0):.2f}
- 52-Week Range: ${info.get('fifty_two_week_low', 0):.2f} - ${info.get('fifty_two_week_high', 0):.2f}
- 50-Day MA: ${info.get('fifty_day_avg', 0):.2f}
- Volume: {info.get('volume', 0):,} (Avg: {info.get('avg_volume', 0):,})

{previous_research if 'No previous research' not in previous_research else ''}

Provide a brief overview covering:
1. What does this company do? (2-3 sentences)
2. Operating leverage potential - can revenue scale without proportional cost increases?
3. Key catalysts that could move the stock
4. Major risks to watch
5. Technical setup assessment based on the price data above"""

        result = self._call_groq(prompt, system_prompt)

        # Save to memory for future sessions
        if save_to_memory and result and "Error" not in result:
            self.memory.remember_stock_insight(
                symbol=symbol,
                memory_type="overview",
                content=result[:500],  # Store summary
                confidence=0.8,
                source="AI Research"
            )

        return result

    def analyze_momentum_signal(self, metrics: Dict) -> str:
        """
        Analyze why a stock triggered an alert and assess the quality of the signal.
        """
        system_prompt = """You are a technical analyst specializing in momentum breakouts
        in small-cap stocks. Evaluate signals objectively and highlight both bullish and
        bearish factors. Be direct and concise."""

        prompt = f"""Analyze this momentum signal for {metrics.get('symbol', 'Unknown')}:

Current Metrics:
- Price: ${metrics.get('current_price', 0):.2f}
- % From 52-Week Low: {metrics.get('pct_from_52wk_low', 0):.1f}%
- % From 52-Week High: {metrics.get('pct_from_52wk_high', 0):.1f}%
- Days Since 52-Week Low: {metrics.get('days_since_52wk_low', 0)}
- Above 50-Day MA: {metrics.get('pct_above_50dma', 0):.1f}%
- Above 200-Day MA: {metrics.get('pct_above_200dma', 0):.1f}%
- Volume Ratio (vs avg): {metrics.get('volume_ratio', 0):.2f}x
- 30-Day Consolidation Range: {metrics.get('consolidation_range_30d', 0):.1f}%
- 1-Day Change: {metrics.get('price_change_1d', 0):.1f}%
- 7-Day Change: {metrics.get('price_change_7d', 0):.1f}%
- 30-Day Change: {metrics.get('price_change_30d', 0):.1f}%
- Alert Tier: {metrics.get('tier', 'N/A')}

Assess:
1. Signal quality (Strong/Moderate/Weak) and why
2. Is this a genuine breakout or potential false signal?
3. Key levels to watch (support/resistance)
4. Risk/reward assessment
5. Recommended action (Buy/Watch/Avoid) with reasoning"""

        return self._call_groq(prompt, system_prompt)

    def analyze_news_sentiment(self, symbol: str) -> str:
        """
        Fetch recent news and analyze sentiment.
        """
        news = data_fetcher.get_news(symbol, limit=5)
        if not news:
            return f"No recent news found for {symbol}"

        news_text = "\n".join([
            f"- {item['title']} ({item['publisher']}, {item['published'].strftime('%Y-%m-%d')})"
            for item in news
        ])

        system_prompt = """You are a sentiment analyst. Evaluate news objectively and
        identify potential market-moving information. Be concise."""

        prompt = f"""Analyze recent news for {symbol}:

{news_text}

Provide:
1. Overall sentiment (Bullish/Neutral/Bearish)
2. Key themes in recent coverage
3. Any potential catalysts or concerns
4. How this might affect near-term price action"""

        return self._call_groq(prompt, system_prompt)

    def get_sector_analysis(self, sector: str, stocks: List[Dict]) -> str:
        """
        Analyze a sector based on the stocks in the watchlist.
        """
        if not stocks:
            return f"No stocks found in {sector} sector"

        stocks_summary = "\n".join([
            f"- {s['symbol']}: ${s.get('current_price', 0):.2f}, "
            f"{s.get('pct_from_52wk_low', 0):.1f}% from low, "
            f"Tier {s.get('tier', 'N/A')}"
            for s in stocks[:20]  # Limit to top 20
        ])

        system_prompt = """You are a sector analyst specializing in small-cap equities.
        Focus on operating leverage, industry trends, and relative strength."""

        prompt = f"""Analyze the {sector} sector based on these stocks:

{stocks_summary}

Provide:
1. Sector health assessment
2. Common themes or patterns
3. Which stocks stand out and why
4. Sector-specific catalysts to watch
5. Recommended allocation (Overweight/Neutral/Underweight)"""

        return self._call_groq(prompt, system_prompt)

    def generate_trade_thesis(self, symbol: str, metrics: Dict) -> str:
        """
        Generate a complete trade thesis for a stock.
        """
        info = data_fetcher.get_stock_info(symbol)
        news = data_fetcher.get_news(symbol, limit=3)

        news_text = "\n".join([f"- {n['title']}" for n in news]) if news else "No recent news"

        system_prompt = """You are a professional trader writing a trade thesis.
        Be specific about entry, targets, and stop-loss levels. Focus on risk management."""

        prompt = f"""Generate a trade thesis for {symbol}:

Company: {info.get('name', 'Unknown') if info else 'Unknown'}
Sector: {info.get('sector', 'N/A') if info else 'N/A'}
Industry: {info.get('industry', 'N/A') if info else 'N/A'}

Current Metrics:
- Price: ${metrics.get('current_price', 0):.2f}
- 52-Week Low: ${metrics.get('fifty_two_week_low', 0):.2f}
- 52-Week High: ${metrics.get('fifty_two_week_high', 0):.2f}
- % From Low: {metrics.get('pct_from_52wk_low', 0):.1f}%
- Volume Ratio: {metrics.get('volume_ratio', 0):.2f}x
- Market Cap: ${metrics.get('market_cap', 0):,.0f}

Recent News:
{news_text}

Provide a complete trade thesis:
1. THESIS: One sentence summary of the trade
2. ENTRY: Specific entry point or zone
3. TARGETS: Price targets (T1, T2, T3) with reasoning
4. STOP-LOSS: Where to exit if wrong
5. POSITION SIZE: Suggested % of portfolio given the risk
6. TIMEFRAME: Expected holding period
7. CATALYSTS: What could move the stock
8. RISKS: What could go wrong"""

        return self._call_groq(prompt, system_prompt)

    def compare_stocks(self, symbols: List[str]) -> str:
        """
        Compare multiple stocks for relative strength analysis.
        """
        stocks_data = []
        for symbol in symbols[:5]:  # Limit to 5 stocks
            metrics = data_fetcher.calculate_metrics(symbol)
            if metrics:
                stocks_data.append(metrics)

        if not stocks_data:
            return "Could not fetch data for comparison"

        comparison = "\n".join([
            f"{s['symbol']}: ${s['current_price']:.2f}, "
            f"{s['pct_from_52wk_low']:.1f}% from low, "
            f"Vol ratio: {s['volume_ratio']:.2f}x, "
            f"30d: {s['price_change_30d']:.1f}%"
            for s in stocks_data
        ])

        system_prompt = """You are comparing stocks for relative strength.
        Identify the strongest setup and explain why."""

        prompt = f"""Compare these stocks:

{comparison}

Provide:
1. Rank them from strongest to weakest setup
2. What makes the #1 pick stand out?
3. Any stocks to avoid and why
4. Correlation considerations"""

        return self._call_groq(prompt, system_prompt)

    def answer_question(self, question: str, context: Dict = None) -> str:
        """
        Answer a free-form question about a stock or the market.
        """
        system_prompt = """You are a knowledgeable stock analyst assistant.
        Answer questions clearly and provide actionable insights when possible.
        If you don't have enough information, say so."""

        context_str = ""
        if context:
            context_str = f"\nContext provided:\n{json.dumps(context, indent=2, default=str)}"

        prompt = f"""Question: {question}{context_str}

Provide a clear, helpful answer."""

        return self._call_groq(prompt, system_prompt)


# Singleton instance
ai_researcher = AIResearcher()
