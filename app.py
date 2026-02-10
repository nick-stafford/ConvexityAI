"""
Convexity AI - Stock Scanner & Research Platform
Main Streamlit Application
"""
import streamlit as st
from datetime import datetime

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Convexity AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components
from src.components.dashboard import render_dashboard, run_scanner_with_progress
from src.components.stock_detail import render_stock_detail
from src.components.heatmap import render_heatmap_page
from src.components.alerts_table import render_watchlist
from src.components.charts import create_backtest_equity_curve
from src.components.sector_rotation import render_sector_rotation_page
from src.components.spline_3d import (
    render_spline_scene, render_3d_header, render_3d_sector_globe,
    render_spline_showcase, render_3d_cube_with_text, DEMO_SCENES
)
from src.components.advanced_visuals import (
    render_particle_background, render_aurora_background,
    render_floating_blobs, render_wave_divider, render_animated_counter,
    render_neumorphic_card, render_skeleton_loader, render_glowing_border_card,
    render_morphing_shape, render_typing_text
)

# Import services
from src.services.scanner import scanner
from src.services.ai_research import ai_researcher
from src.services.backtest import backtester
from src.services.data_fetcher import data_fetcher
from src.services.earnings import get_upcoming_earnings, get_recent_earnings
from src.services.insider import get_insider_buying, format_insider_data

# Import database functions
from src.utils.database import (
    get_watchlist, remove_from_watchlist, add_stock,
    get_all_stocks, get_tier_alerts
)


# Initialize session state
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'


def set_selected_stock(symbol: str):
    """Set the selected stock and navigate to detail page."""
    st.session_state.selected_stock = symbol
    st.session_state.current_page = 'Stock Detail'


