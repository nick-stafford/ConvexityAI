"""
Advanced Visual Effects Components
Particle effects, aurora backgrounds, neumorphism, and more
"""
import streamlit as st
import streamlit.components.v1 as components


def render_particle_background(
    particle_count: int = 50,
    color: str = "#26a69a",
    height: int = 400,
    key: str = None
):
    """
    Render an interactive particle background that reacts to mouse movement.
    """
    particle_html = f"""
    <div id="particle-container" style="
        position: relative;
        width: 100%;
        height: {height}px;
        background: linear-gradient(135deg, #0a0a12 0%, #12121a 50%, #0a0a12 100%);
        border-radius: 16px;
        overflow: hidden;
    ">
        <canvas id="particles"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('particles');
        const ctx = canvas.getContext('2d');
        const container = document.getElementById('particle-container');

        canvas.width = container.offsetWidth;
        canvas.height = container.offsetHeight;

        let mouseX = canvas.width / 2;
        let mouseY = canvas.height / 2;

        const particles = [];
        const particleCount = {particle_count};

        class Particle {{
            constructor() {{
                this.reset();
            }}

            reset() {{
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 3 + 1;
                this.speedX = (Math.random() - 0.5) * 0.5;
                this.speedY = (Math.random() - 0.5) * 0.5;
                this.opacity = Math.random() * 0.5 + 0.2;
                this.color = this.getRandomColor();
            }}

            getRandomColor() {{
                const colors = ['{color}', '#42a5f5', '#ab47bc', '#ffc107'];
                return colors[Math.floor(Math.random() * colors.length)];
            }}

            update() {{
                // Mouse attraction
                const dx = mouseX - this.x;
                const dy = mouseY - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 150) {{
                    this.x += dx * 0.01;
                    this.y += dy * 0.01;
                }}

                this.x += this.speedX;
                this.y += this.speedY;

                // Wrap around
                if (this.x < 0) this.x = canvas.width;
                if (this.x > canvas.width) this.x = 0;
                if (this.y < 0) this.y = canvas.height;
                if (this.y > canvas.height) this.y = 0;
            }}

            draw() {{
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.globalAlpha = this.opacity;
                ctx.fill();
                ctx.globalAlpha = 1;
            }}
        }}

        // Create particles
        for (let i = 0; i < particleCount; i++) {{
            particles.push(new Particle());
        }}

        // Draw connections between nearby particles
        function drawConnections() {{
            for (let i = 0; i < particles.length; i++) {{
                for (let j = i + 1; j < particles.length; j++) {{
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 100) {{
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = '{color}';
                        ctx.globalAlpha = 0.1 * (1 - dist / 100);
                        ctx.stroke();
                        ctx.globalAlpha = 1;
                    }}
                }}
            }}
        }}

        function animate() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            drawConnections();

            particles.forEach(p => {{
                p.update();
                p.draw();
            }});

            requestAnimationFrame(animate);
        }}

        container.addEventListener('mousemove', (e) => {{
            const rect = container.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        }});

        animate();
    </script>
    """
    components.html(particle_html, height=height + 10, key=key)


