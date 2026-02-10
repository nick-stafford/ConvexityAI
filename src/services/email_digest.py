"""
Email digest service - sends daily alert summaries
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from typing import List, Dict

from ..utils.config import (
    EMAIL_ENABLED, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT,
    EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_RECIPIENTS
)
from ..utils.database import get_tier_alerts, get_top_performers


class EmailDigest:
    """
    Sends daily digest emails with scan results.
    """

    def __init__(self):
        self.enabled = EMAIL_ENABLED
        self.smtp_server = EMAIL_SMTP_SERVER
        self.smtp_port = EMAIL_SMTP_PORT
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
        self.recipients = EMAIL_RECIPIENTS

    def _format_stock_table(self, stocks: List[Dict], columns: List[str]) -> str:
        """Format stocks as HTML table."""
        if not stocks:
            return "<p>No stocks found.</p>"

        html = "<table style='border-collapse: collapse; width: 100%;'>"

        # Header
        html += "<tr style='background-color: #1a1a2e; color: white;'>"
        for col in columns:
            html += f"<th style='padding: 8px; text-align: left;'>{col}</th>"
        html += "</tr>"

        # Rows
        for i, stock in enumerate(stocks):
            bg = "#f8f9fa" if i % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color: {bg};'>"

            for col in columns:
                key = col.lower().replace(' ', '_').replace('%', 'pct')
                value = stock.get(key, 'N/A')

                # Format numbers
                if isinstance(value, float):
                    if 'pct' in key or 'return' in key or 'change' in key:
                        value = f"{value:.1f}%"
                    elif 'price' in key:
                        value = f"${value:.2f}"
                    else:
                        value = f"{value:.2f}"
                elif isinstance(value, int) and value > 1000:
                    value = f"{value:,}"

                html += f"<td style='padding: 8px; border-bottom: 1px solid #ddd;'>{value}</td>"

            html += "</tr>"

        html += "</table>"
        return html

    def generate_digest_html(self) -> str:
        """Generate the HTML content for the daily digest."""
        tier1 = get_tier_alerts(1)
        tier2 = get_tier_alerts(2)
        top_1d = get_top_performers(days=1, limit=5)

        tier1_list = tier1.to_dict('records') if not tier1.empty else []
        tier2_list = tier2.to_dict('records') if not tier2.empty else []
        top_1d_list = top_1d.to_dict('records') if not top_1d.empty else []

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    padding: 20px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                }}
                h1 {{
                    color: #1a1a2e;
                    border-bottom: 2px solid #e94560;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #16213e;
                    margin-top: 30px;
                }}
                .tier1 {{
                    background-color: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 10px;
                    margin: 10px 0;
                }}
                .tier2 {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 10px 0;
                }}
                .summary {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Convexity AI Daily Digest</h1>
                <p><strong>Date:</strong> {date.today().strftime('%B %d, %Y')}</p>

                <div class="summary">
                    <strong>Today's Summary:</strong><br>
                    🟢 Tier 1 Alerts: {len(tier1_list)}<br>
                    🟡 Tier 2 Alerts: {len(tier2_list)}
                </div>

                <h2>🟢 Tier 1 - Strong Signals</h2>
                <div class="tier1">
                    {self._format_stock_table(
                        tier1_list[:10],
                        ['Symbol', 'Current_Price', 'Pct_From_52wk_Low', 'Volume_Ratio', 'Price_Change_1d']
                    )}
                </div>

                <h2>🟡 Tier 2 - Watch List</h2>
                <div class="tier2">
                    {self._format_stock_table(
                        tier2_list[:10],
                        ['Symbol', 'Current_Price', 'Pct_From_52wk_Low', 'Volume_Ratio', 'Price_Change_1d']
                    )}
                </div>

                <h2>🔥 Top Movers Today</h2>
                {self._format_stock_table(
                    top_1d_list,
                    ['Symbol', 'Current_Price', 'Price_Change_1d', 'Volume_Ratio']
                )}

                <div class="footer">
                    <p>This digest was generated by Convexity AI at {datetime.now().strftime('%H:%M:%S')}</p>
                    <p>⚠️ This is not financial advice. Always do your own research.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def send_digest(self) -> bool:
        """
        Send the daily digest email.

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            print("Email digest is disabled")
            return False

        if not self.email_address or not self.email_password:
            print("Email credentials not configured")
            return False

        if not self.recipients:
            print("No email recipients configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Convexity AI Digest - {date.today().strftime('%B %d, %Y')}"
            msg['From'] = self.email_address
            msg['To'] = ', '.join(self.recipients)

            # Generate content
            html_content = self.generate_digest_html()
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, self.recipients, msg.as_string())

            print(f"Digest sent to {len(self.recipients)} recipients")
            return True

        except Exception as e:
            print(f"Error sending digest: {e}")
            return False

    def send_alert_notification(self, symbol: str, tier: int, metrics: Dict) -> bool:
        """
        Send an immediate notification for a new Tier 1 alert.
        """
        if not self.enabled or not self.recipients:
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Tier {tier} Alert: {symbol}"
            msg['From'] = self.email_address
            msg['To'] = ', '.join(self.recipients)

            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>{'🟢' if tier == 1 else '🟡'} Tier {tier} Alert: {symbol}</h2>
                <table style="border-collapse: collapse;">
                    <tr><td><strong>Price:</strong></td><td>${metrics.get('current_price', 0):.2f}</td></tr>
                    <tr><td><strong>% From 52wk Low:</strong></td><td>{metrics.get('pct_from_52wk_low', 0):.1f}%</td></tr>
                    <tr><td><strong>Volume Ratio:</strong></td><td>{metrics.get('volume_ratio', 0):.2f}x</td></tr>
                    <tr><td><strong>30d Range:</strong></td><td>{metrics.get('consolidation_range_30d', 0):.1f}%</td></tr>
                    <tr><td><strong>Days Since Low:</strong></td><td>{metrics.get('days_since_52wk_low', 0)}</td></tr>
                </table>
                <p style="margin-top: 20px; color: #666; font-size: 12px;">
                    Generated by Convexity AI at {datetime.now().strftime('%H:%M:%S')}
                </p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, self.recipients, msg.as_string())

            return True

        except Exception as e:
            print(f"Error sending alert notification: {e}")
            return False


# Singleton instance
email_digest = EmailDigest()