# Theme state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Custom CSS with enhanced visuals - Professional & Sleek
def get_custom_css(dark_mode=True):
    if dark_mode:
        bg_primary = "#0a0a0f"
        bg_secondary = "#12121a"
        bg_card = "rgba(26, 26, 46, 0.7)"
        text_primary = "#ffffff"
        text_secondary = "#a0a0a0"
        accent_green = "#26a69a"
        accent_blue = "#42a5f5"
        accent_purple = "#ab47bc"
        accent_red = "#ef5350"
        accent_gold = "#ffc107"
        border_color = "rgba(255, 255, 255, 0.1)"
        glass_bg = "rgba(255, 255, 255, 0.05)"
    else:
        bg_primary = "#f5f7fa"
        bg_secondary = "#ffffff"
        bg_card = "rgba(255, 255, 255, 0.9)"
        text_primary = "#1a1a2e"
        text_secondary = "#666"
        accent_green = "#28a745"
        accent_blue = "#2196f3"
        accent_purple = "#9c27b0"
        accent_red = "#dc3545"
        accent_gold = "#ffc107"
        border_color = "rgba(0, 0, 0, 0.1)"
        glass_bg = "rgba(255, 255, 255, 0.8)"

    return f"""
    <style>
    /* Import premium fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Root variables */
    :root {{
        --accent-gradient: linear-gradient(135deg, {accent_green} 0%, {accent_blue} 50%, {accent_purple} 100%);
        --glass-bg: {glass_bg};
        --border-glow: 0 0 20px rgba(38, 166, 154, 0.3);
    }}

    /* Global typography */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* Main layout with subtle animated gradient background */
    .main {{
        padding: 1rem;
        background: {bg_primary};
    }}

    /* Glassmorphism card base */
    .glass-card {{
        background: {glass_bg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {border_color};
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }}

    /* Enhanced metric cards with glassmorphism */
    .stMetric {{
        background: {glass_bg} !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 24px !important;
        border-radius: 16px !important;
        border: 1px solid {border_color} !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .stMetric::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--accent-gradient);
    }}
    .stMetric:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(38, 166, 154, 0.2), var(--border-glow);
        border-color: rgba(38, 166, 154, 0.3) !important;
    }}

    /* Tier 1 card styling - Premium */
    .tier1-card {{
        background: linear-gradient(135deg, rgba(38, 166, 154, 0.15) 0%, rgba(38, 166, 154, 0.05) 100%);
        border: 1px solid rgba(38, 166, 154, 0.3);
        border-left: 4px solid {accent_green};
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(38, 166, 154, 0.1);
        transition: all 0.3s ease;
    }}
    .tier1-card:hover {{
        box-shadow: 0 8px 30px rgba(38, 166, 154, 0.2);
        border-color: rgba(38, 166, 154, 0.5);
    }}

    /* Tier 2 card styling - Premium */
    .tier2-card {{
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 193, 7, 0.05) 100%);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-left: 4px solid {accent_gold};
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(255, 193, 7, 0.1);
        transition: all 0.3s ease;
    }}

    /* Tab styling - Modern */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: {glass_bg};
        backdrop-filter: blur(20px);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid {border_color};
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(38, 166, 154, 0.1);
        border-color: rgba(38, 166, 154, 0.3);
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {accent_green} 0%, {accent_blue} 100%) !important;
        box-shadow: 0 4px 15px rgba(38, 166, 154, 0.4);
    }}

    /* Sidebar styling - Premium */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0a0a12 0%, #12121a 50%, #0a0a12 100%);
        border-right: 1px solid {border_color};
    }}
    section[data-testid="stSidebar"] > div {{
        padding-top: 2rem;
    }}

    /* Button styling - Premium */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid {border_color};
        backdrop-filter: blur(10px);
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(38, 166, 154, 0.3);
    }}

    /* Primary button - Gradient */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {accent_green} 0%, {accent_blue} 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(38, 166, 154, 0.3);
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {accent_blue} 0%, {accent_purple} 100%);
        box-shadow: 0 8px 25px rgba(66, 165, 245, 0.4);
    }}

    /* Data tables - Sleek */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {border_color};
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }}

    /* Progress bar animation - Smooth gradient */
    .stProgress > div > div {{
        background: linear-gradient(90deg, {accent_green}, {accent_blue}, {accent_purple}, {accent_green});
        background-size: 300% 100%;
        animation: shimmer 2s infinite linear;
        border-radius: 10px;
    }}
    @keyframes shimmer {{
        0% {{ background-position: -300% 0; }}
        100% {{ background-position: 300% 0; }}
    }}

    /* Animated scanning indicator */
    .scanning-indicator {{
        display: inline-block;
        animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.7; transform: scale(1.1); }}
    }}

    /* Stock cards - Premium glassmorphism */
    .stock-card {{
        background: {glass_bg};
        backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
        border: 1px solid {border_color};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .stock-card::after {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s ease;
    }}
    .stock-card:hover {{
        border-color: rgba(38, 166, 154, 0.5);
        box-shadow: 0 8px 30px rgba(38, 166, 154, 0.15);
        transform: translateX(4px);
    }}
    .stock-card:hover::after {{
        left: 100%;
    }}

    /* Positive/Negative indicators with glow */
    .positive {{
        color: {accent_green};
        font-weight: 600;
        text-shadow: 0 0 10px rgba(38, 166, 154, 0.5);
    }}
    .negative {{
        color: {accent_red};
        font-weight: 600;
        text-shadow: 0 0 10px rgba(239, 83, 80, 0.5);
    }}

    /* Section headers - Elegant */
    .section-header {{
        background: linear-gradient(90deg, {glass_bg}, transparent);
        padding: 14px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 3px solid transparent;
        border-image: var(--accent-gradient) 1;
        backdrop-filter: blur(10px);
    }}

    /* Inputs - Modern */
    .stTextInput > div > div > input {{
        background: {glass_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {accent_green} !important;
        box-shadow: 0 0 20px rgba(38, 166, 154, 0.2) !important;
    }}

    /* Select boxes - Modern */
    .stSelectbox > div > div {{
        background: {glass_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
    }}

    /* Scrollbar styling - Sleek */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {accent_green}, {accent_blue});
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, {accent_blue}, {accent_purple});
    }}

    /* Dividers - Subtle gradient */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, {border_color}, transparent);
        margin: 24px 0;
    }}

    /* Expander - Modern */
    .streamlit-expanderHeader {{
        background: {glass_bg};
        border-radius: 10px;
        border: 1px solid {border_color};
    }}

    /* Alert boxes - Sleek */
    .stAlert {{
        background: {glass_bg};
        backdrop-filter: blur(20px);
        border-radius: 12px;
        border: 1px solid {border_color};
    }}

    /* Chat messages - Premium */
    .stChatMessage {{
        background: {glass_bg} !important;
        backdrop-filter: blur(20px);
        border-radius: 16px !important;
        border: 1px solid {border_color} !important;
        padding: 16px !important;
    }}

    /* Floating action indicator */
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}

    /* Glow effect for important elements */
    .glow {{
        animation: glow 2s infinite alternate;
    }}
    @keyframes glow {{
        from {{ box-shadow: 0 0 10px rgba(38, 166, 154, 0.3); }}
        to {{ box-shadow: 0 0 20px rgba(38, 166, 154, 0.6), 0 0 30px rgba(66, 165, 245, 0.4); }}
    }}

    /* Animated background gradient (subtle) */
    .animated-bg {{
        background: linear-gradient(-45deg, #0a0a12, #12121a, #0d1520, #0a0a12);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }}
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    </style>
    """