def render_aurora_background(height: int = 300, key: str = None):
    """
    Render an animated aurora/northern lights background effect.
    """
    aurora_html = f"""
    <div class="aurora-container" style="
        position: relative;
        width: 100%;
        height: {height}px;
        border-radius: 16px;
        overflow: hidden;
        background: #0a0a12;
    ">
        <div class="aurora"></div>
        <div class="aurora aurora-2"></div>
        <div class="aurora aurora-3"></div>
        <div class="stars"></div>
    </div>

    <style>
        .aurora-container {{
            position: relative;
        }}

        .aurora {{
            position: absolute;
            top: 0;
            left: -50%;
            width: 200%;
            height: 100%;
            background: linear-gradient(
                180deg,
                transparent 0%,
                rgba(38, 166, 154, 0.3) 20%,
                rgba(66, 165, 245, 0.2) 40%,
                rgba(171, 71, 188, 0.2) 60%,
                transparent 100%
            );
            filter: blur(40px);
            animation: aurora-wave 8s ease-in-out infinite;
            transform-origin: center;
        }}

        .aurora-2 {{
            animation-delay: -3s;
            animation-duration: 12s;
            opacity: 0.7;
        }}

        .aurora-3 {{
            animation-delay: -5s;
            animation-duration: 15s;
            opacity: 0.5;
            background: linear-gradient(
                180deg,
                transparent 0%,
                rgba(171, 71, 188, 0.3) 30%,
                rgba(38, 166, 154, 0.2) 50%,
                transparent 100%
            );
        }}

        .stars {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                radial-gradient(1px 1px at 10% 20%, white, transparent),
                radial-gradient(1px 1px at 30% 60%, white, transparent),
                radial-gradient(1px 1px at 50% 30%, white, transparent),
                radial-gradient(1px 1px at 70% 70%, white, transparent),
                radial-gradient(1px 1px at 90% 40%, white, transparent),
                radial-gradient(2px 2px at 20% 80%, rgba(255,255,255,0.8), transparent),
                radial-gradient(2px 2px at 80% 10%, rgba(255,255,255,0.8), transparent);
            animation: twinkle 4s ease-in-out infinite alternate;
        }}

        @keyframes aurora-wave {{
            0%, 100% {{
                transform: translateX(-10%) rotate(-5deg) scale(1);
            }}
            25% {{
                transform: translateX(5%) rotate(3deg) scale(1.1);
            }}
            50% {{
                transform: translateX(10%) rotate(5deg) scale(1);
            }}
            75% {{
                transform: translateX(-5%) rotate(-3deg) scale(1.05);
            }}
        }}

        @keyframes twinkle {{
            0% {{ opacity: 0.3; }}
            100% {{ opacity: 0.8; }}
        }}
    </style>
    """
    components.html(aurora_html, height=height + 10, key=key)


def render_floating_blobs(height: int = 300, key: str = None):
    """
    Render animated floating blob shapes.
    """
    blob_html = f"""
    <div class="blob-container" style="
        position: relative;
        width: 100%;
        height: {height}px;
        border-radius: 16px;
        overflow: hidden;
        background: linear-gradient(135deg, #0a0a12 0%, #12121a 100%);
    ">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
    </div>

    <style>
        .blob-container {{
            filter: blur(0px);
        }}

        .blob {{
            position: absolute;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.6;
            animation: blob-float 20s ease-in-out infinite;
        }}

        .blob-1 {{
            width: 300px;
            height: 300px;
            background: linear-gradient(135deg, #26a69a 0%, #42a5f5 100%);
            top: -100px;
            left: -50px;
            animation-delay: 0s;
        }}

        .blob-2 {{
            width: 250px;
            height: 250px;
            background: linear-gradient(135deg, #ab47bc 0%, #42a5f5 100%);
            bottom: -80px;
            right: -50px;
            animation-delay: -7s;
        }}

        .blob-3 {{
            width: 200px;
            height: 200px;
            background: linear-gradient(135deg, #ffc107 0%, #26a69a 100%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation-delay: -14s;
        }}

        @keyframes blob-float {{
            0%, 100% {{
                transform: translate(0, 0) scale(1);
            }}
            25% {{
                transform: translate(30px, -30px) scale(1.1);
            }}
            50% {{
                transform: translate(-20px, 20px) scale(0.95);
            }}
            75% {{
                transform: translate(10px, 10px) scale(1.05);
            }}
        }}
    </style>
    """
    components.html(blob_html, height=height + 10, key=key)


