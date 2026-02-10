"""
Spline 3D Integration Component
Embeds interactive 3D scenes from Spline.design into the Streamlit app.
"""
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional


# Default Spline scenes (replace with your own from spline.design)
DEFAULT_SCENES = {
    # These are placeholder URLs - replace with your actual Spline scene URLs
    'logo': 'https://my.spline.design/untitled-0c4c0e6b8c5a4c5a8c5a4c5a8c5a4c5a/',
    'globe': 'https://my.spline.design/untitled-globe-placeholder/',
    'chart_bg': 'https://my.spline.design/untitled-chart-bg/',
    'alert_animation': 'https://my.spline.design/untitled-alert/',
}

# Free public Spline scenes for demo (these actually work!)
DEMO_SCENES = {
    'cube': 'https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode',
    'abstract': 'https://prod.spline.design/aHEZBPNTKcwpLRl6/scene.splinecode',
    'globe': 'https://prod.spline.design/PgmHbETs5rQxNf3v/scene.splinecode',
}


def render_spline_scene(
    scene_url: str,
    height: int = 400,
    width: str = "100%",
    key: str = None
):
    """
    Render a Spline 3D scene.

    Args:
        scene_url: URL to the Spline scene (from spline.design export)
        height: Height in pixels
        width: Width (can be pixels or percentage)
        key: Unique key for the component
    """
    # Spline viewer embed code
    spline_html = f"""
    <div style="width: {width}; height: {height}px; border-radius: 12px; overflow: hidden;">
        <script type="module" src="https://unpkg.com/@splinetool/viewer@1.0.54/build/spline-viewer.js"></script>
        <spline-viewer url="{scene_url}" style="width: 100%; height: 100%;"></spline-viewer>
    </div>
    """

    components.html(spline_html, height=height + 20, key=key)


def render_spline_iframe(
    scene_url: str,
    height: int = 400,
    key: str = None
):
    """
    Render a Spline scene using iframe (alternative method).

    Args:
        scene_url: URL to the Spline scene
        height: Height in pixels
        key: Unique key for the component
    """
    # Convert scene URL to embed URL if needed
    if 'spline.design' in scene_url and '/scene.splinecode' not in scene_url:
        embed_url = scene_url.replace('my.spline.design', 'app.spline.design')
    else:
        embed_url = scene_url

    st.components.v1.iframe(embed_url, height=height, scrolling=False)


def render_3d_cube_with_text(height: int = 140, text: str = "CONVEXITY AI"):
    """
    Render an animated 3D cube with text overlay.
    """
    cube_html = f"""
    <div class="cube-container" style="
        position: relative;
        width: 100%;
        height: {height}px;
        display: flex;
        align-items: center;
        justify-content: center;
        perspective: 1000px;
    ">
        <!-- 3D Cube -->
        <div class="cube-wrapper" style="
            position: relative;
            width: 100px;
            height: 100px;
            transform-style: preserve-3d;
            animation: rotateCube 8s infinite linear;
        ">
            <!-- Cube faces -->
            <div class="cube-face front" style="
                position: absolute;
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, rgba(38, 166, 154, 0.9) 0%, rgba(66, 165, 245, 0.9) 100%);
                border: 2px solid rgba(255,255,255,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                font-weight: 800;
                color: white;
                text-align: center;
                line-height: 1.2;
                text-shadow: 0 2px 10px rgba(0,0,0,0.5);
                transform: translateZ(50px);
                backdrop-filter: blur(5px);
                box-shadow: 0 0 30px rgba(66, 165, 245, 0.5);
            ">CONVEXITY<br/>AI</div>
            <div class="cube-face back" style="
                position: absolute;
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, rgba(171, 71, 188, 0.9) 0%, rgba(66, 165, 245, 0.9) 100%);
                border: 2px solid rgba(255,255,255,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                font-weight: 800;
                color: white;
                text-align: center;
                line-height: 1.2;
                text-shadow: 0 2px 10px rgba(0,0,0,0.5);
                transform: rotateY(180deg) translateZ(50px);
                backdrop-filter: blur(5px);
                box-shadow: 0 0 30px rgba(171, 71, 188, 0.5);
            ">CONVEXITY<br/>AI</div>
            <div class="cube-face right" style="
                position: absolute;
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, rgba(66, 165, 245, 0.9) 0%, rgba(38, 166, 154, 0.9) 100%);
                border: 2px solid rgba(255,255,255,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                font-weight: 800;
                color: white;
                text-align: center;
                line-height: 1.2;
                text-shadow: 0 2px 10px rgba(0,0,0,0.5);
                transform: rotateY(90deg) translateZ(50px);
                backdrop-filter: blur(5px);
                box-shadow: 0 0 30px rgba(38, 166, 154, 0.5);
            ">CONVEXITY<br/>AI</div>
            <div class="cube-face left" style="
                position: absolute;
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, rgba(38, 166, 154, 0.9) 0%, rgba(171, 71, 188, 0.9) 100%);
                border: 2px solid rgba(255,255,255,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                font-weight: 800;
                color: white;
                text-align: center;
                line-height: 1.2;
                text-shadow: 0 2px 10px rgba(0,0,0,0.5);
                transform: rotateY(-90deg) translateZ(50px);
                backdrop-filter: blur(5px);
                box-shadow: 0 0 30px rgba(171, 71, 188, 0.5);
            ">CONVEXITY<br/>AI</div>
            <div class="cube-face top" style="
                position: absolute;
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, rgba(66, 165, 245, 0.9) 0%, rgba(171, 71, 188, 0.9) 100%);
                border: 2px solid rgba(255,255,255,0.3);
                transform: rotateX(90deg) translateZ(50px);
                backdrop-filter: blur(5px);
                box-shadow: 0 0 30px rgba(66, 165, 245, 0.5);
            "></div>
            <div class="cube-face bottom" style="
                position: absolute;
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, rgba(38, 166, 154, 0.9) 0%, rgba(66, 165, 245, 0.9) 100%);
                border: 2px solid rgba(255,255,255,0.3);
                transform: rotateX(-90deg) translateZ(50px);
                backdrop-filter: blur(5px);
                box-shadow: 0 0 30px rgba(38, 166, 154, 0.5);
            "></div>
        </div>

        <!-- Glow effect -->
        <div style="
            position: absolute;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, rgba(66, 165, 245, 0.3) 0%, transparent 70%);
            animation: pulse 2s infinite;
            pointer-events: none;
        "></div>
    </div>

    <style>
        @keyframes rotateCube {{
            0% {{ transform: rotateX(-20deg) rotateY(0deg); }}
            100% {{ transform: rotateX(-20deg) rotateY(360deg); }}
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 0.5; transform: scale(1); }}
            50% {{ opacity: 1; transform: scale(1.1); }}
        }}
    </style>
    """
    components.html(cube_html, height=height + 20)