st.markdown(get_custom_css(st.session_state.dark_mode), unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 📈 Convexity AI")
    with col2:
        if st.button("🌙" if st.session_state.dark_mode else "☀️", key="theme_toggle", help="Toggle dark/light mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.markdown("*Momentum Stock Scanner*")

    st.divider()

    # Navigation
    nav_options = ['Dashboard', 'Sector Rotation', 'Earnings', 'Heatmap', 'Visual FX', 'Watchlist', 'Backtest', 'Add Stock', 'AI Chat']
    page = st.radio(
        "Navigation",
        options=nav_options,
        index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0,
        key='nav_radio'
    )

    # Update current page from radio
    if page != st.session_state.current_page and st.session_state.current_page != 'Stock Detail':
        st.session_state.current_page = page

    st.divider()

    # Quick stock lookup
    st.markdown("### 🔍 Quick Lookup")
    lookup_symbol = st.text_input("Enter symbol:", placeholder="e.g., AAPL")
    if st.button("View Stock", use_container_width=True):
        if lookup_symbol:
            set_selected_stock(lookup_symbol.upper())
            st.rerun()

    st.divider()

    # Selected stock indicator
    if st.session_state.selected_stock:
        st.markdown(f"**Selected:** {st.session_state.selected_stock}")
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.selected_stock = None
            st.session_state.current_page = 'Dashboard'
            st.rerun()

    st.divider()

    # Stats
    all_stocks = get_all_stocks()
    tier1 = get_tier_alerts(1)
    tier2 = get_tier_alerts(2)

    st.markdown("### 📊 Quick Stats")
    st.markdown(f"**Stocks in Universe:** {len(all_stocks)}")
    st.markdown(f"**Tier 1 Alerts:** {len(tier1)}")
    st.markdown(f"**Tier 2 Alerts:** {len(tier2)}")


# Main content area
if st.session_state.current_page == 'Stock Detail' and st.session_state.selected_stock:
    render_stock_detail(st.session_state.selected_stock)

elif st.session_state.current_page == 'Dashboard':
    render_dashboard(on_stock_select=set_selected_stock)

elif st.session_state.current_page == 'Sector Rotation':
    render_sector_rotation_page(on_stock_select=set_selected_stock)

elif st.session_state.current_page == 'Earnings':
    st.markdown("# 📅 Earnings Calendar")

    tab1, tab2 = st.tabs(["📅 Upcoming Earnings", "📊 Recent Earnings"])

    with tab1:
        st.markdown("### Stocks Reporting Soon")
        days_ahead = st.slider("Days ahead", 7, 30, 14)

        if st.button("🔄 Refresh Earnings Data", key="refresh_earnings"):
            st.cache_data.clear()

        with st.spinner("Fetching earnings dates..."):
            upcoming = get_upcoming_earnings(days=days_ahead)

        if upcoming:
            st.success(f"Found {len(upcoming)} stocks with upcoming earnings")

            for earning in upcoming:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                with col1:
                    st.markdown(f"**{earning['symbol']}**")
                with col2:
                    st.markdown(f"📅 {earning['earnings_date']}")
                with col3:
                    days = earning['days_until']
                    if days <= 3:
                        st.markdown(f"🔴 **{days} days**")
                    elif days <= 7:
                        st.markdown(f"🟡 {days} days")
                    else:
                        st.markdown(f"🟢 {days} days")
                with col4:
                    if st.button("→", key=f"earn_{earning['symbol']}"):
                        set_selected_stock(earning['symbol'])
                        st.rerun()
        else:
            st.info("No upcoming earnings found in the selected timeframe.")

    with tab2:
        st.markdown("### Recently Reported")
        days_back = st.slider("Days back", 7, 30, 14, key="days_back")

        with st.spinner("Fetching recent earnings..."):
            recent = get_recent_earnings(days=days_back)

        if recent:
            for earning in recent:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1])

                with col1:
                    st.markdown(f"**{earning['symbol']}**")
                with col2:
                    st.markdown(f"📅 {earning['earnings_date']}")
                with col3:
                    st.markdown(f"{earning['days_ago']}d ago")
                with col4:
                    surprise = earning.get('surprise')
                    if surprise:
                        color = "#26a69a" if surprise > 0 else "#ef5350"
                        st.markdown(f"<span style='color:{color}'>Surprise: {surprise:.1f}%</span>", unsafe_allow_html=True)
                with col5:
                    if st.button("→", key=f"recent_{earning['symbol']}"):
                        set_selected_stock(earning['symbol'])
                        st.rerun()
        else:
            st.info("No recent earnings found.")