def render_wave_divider(color: str = "#26a69a", flip: bool = False):
    """
    Render an animated wave divider between sections.
    """
    transform = "scaleY(-1)" if flip else "scaleY(1)"

    wave_html = f"""
    <div class="wave-container" style="
        width: 100%;
        height: 100px;
        overflow: hidden;
        transform: {transform};
    ">
        <svg viewBox="0 0 1440 100" preserveAspectRatio="none" style="width: 100%; height: 100%;">
            <defs>
                <linearGradient id="wave-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#26a69a;stop-opacity:0.3" />
                    <stop offset="50%" style="stop-color:#42a5f5;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#ab47bc;stop-opacity:0.3" />
                </linearGradient>
            </defs>
            <path class="wave-path" fill="url(#wave-gradient)">
                <animate
                    attributeName="d"
                    dur="10s"
                    repeatCount="indefinite"
                    values="
                        M0,50 C360,100 720,0 1080,50 C1260,75 1440,25 1440,50 L1440,100 L0,100 Z;
                        M0,50 C360,0 720,100 1080,50 C1260,25 1440,75 1440,50 L1440,100 L0,100 Z;
                        M0,50 C360,100 720,0 1080,50 C1260,75 1440,25 1440,50 L1440,100 L0,100 Z"
                />
            </path>
            <path class="wave-path-2" fill="url(#wave-gradient)" opacity="0.5">
                <animate
                    attributeName="d"
                    dur="8s"
                    repeatCount="indefinite"
                    values="
                        M0,60 C400,20 800,80 1200,40 C1320,30 1440,70 1440,60 L1440,100 L0,100 Z;
                        M0,40 C400,80 800,20 1200,60 C1320,70 1440,30 1440,40 L1440,100 L0,100 Z;
                        M0,60 C400,20 800,80 1200,40 C1320,30 1440,70 1440,60 L1440,100 L0,100 Z"
                />
            </path>
        </svg>
    </div>
    """
    components.html(wave_html, height=100)


def render_animated_counter(
    value: float,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 0,
    duration: float = 2.0,
    color: str = "#26a69a",
    size: str = "3rem",
    key: str = None
):
    """
    Render an animated counting number.
    """
    counter_html = f"""
    <div class="counter-container" style="text-align: center; padding: 20px;">
        <div class="counter-value" style="
            font-size: {size};
            font-weight: 800;
            background: linear-gradient(135deg, {color} 0%, #42a5f5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">
            <span class="prefix">{prefix}</span>
            <span class="number" data-target="{value}" data-decimals="{decimals}">0</span>
            <span class="suffix">{suffix}</span>
        </div>
    </div>

    <script>
        const counter = document.querySelector('.number');
        const target = parseFloat(counter.getAttribute('data-target'));
        const decimals = parseInt(counter.getAttribute('data-decimals'));
        const duration = {duration * 1000};
        const startTime = performance.now();

        function easeOutQuart(t) {{
            return 1 - Math.pow(1 - t, 4);
        }}

        function updateCounter(currentTime) {{
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = easeOutQuart(progress);
            const current = target * easedProgress;

            counter.textContent = current.toFixed(decimals);

            if (progress < 1) {{
                requestAnimationFrame(updateCounter);
            }}
        }}

        // Start animation when element is visible
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    requestAnimationFrame(updateCounter);
                    observer.disconnect();
                }}
            }});
        }});

        observer.observe(document.querySelector('.counter-container'));
    </script>
    """
    components.html(counter_html, height=100, key=key)


def render_neumorphic_card(content: str, height: int = 150, key: str = None):
    """
    Render a neumorphic (soft UI) card.
    """
    neumorphic_html = f"""
    <div class="neu-card" style="
        background: #1a1a2e;
        border-radius: 20px;
        padding: 30px;
        height: {height}px;
        box-shadow:
            8px 8px 16px rgba(0, 0, 0, 0.4),
            -8px -8px 16px rgba(50, 50, 70, 0.2),
            inset 1px 1px 2px rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    ">
        <div style="color: #fff; text-align: center;">
            {content}
        </div>
    </div>

    <style>
        .neu-card:hover {{
            box-shadow:
                12px 12px 24px rgba(0, 0, 0, 0.5),
                -12px -12px 24px rgba(50, 50, 70, 0.25),
                inset 1px 1px 2px rgba(255, 255, 255, 0.08);
            transform: translateY(-2px);
        }}
    </style>
    """
    components.html(neumorphic_html, height=height + 20, key=key)


