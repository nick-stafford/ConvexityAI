"""
AI Image Generation Service using Google Gemini (Nano Banana style)
Generates charts, infographics, and visual reports for stocks.
"""
import os
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional
import google.generativeai as genai

from ..utils.config import PROJECT_ROOT


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OUTPUT_DIR = PROJECT_ROOT / "data" / "generated_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ImageGenerator:
    """Generate AI images for stock analysis and reports."""

    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.enabled = True
        else:
            self.enabled = False
            print("Image generation disabled - no GEMINI_API_KEY set")

    def generate_stock_infographic(self, symbol: str, metrics: dict) -> Optional[str]:
        """
        Generate an infographic-style image for a stock.

        Returns path to generated image or None.
        """
        if not self.enabled:
            return None

        prompt = f"""Create a clean, professional stock analysis infographic for {symbol}:

        Key Metrics:
        - Current Price: ${metrics.get('current_price', 0):.2f}
        - Change from 52-week Low: {metrics.get('pct_from_52wk_low', 0):.1f}%
        - 7-Day Change: {metrics.get('price_change_7d', 0):.1f}%
        - 30-Day Change: {metrics.get('price_change_30d', 0):.1f}%
        - Volume Ratio: {metrics.get('volume_ratio', 0):.2f}x

        Style: Modern fintech design, dark theme with green/red accents for gains/losses.
        Include visual representations of the metrics (gauges, bars, arrows).
        Make it look like a professional trading dashboard widget.
        """

        try:
            response = self.model.generate_content(prompt)

            # Save if we got an image
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = base64.b64decode(part.inline_data.data)
                        filename = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        filepath = OUTPUT_DIR / filename

                        with open(filepath, 'wb') as f:
                            f.write(image_data)

                        return str(filepath)

            return None

        except Exception as e:
            print(f"Error generating image: {e}")
            return None

    def generate_sector_heatmap_image(self, sector_data: list) -> Optional[str]:
        """Generate a visual sector heatmap image."""
        if not self.enabled:
            return None

        sectors_text = "\n".join([
            f"- {s['sector']}: {s['avg_change']:.1f}% ({'green' if s['avg_change'] > 0 else 'red'})"
            for s in sector_data
        ])

        prompt = f"""Create a sector heatmap visualization for stock market:

        Sector Performance:
        {sectors_text}

        Style: Grid of boxes, each representing a sector.
        Color intensity based on performance (deep green = strong gains, deep red = strong losses).
        Include sector names and percentage changes.
        Modern, clean fintech design with dark background.
        """

        try:
            response = self.model.generate_content(prompt)

            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = base64.b64decode(part.inline_data.data)
                        filename = f"sector_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        filepath = OUTPUT_DIR / filename

                        with open(filepath, 'wb') as f:
                            f.write(image_data)

                        return str(filepath)

            return None

        except Exception as e:
            print(f"Error generating heatmap: {e}")
            return None

    def generate_alert_banner(self, symbol: str, tier: int, metrics: dict) -> Optional[str]:
        """Generate an eye-catching alert banner image."""
        if not self.enabled:
            return None

        tier_color = "emerald green" if tier == 1 else "golden yellow"
        tier_label = "TIER 1 - STRONG SIGNAL" if tier == 1 else "TIER 2 - WATCH LIST"

        prompt = f"""Create an alert banner for stock trading signal:

        Stock: {symbol}
        Alert: {tier_label}
        Price: ${metrics.get('current_price', 0):.2f}
        Gain from Low: +{metrics.get('pct_from_52wk_low', 0):.1f}%

        Style: Bold, attention-grabbing banner.
        Primary color: {tier_color}
        Include upward arrow icons.
        Dark background with glowing effects.
        Professional trading platform aesthetic.
        Dimensions: Wide banner format (3:1 ratio).
        """

        try:
            response = self.model.generate_content(prompt)

            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = base64.b64decode(part.inline_data.data)
                        filename = f"alert_{symbol}_tier{tier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        filepath = OUTPUT_DIR / filename

                        with open(filepath, 'wb') as f:
                            f.write(image_data)

                        return str(filepath)

            return None

        except Exception as e:
            print(f"Error generating alert banner: {e}")
            return None

    def generate_daily_report_cover(self, stats: dict) -> Optional[str]:
        """Generate a cover image for daily reports."""
        if not self.enabled:
            return None

        prompt = f"""Create a daily stock market report cover image:

        Title: "CONVEXITY AI - Daily Scan Report"
        Date: {datetime.now().strftime('%B %d, %Y')}

        Key Stats:
        - Tier 1 Alerts: {stats.get('tier1_count', 0)}
        - Tier 2 Alerts: {stats.get('tier2_count', 0)}
        - Stocks Scanned: {stats.get('total_stocks', 0)}

        Style: Professional report cover.
        Dark theme with subtle grid pattern background.
        Glowing accent lines in teal/cyan.
        Modern fintech aesthetic.
        Include abstract chart visualization elements.
        """

        try:
            response = self.model.generate_content(prompt)

            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = base64.b64decode(part.inline_data.data)
                        filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.png"
                        filepath = OUTPUT_DIR / filename

                        with open(filepath, 'wb') as f:
                            f.write(image_data)

                        return str(filepath)

            return None

        except Exception as e:
            print(f"Error generating report cover: {e}")
            return None


# Singleton
image_generator = ImageGenerator()