elif st.session_state.current_page == 'Heatmap':
    render_heatmap_page(on_stock_select=set_selected_stock)

elif st.session_state.current_page == 'Visual FX':
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="
                font-size: 2.5rem;
                background: linear-gradient(135deg, #26a69a 0%, #42a5f5 50%, #ab47bc 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">Visual Effects Studio</h1>
            <p style="color: #888; margin-top: 10px;">Advanced 3D visuals & animations for your dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    # Visual effect selector
    effect_tabs = st.tabs([
        "🎯 Branded Cube",
        "✨ Particles",
        "🌌 Aurora",
        "🫧 Floating Blobs",
        "📊 Counters",
        "🎨 Neumorphism",
        "✨ Glow Cards",
        "🌐 Spline 3D"
    ])

    with effect_tabs[0]:
        st.markdown("### Signature Branded 3D Cube")
        st.markdown("The Convexity AI logo cube with smooth rotation and branding on all faces.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            render_3d_cube_with_text(height=220)

    with effect_tabs[1]:
        st.markdown("### Interactive Particle Network")
        st.markdown("Mouse-reactive particles that connect and follow your cursor.")
        render_particle_background(particle_count=60, height=400, key="particle_demo")

    with effect_tabs[2]:
        st.markdown("### Aurora Northern Lights")
        st.markdown("Flowing gradient aurora effect with twinkling stars.")
        render_aurora_background(height=350, key="aurora_demo")

    with effect_tabs[3]:
        st.markdown("### Floating Gradient Blobs")
        st.markdown("Abstract morphing blob shapes with smooth animations.")
        render_floating_blobs(height=350, key="blobs_demo")

    with effect_tabs[4]:
        st.markdown("### Animated Number Counters")
        st.markdown("Numbers that count up with smooth easing animation.")
        col1, col2, col3 = st.columns(3)
        with col1:
            render_animated_counter(value=313, prefix="", suffix=" Stocks", decimals=0, key="counter1")
        with col2:
            render_animated_counter(value=24.7, prefix="+", suffix="%", decimals=1, color="#42a5f5", key="counter2")
        with col3:
            render_animated_counter(value=1250000, prefix="$", suffix="", decimals=0, color="#ab47bc", key="counter3")

    with effect_tabs[5]:
        st.markdown("### Neumorphic (Soft UI) Cards")
        st.markdown("Soft 3D effect with realistic shadows and depth.")
        col1, col2, col3 = st.columns(3)
        with col1:
            render_neumorphic_card(
                "<h2 style='color:#26a69a;margin:0;'>Tier 1</h2><p style='color:#888;'>Strong Signals</p>",
                height=120, key="neu1"
            )
        with col2:
            render_neumorphic_card(
                "<h2 style='color:#ffc107;margin:0;'>Tier 2</h2><p style='color:#888;'>Watch List</p>",
                height=120, key="neu2"
            )
        with col3:
            render_neumorphic_card(
                "<h2 style='color:#42a5f5;margin:0;'>313</h2><p style='color:#888;'>Total Stocks</p>",
                height=120, key="neu3"
            )

    with effect_tabs[6]:
        st.markdown("### Animated Glowing Border Cards")
        st.markdown("Cards with rotating gradient glow effect.")
        col1, col2 = st.columns(2)
        with col1:
            render_glowing_border_card(
                "Tier 1 Alert",
                "Strong momentum signal detected. Stock showing signs of breakout with volume confirmation.",
                height=150, key="glow1"
            )
        with col2:
            render_glowing_border_card(
                "Market Insight",
                "AI analysis suggests bullish sentiment across energy sector with potential rotation incoming.",
                height=150, key="glow2"
            )

        st.markdown("### Morphing Shape")
        render_morphing_shape(height=180, key="morph_demo")

    with effect_tabs[7]:
        render_spline_showcase()
        st.divider()
        st.markdown("## 🎮 Interactive 3D Elements")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🌐 3D Globe")
            render_3d_sector_globe(height=350)
        with col2:
            st.markdown("### ✨ Abstract")
            try:
                render_spline_scene(DEMO_SCENES['abstract'], height=350, key="studio_abstract")
            except:
                st.info("3D scene loading...")

    st.divider()

    # Wave divider demo
    st.markdown("### 🌊 Wave Dividers")
    st.markdown("Animated liquid wave section separators.")
    render_wave_divider()

    st.divider()

    st.markdown("""
    ### 💡 How to Use These Effects

    All these effects can be added to any page in your app:

    ```python
    from src.components.advanced_visuals import render_particle_background
    render_particle_background(particle_count=50, height=400)
    ```

    **Available Effects:**
    - `render_particle_background()` - Interactive particle network
    - `render_aurora_background()` - Northern lights effect
    - `render_floating_blobs()` - Morphing gradient blobs
    - `render_wave_divider()` - Animated wave separator
    - `render_animated_counter()` - Counting numbers
    - `render_neumorphic_card()` - Soft UI cards
    - `render_glowing_border_card()` - Rotating glow borders
    - `render_morphing_shape()` - SVG shape morphing
    """)

elif st.session_state.current_page == 'Watchlist':
    st.markdown("# 👁️ Watchlist")

    watchlist = get_watchlist()

    if watchlist.empty:
        st.info("Your watchlist is empty. Add stocks from the scanner or use the lookup feature.")
    else:
        for _, row in watchlist.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"### {row['symbol']}")
                if row.get('notes'):
                    st.caption(row['notes'])

            with col2:
                if st.button("View", key=f"view_{row['symbol']}"):
                    set_selected_stock(row['symbol'])
                    st.rerun()

            with col3:
                if st.button("Remove", key=f"remove_{row['symbol']}"):
                    remove_from_watchlist(row['symbol'])
                    st.rerun()

            st.divider()

elif st.session_state.current_page == 'Backtest':
    st.markdown("# 📈 Backtest Results")

    col1, col2 = st.columns(2)

    with col1:
        tier = st.selectbox("Alert Tier", options=[1, 2])
    with col2:
        days_back = st.slider("Days of history", 30, 365, 90)

    if st.button("Run Backtest", type="primary"):
        with st.spinner("Running backtest..."):
            result = backtester.backtest_tier_alerts(tier=tier, days_back=days_back)

            if result.total_trades == 0:
                st.warning("No trades found for this period. Run more scans to build alert history.")
            else:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Trades", result.total_trades)
                with col2:
                    st.metric("Win Rate", f"{result.win_rate:.1%}")
                with col3:
                    st.metric("Avg Return", f"{result.avg_return:.1%}")
                with col4:
                    st.metric("Total Return", f"{result.total_return:.1%}")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Max Drawdown", f"{result.max_drawdown:.1%}")
                with col2:
                    st.metric("Sharpe Ratio", f"{result.sharpe_ratio:.2f}")

                # Equity curve
                st.markdown("### Equity Curve")
                fig = create_backtest_equity_curve(result.trades)
                st.plotly_chart(fig, use_container_width=True)

                # Trade list
                st.markdown("### Trade Details")
                trade_data = [{
                    'Symbol': t.symbol,
                    'Entry Date': t.entry_date.strftime('%Y-%m-%d'),
                    'Entry Price': f"${t.entry_price:.2f}",
                    'Exit Date': t.exit_date.strftime('%Y-%m-%d'),
                    'Exit Price': f"${t.exit_price:.2f}",
                    'Return': f"{t.return_pct:.1%}",
                    'Days Held': t.holding_days,
                    'Exit Reason': t.exit_reason
                } for t in result.trades]

                st.dataframe(trade_data, use_container_width=True)

elif st.session_state.current_page == 'Add Stock':
    st.markdown("# ➕ Add Stock to Universe")

    col1, col2 = st.columns(2)

    with col1:
        new_symbol = st.text_input("Stock Symbol:", placeholder="e.g., AAPL")
        new_name = st.text_input("Company Name (optional):")
        new_sector = st.selectbox(
            "Sector:",
            options=[
                "Energy", "Materials", "Technology", "Healthcare",
                "Industrials", "Financials", "Consumer Discretionary",
                "Consumer Staples", "Utilities", "Real Estate", "Communication Services",
                "Other"
            ]
        )

    with col2:
        st.markdown("### Current Universe")
        stocks = get_all_stocks()
        if not stocks.empty:
            st.dataframe(
                stocks[['symbol', 'sector']].head(20),
                use_container_width=True,
                hide_index=True
            )
            st.caption(f"Showing 20 of {len(stocks)} stocks")

    if st.button("Add Stock", type="primary"):
        if new_symbol:
            # Verify the stock exists
            with st.spinner(f"Verifying {new_symbol.upper()}..."):
                info = data_fetcher.get_stock_info(new_symbol)

            if info:
                add_stock(
                    symbol=new_symbol.upper(),
                    name=new_name or info.get('name', ''),
                    sector=new_sector,
                    list_source='manual'
                )
                st.success(f"Added {new_symbol.upper()} to universe!")
            else:
                st.error(f"Could not find stock {new_symbol}. Please verify the symbol.")
        else:
            st.warning("Please enter a stock symbol.")

elif st.session_state.current_page == 'AI Chat':
    st.markdown("# 🤖 AI Research Assistant")

    st.markdown("""
    Ask questions about stocks, markets, or get research assistance.
    The AI has access to all your scanner data and can analyze stocks on demand.
    """)

    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about a stock or the market..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Check if asking about a specific stock
                words = prompt.upper().split()
                potential_symbols = [w for w in words if len(w) <= 5 and w.isalpha()]

                context = {}
                for symbol in potential_symbols[:3]:  # Check up to 3 potential symbols
                    metrics = data_fetcher.calculate_metrics(symbol)
                    if metrics:
                        context[symbol] = metrics

                response = ai_researcher.answer_question(prompt, context if context else None)
                st.markdown(response)

                # Add to history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


# Footer - Professional
st.divider()
st.markdown("""
    <div style="
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(180deg, transparent 0%, rgba(26, 26, 46, 0.3) 100%);
        border-radius: 16px;
        margin-top: 20px;
    ">
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #26a69a 0%, #42a5f5 50%, #ab47bc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 10px;
        ">CONVEXITY AI</div>
        <div style="color: #666; font-size: 12px; margin-top: 8px;">
            v1.0 • Built with Streamlit, Groq & yfinance
        </div>
        <div style="
            color: #888;
            font-size: 11px;
            margin-top: 12px;
            padding: 8px 16px;
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.2);
            border-radius: 20px;
            display: inline-block;
        ">
            ⚠️ Not financial advice • Always do your own research
        </div>
    </div>
""", unsafe_allow_html=True)