def render_neumorphic_button(text: str, key: str = None):
    """
    Render a neumorphic button.
    """
    button_html = f"""
    <button class="neu-button" style="
        background: #1a1a2e;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        color: #26a69a;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        box-shadow:
            5px 5px 10px rgba(0, 0, 0, 0.3),
            -5px -5px 10px rgba(50, 50, 70, 0.15);
        transition: all 0.2s ease;
    ">
        {text}
    </button>

    <style>
        .neu-button:hover {{
            box-shadow:
                7px 7px 14px rgba(0, 0, 0, 0.4),
                -7px -7px 14px rgba(50, 50, 70, 0.2);
            color: #42a5f5;
        }}

        .neu-button:active {{
            box-shadow:
                inset 3px 3px 6px rgba(0, 0, 0, 0.3),
                inset -3px -3px 6px rgba(50, 50, 70, 0.15);
        }}
    </style>
    """
    components.html(button_html, height=60, key=key)


def render_skeleton_loader(height: int = 100, key: str = None):
    """
    Render an elegant skeleton loading placeholder.
    """
    skeleton_html = f"""
    <div class="skeleton-container" style="padding: 20px;">
        <div class="skeleton-header"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-chart"></div>
    </div>

    <style>
        .skeleton-container {{
            background: rgba(26, 26, 46, 0.5);
            border-radius: 12px;
            padding: 20px;
        }}

        .skeleton-header,
        .skeleton-line,
        .skeleton-chart {{
            background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.05) 0%,
                rgba(255, 255, 255, 0.1) 50%,
                rgba(255, 255, 255, 0.05) 100%
            );
            background-size: 200% 100%;
            animation: skeleton-shimmer 1.5s infinite;
            border-radius: 8px;
        }}

        .skeleton-header {{
            width: 40%;
            height: 24px;
            margin-bottom: 15px;
        }}

        .skeleton-line {{
            width: 100%;
            height: 16px;
            margin-bottom: 10px;
        }}

        .skeleton-line.short {{
            width: 60%;
        }}

        .skeleton-chart {{
            width: 100%;
            height: 80px;
            margin-top: 15px;
        }}

        @keyframes skeleton-shimmer {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
    </style>
    """
    components.html(skeleton_html, height=height + 40, key=key)


def render_glowing_border_card(title: str, content: str, height: int = 200, key: str = None):
    """
    Render a card with animated glowing border.
    """
    glow_html = f"""
    <div class="glow-card-wrapper">
        <div class="glow-card" style="height: {height}px;">
            <h3 style="
                margin: 0 0 15px 0;
                background: linear-gradient(135deg, #26a69a, #42a5f5);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{title}</h3>
            <p style="color: #888; margin: 0; line-height: 1.6;">{content}</p>
        </div>
    </div>

    <style>
        .glow-card-wrapper {{
            position: relative;
            padding: 3px;
            border-radius: 16px;
            background: linear-gradient(
                135deg,
                #26a69a,
                #42a5f5,
                #ab47bc,
                #26a69a
            );
            background-size: 400% 400%;
            animation: glow-rotate 5s linear infinite;
        }}

        .glow-card {{
            background: #12121a;
            border-radius: 14px;
            padding: 25px;
            position: relative;
        }}

        .glow-card-wrapper::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            border-radius: 18px;
            background: inherit;
            filter: blur(15px);
            opacity: 0.5;
            z-index: -1;
        }}

        @keyframes glow-rotate {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
    </style>
    """
    components.html(glow_html, height=height + 30, key=key)