def render_3d_header(title: str = "CONVEXITY AI", subtitle: str = "Momentum Stock Scanner"):
    """
    Render a 3D animated header section with branded cube.
    """
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
            <div style="padding: 20px 0;">
                <h1 style="
                    font-size: 3rem;
                    background: linear-gradient(135deg, #26a69a 0%, #42a5f5 50%, #ab47bc 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin: 0;
                    font-weight: 800;
                    letter-spacing: -1px;
                ">{title}</h1>
                <p style="
                    color: #888;
                    font-size: 1.2rem;
                    margin-top: 5px;
                    font-weight: 300;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                ">{subtitle}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # 3D animated cube with "Convexity AI" text
        render_3d_cube_with_text(height=140)


def render_3d_sector_globe(height: int = 400):
    """
    Render a 3D globe for sector visualization.
    """
    st.markdown("### 🌐 Global Sector View")

    try:
        render_spline_scene(DEMO_SCENES['globe'], height=height, key="sector_globe")
    except Exception as e:
        # Fallback
        st.info("3D Globe visualization - Add your Spline scene URL")
        st.markdown(f"""
            <div style="
                height: {height}px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px dashed #333;
            ">
                <span style="color: #666;">🌐 3D Globe Placeholder</span>
            </div>
        """, unsafe_allow_html=True)


def render_3d_alert_banner(tier: int, symbol: str, height: int = 150):
    """
    Render a 3D animated alert banner.
    """
    color = "#26a69a" if tier == 1 else "#ffc107"
    tier_text = "TIER 1 - STRONG SIGNAL" if tier == 1 else "TIER 2 - WATCH"

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {color}33 0%, {color}11 100%);
            border: 2px solid {color};
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 50% 50%, {color}22 0%, transparent 70%);
                animation: pulse 2s infinite;
            "></div>
            <h2 style="margin: 0; color: {color}; font-size: 1.5rem;">🚀 {tier_text}</h2>
            <h1 style="margin: 10px 0; font-size: 3rem;">{symbol}</h1>
        </div>
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 0.5; transform: scale(1); }}
                50% {{ opacity: 1; transform: scale(1.05); }}
            }}
        </style>
    """, unsafe_allow_html=True)


def render_3d_chart_background(height: int = 300):
    """
    Render a 3D background for charts.
    """
    try:
        render_spline_scene(DEMO_SCENES['abstract'], height=height, key="chart_bg")
    except:
        pass


def render_spline_showcase():
    """
    Render a showcase of 3D capabilities with instructions.
    """
    st.markdown("## 🎨 3D Visuals Showcase")
    st.markdown("""
        Add stunning 3D elements to your dashboard using [Spline](https://spline.design).

        **How to add your own 3D scenes:**
        1. Go to [spline.design](https://spline.design) and create a free account
        2. Design your 3D scene (or use their templates)
        3. Click "Export" → "Web" → Copy the scene URL
        4. Paste the URL in the component below
    """)

    st.divider()

    # Custom scene input
    custom_url = st.text_input(
        "Enter your Spline scene URL:",
        placeholder="https://prod.spline.design/xxxxx/scene.splinecode"
    )

    if custom_url:
        st.markdown("### Your 3D Scene")
        render_spline_scene(custom_url, height=400, key="custom_scene")

    st.divider()

    # Demo scenes
    st.markdown("### Demo Scenes")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Interactive Cube**")
        render_spline_scene(DEMO_SCENES['cube'], height=200, key="demo_cube")

    with col2:
        st.markdown("**Abstract Shape**")
        render_spline_scene(DEMO_SCENES['abstract'], height=200, key="demo_abstract")

    with col3:
        st.markdown("**3D Globe**")
        render_spline_scene(DEMO_SCENES['globe'], height=200, key="demo_globe")