def render_mouse_trail_effect(key: str = None):
    """
    Render a custom mouse cursor with trailing effect.
    """
    trail_html = """
    <div id="cursor-container" style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
    ">
        <div id="cursor-dot"></div>
        <div id="cursor-ring"></div>
    </div>

    <style>
        #cursor-dot {
            position: fixed;
            width: 8px;
            height: 8px;
            background: #26a69a;
            border-radius: 50%;
            pointer-events: none;
            transform: translate(-50%, -50%);
            transition: transform 0.1s ease;
            z-index: 10001;
        }

        #cursor-ring {
            position: fixed;
            width: 40px;
            height: 40px;
            border: 2px solid rgba(38, 166, 154, 0.5);
            border-radius: 50%;
            pointer-events: none;
            transform: translate(-50%, -50%);
            transition: all 0.15s ease-out;
            z-index: 10000;
        }
    </style>

    <script>
        const dot = document.getElementById('cursor-dot');
        const ring = document.getElementById('cursor-ring');

        let mouseX = 0, mouseY = 0;
        let ringX = 0, ringY = 0;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;

            dot.style.left = mouseX + 'px';
            dot.style.top = mouseY + 'px';
        });

        function animateRing() {
            ringX += (mouseX - ringX) * 0.15;
            ringY += (mouseY - ringY) * 0.15;

            ring.style.left = ringX + 'px';
            ring.style.top = ringY + 'px';

            requestAnimationFrame(animateRing);
        }

        animateRing();

        // Hover effect on interactive elements
        document.querySelectorAll('button, a, [role="button"]').forEach(el => {
            el.addEventListener('mouseenter', () => {
                ring.style.transform = 'translate(-50%, -50%) scale(1.5)';
                ring.style.borderColor = 'rgba(66, 165, 245, 0.8)';
            });
            el.addEventListener('mouseleave', () => {
                ring.style.transform = 'translate(-50%, -50%) scale(1)';
                ring.style.borderColor = 'rgba(38, 166, 154, 0.5)';
            });
        });
    </script>
    """
    components.html(trail_html, height=0, key=key)


def render_typing_text(text: str, speed: int = 50, key: str = None):
    """
    Render text with a typewriter effect.
    """
    typing_html = f"""
    <div class="typing-container" style="
        font-size: 1.5rem;
        color: #fff;
        padding: 20px;
    ">
        <span class="typing-text"></span>
        <span class="cursor" style="
            display: inline-block;
            width: 3px;
            height: 1.5rem;
            background: #26a69a;
            animation: blink 0.8s infinite;
            margin-left: 2px;
        "></span>
    </div>

    <style>
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0; }}
        }}
    </style>

    <script>
        const text = "{text}";
        const typingElement = document.querySelector('.typing-text');
        let i = 0;

        function typeWriter() {{
            if (i < text.length) {{
                typingElement.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, {speed});
            }}
        }}

        typeWriter();
    </script>
    """
    components.html(typing_html, height=80, key=key)


def render_morphing_shape(height: int = 200, key: str = None):
    """
    Render an SVG shape that morphs between different forms.
    """
    morph_html = f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        height: {height}px;
        background: linear-gradient(135deg, #0a0a12, #12121a);
        border-radius: 16px;
    ">
        <svg viewBox="0 0 200 200" width="150" height="150">
            <defs>
                <linearGradient id="morph-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#26a69a" />
                    <stop offset="50%" style="stop-color:#42a5f5" />
                    <stop offset="100%" style="stop-color:#ab47bc" />
                </linearGradient>
            </defs>
            <path fill="url(#morph-gradient)" opacity="0.8">
                <animate
                    attributeName="d"
                    dur="8s"
                    repeatCount="indefinite"
                    values="
                        M100,20 C150,20 180,50 180,100 C180,150 150,180 100,180 C50,180 20,150 20,100 C20,50 50,20 100,20;
                        M100,40 C140,20 180,60 170,100 C160,140 140,170 100,160 C60,150 30,130 40,100 C50,70 60,60 100,40;
                        M100,30 C160,30 170,70 160,100 C150,130 130,170 100,170 C70,170 40,140 40,100 C40,60 40,30 100,30;
                        M100,20 C150,20 180,50 180,100 C180,150 150,180 100,180 C50,180 20,150 20,100 C20,50 50,20 100,20"
                />
            </path>
        </svg>
    </div>
    """
    components.html(morph_html, height=height + 10, key=key)
