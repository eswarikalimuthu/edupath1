"""
EduPath AI - Modernized Education Advisory Frontend
Features:
- Three.js 3D WebGL Particle Constellation Hero Canvas
- Floating 3D AI Assistant Orb
- Interactive Visual Career Pathway Node Flow
- Dedicated Scholarships & Financial Aid Section with Eligibility Match Badges
- Dedicated Practice & Skills Platform Engine
- Dedicated 30-Day Personalized Action Plan (4-Week Timeline)
- Guidance-Only Vertical Roadmap (Table-free, Checkbox-free)
- Gantt Chart Academic Schedule
- Standalone Grounded Q&A
- SQLite User Authentication & Past Sessions History
"""
import streamlit as st
import requests
import re
import uuid
import json
from datetime import date
import streamlit.components.v1 as components

import sys
import os

# Ensure project root is always in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import importlib
from src import auth
importlib.reload(auth)
from src import db
from src.agents import practice_agent, scholarship_agent

auth.init_users_table()
db.init_db()

st.set_page_config(
    page_title="EduPath AI — Next-Gen Education Adviser",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# ---------------------------------------------------------------------------
# ADVANCED CSS DESIGN SYSTEM (Glassmorphism, Modern Institutional Theme)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F8FAFC;
    color: #1E293B;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', sans-serif;
    color: #0F172A;
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B;
}

section[data-testid="stSidebar"] .stMarkdown, 
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] span {
    color: #94A3B8 !important;
}

section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    color: #F8FAFC !important;
}

/* Sidebar radio buttons custom rectangular chips */
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(51, 65, 85, 0.6);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(59, 130, 246, 0.15);
    border-color: #3B82F6;
    transform: translateX(4px);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, #1E40AF 0%, #2563EB 100%) !important;
    border-color: #60A5FA !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] span,
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) span {
    color: #FFFFFF !important;
    font-weight: 600;
}

/* Glassmorphic Container Cards */
.glass-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
    margin-bottom: 24px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.glass-card:hover {
    box-shadow: 0 10px 28px -4px rgba(0, 0, 0, 0.08);
}

/* Match Badges & Tags */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
    margin-bottom: 8px;
}
.chip-green { background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
.chip-blue { background: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }
.chip-amber { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.chip-purple { background: #F3E8FF; color: #6B21A8; border: 1px solid #D8B4FE; }
.chip-slate { background: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; }

/* Citation tag */
.cit-tag {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    color: #64748B;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-block;
}

.link-tag {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #1D4ED8;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 6px;
    display: inline-block;
}

/* Interactive Pathway Step Card */
.pathway-step {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 20px;
    position: relative;
    border-left: 5px solid #2563EB;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}
.pathway-step:hover {
    transform: translateX(4px);
    border-left-color: #F59E0B;
}

/* Timeline Cards */
.timeline-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    position: relative;
}
.timeline-card.immediate { border-left: 6px solid #10B981; }
.timeline-card.short-term { border-left: 6px solid #3B82F6; }
.timeline-card.medium-term { border-left: 6px solid #8B5CF6; }
.timeline-card.long-term { border-left: 6px solid #F59E0B; }

/* 3D AI Orb Container */
@keyframes orbPulse {
    0% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.4), inset 0 0 15px rgba(255, 255, 255, 0.4); }
    50% { box-shadow: 0 0 35px rgba(147, 51, 234, 0.6), inset 0 0 25px rgba(255, 255, 255, 0.7); }
    100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.4), inset 0 0 15px rgba(255, 255, 255, 0.4); }
}

.ai-orb {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #60A5FA 0%, #2563EB 50%, #1E1B4B 100%);
    animation: orbPulse 4s infinite ease-in-out;
    display: inline-block;
}

/* Auth card */
.auth-box {
    background: white;
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    padding: 36px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.06);
    max-width: 440px;
    margin: 40px auto;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


def render_html(html_str: str):
    """Renders raw HTML cleanly, preventing markdown from interpreting indented lines as code blocks."""
    clean = "\n".join(line.strip() for line in html_str.split("\n") if line.strip())
    st.markdown(clean, unsafe_allow_html=True)




# ---------------------------------------------------------------------------
# 3D THREE.JS HERO CANVAS COMPONENT
# ---------------------------------------------------------------------------
def render_3d_hero_canvas():
    """Renders a responsive, interactive 3D WebGL particle constellation canvas."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; padding: 0; overflow: hidden; background: #0A0F1D; font-family: 'Inter', sans-serif; }
            #container { width: 100%; height: 260px; position: relative; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.4); border: 1px solid rgba(59, 130, 246, 0.25); }
            canvas { width: 100%; height: 100%; display: block; }
            .overlay {
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                padding: 28px 36px;
                pointer-events: none;
                display: flex;
                flex-direction: column;
                justify-content: center;
                background: linear-gradient(90deg, rgba(10, 15, 29, 0.85) 0%, rgba(10, 15, 29, 0.4) 60%, rgba(10, 15, 29, 0.1) 100%);
            }
            .badge-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
            .badge {
                background: rgba(59, 130, 246, 0.2);
                border: 1px solid rgba(96, 165, 250, 0.4);
                color: #93C5FD;
                font-size: 0.72rem;
                padding: 3px 10px;
                border-radius: 16px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .title {
                color: #FFFFFF;
                font-size: 2.2rem;
                font-weight: 800;
                margin: 0;
                letter-spacing: -0.5px;
                font-family: 'Poppins', sans-serif;
                text-shadow: 0 2px 10px rgba(0,0,0,0.5);
            }
            .title span {
                background: linear-gradient(135deg, #60A5FA 0%, #F59E0B 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle {
                color: #94A3B8;
                font-size: 0.95rem;
                margin-top: 6px;
                margin-bottom: 14px;
                max-width: 620px;
                line-height: 1.4;
            }
            .status-chips { display: flex; gap: 10px; flex-wrap: wrap; }
            .chip-live {
                background: rgba(16, 185, 129, 0.15);
                border: 1px solid rgba(16, 185, 129, 0.4);
                color: #34D399;
                font-size: 0.75rem;
                padding: 3px 10px;
                border-radius: 20px;
                font-weight: 600;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }
            .dot { width: 6px; height: 6px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981; }
            .chip-agent {
                background: rgba(245, 158, 11, 0.15);
                border: 1px solid rgba(245, 158, 11, 0.4);
                color: #FBBF24;
                font-size: 0.75rem;
                padding: 3px 10px;
                border-radius: 20px;
                font-weight: 600;
            }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <div id="container">
            <canvas id="canvas"></canvas>
            <div class="overlay">
                <div class="badge-row">
                    <span style="font-size: 1.4rem;">🎓</span>
                    <span class="badge">SIH25094 • AI Education Engine</span>
                </div>
                <h1 class="title">EduPath <span>AI</span></h1>
                <p class="subtitle">Personalized Career, College & Scholarship Advisory for Indian Students</p>
                <div class="status-chips">
                    <span class="chip-live"><span class="dot"></span> Student-Aware Neural RAG Online</span>
                    <span class="chip-agent">🤖 6 Autonomous Specialized Agents Active</span>
                    <span class="chip-agent" style="background: rgba(139, 92, 246, 0.15); border-color: rgba(139, 92, 246, 0.4); color: #C084FC;">💎 3D Intelligent Flow</span>
                </div>
            </div>
        </div>

        <script>
            const canvas = document.getElementById('canvas');
            const container = document.getElementById('container');
            const width = container.clientWidth;
            const height = 260;

            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x0A0F1D, 0.0018);

            const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
            camera.position.z = 240;

            const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
            renderer.setSize(width, height);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            // Create Star Particles
            const particleCount = 450;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);

            for (let i = 0; i < particleCount; i++) {
                positions[i * 3] = (Math.random() - 0.5) * 600;
                positions[i * 3 + 1] = (Math.random() - 0.5) * 350;
                positions[i * 3 + 2] = (Math.random() - 0.5) * 400;

                // Alternate between blue and gold glow
                if (Math.random() > 0.3) {
                    colors[i * 3] = 0.35; colors[i * 3 + 1] = 0.65; colors[i * 3 + 2] = 1.0;
                } else {
                    colors[i * 3] = 0.96; colors[i * 3 + 1] = 0.72; colors[i * 3 + 2] = 0.2;
                }
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({
                size: 3.2,
                vertexColors: true,
                transparent: true,
                opacity: 0.85
            });

            const particles = new THREE.Points(geometry, material);
            scene.add(particles);

            // Glowing Center Polyhedron Orb (Right side)
            const orbGeo = new THREE.IcosahedronGeometry(38, 1);
            const orbMat = new THREE.MeshBasicMaterial({
                color: 0x3B82F6,
                wireframe: true,
                transparent: true,
                opacity: 0.35
            });
            const orbMesh = new THREE.Mesh(orbGeo, orbMat);
            orbMesh.position.set(160, 0, -20);
            scene.add(orbMesh);

            const innerGeo = new THREE.SphereGeometry(18, 16, 16);
            const innerMat = new THREE.MeshBasicMaterial({
                color: 0xF59E0B,
                wireframe: true,
                transparent: true,
                opacity: 0.6
            });
            const innerMesh = new THREE.Mesh(innerGeo, innerMat);
            innerMesh.position.set(160, 0, -20);
            scene.add(innerMesh);

            // Mouse parallax
            let mouseX = 0, mouseY = 0;
            window.addEventListener('mousemove', (e) => {
                mouseX = (e.clientX - window.innerWidth / 2) * 0.05;
                mouseY = (e.clientY - 130) * 0.05;
            });

            function animate() {
                requestAnimationFrame(animate);
                particles.rotation.y += 0.0012;
                particles.rotation.x += 0.0006;

                orbMesh.rotation.y += 0.006;
                orbMesh.rotation.x += 0.004;

                innerMesh.rotation.y -= 0.008;
                innerMesh.rotation.z += 0.005;

                camera.position.x += (mouseX - camera.position.x) * 0.04;
                camera.position.y += (-mouseY - camera.position.y) * 0.04;
                camera.lookAt(scene.position);

                renderer.render(scene, camera);
            }
            animate();

            window.addEventListener('resize', () => {
                const w = container.clientWidth;
                camera.aspect = w / height;
                camera.updateProjectionMatrix();
                renderer.setSize(w, height);
            });
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=270, scrolling=False)


# ---------------------------------------------------------------------------
# INTERACTIVE 3D CAREER PATHWAY NODE FLOW COMPONENT
# ---------------------------------------------------------------------------
def render_pathway_flow_interactive(profile: dict):
    """Renders a responsive SVG node flow representing student progression."""
    stage = str(profile.get("education_stage", "School")).capitalize()
    year = str(profile.get("current_year", "12th Standard")).capitalize()
    stream = str(profile.get("stream", "Engineering")).capitalize()
    goal = str(profile.get("goal", "Career Advice")).capitalize()

    is_ug = "undergraduate" in stage.lower() or any(k in year.lower() for k in ["1st", "2nd", "3rd", "4th", "year"])

    nodes = [
        {"num": "1", "title": f"{stage} ({year})", "desc": f"Current: {stream}", "icon": "📍", "status": "Current Stage"},
        {"num": "2", "title": "Practice Platforms", "desc": "HackerRank & LeetCode", "icon": "💻", "status": "Immediate Focus"},
        {"num": "3", "title": "Admissions & Cutoffs" if not is_ug else "Mini-Projects & Internships", "desc": "TNEA / JEE" if not is_ug else "Real-world portfolio", "icon": "🏛️", "status": "Next Milestone"},
        {"num": "4", "title": "Scholarships & Aid", "desc": "NSP / TN Welfare", "icon": "💰", "status": "Verified Aid"},
        {"num": "5", "title": "Target Career", "desc": goal[:22], "icon": "🎯", "status": "Ultimate Goal"}
    ]

    html = """
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px 24px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(0,0,0,0.03);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.3rem;">🗺️</span>
                <h4 style="margin: 0; color: #0F172A; font-size: 1.1rem; font-weight: 700;">Career & Academic Pathway Flow</h4>
            </div>
            <span style="font-size: 0.78rem; background: #EFF6FF; color: #1D4ED8; font-weight: 600; padding: 4px 12px; border-radius: 12px; border: 1px solid #BFDBFE;">
                Sequential Progression
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; align-items: stretch;">
    """

    for i, node in enumerate(nodes):
        bg = "#F8FAFC" if i > 0 else "#EFF6FF"
        border_col = "#2563EB" if i == 0 else "#E2E8F0"
        tag_bg = "#DBEAFE" if i == 0 else "#F1F5F9"
        tag_col = "#1E40AF" if i == 0 else "#64748B"

        html += f"""
        <div style="background: {bg}; border: 1.5px solid {border_col}; border-radius: 12px; padding: 14px; position: relative; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem;">{node['icon']}</span>
                    <span style="background: {tag_bg}; color: {tag_col}; font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 10px;">Step {node['num']}</span>
                </div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem; margin-bottom: 4px;">{node['title']}</div>
                <div style="color: #64748B; font-size: 0.8rem;">{node['desc']}</div>
            </div>
            <div style="margin-top: 12px; border-top: 1px dashed #CBD5E1; padding-top: 8px; font-size: 0.72rem; font-weight: 600; color: {tag_col};">
                {node['status']}
            </div>
        </div>
        """

    html += """
        </div>
    </div>
    """
    render_html(html)


# ---------------------------------------------------------------------------
# MOTIVATIONAL QUOTE ENGINE
# ---------------------------------------------------------------------------
def get_motivational_message(profile: dict) -> str:
    """Returns a tailored motivational quote based on student stage/year."""
    year = str(profile.get("current_year", "")).lower()
    stage = str(profile.get("education_stage", "")).lower()

    if "3rd" in year or "third" in year:
        return "💡 **Opportunity Awaits:** You already have a strong foundation. Turn your skills into live projects, open-source commits, and internship applications."
    elif "final" in year or "4th" in year or "fourth" in year:
        return "🚀 **Action Time:** Your next opportunity starts with the work you do today. Focus on placement drills, capstones, and company interviews."
    elif "1st" in year or "first" in year:
        return "🌱 **Adapt & Explore:** Adapting to college takes time. Focus on programming fundamentals, mini-projects, and building strong conceptual mastery."
    elif "2nd" in year or "second" in year:
        return "✨ **Consistency Is Key:** Small skills built consistently become big career breakthroughs. Deepen your data structures and hardware/software tools."
    elif "12th" in year or "school" in stage:
        return "🧭 **Your Journey Begins:** Your career does not need to be completely figured out today. Focus on your board exams, state counseling, and targeted scholarships."
    else:
        return "✨ **Take the Next Step:** Your roadmap is a direction, not a deadline. Execute consistently one day at a time."


def format_income_display(raw_income) -> str:
    """Safely formats annual income without crashes on None, string, or special terms."""
    if raw_income is None:
        return "Not specified"
    if isinstance(raw_income, (int, float)):
        if raw_income <= 0:
            return "Not specified"
        return f"₹{int(raw_income):,} / year"
    s = str(raw_income).strip()
    if not s or s.lower() in ["none", "null", "not specified", "n/a", "0"]:
        return "Not specified"
    s_lower = s.lower()
    if "lakh" in s_lower or "lac" in s_lower:
        num_part = re.sub(r"[^\d.]", "", s)
        if num_part:
            try:
                val = int(float(num_part) * 100000)
                return f"₹{val:,} / year ({s})"
            except Exception:
                return s
        return s
    clean = re.sub(r"[^\d.]", "", s)
    if clean:
        try:
            val = int(float(clean))
            return f"₹{val:,} / year"
        except Exception:
            pass
    return s


# ---------------------------------------------------------------------------
# SECTION CARD PARSER & RENDERER
# ---------------------------------------------------------------------------
def parse_recommendation(text: str) -> dict[str, str]:
    """Extracts standard section headers from recommendation text."""
    headers = [
        ("careers", r"(?:###\s*|##\s*|\*\*\s*|^)(?:Suggested\s+)?(?:Career\s+Pathways?|Careers?)[^\n]*"),
        ("courses", r"(?:###\s*|##\s*|\*\*\s*|^)(?:Recommended\s+)?(?:Institutions?\s+(&|and)\s+Courses?|Colleges?|Courses?)[^\n]*"),
        ("scholarships", r"(?:###\s*|##\s*|\*\*\s*|^)(?:Eligible\s+)?(?:Scholarships?|Financial\s+Aid)[^\n]*"),
        ("schemes", r"(?:###\s*|##\s*|\*\*\s*|^)(?:Welfare\s+(&|and)\s+Govt\s+Schemes?|Government\s+Schemes?|Schemes?)[^\n]*"),
        ("next_steps", r"(?:###\s*|##\s*|\*\*\s*|^)(?:Next\s+Steps?(?:\s+(&|and)\s+Action\s+Points?)?|Action\s+Items?)[^\n]*"),
    ]

    positions = []
    for key, pattern in headers:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            positions.append((key, match.start(), match.end()))

    positions.sort(key=lambda x: x[1])
    sections = {"careers": "", "courses": "", "scholarships": "", "schemes": "", "next_steps": ""}

    for i in range(len(positions)):
        key, _, end = positions[i]
        next_start = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        sections[key] = text[end:next_start].strip()

    return sections


def render_section_card(section_text: str, card_title: str, icon: str):
    """Formats AI recommendation section text into structured clean cards."""
    if not section_text.strip() or "no relevant documents found" in section_text.lower():
        st.info(f"No {card_title.lower()} available in current context.")
        return

    # Clean text
    clean = re.sub(r"</?div[^>]*>", "", section_text, flags=re.IGNORECASE)
    clean = clean.replace("### **", "### ").replace("**###", "###")
    clean = re.sub(r"```(?:html|markdown)?", "", clean, flags=re.IGNORECASE).replace("```", "").strip()

    lines = clean.split("\n")
    items = []

    for line in lines:
        line = line.strip()
        if not line or line in ["###", "##", "#"]:
            continue

        line = re.sub(r"^[-*•]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)

        citations = re.findall(r"\((?:source|citation):\s*([^)]+)\)", line, re.IGNORECASE)
        clean_text = re.sub(r"\((?:source|citation):\s*[^)]+\)", "", line, flags=re.IGNORECASE).strip()

        linked = []
        linked_match = re.search(r"\[(?:linked|resources):\s*([^]]+)\]", clean_text, re.IGNORECASE)
        if linked_match:
            linked = [r.strip() for r in linked_match.group(1).split(",")]
            clean_text = re.sub(r"\[(?:linked|resources):\s*[^]]+\]", "", clean_text, flags=re.IGNORECASE).strip()

        clean_text = re.sub(r"<[^>]+>", "", clean_text).strip()
        if clean_text:
            items.append({"text": clean_text, "citations": citations, "linked": linked})

    if not items:
        st.markdown(clean)
        return

    html = f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px; border-bottom: 1px solid #F1F5F9; padding-bottom: 12px;">
            <span style="font-size: 1.4rem;">{icon}</span>
            <span style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">{card_title}</span>
        </div>
        <div>
    """

    for item in items:
        cits = "".join(f'<span class="cit-tag" style="margin-right: 6px;">📄 {c}</span>' for c in item["citations"])
        links = "".join(f'<span class="link-tag" style="margin-right: 6px;">🔗 {l}</span>' for l in item["linked"])
        item_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item["text"])

        html += f"""
        <div style="padding: 12px 0; border-bottom: 1px solid #F8FAFC;">
            <p style="margin: 0 0 6px 0; font-size: 0.92rem; color: #334155; line-height: 1.5;">{item_text}</p>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                {cits}
                {links}
            </div>
        </div>
        """

    html += """
        </div>
    </div>
    """
    render_html(html)


# ---------------------------------------------------------------------------
# ROADMAP & MILESTONES PARSER
# ---------------------------------------------------------------------------
def parse_pathway_to_milestones(pathway_text: str) -> list[dict]:
    """Parses Pathway Planner text into structured milestones with Action, Why it matters, and Skills."""
    phases_patterns = [
        ("Immediate (0-1 month)", r"([#]+\s*[-*•]?\s*Immediate[^\n]*)"),
        ("Short-term (1-6 months)", r"([#]+\s*[-*•]?\s*Short-term[^\n]*)"),
        ("Medium-term (6-18 months)", r"([#]+\s*[-*•]?\s*Medium-term[^\n]*)"),
        ("Long-term (18+ months)", r"([#]+\s*[-*•]?\s*Long-term[^\n]*)"),
    ]

    positions = []
    for name, pattern in phases_patterns:
        match = re.search(pattern, pathway_text, re.IGNORECASE)
        if match:
            positions.append((name, match.start(), match.end()))

    positions.sort(key=lambda x: x[1])
    milestones = []
    if not positions:
        return milestones

    for i in range(len(positions)):
        name, _, end = positions[i]
        next_start = positions[i + 1][1] if i + 1 < len(positions) else len(pathway_text)
        phase_content = pathway_text[end:next_start].strip()

        lines = phase_content.split("\n")
        items = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("- ") or line.startswith("* ") or re.match(r"^\d+\.\s+", line):
                line = re.sub(r"^[-*\d\.\s]+", "", line).strip()

            if not line or line.lower().startswith("most urgent"):
                continue

            citations = re.findall(r"\((?:source|citation):\s*([^)]+)\)", line, re.IGNORECASE)
            clean_text = re.sub(r"\((?:source|citation):\s*[^)]+\)", "", line, re.IGNORECASE).strip()

            linked_resources = []
            linked_match = re.search(r"\[(?:linked|resources):\s*([^]]+)\]", clean_text, re.IGNORECASE)
            if linked_match:
                linked_resources = [r.strip() for r in linked_match.group(1).split(",")]
                clean_text = re.sub(r"\[(?:linked|resources):\s*[^]]+\]", "", clean_text, re.IGNORECASE).strip()

            action = clean_text
            why_it_matters = ""
            skills_opportunity = ""

            if "|" in clean_text:
                parts = clean_text.split("|")
                for part in parts:
                    p_str = part.strip()
                    if p_str.lower().startswith("action:"):
                        action = p_str[7:].strip()
                    elif p_str.lower().startswith("why it matters:"):
                        why_it_matters = p_str[15:].strip()
                    elif p_str.lower().startswith("skills/opportunity:") or p_str.lower().startswith("skills:"):
                        skills_opportunity = p_str.split(":", 1)[1].strip()
                    else:
                        if not why_it_matters and not p_str.lower().startswith("action:"):
                            why_it_matters = p_str

            action = action.replace("### **", "").replace("**", "").strip()
            why_it_matters = why_it_matters.replace("### **", "").replace("**", "").strip()
            skills_opportunity = skills_opportunity.replace("### **", "").replace("**", "").strip()

            items.append({
                "id": str(uuid.uuid4())[:8],
                "action": action,
                "why_it_matters": why_it_matters,
                "skills_opportunity": skills_opportunity,
                "citations": citations,
                "linked_resources": linked_resources,
            })

        milestones.append({"phase": name, "items": items})

    return milestones


def parse_schedule_table(schedule_text: str) -> list[dict]:
    """Parses markdown table from schedule agent."""
    lines = schedule_text.split("\n")
    items = []
    for line in lines:
        line = line.strip()
        if "|" not in line or "Month" in line or "---" in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        if parts and parts[0] == "":
            parts = parts[1:]
        if parts and parts[-1] == "":
            parts = parts[:-1]

        if len(parts) >= 3:
            month = parts[0]
            action = parts[1]
            priority = parts[2]

            citations = re.findall(r"\((?:source|citation):\s*([^)]+)\)", action, re.IGNORECASE)
            clean_action = re.sub(r"\((?:source|citation):\s*[^)]+\)", "", action, re.IGNORECASE).strip()

            linked_resources = []
            linked_match = re.search(r"\[(?:linked|resources):\s*([^]]+)\]", clean_action, re.IGNORECASE)
            if linked_match:
                linked_resources = [r.strip() for r in linked_match.group(1).split(",")]
                clean_action = re.sub(r"\[(?:linked|resources):\s*[^]]+\]", "", clean_action, re.IGNORECASE).strip()

            items.append({
                "id": str(uuid.uuid4())[:8],
                "month": month,
                "action": clean_action,
                "priority": priority,
                "citations": citations,
                "linked_resources": linked_resources,
                "completed": False,
            })
    return items


def render_gantt_chart(schedule_items: list[dict]):
    """Renders HTML Gantt chart for schedule items."""
    if not schedule_items:
        return ""

    months = []
    for item in schedule_items:
        if item["month"] not in months:
            months.append(item["month"])

    if not months:
        return ""

    html = """
    <div style="overflow-x: auto; width: 100%; border: 1px solid #E2E8F0; border-radius: 12px; background: white; padding: 16px; margin-bottom: 24px;">
        <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.85rem;">
            <thead>
                <tr style="border-bottom: 2px solid #E2E8F0; background-color: #F8FAFC;">
                    <th style="text-align: left; padding: 12px; color: #1E3A8A; font-weight: 600;">Action Item</th>
    """
    for m in months:
        html += f'<th style="text-align: center; padding: 12px; color: #1E3A8A; font-weight: 600; min-width: 100px;">{m}</th>'
    html += """
                </tr>
            </thead>
            <tbody>
    """

    for item in schedule_items:
        prio_lower = item["priority"].lower()
        if "high" in prio_lower:
            bar_color, bar_border, bar_text = "#FEE2E2", "#FCA5A5", "#991B1B"
        elif "med" in prio_lower:
            bar_color, bar_border, bar_text = "#FEF3C7", "#FDE68A", "#92400E"
        else:
            bar_color, bar_border, bar_text = "#D1FAE5", "#6EE7B7", "#065F46"

        if item.get("completed"):
            bar_color, bar_border, bar_text = "#E2E8F0", "#CBD5E1", "#475569"

        html += f"""
        <tr style="border-bottom: 1px solid #F1F5F9;">
            <td style="padding: 12px; text-align: left; font-weight: 500; color: #334155;">
                {item["action"]} {" ✅" if item.get("completed") else ""}
            </td>
        """
        for m in months:
            if item["month"] == m:
                html += f"""
                <td style="padding: 6px; text-align: center;">
                    <div style="background-color: {bar_color}; border: 1px solid {bar_border}; color: {bar_text}; padding: 6px 10px; border-radius: 6px; font-weight: 600; font-size: 0.72rem; text-transform: uppercase;">
                        {item["priority"]}
                    </div>
                </td>
                """
            else:
                html += '<td style="padding: 6px; text-align: center; color: #CBD5E1;">•</td>'
        html += "</tr>"

    html += """
            </tbody>
        </table>
    </div>
    """
    return html


def update_schedule_db(session_id: str, sched_items: list[dict]):
    """Saves updated schedule items completion state to SQLite database."""
    db.update_session_schedule_json(session_id, json.dumps(sched_items))
    if st.session_state.get("loaded_session") and st.session_state["loaded_session"]["id"] == session_id:
        st.session_state["loaded_session"]["schedule_json"] = json.dumps(sched_items)


def update_milestones_db(session_id: str, milestones: list[dict]):
    """Saves updated roadmap milestones completion state to SQLite database."""
    db.update_session_milestones(session_id, json.dumps(milestones))
    if st.session_state.get("loaded_session") and st.session_state["loaded_session"]["id"] == session_id:
        st.session_state["loaded_session"]["milestones_json"] = json.dumps(milestones)


def get_default_phased_milestones(profile: dict, target_goal: str = "") -> list[dict]:
    """Provides stage-aware default 4-phase roadmap milestones if LLM output requires structural completion."""
    stage = str(profile.get("education_stage", "")).lower()
    year = str(profile.get("current_year", "")).lower()
    stream = str(profile.get("stream", "Engineering")).title()
    is_ug = "undergraduate" in stage or any(k in year for k in ["1st", "2nd", "3rd", "4th", "year"])
    goal_name = target_goal or profile.get("goal") or "Software / Robotics Engineer"

    if "3rd" in year or "third" in year:
        return [
            {
                "phase": "Immediate (0-1 month)",
                "objective": "Diagnostic Skills Audit, Resume Setup & Welfare Verification",
                "items": [
                    {
                        "id": "imm_1",
                        "action": f"Audit technical skill gaps and create a production-grade GitHub portfolio for {goal_name}",
                        "why_it_matters": "Hiring managers and technical leads inspect verified git commit histories and readme documentation over general GPA.",
                        "skills_opportunity": "Git, GitHub CI/CD, Markdown Documentation, Clean Code",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["GitHub", "Git Guides"],
                        "completed": False
                    },
                    {
                        "id": "imm_2",
                        "action": "Complete a diagnostic coding & data structures assessment on HackerRank / LeetCode",
                        "why_it_matters": "Pinpoints strengths and weaknesses across standard data structures before upcoming placement training season.",
                        "skills_opportunity": "Arrays, Strings, HashMaps, Big-O Complexity",
                        "citations": ["job_dataset.csv"],
                        "linked_resources": ["HackerRank", "LeetCode"],
                        "completed": False
                    },
                    {
                        "id": "imm_3",
                        "action": "Verify eligibility and renewal documentation for state post-matric scholarships & fee concessions",
                        "why_it_matters": "Prevents financial disruptions during the 3rd year by locking in state welfare and tuition reimbursements.",
                        "skills_opportunity": "NSP Portal, Income & Community Certificate Compliance",
                        "citations": ["indian_govt_scholarships.csv"],
                        "linked_resources": ["NSP Portal", "TN e-Scholarship"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Short-term (1-6 months)",
                "objective": "Advanced Problem Solving, Mini-Projects & Hackathon Participation",
                "items": [
                    {
                        "id": "st_1",
                        "action": f"Design and deploy two full-stack or hardware-integrated projects in {goal_name}",
                        "why_it_matters": "Demonstrates architectural understanding, API integration, and real-world system capability.",
                        "skills_opportunity": "System Design, Microservices, API Development, Testing",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["Google Colab", "GitHub Repositories"],
                        "completed": False
                    },
                    {
                        "id": "st_2",
                        "action": "Master 120+ standard algorithmic problems covering trees, graphs, and dynamic programming",
                        "why_it_matters": "Builds algorithmic intuition required to clear high-compensation tier-one recruitment screening rounds.",
                        "skills_opportunity": "Trees, Graphs, BFS/DFS, Dynamic Programming",
                        "citations": ["job_dataset.csv"],
                        "linked_resources": ["LeetCode Top 150"],
                        "completed": False
                    },
                    {
                        "id": "st_3",
                        "action": "Participate in national competitive hackathons (Smart India Hackathon, Unstop, Devfolio)",
                        "why_it_matters": "Simulates rapid sprint pressure, teamwork, and produces award-winning prototype demonstrations.",
                        "skills_opportunity": "Agile Prototyping, Pitch Presentation, Team Leadership",
                        "citations": ["Naan Mudhalvan.pdf"],
                        "linked_resources": ["SIH Portal", "Unstop"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Medium-term (6-18 months)",
                "objective": "Summer Industrial Internship, Industry Certifications & Pre-Placement Prep",
                "items": [
                    {
                        "id": "mt_1",
                        "action": f"Secure and complete an 8-to-12 week summer internship in {goal_name}",
                        "why_it_matters": "Internships are the highest-probability bridge to direct Pre-Placement Offers (PPO) before 7th semester.",
                        "skills_opportunity": "Production Codebase, CI/CD, Agile/Scrum Workflows",
                        "citations": ["job_dataset.csv"],
                        "linked_resources": ["Internshala", "LinkedIn Jobs"],
                        "completed": False
                    },
                    {
                        "id": "mt_2",
                        "action": "Attain recognized industry certification (AWS Certified Developer, NPTEL Elite, or ROS Developer)",
                        "why_it_matters": "Provides third-party credentialing that differentiates your resume in high-volume applicant pools.",
                        "skills_opportunity": "Cloud Engineering / Advanced Automation",
                        "citations": ["NIRF Ranking 2025.csv"],
                        "linked_resources": ["NPTEL", "Coursera"],
                        "completed": False
                    },
                    {
                        "id": "mt_3",
                        "action": "Conduct rigorous peer mock interviews and resume reviews with college alumni",
                        "why_it_matters": "Eliminates hesitation, refines behavioral STAR answering, and sharpens technical explanations.",
                        "skills_opportunity": "STAR Interview Method, System Architecture Presentation",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["Pramp", "Mock Interview Hub"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Long-term (18+ months)",
                "objective": "Final Capstone Design Thesis, Day-Zero Placements & Career Launch",
                "items": [
                    {
                        "id": "lt_1",
                        "action": "Complete a high-impact capstone thesis project solving an authentic industry or societal problem",
                        "why_it_matters": "Serves as the primary discussion centerpiece during final-round executive and hiring-manager interviews.",
                        "skills_opportunity": "Full-Lifecycle Engineering, Technical Writing, System Deployment",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["IEEE Xplore", "GitHub Capstones"],
                        "completed": False
                    },
                    {
                        "id": "lt_2",
                        "action": f"Target dream and core company placements in {goal_name} through campus drives and off-campus portals",
                        "why_it_matters": "Secures prime entry compensation and launches full-time career trajectory.",
                        "skills_opportunity": "Offer Evaluation, Technical Negotiation, Professional Onboarding",
                        "citations": ["job_dataset.csv"],
                        "linked_resources": ["Campus Placement Cell"],
                        "completed": False
                    }
                ]
            }
        ]
    elif not is_ug:
        # School / 12th standard student
        return [
            {
                "phase": "Immediate (0-1 month)",
                "objective": "Academic Performance, Counseling Document Prep & Scholarship Discovery",
                "items": [
                    {
                        "id": "sch_1",
                        "action": "Focus on 12th board examination preparation to maximize cut-off marks for admissions",
                        "why_it_matters": "Tamil Nadu TNEA engineering counseling admissions are based purely on 12th standard Maths, Physics, and Chemistry scores.",
                        "skills_opportunity": "Maths, Physics, Analytical Problem Solving",
                        "citations": ["NIRF Ranking 2025.csv"],
                        "linked_resources": ["TNEA Online Portal"],
                        "completed": False
                    },
                    {
                        "id": "sch_2",
                        "action": "Assemble community certificate, income certificate, and first-generation graduate documents",
                        "why_it_matters": "Required for claiming fee concessions, 7.5% government school quotas, and state scholarships during counseling.",
                        "skills_opportunity": "Document Verification, Citizen Services",
                        "citations": ["indian_govt_scholarships.csv"],
                        "linked_resources": ["TN e-Sevai", "NSP Portal"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Short-term (1-6 months)",
                "objective": "Single-Window Counseling Registration, Choice Filling & College Enrollment",
                "items": [
                    {
                        "id": "sch_3",
                        "action": "Register for TNEA Single-Window Counseling and submit preferred college choice list (CEG, MIT, PSG Tech)",
                        "why_it_matters": "Strategic choice-filling order ensures admission into top accredited government and aided institutions.",
                        "skills_opportunity": "Counseling Analysis, Cutoff Evaluation",
                        "citations": ["NIRF Ranking 2025.csv"],
                        "linked_resources": ["TNEA Single-Window Portal"],
                        "completed": False
                    },
                    {
                        "id": "sch_4",
                        "action": "Complete admissions onboarding and apply for tuition fee waivers and hostel subsidies",
                        "why_it_matters": "Locks in government-subsidized tuition rates and institutional accommodation.",
                        "skills_opportunity": "Institutional Onboarding",
                        "citations": ["Naan Mudhalvan.pdf"],
                        "linked_resources": ["College Admissions Cell"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Medium-term (6-18 months)",
                "objective": "Foundational Coding, College Adaptation & Naan Mudhalvan Skill Training",
                "items": [
                    {
                        "id": "sch_5",
                        "action": "Build strong foundations in Python and C programming with data structures",
                        "why_it_matters": "First-year programming mastery sets the trajectory for subsequent technical specializations.",
                        "skills_opportunity": "Python, C, Problem Solving",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["HackerRank", "W3Schools"],
                        "completed": False
                    },
                    {
                        "id": "sch_6",
                        "action": "Enroll in free industry training modules via Naan Mudhalvan Skill Portal",
                        "why_it_matters": "Provides industry-vetted technology certifications alongside university curriculum.",
                        "skills_opportunity": "Industry Readiness, Emerging Technologies",
                        "citations": ["Naan Mudhalvan.pdf"],
                        "linked_resources": ["Naan Mudhalvan Portal"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Long-term (18+ months)",
                "objective": "Core Domain Specialization & Industry Internship Preparation",
                "items": [
                    {
                        "id": "sch_7",
                        "action": f"Choose academic electives and laboratory specializations aligned with {goal_name}",
                        "why_it_matters": "Aligns advanced semester coursework directly with high-growth market demand.",
                        "skills_opportunity": "Specialized Domain Engineering",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["Department Syllabus"],
                        "completed": False
                    }
                ]
            }
        ]
    else:
        # General undergraduate student
        return [
            {
                "phase": "Immediate (0-1 month)",
                "objective": "Academic Mastery & Foundations",
                "items": [
                    {
                        "id": "gen_1",
                        "action": "Strengthen programming fundamentals and establish daily practice habits",
                        "why_it_matters": "Consistent early problem-solving creates effortless mastery in subsequent semesters.",
                        "skills_opportunity": "Logic Building, Python, Git",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["HackerRank"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Short-term (1-6 months)",
                "objective": "Data Structures & Mini Projects",
                "items": [
                    {
                        "id": "gen_2",
                        "action": f"Build your first two mini-projects in {goal_name}",
                        "why_it_matters": "Practical hands-on application solidifies classroom concepts into portfolio assets.",
                        "skills_opportunity": "Project Architecture, Code Repositories",
                        "citations": ["job_dataset.csv"],
                        "linked_resources": ["GitHub"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Medium-term (6-18 months)",
                "objective": "Internships & Technical Certifications",
                "items": [
                    {
                        "id": "gen_3",
                        "action": "Apply for summer internships and open-source contributions",
                        "why_it_matters": "Industry exposure refines practical problem solving.",
                        "skills_opportunity": "Agile, Code Review, Teamwork",
                        "citations": ["job_dataset.csv"],
                        "linked_resources": ["Internshala"],
                        "completed": False
                    }
                ]
            },
            {
                "phase": "Long-term (18+ months)",
                "objective": "Placement Preparation & Final Year Capstone",
                "items": [
                    {
                        "id": "gen_4",
                        "action": "Execute capstone project and participate in campus placement interviews",
                        "why_it_matters": "Converts university education into full-time employment offers.",
                        "skills_opportunity": "Technical Interviews, Capstone Deployment",
                        "citations": ["expanded_careers.csv"],
                        "linked_resources": ["Placement Cell"],
                        "completed": False
                    }
                ]
            }
        ]


# ---------------------------------------------------------------------------
# INTERACTIVE CAREER RECOMMENDATION ENGINE
# ---------------------------------------------------------------------------
# ===========================================================================
# STREAM DETECTION UTILITY
# ===========================================================================

def detect_stream_key(raw_input) -> str:
    """Identifies the primary academic stream from student profile text, session, or dict."""
    if isinstance(raw_input, dict):
        parts = [
            str(raw_input.get("stream", "")),
            str(raw_input.get("goal", "")),
            str(raw_input.get("target_career", "")),
            str(raw_input.get("constraints", "")),
            str(raw_input.get("education_stage", ""))
        ]
        interests = raw_input.get("interests", [])
        if isinstance(interests, list):
            parts.extend([str(i) for i in interests])
        else:
            parts.append(str(interests))
        s = " ".join(parts).lower()
    else:
        s = str(raw_input).lower()

    if re.search(r"\b(viscom|visual communication|video editing|video editor|video production|video|film|filmmaking|cinema|cinematography|animation|vfx|motion graphics|multimedia|graphic design|ui/?ux|design|designer|photography|photographer|media|journalism|mass communication|direction|sound design|audio engineering|post production|storytelling|editing|fine arts|arts?|literature|humanities|psychology|sociology|history|theatre)\b", s):
        return "arts"
    elif re.search(r"\b(commerce|b\.?com|bba|accounting|accountancy|finance|banking|ca|c\.a\.|business|chartered accountan\w*|company secretary|cs|cma|audit|taxation)\b", s):
        return "commerce"
    elif re.search(r"\b(medical|mbbs|bds|nursing|pharmacy|pharma|doctor|allied health|biotech\w*|clinical|dental|ayush|bams|bhms)\b", s):
        return "medical"
    elif re.search(r"\b(law|ll\.?b|legal|advocate|judge|judiciary|clat|bar council|litigation)\b", s):
        return "law"
    elif re.search(r"\b(science|b\.?sc|physics|chemistry|mathematics|statistics|data science|botany|zoology)\b", s):
        return "science"
    elif re.search(r"\b(engineering|b\.?tech|b\.?e|technology|polytechnic|computer science|cse|mechanical|civil|electrical|ece|eee|software engineering)\b", s):
        return "engineering"
    return "engineering"


# ---------------------------------------------------------------------------
# INTERACTIVE CAREER KNOWLEDGE BASE & ENTITIES
# ---------------------------------------------------------------------------
CAREER_KNOWLEDGE_BASE = {
    # Arts, VisCom, Video & Media
    "video": {
        "domain": "Visual Communication & Video Production",
        "skills": ["Non-Linear Video Editing (Premiere/FCP)", "Motion Graphics & VFX (After Effects)", "Color Grading (DaVinci Resolve)", "Audio Post-Production & Sound Design", "Visual Storytelling & Pacing", "Digital Cinematography"],
        "salary": "INR 4.5L - 15.0L PA",
        "demand": "High Media, OTT & Video Production Demand (+26% YoY)",
        "companies": ["Sun TV Network", "Vijay TV / Disney+ Hotstar", "Netflix India", "Red Chillies Entertainment", "Zoho Creative Studios", "Ogilvy India", "Digital Media Houses"],
        "degree": "B.Sc Visual Communication (VisCom) / BA Film & Television Production / Diploma in Direction & Editing",
        "certifications": ["Adobe Certified Professional (Premiere Pro & After Effects)", "DaVinci Resolve Certified Colorist", "Avid Media Composer Certified"],
        "score": 96
    },
    "viscom": {
        "domain": "Visual Communication & Media Arts",
        "skills": ["Visual Storytelling", "Video Editing & Direction", "Motion Graphics (After Effects)", "Graphic Design (Photoshop/Illustrator)", "Digital Cinematography", "Audio-Visual Production"],
        "salary": "INR 4.5L - 15.0L PA",
        "demand": "High Creative Industry Demand (+25% YoY)",
        "companies": ["Sun TV", "Star Vijay", "Creative Ad Agencies (Ogilvy, DDB Mudra)", "Red Chillies VFX", "Zoho Design Labs", "The Hindu Group"],
        "degree": "B.Sc Visual Communication (VisCom) / B.Des / BA Media Arts",
        "certifications": ["Adobe Certified Professional (Creative Cloud)", "DaVinci Resolve Certified Editor", "Google UX Design Certificate"],
        "score": 96
    },
    "film": {
        "domain": "Film Direction, Cinematography & Post-Production",
        "skills": ["Screenwriting & Storyboarding", "Camera Direction & Lighting", "Film Editing (Premiere/FCP)", "Sound Design & Dubbing", "Production Management"],
        "salary": "INR 5.0L - 18.0L PA",
        "demand": "Thriving Cinema, Streaming & OTT Sector",
        "companies": ["Tamil Cinema Production Studios", "Lyca Productions", "Zee Studios", "Disney+ Hotstar", "Independent Film Houses"],
        "degree": "B.Sc Visual Communication / B.A. in Film Making / Diploma in Film Technology (FTII / MGR FTI)",
        "certifications": ["Cinematography Masterclasses", "Apple Certified Final Cut Pro Specialist"],
        "score": 94
    },
    "animat": {
        "domain": "3D Animation, VFX & Motion Graphics",
        "skills": ["3D Modeling & Texturing (Blender/Maya)", "Character Animation", "VFX Compositing (After Effects/Nuke)", "Rigging & Lighting", "Motion Graphics Design"],
        "salary": "INR 5.0L - 16.0L PA",
        "demand": "Booming Gaming, VFX & Commercial Animation (+30% YoY)",
        "companies": ["MPC Film India", "DNEG", "Technicolor India", "Green Gold Animation", "Ubisoft India"],
        "degree": "B.Sc Animation & VFX / B.Sc Visual Communication / B.Des Animation",
        "certifications": ["Autodesk Maya Certified Professional", "Unreal Engine Authorized Creator"],
        "score": 94
    },
    "design": {
        "domain": "UI/UX Design & Digital Product Experience",
        "skills": ["UI/UX Prototyping (Figma)", "User Research & Wireframing", "Design Systems", "Typography & Branding", "Interaction Design", "Graphic Design (Illustrator)"],
        "salary": "INR 6.0L - 18.0L PA",
        "demand": "Very High Industry Demand (+28% YoY)",
        "companies": ["Zoho Design Labs", "Freshworks", "Swiggy Design Team", "CRED", "Flipkart", "Razorpay"],
        "degree": "B.Des / B.Sc Visual Communication / B.Sc Multimedia",
        "certifications": ["Google UX Design Professional Certificate", "Nielsen Norman Group UX Certification"],
        "score": 95
    },
    "graphic": {
        "domain": "Graphic Design, Branding & Visual Identity",
        "skills": ["Brand Identity Design", "Typography & Layout", "Vector Illustration (Adobe Illustrator)", "Photo Manipulation (Photoshop)", "Print & Digital Publishing"],
        "salary": "INR 4.0L - 12.0L PA",
        "demand": "Steady Corporate & Agency Demand",
        "companies": ["Advertising Agencies", "Brand Consultancies", "Publishing Houses", "Zoho Design", "E-Commerce Brands"],
        "degree": "B.Sc Visual Communication / B.Des / BFA Applied Arts",
        "certifications": ["Adobe Certified Professional in Visual Design", "Coursera Graphic Design Specialization (CalArts)"],
        "score": 93
    },
    "media": {
        "domain": "Media Production & Digital Journalism",
        "skills": ["Investigative Reporting", "Digital Content Strategy", "Broadcast Journalism", "Podcasting & Media Production", "Media Ethics"],
        "salary": "INR 4.5L - 12.0L PA",
        "demand": "High Digital Content Demand",
        "companies": ["The Hindu", "NDTV", "Times Internet", "Scroll.in", "BBC News India"],
        "degree": "BA Journalism & Mass Communication / B.Sc VisCom",
        "certifications": ["Reuters Digital Journalism Certificate", "SEO & Content Marketing Certification"],
        "score": 90
    },

    # Engineering & Technology
    "robot": {
        "domain": "Robotics & Hardware Systems",
        "skills": ["Python", "ROS (Robot Operating System)", "C/C++", "Sensors & Actuators", "CAD/SolidWorks"],
        "salary": "INR 6.5L - 15.0L PA",
        "demand": "High Growth (+24% YoY)",
        "companies": ["Ather Energy", "Bosch India", "TCS Robotics Lab", "L&T Technology Services", "Fanuc India"],
        "degree": "B.Tech in Robotics / Mechatronics / ECE / Mechanical",
        "certifications": ["NPTEL Robotics Specialization", "ROS for Beginners (Coursera)", "Industrial Automation (SMC)"],
        "score": 96
    },
    "ai": {
        "domain": "Artificial Intelligence & ML",
        "skills": ["Python", "PyTorch / TensorFlow", "SQL", "Statistics & Linear Algebra", "Scikit-Learn", "Git"],
        "salary": "INR 8.0L - 18.0L PA",
        "demand": "Very High Growth (+28% YoY)",
        "companies": ["Google India", "Zoho Corporation", "Fractal Analytics", "Microsoft", "TCS Research"],
        "degree": "B.Tech Computer Science / AI & Data Science",
        "certifications": ["DeepLearning.AI Specialization", "AWS Certified Machine Learning", "NPTEL AI/ML by IITM"],
        "score": 95
    },
    "data": {
        "domain": "Data Science & Analytics",
        "skills": ["Python", "SQL", "Pandas / NumPy", "Power BI / Tableau", "Machine Learning", "Statistics"],
        "salary": "INR 6.0L - 14.0L PA",
        "demand": "High Industry Demand",
        "companies": ["Mu Sigma", "Tiger Analytics", "LatentView", "Cognizant", "Accenture"],
        "degree": "B.Tech / B.Sc in Data Science, CS, or Mathematics",
        "certifications": ["Google Data Analytics Certificate", "IBM Data Science Professional", "NPTEL Data Analytics"],
        "score": 92
    },
    "embedded": {
        "domain": "IoT & Embedded Firmware",
        "skills": ["Embedded C", "C++", "RTOS", "Microcontrollers (STM32/ESP32)", "I2C/SPI Protocols", "PCB Design"],
        "salary": "INR 5.5L - 13.0L PA",
        "demand": "Steady Electronics Growth",
        "companies": ["Qualcomm India", "Texas Instruments", "Bosch", "Samsung Semiconductor", "Tata Elxsi"],
        "degree": "B.Tech in ECE / EEE / Embedded Systems",
        "certifications": ["Arm Certified Engineer", "Embedded Systems by UT Austin (edX)", "NPTEL Embedded Systems"],
        "score": 93
    },
    "software": {
        "domain": "Software & Full-Stack Development",
        "skills": ["Data Structures & Algorithms", "Python / Java / TypeScript", "React / Node.js", "SQL & NoSQL", "System Design"],
        "salary": "INR 6.0L - 16.0L PA",
        "demand": "Very High Market Volume",
        "companies": ["Zoho", "Freshworks", "Amazon India", "Infosys", "Cognizant"],
        "degree": "B.Tech / B.E in Computer Science / Information Technology",
        "certifications": ["Meta Full-Stack Engineer", "AWS Certified Cloud Practitioner", "HackerRank 5-Star Badges"],
        "score": 94
    },
    "cyber": {
        "domain": "Cybersecurity & Network Defense",
        "skills": ["Network Protocols (TCP/IP)", "Linux", "Python / Bash", "SIEM Tools", "Vulnerability Assessment"],
        "salary": "INR 6.5L - 15.0L PA",
        "demand": "Critical National Demand",
        "companies": ["Palo Alto Networks", "Quick Heal", "Wipro CyberSec", "EY GDS", "Infosys Cyber Defense"],
        "degree": "B.Tech in Cybersecurity / CSE / IT",
        "certifications": ["CompTIA Security+", "CEH (Certified Ethical Hacker)", "Cisco CCNA Security"],
        "score": 91
    },

    # Commerce & Management
    "ca": {
        "domain": "Accounting, Auditing & Taxation",
        "skills": ["Financial Reporting (Ind AS)", "Direct & Indirect Taxation (GST)", "Auditing Standards", "Corporate Law", "TallyPrime / SAP FICO", "Forensic Accounting"],
        "salary": "INR 8.5L - 25.0L PA",
        "demand": "Evergreen High Corporate Demand (+22% YoY)",
        "companies": ["Deloitte", "PwC", "EY", "KPMG", "Grant Thornton", "BDO India"],
        "degree": "B.Com (General/Honours) / CA Qualification (ICAI)",
        "certifications": ["ICAI Chartered Accountant (FCA/ACA)", "ACCA (Global)", "US CPA", "CMA India"],
        "score": 96
    },
    "account": {
        "domain": "Accounting, Auditing & Taxation",
        "skills": ["Financial Reporting (Ind AS)", "Direct & Indirect Taxation (GST)", "Auditing Standards", "Corporate Law", "TallyPrime / SAP FICO", "Forensic Accounting"],
        "salary": "INR 8.5L - 25.0L PA",
        "demand": "Evergreen High Corporate Demand (+22% YoY)",
        "companies": ["Deloitte", "PwC", "EY", "KPMG", "Grant Thornton", "BDO India"],
        "degree": "B.Com (General/Honours) / CA Qualification (ICAI)",
        "certifications": ["ICAI Chartered Accountant (FCA/ACA)", "ACCA (Global)", "US CPA", "CMA India"],
        "score": 96
    },
    "audit": {
        "domain": "Accounting, Auditing & Taxation",
        "skills": ["Financial Reporting (Ind AS)", "Direct & Indirect Taxation (GST)", "Auditing Standards", "Corporate Law", "TallyPrime / SAP FICO", "Forensic Accounting"],
        "salary": "INR 8.5L - 25.0L PA",
        "demand": "Evergreen High Corporate Demand (+22% YoY)",
        "companies": ["Deloitte", "PwC", "EY", "KPMG", "Grant Thornton", "BDO India"],
        "degree": "B.Com (General/Honours) / CA Qualification (ICAI)",
        "certifications": ["ICAI Chartered Accountant (FCA/ACA)", "ACCA (Global)", "US CPA", "CMA India"],
        "score": 96
    },
    "finance": {
        "domain": "Banking, Investment & Financial Analytics",
        "skills": ["Financial Modeling (DCF/LBO)", "Valuation & Equity Research", "Portfolio Management", "Capital Markets", "Bloomberg Terminal / Excel", "Derivatives Analysis"],
        "salary": "INR 7.5L - 22.0L PA",
        "demand": "Very High Growth Sector (+26% YoY)",
        "companies": ["JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "HDFC Bank", "Barclays", "ICICI Securities"],
        "degree": "B.Com (Accounting & Finance) / BBA / MBA Finance",
        "certifications": ["CFA (Chartered Financial Analyst)", "FRM (Financial Risk Manager)", "NISM Series VIII/XV"],
        "score": 95
    },
    "bank": {
        "domain": "Banking, Investment & Financial Analytics",
        "skills": ["Credit Analysis", "Commercial Banking Protocols", "Risk Assessment", "Wealth Management", "Fintech Innovations", "Financial Modeling"],
        "salary": "INR 6.5L - 18.0L PA",
        "demand": "High National Expansion",
        "companies": ["State Bank of India", "HDFC Bank", "Axis Bank", "Kotak Mahindra", "Standard Chartered"],
        "degree": "B.Com / BBA / MBA in Banking & Finance",
        "certifications": ["JAIIB / CAIIB Certification", "NISM Wealth Management", "CFA Level 1"],
        "score": 92
    },
    "commerce": {
        "domain": "Corporate Commerce & Management",
        "skills": ["Business Strategy", "Financial Accounting", "Managerial Economics", "Supply Chain Finance", "Corporate Law Compliance"],
        "salary": "INR 6.0L - 16.0L PA",
        "demand": "Stable Corporate Demand",
        "companies": ["Tata Consultancy Services", "Zoho Corporation", "ITC Limited", "Hindustan Unilever", "Amazon India"],
        "degree": "B.Com / BBA / M.Com / MBA",
        "certifications": ["ACCA Diploma in IFRS", "Certified Management Accountant (CMA)", "Digital Marketing (Google)"],
        "score": 93
    },

    # Medical & Allied Health
    "doctor": {
        "domain": "Clinical Medicine & Surgery",
        "skills": ["Patient Diagnostics", "Clinical Pharmacology", "Pathology & Therapeutics", "Emergency Care (BLS/ACLS)", "Medical Ethics"],
        "salary": "INR 9.0L - 28.0L PA",
        "demand": "Critical National & Global Need",
        "companies": ["Apollo Hospitals", "Fortis Healthcare", "Manipal Hospitals", "AIIMS", "State Health Mission"],
        "degree": "MBBS / MD / MS / BDS",
        "certifications": ["State Medical Council Registration", "BLS/ACLS AHA Certification", "USMLE / PLAB"],
        "score": 98
    },
    "medical": {
        "domain": "Clinical Medicine & Healthcare",
        "skills": ["Clinical Diagnosis", "Anatomy & Physiology", "Pharmacology", "Patient Care", "Healthcare Management"],
        "salary": "INR 8.0L - 24.0L PA",
        "demand": "Critical Healthcare Need",
        "companies": ["Apollo Hospitals", "Kauvery Hospital", "MIOT International", "Dr. Mehta's Hospitals"],
        "degree": "MBBS / B.Sc Nursing / Allied Health Sciences",
        "certifications": ["Medical Council of India Registration", "Clinical Research Certification"],
        "score": 97
    },
    "pharma": {
        "domain": "Pharmaceutical Sciences & Research",
        "skills": ["Formulation Development", "Good Manufacturing Practices (GMP)", "Pharmacovigilance", "Clinical Trial Protocols", "HPLC/GC Instrumentation"],
        "salary": "INR 5.0L - 14.0L PA",
        "demand": "Rapid Global Pharma Growth",
        "companies": ["Sun Pharma", "Dr. Reddy's Laboratories", "Cipla", "Biocon", "Pfizer India"],
        "degree": "B.Pharm / Pharm.D / M.Pharm",
        "certifications": ["Registered Pharmacist (PCI)", "ICH-GCP Clinical Trials Certification"],
        "score": 91
    },

    # Law & Legal
    "law": {
        "domain": "Corporate Law & Legal Practice",
        "skills": ["Legal Drafting & Pleadings", "Corporate Governance & M&A", "Constitutional Law", "Commercial Arbitration", "Due Diligence"],
        "salary": "INR 7.5L - 24.0L PA",
        "demand": "High Commercial Growth (+20% YoY)",
        "companies": ["Shardul Amarchand Mangaldas", "AZB & Partners", "Trilegal", "Khaitan & Co", "Cyril Amarchand Mangaldas"],
        "degree": "BA LL.B / BBA LL.B (5-Year Integrated) / LL.M",
        "certifications": ["Bar Council of India Enrollment (AIBE)", "Certified Corporate Arbitrator", "Cyber Law Specialization"],
        "score": 94
    }
}

# Ensure both score and match_score are uniformly present across knowledge base
for _k, _v in CAREER_KNOWLEDGE_BASE.items():
    _sc = _v.get("score", _v.get("match_score", 92))
    _v["score"] = _sc
    _v["match_score"] = _sc


def _normalize_career_item(c: dict) -> dict:
    """Guarantees all required fields and match_score are safely present in career dict."""
    sc = c.get("match_score", c.get("score", 92))
    return {
        "title": c.get("title", "Career Pathway"),
        "domain": c.get("domain", "General Industry"),
        "skills": c.get("skills", []),
        "salary": c.get("salary", "INR 6.0L - 14.0L PA"),
        "demand": c.get("demand", "High Industry Demand"),
        "companies": c.get("companies", []),
        "degree": c.get("degree", "Relevant Degree"),
        "certifications": c.get("certifications", []),
        "match_score": sc,
        "score": sc,
        "description": c.get("description", ""),
        "citations": c.get("citations", []),
    }


def parse_structured_careers(careers_text: str, profile: dict) -> list[dict]:
    """Parses raw recommendation text into structured career objects with stream-aware rich metadata."""
    st_key = detect_stream_key(profile)

    # Stream-tailored fallback entities when LLM text is unavailable or generic
    if not careers_text.strip() or "no relevant" in careers_text.lower():
        if st_key == "commerce":
            fallback = [
                {
                    "title": "Chartered Accountant (ICAI) & Tax Consultant",
                    **CAREER_KNOWLEDGE_BASE["ca"],
                    "description": "Lead corporate financial reporting, statutory audits, tax advisory, and strategic financial management for enterprises.",
                    "citations": ["icai_chartered_accountancy_syllabus.pdf", "expanded_careers.csv"]
                },
                {
                    "title": "Financial Analyst & Investment Portfolio Manager",
                    **CAREER_KNOWLEDGE_BASE["finance"],
                    "description": "Perform equity valuation, financial modeling, capital allocation, and asset management for global financial institutions.",
                    "citations": ["expanded_careers.csv", "nirf_institutions.pdf"]
                }
            ]
        elif st_key == "medical":
            fallback = [
                {
                    "title": "Clinical Medical Doctor (MBBS) & Diagnostician",
                    **CAREER_KNOWLEDGE_BASE["doctor"],
                    "description": "Diagnose acute and chronic illnesses, formulate treatment regimens, and administer clinical therapeutics in premier hospitals.",
                    "citations": ["nmc_medical_guidelines.pdf", "expanded_careers.csv"]
                },
                {
                    "title": "Pharmaceutical Scientist & Drug Development Specialist",
                    **CAREER_KNOWLEDGE_BASE["pharma"],
                    "description": "Research novel drug formulations, conduct bio-equivalence studies, and manage regulatory pharmacovigilance.",
                    "citations": ["expanded_careers.csv"]
                }
            ]
        elif st_key == "law":
            fallback = [
                {
                    "title": "Corporate Legal Counsel & Compliance Lead",
                    **CAREER_KNOWLEDGE_BASE["law"],
                    "description": "Draft complex commercial agreements, oversee mergers & acquisitions, and maintain regulatory compliance.",
                    "citations": ["bar_council_guidelines.pdf", "expanded_careers.csv"]
                }
            ]
        elif st_key == "arts":
            fallback = [
                {
                    "title": "Video Editor & Post-Production Specialist",
                    **CAREER_KNOWLEDGE_BASE["video"],
                    "description": "Direct non-linear video editing, multi-track audio mixing, color correction, and visual pacing for films, OTT series, and digital media.",
                    "citations": ["design_curriculum_tn.pdf", "expanded_careers.csv"]
                },
                {
                    "title": "Visual Communication & Media Producer",
                    **CAREER_KNOWLEDGE_BASE["viscom"],
                    "description": "Craft engaging visual narratives, brand design systems, and multi-camera studio productions.",
                    "citations": ["design_curriculum_tn.pdf", "expanded_careers.csv"]
                },
                {
                    "title": "UI/UX & Digital Product Designer",
                    **CAREER_KNOWLEDGE_BASE["design"],
                    "description": "Design user-centered digital interfaces, interactive wireframes, and design systems for mobile and web platforms.",
                    "citations": ["expanded_careers.csv"]
                }
            ]
        else:
            interests = [i.lower() for i in profile.get("interests", [])]
            if any("robot" in i for i in interests):
                fallback = [
                    {
                        "title": "Robotics & Automation Engineer",
                        **CAREER_KNOWLEDGE_BASE["robot"],
                        "description": "Design, build, and program autonomous robotics systems, sensor feedback networks, and robotic manipulators.",
                        "citations": ["expanded_careers.csv", "ai_curriculum_tn.pdf"]
                    },
                    {
                        "title": "AI & Machine Learning Engineer",
                        **CAREER_KNOWLEDGE_BASE["ai"],
                        "description": "Develop deep neural networks, vision systems, and intelligent decision pipelines for next-gen automation.",
                        "citations": ["expanded_careers.csv", "nirf_institutions.pdf"]
                    }
                ]
            else:
                fallback = [
                    {
                        "title": "AI & Software Development Engineer",
                        **CAREER_KNOWLEDGE_BASE["ai"],
                        "description": "Build high-performance algorithms, data pipelines, and scalable software applications.",
                        "citations": ["expanded_careers.csv"]
                    },
                    {
                        "title": "Full-Stack Software Engineer",
                        **CAREER_KNOWLEDGE_BASE["software"],
                        "description": "Architect and deploy end-to-end cloud and web applications with robust backends and clean user interfaces.",
                        "citations": ["expanded_careers.csv"]
                    }
                ]
        return [_normalize_career_item(c) for c in fallback]

    # Parse LLM generated careers
    lines = careers_text.strip().split("\n")
    careers = []
    seen_titles = set()

    # Determine default stream-aligned fallback metadata
    default_meta_key = (
        "ca" if st_key == "commerce"
        else ("doctor" if st_key == "medical"
        else ("law" if st_key == "law"
        else ("video" if st_key == "arts"
        else ("data" if st_key == "science"
        else "software"))))
    )
    stream_default_meta = CAREER_KNOWLEDGE_BASE.get(default_meta_key, CAREER_KNOWLEDGE_BASE["software"])

    # High-precision patterns for role recognition
    role_matching_patterns = [
        # Arts, VisCom, Video & Media
        (r"\b(video\s*edit\w*|film\s*edit\w*|post\s*product\w*|colorist|video\s*product\w*|cinematograph\w*|motion\s*graphic\w*)\b", "video"),
        (r"\b(viscom|visual\s*communicat\w*|multimedia|creative\s*direct\w*|broadcast\w*)\b", "viscom"),
        (r"\b(film\s*mak\w*|filmmak\w*|cinema\w*|film\s*direct\w*|screenwrit\w*)\b", "film"),
        (r"\b(animat\w*|3d\s*model\w*|vfx|visual\s*effects|game\s*art\w*)\b", "animat"),
        (r"\b(ui/?ux|product\s*design\w*|interaction\s*design\w*|ux\s*design\w*|user\s*experience|web\s*design\w*)\b", "design"),
        (r"\b(graphic\s*design\w*|brand\s*design\w*|illustrat\w*|typograph\w*)\b", "graphic"),
        (r"\b(journalis\w*|reporter|news\s*anchor|content\s*strat\w*|copywrit\w*|media\s*product\w*)\b", "media"),

        # Commerce & Finance
        (r"\b(chartered\s*account\w*|ca|auditor|tax\s*consult\w*|statutory\s*audit\w*)\b", "ca"),
        (r"\b(financial\s*analyst|investment\s*bank\w*|equity\s*research|portfolio\s*manag\w*|wealth\s*manag\w*)\b", "finance"),
        (r"\b(bank\w*|credit\s*analyst|commercial\s*bank\w*)\b", "bank"),
        (r"\b(accountant|accounting|tally|bookkeep\w*)\b", "account"),
        (r"\b(company\s*secretary|cs|corporate\s*govern\w*|compliance\s*officer)\b", "commerce"),

        # Medical & Health
        (r"\b(doctor|physician|surgeon|mbbs|medical\s*officer|clinical\s*specialist)\b", "doctor"),
        (r"\b(pharmac\w*|drug\s*development|clinical\s*research|formulat\w*)\b", "pharma"),
        (r"\b(nurse|nursing|allied\s*health|physiotherap\w*|bpt)\b", "medical"),

        # Law
        (r"\b(lawyer|advocate|legal\s*counsel|litigat\w*|arbitrat\w*|solicitor|judge|magistrate|corporate\s*law\w*)\b", "law"),

        # Science
        (r"\b(data\s*scien\w*|data\s*analyst|quantitative\s*analyst|statistician|business\s*intelligence)\b", "data"),

        # Engineering & Tech
        (r"\b(robot\w*|mechatron\w*|automation\s*engineer|drone|actuator)\b", "robot"),
        (r"\b(ai\s*engineer|machine\s*learning|deep\s*learning|computer\s*vision|nlp\s*engineer)\b", "ai"),
        (r"\b(embedded|iot|firmware|microcontroller|vlsi|pcb|stm32|arduino)\b", "embedded"),
        (r"\b(cyber\s*sec\w*|ethical\s*hack\w*|infosec|security\s*analyst|pen\s*test\w*)\b", "cyber"),
        (r"\b(software\s*engineer|software\s*develop\w*|full\s*stack|web\s*develop\w*|backend|frontend|devops|cloud\s*engineer)\b", "software"),
    ]

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line in ["---", "***"]:
            continue
        line = re.sub(r"^[-*•\d\.]+\s*", "", line)

        title_match = re.search(r"\*\*([^*]+)\*\*", line)
        title = title_match.group(1).strip() if title_match else line.split(":")[0].strip()
        title = title.replace("Career:", "").replace("Role:", "").strip()

        if len(title) > 55 or not title:
            continue

        norm_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
        if norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)

        lower_title = title.lower()
        # Clean line to eliminate false-positive triggers like "software skills" or "editing software"
        clean_line = re.sub(r"\b(software\s+(?:skills?|tools?|packages?|applications?)|(?:editing|accounting|tax|design|cad|office)\s+software)\b", "tools", line.lower())
        lower_t = (lower_title + " " + clean_line).lower()

        matched_key = None
        # Step 1: Match against specific title keywords with highest confidence
        for pat, key in role_matching_patterns:
            if re.search(pat, lower_title):
                matched_key = key
                break

        # Step 2: If title didn't directly match, search line with priority for current student stream!
        if not matched_key:
            stream_relevant_keys = {
                "arts": ["video", "viscom", "film", "animat", "design", "graphic", "media"],
                "commerce": ["ca", "account", "audit", "finance", "bank", "commerce"],
                "medical": ["doctor", "pharma", "medical"],
                "law": ["law"],
                "science": ["data"],
                "engineering": ["ai", "robot", "data", "embedded", "software", "cyber"]
            }.get(st_key, [])

            for pat, key in role_matching_patterns:
                if key in stream_relevant_keys and re.search(pat, lower_t):
                    matched_key = key
                    break

        # Step 3: General line search across all patterns
        if not matched_key:
            for pat, key in role_matching_patterns:
                if re.search(pat, lower_t):
                    matched_key = key
                    break

        matched_meta = CAREER_KNOWLEDGE_BASE.get(matched_key, stream_default_meta)

        citations = re.findall(r"\((?:source|citation):\s*([^)]+)\)", line, re.IGNORECASE)
        clean_desc = re.sub(r"\((?:source|citation):\s*[^)]+\)", "", line, flags=re.IGNORECASE)
        clean_desc = re.sub(r"\[(?:linked|resources):\s*[^]]+\]", "", clean_desc, flags=re.IGNORECASE)
        clean_desc = clean_desc.replace(f"**{title}**", "").replace(title, "").replace(":", "").strip()
        if not clean_desc:
            clean_desc = f"Pursue a high-impact specialization in {matched_meta['domain']} focusing on practical applications and industry problem-solving."

        careers.append({
            "title": title,
            "domain": matched_meta["domain"],
            "skills": matched_meta["skills"],
            "salary": matched_meta["salary"],
            "demand": matched_meta["demand"],
            "companies": matched_meta["companies"],
            "degree": matched_meta["degree"],
            "certifications": matched_meta["certifications"],
            "match_score": matched_meta["score"],
            "description": clean_desc,
            "citations": citations
        })

    # If parsing found nothing, fallback to stream-tailored roles
    if not careers:
        if st_key == "commerce":
            careers = [
                {
                    "title": "Chartered Accountant (ICAI) & Tax Consultant",
                    **CAREER_KNOWLEDGE_BASE["ca"],
                    "description": "Lead corporate financial reporting, statutory audits, tax advisory, and strategic financial management for enterprises.",
                    "citations": ["icai_chartered_accountancy_syllabus.pdf"]
                },
                {
                    "title": "Financial Analyst & Investment Portfolio Manager",
                    **CAREER_KNOWLEDGE_BASE["finance"],
                    "description": "Perform equity valuation, financial modeling, capital allocation, and asset management for global financial institutions.",
                    "citations": ["expanded_careers.csv"]
                }
            ]
        elif st_key == "medical":
            careers = [
                {
                    "title": "Clinical Medical Doctor (MBBS)",
                    **CAREER_KNOWLEDGE_BASE["doctor"],
                    "description": "Diagnose illnesses, administer treatments, and guide clinical healthcare delivery.",
                    "citations": ["nmc_guidelines.pdf"]
                }
            ]
        elif st_key == "arts":
            careers = [
                {
                    "title": "Video Editor & Post-Production Specialist",
                    **CAREER_KNOWLEDGE_BASE["video"],
                    "description": "Direct non-linear video editing, multi-track audio mixing, color correction, and visual pacing for films, OTT series, and digital media.",
                    "citations": ["design_curriculum_tn.pdf"]
                },
                {
                    "title": "Visual Communication & Media Producer",
                    **CAREER_KNOWLEDGE_BASE["viscom"],
                    "description": "Craft engaging visual narratives, brand design systems, and multi-camera studio productions.",
                    "citations": ["design_curriculum_tn.pdf"]
                }
            ]
        elif st_key == "law":
            careers = [
                {
                    "title": "Corporate Legal Counsel & Compliance Lead",
                    **CAREER_KNOWLEDGE_BASE["law"],
                    "description": "Draft complex commercial agreements, oversee mergers & acquisitions, and maintain regulatory compliance.",
                    "citations": ["bar_council_guidelines.pdf"]
                }
            ]
        else:
            careers = [
                {
                    "title": "Robotics & Automation Engineer",
                    **CAREER_KNOWLEDGE_BASE["robot"],
                    "description": "Design and build robotic actuators, ROS control systems, and automation software.",
                    "citations": ["expanded_careers.csv"]
                },
                {
                    "title": "AI & Machine Learning Engineer",
                    **CAREER_KNOWLEDGE_BASE["ai"],
                    "description": "Train machine learning models and computer vision pipelines for intelligent automation.",
                    "citations": ["expanded_careers.csv"]
                }
            ]

    return [_normalize_career_item(c) for c in careers]


COMMERCE_COLLEGES_DATABASE = [
    {
        "name": "Loyola College (Autonomous), Chennai",
        "tnea_code": "Univ of Madras (Aided/Self-Financed)",
        "location": "Sterling Road, Nungambakkam, Chennai, Tamil Nadu",
        "ranking": "NIRF Rank #4 in India (Colleges) • Premier Commerce & Economics Institution",
        "type": "Tamil Nadu State (Autonomous)",
        "established": "1925",
        "programs": "B.Com (General), B.Com (Corporate Secretaryship), BBA, B.Com (Accounting & Finance)",
        "min_cutoff": 93.0,
        "max_cutoff": 98.0,
        "cutoff": "Board Merit Cutoff: ~93.0% - 98.0% (BC: ~91-96%, SC/ST: ~84-91%)",
        "fees": "Aided: ~INR 12,000 - 24,000/yr • Shift II: ~INR 45,000 - 65,000/yr",
        "placements": "Average CTC: INR 6.8 LPA • Deloitte, EY, KPMG, Goldman Sachs, McKinsey, Barclays",
        "strengths": "Commerce Computer Lab, Live Stock Market Terminal, Big 4 MoUs, CA Foundation Coaching",
        "website": "https://www.loyolacollege.edu",
        "portal": "https://erp.loyolacollege.edu/loyolaonline/application/",
        "stream": "commerce"
    },
    {
        "name": "Madras Christian College (MCC Chennai)",
        "tnea_code": "University of Madras",
        "location": "Tambaram, Chennai, Tamil Nadu",
        "ranking": "NIRF Top 15 in India (Colleges) • 185-Year Historic Legacy",
        "type": "Tamil Nadu State (Autonomous)",
        "established": "1837",
        "programs": "B.Com (General), B.Com (Professional Accounting), BBA, B.Com (Finance & Taxation)",
        "min_cutoff": 91.0,
        "max_cutoff": 96.5,
        "cutoff": "Board Merit Cutoff: ~91.0% - 96.5% (BC: ~89-94.5%, SC/ST: ~81-89%)",
        "fees": "~INR 18,000 - 38,000 / year",
        "placements": "Average CTC: INR 6.2 LPA • JPMorgan Chase, PwC, Wells Fargo, Standard Chartered, Zoho",
        "strengths": "Center for Financial Studies, Business Incubator, ICAI/ACCA curriculum accreditation",
        "website": "https://mcc.edu.in",
        "portal": "https://mcc.edu.in/admissions/",
        "stream": "commerce"
    },
    {
        "name": "PSG College of Arts and Science (PSG CAS Coimbatore)",
        "tnea_code": "Bharathiar University",
        "location": "Civil Aerodrome Post, Coimbatore, Tamil Nadu",
        "ranking": "NIRF Rank #20 in India (Colleges) • Premier Autonomous Commerce Hub",
        "type": "Tamil Nadu State (Govt-Aided & Self-Financed)",
        "established": "1947",
        "programs": "B.Com (CA), B.Com (FinTech), B.Com (Professional Accounting), BBA (Logistics)",
        "min_cutoff": 89.0,
        "max_cutoff": 95.5,
        "cutoff": "Board Merit Cutoff: ~89.0% - 95.5% (BC: ~87-93%, SC/ST: ~79-87%)",
        "fees": "Aided: ~INR 15,000/yr • Self-Finance: ~INR 45,000 - 60,000/yr",
        "placements": "Average CTC: INR 5.8 LPA • Amazon, Cognizant, Grant Thornton, South Indian Bank, Zoho",
        "strengths": "Industry 4.0 FinTech Centre, PSG Institute of Management tie-up, Tally & SAP Certified Labs",
        "website": "https://www.psgcas.ac.in",
        "portal": "https://www.psgcas.ac.in/admissions/",
        "stream": "commerce"
    },
    {
        "name": "Shri Ram College of Commerce (SRCC, University of Delhi)",
        "tnea_code": "Central University (CUET-UG)",
        "location": "Maurice Nagar, North Campus, New Delhi",
        "ranking": "NIRF #1 in India for Commerce & Economics",
        "type": "Premier Central University (CUET-UG)",
        "established": "1926",
        "programs": "B.Com (Honours), B.A. (Honours) Economics",
        "min_cutoff": 96.0,
        "max_cutoff": 99.8,
        "cutoff": "Admissions via CUET-UG (NTA Percentile 98.5+ / Board Merit 96%+)",
        "fees": "Central Govt Subsidized (~INR 30,000 / year)",
        "placements": "Average CTC: INR 10.5 LPA • Highest: INR 35 LPA (Bain, BCG, Morgan Stanley, Lehman)",
        "strengths": "Asia's premier commerce alumni network, Global Business Operations Center",
        "website": "https://www.srcc.edu",
        "portal": "https://ugadmission.uod.ac.in",
        "stream": "commerce"
    },
    {
        "name": "Stella Maris College for Women (Autonomous, Chennai)",
        "tnea_code": "University of Madras",
        "location": "Cathedral Road, Chennai, Tamil Nadu",
        "ranking": "NIRF Top 30 in India (Colleges) • Premier Women's Business Institution",
        "type": "Tamil Nadu State (Autonomous)",
        "established": "1947",
        "programs": "B.Com (Corporate Secretaryship), B.Com (Honours), BBA, B.Com (Business Analytics)",
        "min_cutoff": 87.0,
        "max_cutoff": 94.0,
        "cutoff": "Board Merit Cutoff: ~87.0% - 94.0% (BC: ~85-92%, SC/ST: ~77-85%)",
        "fees": "~INR 25,000 - 50,000 / year",
        "placements": "Average CTC: INR 5.5 LPA • EY, RBS, TCS, Ford Financial, BNY Mellon",
        "strengths": "Women Leadership Incubator, CMA & ACCA Global curriculum integration",
        "website": "https://stellamariscollege.edu.in",
        "portal": "https://stellamariscollege.edu.in/admissions/",
        "stream": "commerce"
    },
    {
        "name": "Christ University (School of Commerce & Finance, Bangalore)",
        "tnea_code": "Deemed University",
        "location": "Hosur Road, Bangalore, Karnataka",
        "ranking": "Premier Deemed University • Top Private Commerce Campus in South India",
        "type": "All-India Entrance & Merit",
        "established": "1969",
        "programs": "B.Com (Finance & Investment), BBA (FinTech), B.Com (Applied Finance & CA)",
        "min_cutoff": 86.0,
        "max_cutoff": 94.0,
        "cutoff": "Entrance Test + Micro Presentation + 12th Board Marks (86%+)",
        "fees": "~INR 95,000 - 1,40,000 / year",
        "placements": "Average CTC: INR 6.5 LPA • DE Shaw, Goldman Sachs, Deloitte, Dell, Oracle",
        "strengths": "Bloomberg Financial Markets Lab, CFA Institute University Affiliation Program",
        "website": "https://www.christuniversity.in",
        "portal": "https://espro.christuniversity.in",
        "stream": "commerce"
    },
    {
        "name": "Presidency College (Autonomous), Chennai",
        "tnea_code": "Govt of Tamil Nadu (TNGASA)",
        "location": "Marina Beach Road, Chennai, Tamil Nadu",
        "ranking": "NIRF Rank #3 in India (Colleges Category) • Historic State Govt College",
        "type": "State Government (TNGASA Single-Window)",
        "established": "1840",
        "programs": "B.Com (General), B.Com (Corporate Secretaryship), B.A. Economics",
        "min_cutoff": 82.0,
        "max_cutoff": 91.0,
        "cutoff": "Single-Window Merit (TNGASA): ~82.0% - 91.0% (Subsidized for SC/ST/BC)",
        "fees": "Ultra-subsidized Govt Fees (~INR 2,500 - 5,000 / year)",
        "placements": "Average CTC: INR 4.5 LPA • Nationalized bank clerkships, TCS, Cognizant, Southern Railways",
        "strengths": "Free education for underprivileged, 100% reservation compliance, Research library",
        "website": "https://presidencycollegechennai.ac.in",
        "portal": "https://www.tngasa.in",
        "stream": "commerce"
    },
    {
        "name": "The New College (Autonomous), Royapettah, Chennai",
        "tnea_code": "University of Madras",
        "location": "Peters Road, Royapettah, Chennai, Tamil Nadu",
        "ranking": "NAAC 'A' Grade • Renowned Minority & General Commerce Hub",
        "type": "Tamil Nadu State (Govt-Aided & Self-Financed)",
        "established": "1951",
        "programs": "B.Com (General), B.Com (Information Systems & Management), BBA, B.Com (Bank Management)",
        "min_cutoff": 78.0,
        "max_cutoff": 89.0,
        "cutoff": "Board Merit Cutoff: ~78.0% - 89.0% (BC/Minority/SC/ST quotas)",
        "fees": "Subsidized Aided: ~INR 10,000/yr • Self-Finance: ~INR 35,000/yr",
        "placements": "Average CTC: INR 4.8 LPA • Standard Chartered, HDFC Bank, Sutherland, Zoho",
        "strengths": "Commerce Computer Centre, Placement cell with Gulf and National corporate tie-ups",
        "website": "https://thenewcollege.edu.in",
        "portal": "https://thenewcollege.edu.in/admission/",
        "stream": "commerce"
    }
]

ENGINEERING_COLLEGES_DATABASE = [
    {
        "name": "College of Engineering, Guindy (CEG Anna University)",
        "tnea_code": "0001",
        "location": "Guindy, Chennai, Tamil Nadu",
        "ranking": "NIRF Rank #13 (Engineering) • Top State University",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1794 (Oldest Technical Institution in India)",
        "programs": "B.Tech Computer Science, B.Tech Robotics & Automation, B.E ECE, B.E Mechanical, B.Tech IT",
        "min_cutoff": 191.5,
        "max_cutoff": 199.0,
        "cutoff": "TNEA General Cutoff: ~191.5 - 198.5 / 200 (BC: ~189-197, SC/ST: ~175-190)",
        "fees": "Highly Subsidized Govt Fees (~INR 18,000 - 32,000 / year)",
        "placements": "Average CTC: INR 9.5 LPA • Highest CTC: INR 40 LPA (Microsoft, Zoho, Caterpillar, Bosch, Amazon, TCS)",
        "strengths": "Siemens Centre of Excellence, Centre for Artificial Intelligence & Robotics, State Central Library",
        "website": "https://ceg.annauniv.edu",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "Madras Institute of Technology (MIT Campus, Anna University)",
        "tnea_code": "0004",
        "location": "Chromepet, Chennai, Tamil Nadu",
        "ranking": "Premier State University Campus • Alma Mater of Dr. APJ Abdul Kalam",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1949",
        "programs": "B.E Aeronautical Engineering, B.E Robotics & Mechatronics, B.Tech IT, B.E EIE, B.E Automobile",
        "min_cutoff": 189.0,
        "max_cutoff": 196.5,
        "cutoff": "TNEA General Cutoff: ~189.0 - 196.5 / 200 (BC: ~187-195, SC/ST: ~170-188)",
        "fees": "Highly Subsidized Govt Fees (~INR 18,000 - 32,000 / year)",
        "placements": "Average CTC: INR 8.8 LPA • Premier recruiters: Boeing, HAL, Renault-Nissan, Qualcomm, Infosys, Zoho",
        "strengths": "Kalam Aerospace & Avionics Hangars, Embedded Systems & IoT Hub, Advanced Mechatronics Labs",
        "website": "https://www.mitindia.edu",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "PSG College of Technology (PSG Tech)",
        "tnea_code": "2006",
        "location": "Peelamedu, Coimbatore, Tamil Nadu",
        "ranking": "NIRF Top 60 (Engineering) • Premier Industry-Integrated Autonomous Institution",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1951",
        "programs": "B.E Robotics & Automation, B.Tech AI & Data Science, B.E Mechatronics, B.E Computer Science",
        "min_cutoff": 188.0,
        "max_cutoff": 197.0,
        "cutoff": "TNEA General Cutoff: ~188.0 - 197.0 / 200 (BC: ~186-195, SC/ST: ~168-185)",
        "fees": "Govt-Aided Seats: ~INR 25,000/yr • Self-Financing: ~INR 85,000/yr",
        "placements": "Average CTC: INR 9.2 LPA • 95%+ Placement rate with Bosch, Festo, L&T, Microsoft, Ather Energy",
        "strengths": "Festo Industrial Automation Centre, Fanuc Industrial Robotics Lab, Heavy Engineering Incubator",
        "website": "https://www.psgtech.edu",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "SSN College of Engineering",
        "tnea_code": "1315",
        "location": "Kalavakkam, OMR, Chennai, Tamil Nadu",
        "ranking": "NIRF Top 45 (Engineering) • Top Ranked Private Research Institution",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1996",
        "programs": "B.Tech Computer Science, B.Tech AI & Data Science, B.E ECE, B.E Biomedical Engineering",
        "min_cutoff": 187.0,
        "max_cutoff": 196.0,
        "cutoff": "TNEA General Cutoff: ~187.0 - 196.0 / 200 (BC: ~185-194, SC/ST: ~165-182)",
        "fees": "~INR 85,000/yr • Generous Shiv Nadar Foundation Merit Scholarships",
        "placements": "Average CTC: INR 9.8 LPA • Highest CTC: INR 42 LPA (Amazon, Goldman Sachs, Hyundai, Zoho)",
        "strengths": "Centre for Speech & Image Processing, Autonomous Vehicle Lab, IBM Centre of Excellence",
        "website": "https://www.ssn.edu.in",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "Thiagarajar College of Engineering (TCE Madurai)",
        "tnea_code": "5008",
        "location": "Thiruparankundram, Madurai, Tamil Nadu",
        "ranking": "NIRF Top 85 (Engineering) • Premier Engineering Hub of Southern Tamil Nadu",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1957",
        "programs": "B.E Mechatronics Engineering, B.E Computer Science, B.Tech AI & Data Science, B.E EEE",
        "min_cutoff": 182.0,
        "max_cutoff": 193.0,
        "cutoff": "TNEA General Cutoff: ~182.0 - 193.0 / 200 (BC: ~180-191, SC/ST: ~162-180)",
        "fees": "Govt-Aided Seats: ~INR 22,000 - 45,000 / year (Hostel Subsidized)",
        "placements": "Average CTC: INR 7.8 LPA • Premier recruiters: Honeywell, TVS Motor, TCS, Zoho, HCL",
        "strengths": "Honeywell Industrial Automation Lab, TVS Mechatronics R&D Hub, Intel Intelligent Systems Lab",
        "website": "https://www.tce.edu",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "Coimbatore Institute of Technology (CIT Coimbatore)",
        "tnea_code": "2007",
        "location": "Civil Aerodrome Post, Coimbatore, Tamil Nadu",
        "ranking": "NIRF Top 100 • Legacy Govt-Aided Research Institution",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1956",
        "programs": "B.E Electronics & Communication, B.Tech AI & ML, B.E Mechanical Engineering, B.Tech CSE",
        "min_cutoff": 180.0,
        "max_cutoff": 191.0,
        "cutoff": "TNEA General Cutoff: ~180.0 - 191.0 / 200 (BC: ~178-189, SC/ST: ~160-178)",
        "fees": "Govt-Aided Seats: ~INR 22,000 - 42,000 / year",
        "placements": "Average CTC: INR 7.5 LPA • Strong core engineering & IT placements in Chennai & Bangalore corridors",
        "strengths": "Texas Instruments DSP Innovation Lab, IoT Technology Centre, Automotive Testing Facility",
        "website": "https://www.cit.edu.in",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "Government College of Technology (GCT Coimbatore)",
        "tnea_code": "2005",
        "location": "Thadagam Road, Coimbatore, Tamil Nadu",
        "ranking": "NIRF Top 150 • Top Public Government Institution",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1945",
        "programs": "B.E Computer Science, B.E Electronics & Instrumentation, B.E Civil, B.E Mechanical",
        "min_cutoff": 178.0,
        "max_cutoff": 189.0,
        "cutoff": "TNEA General Cutoff: ~178.0 - 189.0 / 200 (BC: ~175-186, SC/ST: ~156-174)",
        "fees": "Highly Subsidized Govt Fees (~INR 16,000 - 28,000 / year)",
        "placements": "Average CTC: INR 7.2 LPA • Recruiters: Bosch, Zoho, Cognizant, L&T, Murugappa Group",
        "strengths": "Automotive Engineering Testing Rig, VLSI Circuit Lab, Solar Energy Centre",
        "website": "https://gct.ac.in",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "Kumaraguru College of Technology (KCT Coimbatore)",
        "tnea_code": "2712",
        "location": "Saravanampatti, Coimbatore, Tamil Nadu",
        "ranking": "NIRF Top 100 • Premier Autonomous Innovation Campus",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1984",
        "programs": "B.Tech Artificial Intelligence, B.E Mechatronics, B.E Computer Science, B.Tech IT",
        "min_cutoff": 176.0,
        "max_cutoff": 187.5,
        "cutoff": "TNEA General Cutoff: ~176.0 - 187.5 / 200 (BC: ~173-185, SC/ST: ~152-171)",
        "fees": "~INR 65,000 - 85,000 / year",
        "placements": "Average CTC: INR 6.8 LPA • Recruiters: Bosch, Amazon, Alstom, Zoho, Cognizant, Soliton",
        "strengths": "Forge Innovation Accelerator, Garage Automotive Research Lab, AI Edge Computing Cluster",
        "website": "https://www.kct.ac.in",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "Bannari Amman Institute of Technology (BIT Sathy)",
        "tnea_code": "2702",
        "location": "Sathyamangalam, Erode District, Tamil Nadu",
        "ranking": "NIRF Top 120 • Rural Innovation Technology Campus",
        "type": "Tamil Nadu (TNEA Single-Window)",
        "established": "1996",
        "programs": "B.Tech AI & ML, B.E Computer Technology, B.E Electronics & Automation, B.Tech Biotechnology",
        "min_cutoff": 161.0,
        "max_cutoff": 176.0,
        "cutoff": "TNEA General Cutoff: ~161.0 - 176.0 / 200 (BC: ~158-173, SC/ST: ~139-156)",
        "fees": "~INR 65,000 - 85,000 / year",
        "placements": "Average CTC: INR 6.2 LPA • Recruiters: Bosch, Zoho, Soliton Technologies, Cognizant",
        "strengths": "Industry 4.0 Center of Excellence, Biotech Incubator, Special Lab Ecosystem",
        "website": "https://www.bitsathy.ac.in",
        "portal": "https://www.tneaonline.org",
        "stream": "engineering"
    },
    {
        "name": "Indian Institute of Technology Madras (IIT Madras)",
        "tnea_code": "National (JEE Advanced)",
        "location": "Adyar / Guindy, Chennai, Tamil Nadu",
        "ranking": "NIRF Rank #1 in India (Overall & Engineering) for 8 Consecutive Years",
        "type": "Premier National (JoSAA / IITs)",
        "established": "1959",
        "programs": "B.Tech Computer Science, Interdisciplinary Dual Degree in Robotics, B.Tech Electrical",
        "min_cutoff": 195.0,
        "max_cutoff": 200.0,
        "cutoff": "Admissions strictly via JEE Advanced (AIR Top 200 - 1500 for CS/Robotics)",
        "fees": "100% Tuition Waiver for SC/ST/PwD & EWS (< INR 1L income)",
        "placements": "Average CTC: INR 21.5 LPA • Recruiters: Google, Qualcomm, Apple, Microsoft, Jane Street",
        "strengths": "Robert Bosch Centre for Data Science & AI (RBCDSAI), IITM Research Park",
        "website": "https://www.iitm.ac.in",
        "portal": "https://josaa.nic.in",
        "stream": "engineering"
    }
]

MEDICAL_COLLEGES_DATABASE = [
    {
        "name": "Madras Medical College (MMC Chennai)",
        "tnea_code": "Govt Medical College",
        "location": "Park Town, Chennai, Tamil Nadu",
        "ranking": "NIRF Rank #11 in India (Medical) • Oldest Medical College in South India",
        "type": "Tamil Nadu State Government (DME / NEET-UG)",
        "established": "1835",
        "programs": "MBBS, B.Sc Nursing, B.Pharm, BPT (Physiotherapy), Allied Health Sciences",
        "min_cutoff": 91.0,
        "max_cutoff": 98.0,
        "cutoff": "NEET-UG Cutoff: 650+ / 720 (General) • State Quota 625+ (BC: 615+, SC/ST: 520+)",
        "fees": "Highly Subsidized Govt Fees (~INR 13,600 / year for MBBS)",
        "placements": "Mandatory Paid Internship (CRRI): INR 25,000/month • Premier PG residency tracks",
        "strengths": "Rajiv Gandhi Government General Hospital (3,000+ beds), Advanced Clinical Labs",
        "website": "https://mmc.ac.in",
        "portal": "https://tnmedicalselection.net",
        "stream": "medical"
    },
    {
        "name": "Stanley Medical College (SMC Chennai)",
        "tnea_code": "Govt Medical College",
        "location": "Old Jail Road, Royapuram, Chennai, Tamil Nadu",
        "ranking": "Premier State Medical Institution • Globally renowned Hand Surgery Centre",
        "type": "Tamil Nadu State Government (DME / NEET-UG)",
        "established": "1938",
        "programs": "MBBS, B.Sc Radiology & Imaging, B.Sc Medical Lab Technology",
        "min_cutoff": 88.0,
        "max_cutoff": 95.0,
        "cutoff": "NEET-UG Cutoff: 625+ / 720 • State Quota 605+ (BC: 595+, SC/ST: 495+)",
        "fees": "Subsidized Govt Fees (~INR 13,600 / year)",
        "placements": "CRRI Stipend + State healthcare medical officer positions",
        "strengths": "Institute for Research and Rehabilitation of Hand, Liver Transplant Unit",
        "website": "https://stanleymedicalcollege.ac.in",
        "portal": "https://tnmedicalselection.net",
        "stream": "medical"
    },
    {
        "name": "Coimbatore Medical College (CMC Coimbatore)",
        "tnea_code": "Govt Medical College",
        "location": "Avinashi Road, Civil Aerodrome Post, Coimbatore, Tamil Nadu",
        "ranking": "Top Medical Institution in Western Tamil Nadu",
        "type": "Tamil Nadu State Government (DME / NEET-UG)",
        "established": "1966",
        "programs": "MBBS, B.Sc Dialysis Technology, B.Sc Operation Theatre Tech",
        "min_cutoff": 86.0,
        "max_cutoff": 94.0,
        "cutoff": "NEET-UG Cutoff: 610+ / 720 • State Quota 595+ (BC: 585+, SC/ST: 480+)",
        "fees": "Subsidized Govt Fees (~INR 13,600 / year)",
        "placements": "Govt clinical postings, corporate hospital residencies (Ganga Hospital, KMCH)",
        "strengths": "Multispecialty Trauma Care, ICMR Clinical Research Centre",
        "website": "https://cmc-cbe.org.in",
        "portal": "https://tnmedicalselection.net",
        "stream": "medical"
    },
    {
        "name": "Christian Medical College (CMC Vellore)",
        "tnea_code": "Premier Autonomous Institution",
        "location": "Ida Scudder Road, Vellore, Tamil Nadu",
        "ranking": "NIRF Rank #3 in India (Medical Category) • World Renowned Healthcare Center",
        "type": "Private Autonomous / All-India & State Merit",
        "established": "1900",
        "programs": "MBBS, B.Sc Nursing, B.Sc Medical Laboratory Technology, BPT",
        "min_cutoff": 92.0,
        "max_cutoff": 99.0,
        "cutoff": "NEET-UG Cutoff: 640+ / 720 + CMC Institutional Aptitude Assessment",
        "fees": "Subsidized Philanthropic Education (~INR 52,000 / year)",
        "placements": "100% Clinical Fellowship & Global healthcare placement tracks",
        "strengths": "Bio-safety Level 3 Research Labs, Stem Cell Research Centre",
        "website": "https://www.cmch-vellore.edu",
        "portal": "https://admissions.cmcvellore.ac.in",
        "stream": "medical"
    },
    {
        "name": "Tamil Nadu Dr. M.G.R. Medical University (Allied Health)",
        "tnea_code": "State Medical University",
        "location": "Guindy, Chennai, Tamil Nadu",
        "ranking": "Apex State Medical University of Tamil Nadu",
        "type": "State University (Single-Window Allied Health)",
        "established": "1987",
        "programs": "B.Pharm (Pharmacy), BPT (Physiotherapy), B.Sc Cardiac Tech, B.Sc Medical Lab Tech",
        "min_cutoff": 82.0,
        "max_cutoff": 92.0,
        "cutoff": "Single-Window PCB Board Cutoff: ~84.0% - 94.0% (No NEET required for Allied Health)",
        "fees": "Govt/Govt-Aided: ~INR 15,000 - 35,000 / year",
        "placements": "Pharmaceutical R&D (Sun Pharma, Pfizer), Diagnostic networks (Apollo, Dr Lal)",
        "strengths": "Central Research Facility, Molecular Biology Lab, State Pharmacovigilance Centre",
        "website": "https://www.tnmgrmu.ac.in",
        "portal": "https://tnmedicalselection.net",
        "stream": "medical"
    }
]

LAW_COLLEGES_DATABASE = [
    {
        "name": "TNDALU - School of Excellence in Law (SOEL Chennai)",
        "tnea_code": "State Apex Law University",
        "location": "Poompozhil, Greenways Road, Chennai, Tamil Nadu",
        "ranking": "Premier State Law Institution • Bar Council of India Recognized",
        "type": "Tamil Nadu State Law University (Merit Single-Window)",
        "established": "1997",
        "programs": "5-Year Integrated B.A. LL.B (Hons), B.B.A. LL.B (Hons), B.Com. LL.B (Hons)",
        "min_cutoff": 88.0,
        "max_cutoff": 96.0,
        "cutoff": "12th Board Exam Cutoff: ~88.0% - 96.0% (BC: ~86-93%, SC/ST: ~78-88%)",
        "fees": "~INR 45,000 - 65,000 / year",
        "placements": "Average CTC: INR 7.2 LPA • Corporate Law firms (Shardul Amarchand, AZB, Trilegal)",
        "strengths": "Moot Court Society with Global Wins, Alternate Dispute Resolution (ADR) Cell",
        "website": "https://tndalu.ac.in",
        "portal": "https://tndalu.ac.in/admission.html",
        "stream": "law"
    },
    {
        "name": "National Law School of India University (NLSIU Bangalore)",
        "tnea_code": "National Law University",
        "location": "Nagarbhavi, Bangalore, Karnataka",
        "ranking": "NIRF Rank #1 in India for Law for 6 Consecutive Years",
        "type": "Premier National Law University (CLAT-UG)",
        "established": "1987",
        "programs": "B.A. LL.B (Honours) 5-Year Integrated Degree",
        "min_cutoff": 94.0,
        "max_cutoff": 99.5,
        "cutoff": "Admissions strictly via Common Law Admission Test (CLAT AIR Top 1 - 120)",
        "fees": "~INR 2,80,000 / year (Full merit-cum-means waivers for low-income students)",
        "placements": "Average CTC: INR 16.0 LPA • Highest CTC: INR 32 LPA (Magic Circle firms, Supreme Court)",
        "strengths": "Finest Law Library in Asia, Centre for Child and the Law, Global Law Clinics",
        "website": "https://www.nls.ac.in",
        "portal": "https://consortiumofnlus.ac.in",
        "stream": "law"
    },
    {
        "name": "Tamil Nadu National Law University (TNNLU Tiruchirappalli)",
        "tnea_code": "NLU Consortium",
        "location": "Dindigul Main Road, Navalurkottapattu, Tiruchirappalli, Tamil Nadu",
        "ranking": "NIRF Top 25 (Law) • State National Law University",
        "type": "Autonomous National Law University (CLAT-UG)",
        "established": "2012",
        "programs": "5-Year Integrated B.A. LL.B (Hons), B.Com. LL.B (Hons)",
        "min_cutoff": 85.0,
        "max_cutoff": 94.0,
        "cutoff": "Admissions via CLAT-UG (50% State Domicile Quota for Tamil Nadu Students)",
        "fees": "~INR 1,60,000 / year",
        "placements": "Average CTC: INR 6.5 LPA • Corporate legal advisory, Judicial clerkships, LKS",
        "strengths": "Intellectual Property Rights Chair, Legal Aid Clinic across rural Tiruchirappalli",
        "website": "https://tnnlu.ac.in",
        "portal": "https://consortiumofnlus.ac.in",
        "stream": "law"
    },
    {
        "name": "Government Law College (GLC Chennai / Coimbatore / Madurai)",
        "tnea_code": "DoLE Tamil Nadu",
        "location": "Pattabiram, Chennai / Coimbatore / Madurai",
        "ranking": "Historic State Legal Institutions • Alma Mater of Supreme Court Judges",
        "type": "State Government (TNDALU Single-Window)",
        "established": "1891 (GLC Chennai)",
        "programs": "3-Year LL.B / 5-Year Integrated B.A. LL.B",
        "min_cutoff": 78.0,
        "max_cutoff": 88.0,
        "cutoff": "TNDALU Merit Cutoff: ~78.0% - 88.0% (Subsidized for SC/ST/BC)",
        "fees": "Highly Subsidized Govt Fees (~INR 3,000 - 6,000 / year)",
        "placements": "High Court / District Court litigation practice, State Public Prosecutor exams",
        "strengths": "Litigation foundation, Moot Court training, Legal Aid cells",
        "website": "https://glcchennai.ac.in",
        "portal": "https://tndalu.ac.in",
        "stream": "law"
    }
]

ARTS_COLLEGES_DATABASE = [
    {
        "name": "Loyola College (Visual Communication & Media Arts, Chennai)",
        "tnea_code": "Univ of Madras",
        "location": "Nungambakkam, Chennai, Tamil Nadu",
        "ranking": "NIRF Rank #4 in India (Colleges) • Gold Standard in Media & Visual Communication",
        "type": "Tamil Nadu State (Autonomous)",
        "established": "1925",
        "programs": "B.Sc Visual Communication, B.A. English Literature, B.A. Economics, B.Voc Digital Journalism",
        "min_cutoff": 90.0,
        "max_cutoff": 97.0,
        "cutoff": "12th Board Merit Cutoff: ~90.0% - 97.0% + Creative Portfolio Assessment",
        "fees": "~INR 35,000 - 75,000 / year",
        "placements": "Average CTC: INR 5.5 LPA • Media Houses, Ad Agencies (Ogilvy, Sun TV, The Hindu, Zoho)",
        "strengths": "Sound Recording Studio, 4K Multi-Camera Production Floor, Animation Suite",
        "website": "https://www.loyolacollege.edu",
        "portal": "https://erp.loyolacollege.edu/loyolaonline/application/",
        "stream": "arts"
    },
    {
        "name": "National Institute of Design (NID Ahmedabad / AP)",
        "tnea_code": "Institute of National Importance",
        "location": "Paldi, Ahmedabad, Gujarat / Amaravati, AP",
        "ranking": "India's #1 Design Institution • Globally Renowned Design School",
        "type": "Central Govt Autonomous (NID DAT)",
        "established": "1961",
        "programs": "B.Des (Communication Design, Industrial Design, Textile & Apparel Design, UI/UX)",
        "min_cutoff": 92.0,
        "max_cutoff": 99.0,
        "cutoff": "NID Design Aptitude Test (DAT Prelims + DAT Mains)",
        "fees": "~INR 2,20,000 / year (Central Scholarships & Fee Waivers available)",
        "placements": "Average CTC: INR 14.2 LPA • Highest: INR 32 LPA (Google, Apple, Microsoft, Tata Motors)",
        "strengths": "World-class prototyping labs, Material research workshop, UX research center",
        "website": "https://www.nid.edu",
        "portal": "https://admissions.nid.edu",
        "stream": "arts"
    },
    {
        "name": "National Institute of Fashion Technology (NIFT Chennai)",
        "tnea_code": "Ministry of Textiles",
        "location": "Rajiv Gandhi Salai, Taramani, Chennai, Tamil Nadu",
        "ranking": "NIRF Top 5 in Fashion & Apparel Design in India",
        "type": "Statutory Institute under Ministry of Textiles (NIFT Entrance)",
        "established": "1995",
        "programs": "B.Des (Fashion Communication, Fashion Design, Accessory Design), B.F.Tech",
        "min_cutoff": 86.0,
        "max_cutoff": 95.0,
        "cutoff": "NIFT Entrance Exam (Creative Ability Test + General Ability Test + Situation Test)",
        "fees": "~INR 1,80,000 / year (SARTHAK financial aid scheme)",
        "placements": "Average CTC: INR 6.8 LPA • Titan, Madura Fashion, Myntra, Reliance Retail, Raymond",
        "strengths": "Textile Testing Lab, Fashion Photography Studio, CAD Garment Design Suite",
        "website": "https://www.nift.ac.in/chennai",
        "portal": "https://nift.ac.in/admission",
        "stream": "arts"
    },
    {
        "name": "Madras Christian College (BA Journalism & Literature, Chennai)",
        "tnea_code": "University of Madras",
        "location": "Tambaram, Chennai, Tamil Nadu",
        "ranking": "NIRF Top 15 (Colleges) • Historic Humanities Campus",
        "type": "Tamil Nadu State (Autonomous)",
        "established": "1837",
        "programs": "B.A. Journalism, B.A. English Language & Literature, B.A. History, B.A. Political Science",
        "min_cutoff": 86.0,
        "max_cutoff": 94.0,
        "cutoff": "12th Board Merit Cutoff: ~86.0% - 94.0% (BC: ~84-91%, SC/ST: ~76-85%)",
        "fees": "~INR 15,000 - 32,000 / year",
        "placements": "Average CTC: INR 4.8 LPA • The Hindu, Times of India, NDTV, EdTech, Content Strategy",
        "strengths": "Miller Memorial Library (over 100,000 volumes), Campus Radio, Media Archive",
        "website": "https://mcc.edu.in",
        "portal": "https://mcc.edu.in/admissions/",
        "stream": "arts"
    }
]

SCIENCE_COLLEGES_DATABASE = [
    {
        "name": "Indian Institute of Science (IISc Bangalore)",
        "tnea_code": "Institute of Eminence",
        "location": "CV Raman Road, Bangalore, Karnataka",
        "ranking": "NIRF Rank #1 in India (University & Research Category)",
        "type": "Premier National Research Institute",
        "established": "1909",
        "programs": "Bachelor of Science (Research) in Mathematics, Physics, Chemistry, Biology, Earth Science",
        "min_cutoff": 96.0,
        "max_cutoff": 99.8,
        "cutoff": "Admissions via KVPY / JEE Advanced / NEET-UG / IAT (Top Percentile in India)",
        "fees": "Subsidized (~INR 35,000 / year) + Monthly Government Fellowship (KVPY/INSPIRE)",
        "placements": "Global Ph.D. admissions (MIT, Stanford, Cambridge, Max Planck) & R&D Corporate Labs",
        "strengths": "Supercomputer Education & Research Centre, Quantum Materials Lab, Nanotech Hub",
        "website": "https://iisc.ac.in",
        "portal": "https://admissions.iisc.ac.in",
        "stream": "science"
    },
    {
        "name": "Loyola College (B.Sc Mathematics & Statistics, Chennai)",
        "tnea_code": "Univ of Madras",
        "location": "Nungambakkam, Chennai, Tamil Nadu",
        "ranking": "NIRF Rank #4 in India (Colleges) • Apex Pure Sciences Hub",
        "type": "Tamil Nadu State (Autonomous)",
        "established": "1925",
        "programs": "B.Sc Mathematics, B.Sc Statistics, B.Sc Physics, B.Sc Chemistry",
        "min_cutoff": 91.0,
        "max_cutoff": 97.0,
        "cutoff": "12th Board Merit Cutoff: ~91.0% - 97.0% (BC: ~89-95%, SC/ST: ~80-88%)",
        "fees": "Aided: ~INR 12,000/yr • Self-Finance: ~INR 38,000/yr",
        "placements": "Average CTC: INR 6.0 LPA • Mu Sigma, Tiger Analytics, LatentView, TCS, Zoho",
        "strengths": "Statistical Computing Lab, Actuarial Science Training, DST-FIST Supported Labs",
        "website": "https://www.loyolacollege.edu",
        "portal": "https://erp.loyolacollege.edu/loyolaonline/application/",
        "stream": "science"
    },
    {
        "name": "PSG College of Arts and Science (B.Sc Data Science, Coimbatore)",
        "tnea_code": "Bharathiar University",
        "location": "Civil Aerodrome Post, Coimbatore, Tamil Nadu",
        "ranking": "NIRF Rank #20 in India (Colleges) • Applied Sciences Leader",
        "type": "Tamil Nadu State (Govt-Aided & Self-Financed)",
        "established": "1947",
        "programs": "B.Sc Data Science, B.Sc Mathematics, B.Sc Electronics, B.Sc Biotechnology",
        "min_cutoff": 88.0,
        "max_cutoff": 95.0,
        "cutoff": "12th Board Merit Cutoff: ~88.0% - 95.0% (BC: ~86-93%, SC/ST: ~78-86%)",
        "fees": "Aided: ~INR 14,000/yr • Self-Finance: ~INR 42,000/yr",
        "placements": "Average CTC: INR 5.5 LPA • Cognizant, Wipro, Infosys, Robert Bosch, Biocon",
        "strengths": "Data Analytics High-Performance Cluster, Biotechnology Culture Suite",
        "website": "https://www.psgcas.ac.in",
        "portal": "https://www.psgcas.ac.in/admissions/",
        "stream": "science"
    }
]

STREAM_COLLEGES_CATALOG = {
    "commerce": COMMERCE_COLLEGES_DATABASE,
    "engineering": ENGINEERING_COLLEGES_DATABASE,
    "medical": MEDICAL_COLLEGES_DATABASE,
    "law": LAW_COLLEGES_DATABASE,
    "arts": ARTS_COLLEGES_DATABASE,
    "science": SCIENCE_COLLEGES_DATABASE,
}

# Unified Directory of all cataloged institutions
COLLEGES_DATABASE = (
    COMMERCE_COLLEGES_DATABASE +
    ENGINEERING_COLLEGES_DATABASE +
    MEDICAL_COLLEGES_DATABASE +
    LAW_COLLEGES_DATABASE +
    ARTS_COLLEGES_DATABASE +
    SCIENCE_COLLEGES_DATABASE
)


def get_top_5_colleges_for_marks(
    marks_pct: float,
    category: str = "general",
    direct_cutoff: float = None,
    stream: str = "engineering"
) -> list[dict]:
    """Dynamically matches and ranks top 5 colleges tailored to student's academic stream, marks, and category."""
    st_key = detect_stream_key(stream)
    colleges_pool = STREAM_COLLEGES_CATALOG.get(st_key, ENGINEERING_COLLEGES_DATABASE)

    is_engineering = (st_key == "engineering")

    if is_engineering:
        if direct_cutoff is not None:
            student_score = min(200.0, max(60.0, float(direct_cutoff)))
        else:
            student_score = min(200.0, max(60.0, float(marks_pct) * 2.0))
    else:
        if direct_cutoff is not None:
            student_score = min(100.0, max(35.0, float(direct_cutoff)))
        else:
            student_score = min(100.0, max(35.0, float(marks_pct)))

    cat_lower = str(category).lower()
    if is_engineering:
        if "sc" in cat_lower or "st" in cat_lower:
            cat_bonus = 14.0
            cat_label = "SC / ST Quota (+14 Cutoff Benefit)"
        elif "mbc" in cat_lower or "dnc" in cat_lower:
            cat_bonus = 6.0
            cat_label = "MBC / DNC Quota (+6 Cutoff Benefit)"
        elif "bc" in cat_lower or "obc" in cat_lower:
            cat_bonus = 3.0
            cat_label = "BC Quota (+3 Cutoff Benefit)"
        else:
            cat_bonus = 0.0
            cat_label = "Open Competition (General Merit)"
    else:
        if "sc" in cat_lower or "st" in cat_lower:
            cat_bonus = 7.0
            cat_label = "SC / ST Quota (+7% Benefit)"
        elif "mbc" in cat_lower or "dnc" in cat_lower:
            cat_bonus = 3.0
            cat_label = "MBC / DNC Quota (+3% Benefit)"
        elif "bc" in cat_lower or "obc" in cat_lower:
            cat_bonus = 1.5
            cat_label = "BC Quota (+1.5% Benefit)"
        else:
            cat_bonus = 0.0
            cat_label = "Open Competition (General Merit)"

    effective_score = student_score + cat_bonus
    reach_tolerance = 6.5 if is_engineering else 4.0
    target_tolerance = 2.0 if is_engineering else 1.5

    scored_colleges = []
    for c in colleges_pool:
        midpoint = (c["min_cutoff"] + c["max_cutoff"]) / 2.0
        diff = effective_score - midpoint

        if effective_score < c["min_cutoff"]:
            diff_to_min = c["min_cutoff"] - effective_score
            if diff_to_min <= reach_tolerance:
                fit_tier = "🌟 Dream College (Aspirational Reach)"
                fit_badge = "chip-amber"
                chance_pct = max(35, int(70 - (diff_to_min * (5.5 if is_engineering else 7.0))))
                tier_order = 1
            else:
                fit_tier = "High Reach"
                fit_badge = "chip-slate"
                chance_pct = 20
                tier_order = 4
        elif c["min_cutoff"] <= effective_score <= c["max_cutoff"] + target_tolerance:
            fit_tier = "🎯 Target Match (Optimal Admission Fit)"
            fit_badge = "chip-green"
            chance_pct = min(94, int(75 + ((effective_score - c["min_cutoff"]) / (c["max_cutoff"] - c["min_cutoff"] + 0.1) * 18)))
            tier_order = 2
        else:
            fit_tier = "🛡️ Safe Institution (High Probability / Assured)"
            fit_badge = "chip-blue"
            chance_pct = 97
            tier_order = 3

        scored_colleges.append({
            **c,
            "fit_tier": fit_tier,
            "fit_badge": fit_badge,
            "chance_pct": chance_pct,
            "tier_order": tier_order,
            "effective_cutoff": effective_score,
            "student_cutoff": student_score,
            "cat_label": cat_label,
            "diff_from_target": abs(effective_score - midpoint)
        })

    dreams = [c for c in scored_colleges if c["tier_order"] == 1]
    targets = [c for c in scored_colleges if c["tier_order"] == 2]
    safes = [c for c in scored_colleges if c["tier_order"] == 3]

    dreams.sort(key=lambda x: x["diff_from_target"])
    targets.sort(key=lambda x: x["diff_from_target"])
    safes.sort(key=lambda x: x["diff_from_target"])

    final_top_5 = []
    if dreams:
        final_top_5.append(dreams[0])
    final_top_5.extend(targets[:3])
    if safes:
        final_top_5.append(safes[0])

    if len(final_top_5) < 5:
        existing_names = {c["name"] for c in final_top_5}
        remaining = [c for c in sorted(scored_colleges, key=lambda x: x["diff_from_target"]) if c["name"] not in existing_names]
        final_top_5.extend(remaining[: 5 - len(final_top_5)])

    return final_top_5[:5]


def render_colleges_and_institutions_view(profile: dict = None, key_prefix: str = "main"):
    """Renders the comprehensive Top 5 Colleges recommendation engine and directory tailored to the student's stream."""
    if profile is None:
        profile = {}

    # Extract baseline student stream
    detected_stream = detect_stream_key(profile)
    if detected_stream == "engineering" and st.session_state.get("primary_target_goal"):
        goal_st = detect_stream_key(st.session_state.get("primary_target_goal"))
        if goal_st != "engineering":
            detected_stream = goal_st
    if detected_stream == "engineering" and st.session_state.get("loaded_session"):
        rec_snippet = str(st.session_state["loaded_session"].get("recommendation", ""))[:500]
        rec_st = detect_stream_key(rec_snippet)
        if rec_st != "engineering":
            detected_stream = rec_st

    stream_display_options = [
        "💼 Commerce & Management (B.Com / BBA / CA / Finance)",
        "⚙️ Engineering & Technology (B.E / B.Tech)",
        "🩺 Medical & Allied Health Sciences (MBBS / BDS / B.Pharm / Nursing)",
        "🎨 Arts, Media, Design & Humanities (BA / VisCom / Design)",
        "⚖️ Law & Legal Studies (BA LL.B / BBA LL.B)",
        "🔬 Pure Science & Mathematics (B.Sc / Data Science)"
    ]
    stream_idx_map = {
        "commerce": 0,
        "engineering": 1,
        "medical": 2,
        "arts": 3,
        "law": 4,
        "science": 5
    }
    default_stream_idx = stream_idx_map.get(detected_stream, 1)

    # Extract baseline student marks & category
    raw_marks = profile.get("board_percentage")
    raw_cgpa = profile.get("cgpa")
    if raw_marks:
        try:
            clean_m = re.sub(r"[^\d.]", "", str(raw_marks))
            default_marks = float(clean_m) if clean_m else 85.0
        except Exception:
            default_marks = 85.0
    elif raw_cgpa:
        try:
            clean_c = re.sub(r"[^\d.]", "", str(raw_cgpa))
            default_marks = float(clean_c) * 10.0 if clean_c else 85.0
        except Exception:
            default_marks = 85.0
    else:
        default_marks = 85.0

    student_cat = str(profile.get("category", "general")).lower()
    cat_options = ["General (OC)", "BC (Backward Class)", "MBC / DNC", "SC / ST"]
    if "sc" in student_cat or "st" in student_cat:
        cat_idx = 3
    elif "mbc" in student_cat or "dnc" in student_cat:
        cat_idx = 2
    elif "bc" in student_cat or "obc" in student_cat:
        cat_idx = 1
    else:
        cat_idx = 0

    # Interactive Stream & Cutoff Calculator Card
    with st.expander("🎛️ Student Marks & Academic Cutoff Engine (Stream-Calibrated)", expanded=True):
        col_st_sel, col_cat_sel = st.columns([1.5, 1])
        with col_st_sel:
            selected_stream_label = st.selectbox(
                "🎯 Select Academic Stream / Field of Study:",
                stream_display_options,
                index=default_stream_idx,
                key=f"{key_prefix}_stream_select",
                help="Institutions and cutoff scoring formulas automatically calibrate to your chosen discipline."
            )
            current_stream = "commerce" if "Commerce" in selected_stream_label else ("engineering" if "Engineering" in selected_stream_label else ("medical" if "Medical" in selected_stream_label else ("law" if "Law" in selected_stream_label else ("arts" if "Arts" in selected_stream_label else "science"))))

        with col_cat_sel:
            selected_cat_str = st.selectbox(
                "Select Reservation Category / Quota:",
                cat_options,
                index=cat_idx,
                key=f"{key_prefix}_cat_select",
                help="Reservation quota provides concession benefits in state and central single-window counseling."
            )

        if current_stream == "commerce":
            input_mode = st.radio(
                "Select Academic Marks Input Mode:",
                [
                    "📐 Enter Commerce Subject Marks (Accountancy + Commerce + Economics + Maths/Comp)",
                    "📊 Enter Overall 12th Board Percentage (%)",
                    "🎯 Enter Known Merit Score Directly (/100)"
                ],
                horizontal=True,
                key=f"{key_prefix}_marks_input_mode_comm"
            )

            if "Subject Marks" in input_mode:
                st.markdown("<p style='font-size: 0.85rem; color: #475569; margin-bottom: 6px;'>Enter your 12th standard commerce subject marks out of 100 to compute your official Tamil Nadu Arts & Science (TNGASA / University of Madras) cutoff:</p>", unsafe_allow_html=True)
                col_acc, col_comm, col_eco, col_mat = st.columns(4)
                with col_acc:
                    acc_val = st.number_input("📊 Accountancy (/100):", min_value=0.0, max_value=100.0, value=float(min(100.0, default_marks)), step=0.5, key=f"{key_prefix}_acc_val")
                with col_comm:
                    comm_val = st.number_input("💼 Commerce / Business (/100):", min_value=0.0, max_value=100.0, value=float(min(100.0, default_marks)), step=0.5, key=f"{key_prefix}_comm_val")
                with col_eco:
                    eco_val = st.number_input("📈 Economics (/100):", min_value=0.0, max_value=100.0, value=float(min(100.0, default_marks)), step=0.5, key=f"{key_prefix}_eco_val")
                with col_mat:
                    mat_val = st.number_input("🧮 Business Maths / Comp (/100):", min_value=0.0, max_value=100.0, value=float(min(100.0, default_marks)), step=0.5, key=f"{key_prefix}_mat_val")

                calc_cutoff = (acc_val + comm_val + eco_val + mat_val) / 4.0
                user_marks = calc_cutoff

                render_html(f"""
                <div style="background: #EFF6FF; border: 1.5px solid #BFDBFE; border-radius: 10px; padding: 12px 16px; margin: 12px 0;">
                    <div style="font-weight: 700; color: #1E40AF; font-size: 0.88rem; margin-bottom: 4px;">
                        🧮 Official Commerce Admission Cutoff: <code>(Accountancy + Commerce + Economics + Business Maths) ÷ 4</code>
                    </div>
                    <div style="font-size: 0.92rem; color: #1E293B;">
                        <strong>Step-by-step arithmetic:</strong> ({acc_val:.1f} + {comm_val:.1f} + {eco_val:.1f} + {mat_val:.1f}) ÷ 4 = <strong style="color: #2563EB; font-size: 1.1rem;">{calc_cutoff:.2f}%</strong>
                    </div>
                </div>
                """)
            elif "Percentage" in input_mode:
                user_marks = st.slider("Your 12th Board Aggregate Percentage (%):", min_value=50.0, max_value=100.0, value=float(min(100.0, max(50.0, default_marks))), step=0.5, key=f"{key_prefix}_comm_slider_pct")
                calc_cutoff = user_marks
            else:
                calc_cutoff = st.number_input("Enter Known Merit Score / Cutoff (%):", min_value=40.0, max_value=100.0, value=float(min(100.0, max(40.0, default_marks))), step=0.25, key=f"{key_prefix}_comm_direct_cut")
                user_marks = calc_cutoff

            cat_bonus_num = 7.0 if "SC" in selected_cat_str else (3.0 if "MBC" in selected_cat_str else (1.5 if "BC" in selected_cat_str else 0.0))
            cat_concession = f"+{cat_bonus_num:.1f}% Benefit" if cat_bonus_num > 0 else "General Merit"
            effective_cutoff = min(100.0, calc_cutoff + cat_bonus_num)

            render_html(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin-top: 8px;">
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Commerce Board Cutoff</div>
                    <div style="font-size: 1.35rem; color: #059669; font-weight: 800;">{calc_cutoff:.2f}%</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Active Stream</div>
                    <div style="font-size: 1.15rem; color: #1D4ED8; font-weight: 700;">💼 Commerce & B.Com</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Effective Quota Score</div>
                    <div style="font-size: 1.2rem; color: #6D28D9; font-weight: 800;">{effective_cutoff:.2f}%</div>
                    <div style="font-size: 0.72rem; color: #166534; font-weight: 600;">{selected_cat_str} ({cat_concession})</div>
                </div>
            </div>
            """)

        elif current_stream == "engineering":
            input_mode = st.radio(
                "Select Academic Marks Input Mode:",
                [
                    "📐 Enter Subject Marks (Maths + Physics + Chemistry)",
                    "📊 Enter Overall Board Percentage (%)",
                    "🎯 Enter Known Cutoff Directly (/200)"
                ],
                horizontal=True,
                key=f"{key_prefix}_marks_input_mode_eng"
            )

            if "Subject Marks" in input_mode:
                st.markdown("<p style='font-size: 0.85rem; color: #475569; margin-bottom: 6px;'>Enter your 12th standard subject marks out of 100 to compute your official single-window TNEA cutoff:</p>", unsafe_allow_html=True)
                col_m, col_p, col_c = st.columns(3)
                with col_m:
                    m_score = st.number_input("📐 Mathematics (/100):", min_value=0.0, max_value=100.0, value=float(min(100.0, default_marks)), step=0.5, key=f"{key_prefix}_maths_val")
                with col_p:
                    p_score = st.number_input("⚡ Physics (/100):", min_value=0.0, max_value=100.0, value=float(min(100.0, default_marks)), step=0.5, key=f"{key_prefix}_phys_val")
                with col_c:
                    c_score = st.number_input("🧪 Chemistry (/100):", min_value=0.0, max_value=100.0, value=float(min(100.0, default_marks)), step=0.5, key=f"{key_prefix}_chem_val")

                calc_cutoff = m_score + (p_score / 2.0) + (c_score / 2.0)
                user_marks = calc_cutoff / 2.0

                render_html(f"""
                <div style="background: #EFF6FF; border: 1.5px solid #BFDBFE; border-radius: 10px; padding: 12px 16px; margin: 12px 0;">
                    <div style="font-weight: 700; color: #1E40AF; font-size: 0.88rem; margin-bottom: 4px;">
                        🧮 Official TNEA Cutoff Formula: <code>Maths + (Physics / 2) + (Chemistry / 2)</code>
                    </div>
                    <div style="font-size: 0.92rem; color: #1E293B;">
                        <strong>Step-by-step calculation:</strong> {m_score:.1f} + ({p_score:.1f} ÷ 2) + ({c_score:.1f} ÷ 2) = <strong style="color: #2563EB; font-size: 1.1rem;">{calc_cutoff:.2f} / 200.0</strong>
                    </div>
                </div>
                """)
            elif "Percentage" in input_mode:
                user_marks = st.slider("Your Overall Board Exam Score (%):", min_value=50.0, max_value=100.0, value=float(min(100.0, max(50.0, default_marks))), step=0.5, key=f"{key_prefix}_eng_slider_marks")
                calc_cutoff = user_marks * 2.0
            else:
                calc_cutoff = st.number_input("Enter Known TNEA Single-Window Cutoff (/200):", min_value=60.0, max_value=200.0, value=float(min(200.0, max(60.0, default_marks * 2.0))), step=0.25, key=f"{key_prefix}_eng_direct_cutoff_val")
                user_marks = calc_cutoff / 2.0

            cat_bonus_num = 14.0 if "SC" in selected_cat_str else (6.0 if "MBC" in selected_cat_str else (3.0 if "BC" in selected_cat_str else 0.0))
            cat_concession = f"+{cat_bonus_num:.0f} Cutoff Benefit" if cat_bonus_num > 0 else "General Merit"
            effective_cutoff = min(200.0, calc_cutoff + cat_bonus_num)

            render_html(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin-top: 8px;">
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Calculated TNEA Cutoff</div>
                    <div style="font-size: 1.35rem; color: #059669; font-weight: 800;">{calc_cutoff:.2f} <span style="font-size: 0.8rem; color: #64748B;">/ 200</span></div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Equivalent Board %</div>
                    <div style="font-size: 1.2rem; color: #1D4ED8; font-weight: 800;">{user_marks:.1f}%</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Effective Quota Score</div>
                    <div style="font-size: 1.2rem; color: #6D28D9; font-weight: 800;">{effective_cutoff:.2f} <span style="font-size: 0.75rem; color: #64748B;">/ 200</span></div>
                    <div style="font-size: 0.72rem; color: #166534; font-weight: 600;">{selected_cat_str} ({cat_concession})</div>
                </div>
            </div>
            """)

        else:
            # Generic Stream (Medical, Law, Arts, Science)
            user_marks = st.slider("Your 12th Board Aggregate Percentage (%) / Entrance Equivalent:", min_value=50.0, max_value=100.0, value=float(min(100.0, max(50.0, default_marks))), step=0.5, key=f"{key_prefix}_gen_slider_marks")
            calc_cutoff = user_marks
            cat_bonus_num = 7.0 if "SC" in selected_cat_str else (3.0 if "MBC" in selected_cat_str else (1.5 if "BC" in selected_cat_str else 0.0))
            effective_cutoff = min(100.0, calc_cutoff + cat_bonus_num)

            render_html(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin-top: 8px;">
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Academic Board Score</div>
                    <div style="font-size: 1.35rem; color: #059669; font-weight: 800;">{user_marks:.1f}%</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Target Discipline</div>
                    <div style="font-size: 1.15rem; color: #1D4ED8; font-weight: 700;">{current_stream.capitalize()}</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Quota Effective Score</div>
                    <div style="font-size: 1.2rem; color: #6D28D9; font-weight: 800;">{effective_cutoff:.1f}%</div>
                    <div style="font-size: 0.72rem; color: #166534; font-weight: 600;">{selected_cat_str} (+{cat_bonus_num:.1f}% Benefit)</div>
                </div>
            </div>
            """)

    # View Mode Selector
    view_mode = st.radio(
        "Select Institutional View:",
        ["🎯 Top 5 Colleges Matched to Your Marks", "🏛️ All Premier Institutions Catalog (Full Directory)"],
        horizontal=True,
        key=f"{key_prefix}_inst_view_mode"
    )

    if view_mode == "🎯 Top 5 Colleges Matched to Your Marks":
        top_5 = get_top_5_colleges_for_marks(user_marks, selected_cat_str, direct_cutoff=calc_cutoff, stream=current_stream)

        score_label = f"{calc_cutoff:.2f} Cutoff / 200" if current_stream == "engineering" else f"{calc_cutoff:.1f}% Aggregate Score"
        st.markdown(f"##### 🎯 Top 5 {current_stream.capitalize()} Colleges for {score_label}")
        st.caption("Curated balanced admission portfolio: 1 Aspirational Dream, 3 High-Probability Target Matches, and 1 Safe Assured Institution.")

        for rank, col in enumerate(top_5, 1):
            tier_color = "#F59E0B" if "Dream" in col["fit_tier"] else ("#10B981" if "Target" in col["fit_tier"] else "#3B82F6")
            chance_val = col.get("chance_pct", 85)
            progress_width = min(100, max(10, chance_val))

            code_badge = f'<span class="chip chip-blue" style="font-size: 0.72rem;">Code: {col["tnea_code"]}</span>' if str(col.get("tnea_code","")).isdigit() else f'<span class="chip chip-amber" style="font-size: 0.72rem;">{col.get("tnea_code", "Merit")}</span>'

            render_html(f"""
            <div class="glass-card" style="border-left: 6px solid {tier_color}; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <span style="background: {tier_color}; color: white; font-weight: 800; border-radius: 6px; padding: 2px 8px; font-size: 0.78rem;">#{rank}</span>
                            <h4 style="margin: 0; color: #0F172A; font-size: 1.18rem;">{col['name']}</h4>
                            {code_badge}
                        </div>
                        <div style="font-size: 0.83rem; color: #64748B; margin-top: 3px;">
                            📍 {col['location']} • <strong style="color: #6D28D9;">{col['ranking']}</strong>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span class="chip {col['fit_badge']}" style="font-size: 0.8rem; font-weight: 700;">{col['fit_tier']}</span>
                        <div style="margin-top: 5px; font-size: 0.8rem; color: #475569;">
                            Admission Probability: <strong style="color: {tier_color};">{chance_val}%</strong>
                        </div>
                        <div style="width: 140px; background: #E2E8F0; height: 6px; border-radius: 3px; overflow: hidden; margin-top: 4px; display: inline-block;">
                            <div style="width: {progress_width}%; background: {tier_color}; height: 100%;"></div>
                        </div>
                    </div>
                </div>

                <div style="margin: 10px 0; font-size: 0.9rem; color: #1E293B;">
                    <strong>Recommended Degree Programs:</strong> {col['programs']}
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Cutoff Score Bracket</div>
                        <div style="font-size: 0.84rem; color: #1E40AF; font-weight: 600; margin-top: 2px;">{col['cutoff']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Tuition & Affordability</div>
                        <div style="font-size: 0.84rem; color: #166534; font-weight: 600; margin-top: 2px;">{col['fees']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Placement Track Record</div>
                        <div style="font-size: 0.84rem; color: #0F172A; font-weight: 600; margin-top: 2px;">{col['placements']}</div>
                    </div>
                </div>

                <div style="font-size: 0.84rem; color: #475569; margin-bottom: 12px;">
                    <strong>🔬 Key Facilities & Strengths:</strong> {col['strengths']}
                </div>

                <div style="display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #F1F5F9; padding-top: 10px;">
                    <a href="{col['website']}" target="_blank" style="background: #F1F5F9; color: #334155; text-decoration: none; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; border: 1px solid #CBD5E1;">
                        Official Website ↗
                    </a>
                    <a href="{col['portal']}" target="_blank" style="background: #6D28D9; color: white; text-decoration: none; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">
                        Admissions Portal ↗
                    </a>
                </div>
            </div>
            """)

    else:
        col_stream_filter = st.radio(
            "Filter Catalog by Discipline:",
            ["All Disciplines (40+ Cataloged)", "💼 Commerce & Management", "⚙️ Engineering & Technology", "🩺 Medical & Health", "⚖️ Law & Legal", "🎨 Arts & Media", "🔬 Pure Science"],
            horizontal=True,
            key=f"{key_prefix}_inst_tier_filter"
        )

        catalog_search = st.text_input(
            "🔍 Search College Catalog (Name, District, Degree, or Location):",
            placeholder="e.g. Loyola, Commerce, Coimbatore, Anna University, VisCom...",
            key=f"{key_prefix}_catalog_search"
        ).strip().lower()

        filter_key = None
        if "Commerce" in col_stream_filter: filter_key = "commerce"
        elif "Engineering" in col_stream_filter: filter_key = "engineering"
        elif "Medical" in col_stream_filter: filter_key = "medical"
        elif "Law" in col_stream_filter: filter_key = "law"
        elif "Arts" in col_stream_filter: filter_key = "arts"
        elif "Science" in col_stream_filter: filter_key = "science"

        active_db = STREAM_COLLEGES_CATALOG.get(filter_key, COLLEGES_DATABASE) if filter_key else COLLEGES_DATABASE

        filtered_courses = [
            inst for inst in active_db
            if not catalog_search or catalog_search in inst["name"].lower() or catalog_search in inst["programs"].lower() or catalog_search in inst["location"].lower() or catalog_search in str(inst.get("tnea_code","")).lower()
        ]

        for inst in filtered_courses:
            code_badge = f'<span class="chip chip-blue" style="font-size: 0.72rem;">Code: {inst.get("tnea_code","N/A")}</span>' if str(inst.get("tnea_code","")).isdigit() else f'<span class="chip chip-amber" style="font-size: 0.72rem;">{inst.get("tnea_code","Merit")}</span>'

            render_html(f"""
            <div class="glass-card" style="border-left: 6px solid #8B5CF6; margin-bottom: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <h4 style="margin: 0; color: #0F172A; font-size: 1.22rem;">{inst['name']}</h4>
                            {code_badge}
                        </div>
                        <span style="font-size: 0.84rem; color: #64748B;">📍 {inst['location']} • <strong style="color: #6D28D9;">{inst['ranking']}</strong></span>
                    </div>
                    <span class="chip chip-purple">{inst['type']}</span>
                </div>

                <div style="margin: 10px 0; font-size: 0.92rem; color: #1E293B;">
                    <strong>Offered Specializations:</strong> {inst['programs']}
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Admissions & Cutoff</div>
                        <div style="font-size: 0.84rem; color: #1E40AF; font-weight: 600; margin-top: 2px;">{inst['cutoff']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Tuition & Affordability</div>
                        <div style="font-size: 0.84rem; color: #166534; font-weight: 600; margin-top: 2px;">{inst['fees']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Placement Track Record</div>
                        <div style="font-size: 0.84rem; color: #0F172A; font-weight: 600; margin-top: 2px;">{inst['placements']}</div>
                    </div>
                </div>

                <div style="font-size: 0.85rem; color: #475569; margin-bottom: 14px;">
                    <strong>🔬 Labs & Key Strengths:</strong> {inst['strengths']}
                </div>

                <div style="display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #F1F5F9; padding-top: 10px;">
                    <a href="{inst['website']}" target="_blank" style="background: #F1F5F9; color: #334155; text-decoration: none; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; border: 1px solid #CBD5E1;">
                        Official Website ↗
                    </a>
                    <a href="{inst['portal']}" target="_blank" style="background: #6D28D9; color: white; text-decoration: none; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">
                        Admissions Portal ↗
                    </a>
                </div>
            </div>
            """)


def parse_structured_courses(courses_text: str) -> list[dict]:
    """Provides curated, high-fidelity college recommendation profiles for top institutions."""
    st_key = detect_stream_key(courses_text) if courses_text else None
    if st_key and st_key in STREAM_COLLEGES_CATALOG:
        return STREAM_COLLEGES_CATALOG[st_key]
    return COLLEGES_DATABASE


def parse_structured_schemes(schemes_text: str) -> list[dict]:
    """Parses welfare and government schemes into interactive benefit cards."""
    return [
        {
            "name": "Naan Mudhalvan Skill Initiative (Government of Tamil Nadu)",
            "authority": "Tamil Nadu Skill Development Corporation (TNSDC)",
            "benefit": "Free industry-aligned training in AI, Robotics, Data Analytics, and Cloud Computing with corporate placement drives.",
            "eligibility": "Enrolled engineering and arts & science college students in Tamil Nadu.",
            "portal": "https://www.naanmudhalvan.tn.gov.in"
        },
        {
            "name": "Free Higher Education Scheme for SC / ST Students",
            "authority": "Adi Dravidar and Tribal Welfare Department (Tamil Nadu)",
            "benefit": "100% Tuition Fee Exemption and special book grant in Government and Govt-Aided engineering colleges.",
            "eligibility": "SC / ST students admitted through single-window TNEA state counseling with family income up to INR 2.5 Lakhs.",
            "portal": "https://escholarship.tn.gov.in"
        },
        {
            "name": "7.5% Preferential Quota for Government School Students",
            "authority": "Higher Education Department, Government of Tamil Nadu",
            "benefit": "7.5% horizontal reservation in professional engineering admissions + 100% college fee, hostel and counseling fee paid by government.",
            "eligibility": "Students who studied from 6th to 12th standard in Tamil Nadu Government schools.",
            "portal": "https://www.tneaonline.org"
        }
    ]


# ---------------------------------------------------------------------------
# DEDICATED SCHOLARSHIPS & FINANCIAL AID COMPONENT
# ---------------------------------------------------------------------------
def render_scholarships_and_aid_view(profile: dict = None, session: dict = None, key_prefix: str = "sch"):
    """
    Renders the dedicated, interactive Scholarships & Financial Aid matching engine.
    Supports real-time criteria simulation, eligibility scoring, quota checks, and direct application portals.
    """
    if profile is None:
        profile = {}
    if session is None:
        session = {}

    # Extract baseline income safely
    raw_inc = profile.get("annual_income")
    clean_inc = 200000
    if raw_inc is not None:
        try:
            if isinstance(raw_inc, (int, float)):
                clean_inc = int(raw_inc)
            else:
                s = str(raw_inc).lower()
                if "lakh" in s or "lac" in s:
                    np = re.sub(r"[^\d.]", "", s)
                    clean_inc = int(float(np) * 100000) if np else 200000
                else:
                    np = re.sub(r"[^\d.]", "", s)
                    clean_inc = int(float(np)) if np else 200000
        except Exception:
            clean_inc = 200000

    # Extract baseline category
    student_cat = str(profile.get("category", "bc")).lower()
    cat_options = [
        "BC (Backward Class)",
        "MBC / DNC (Most Backward Class)",
        "SC (Scheduled Caste)",
        "ST (Scheduled Tribe)",
        "General / Open Competition (OC)",
        "EWS (Economically Weaker Section)"
    ]
    cat_idx = 0
    if "sc" in student_cat:
        cat_idx = 2
    elif "st" in student_cat:
        cat_idx = 3
    elif "mbc" in student_cat or "dnc" in student_cat:
        cat_idx = 1
    elif "ews" in student_cat:
        cat_idx = 5
    elif "general" in student_cat or "oc" in student_cat:
        cat_idx = 4
    else:
        cat_idx = 0

    with st.expander("🎛️ Scholarship Eligibility Simulator & Criteria Calibration", expanded=True):
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            selected_cat_label = st.selectbox(
                "Social Reservation Category:",
                cat_options,
                index=cat_idx,
                key=f"{key_prefix}_category_select"
            )
            domicile_option = st.selectbox(
                "State Domicile / Residence:",
                ["Tamil Nadu (State + Central Quotas)", "All-India / Other State (Central Quota Only)"],
                index=0 if "tamil nadu" in str(profile.get("state", "Tamil Nadu")).lower() else 1,
                key=f"{key_prefix}_domicile_select"
            )
        with sim_col2:
            selected_income = st.slider(
                "Annual Family Income (₹):",
                min_value=50000,
                max_value=1200000,
                value=max(50000, min(1200000, clean_inc)),
                step=25000,
                key=f"{key_prefix}_income_slider"
            )
            st.caption(f"Selected: **₹{selected_income:,} / year** (Affects fee waiver & income ceiling eligibility)")

        st.markdown("**Special Eligibility Quotas & Focus Groups (Check all that apply):**")
        sp_col1, sp_col2, sp_col3, sp_col4 = st.columns(4)
        with sp_col1:
            is_girl = st.checkbox("👩 Girl Student", value=bool(profile.get("is_girl", False)), key=f"{key_prefix}_is_girl", help="Unlocks AICTE Pragati (₹50k/yr) & Pudhumai Penn")
        with sp_col2:
            is_first_grad = st.checkbox("🎓 First Graduate", value=bool(profile.get("is_first_graduate", False)), key=f"{key_prefix}_is_first_grad", help="Unlocks TN DoTE 100% Tuition Fee Concession")
        with sp_col3:
            is_gov_school = st.checkbox("🏫 TN Govt School (6-12)", value=bool(profile.get("is_gov_school", False)), key=f"{key_prefix}_is_gov_school", help="Unlocks Pudhumai Penn / Tamizh Pudhalvan monthly grant")
        with sp_col4:
            is_pwd = st.checkbox("♿ Specially-Abled (40%+)", value=bool(profile.get("is_specially_abled", False)), key=f"{key_prefix}_is_pwd", help="Unlocks AICTE Saksham (₹50k/yr) grant")

    cat_map = {
        "BC (Backward Class)": "bc",
        "MBC / DNC (Most Backward Class)": "mbc",
        "SC (Scheduled Caste)": "sc",
        "ST (Scheduled Tribe)": "st",
        "General / Open Competition (OC)": "general",
        "EWS (Economically Weaker Section)": "ews"
    }
    sim_cat = cat_map.get(selected_cat_label, "bc")

    simulated_profile = {
        "category": sim_cat,
        "annual_income": selected_income,
        "state": "Tamil Nadu" if "tamil nadu" in domicile_option.lower() else "Other",
        "education_stage": str(profile.get("education_stage", "undergraduate")),
        "is_girl": is_girl,
        "is_first_graduate": is_first_grad,
        "is_gov_school": is_gov_school,
        "is_specially_abled": is_pwd,
    }

    raw_chunks = session.get("scholarships", []) if session else []
    evaluated_scholarships = scholarship_agent.evaluate_scholarships(raw_chunks, simulated_profile)

    # Active Profile Filter Bar
    special_badges = []
    if is_girl:
        special_badges.append('<span class="chip chip-purple">👩 Girl Student Scheme</span>')
    if is_first_grad:
        special_badges.append('<span class="chip chip-blue">🎓 First Graduate Concession</span>')
    if is_gov_school:
        special_badges.append('<span class="chip chip-green">🏫 TN Govt School Quota</span>')
    if is_pwd:
        special_badges.append('<span class="chip chip-amber">♿ Specially-Abled Support</span>')
    special_html = " ".join(special_badges)

    domicile_short = "Tamil Nadu" if "tamil nadu" in domicile_option.lower() else "All-India"

    render_html(f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 20px; margin-bottom: 20px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
        <span style="font-weight: 700; color: #1E3A8A; font-size: 0.88rem;">Active Evaluation Criteria:</span>
        <span class="chip chip-amber">Category: {sim_cat.upper()}</span>
        <span class="chip chip-green">Family Income: ₹{selected_income:,} / yr</span>
        <span class="chip chip-blue">State: {domicile_short}</span>
        {special_html}
    </div>
    """)

    # 4-Column Metrics KPI Row
    eligible_count = len([s for s in evaluated_scholarships if s.get("eligibility_status") == "eligible"])
    potential_count = len([s for s in evaluated_scholarships if s.get("eligibility_status") != "eligible"])

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("100% Eligible Schemes", f"{eligible_count} Schemes", delta="Direct Fit ✓")
    with col_m2:
        st.metric("Potential / Secondary", f"{potential_count} Schemes", delta="Review Norms")
    with col_m3:
        st.metric("Max Tuition Waiver", "100% Fee Exemption", delta="Government Norms")
    with col_m4:
        st.metric("Disbursement Mode", "Direct Benefit Transfer (DBT)", delta="Aadhaar-Seeded")

    st.markdown("---")

    # Filter Tabs
    sch_tab1, sch_tab2, sch_tab3, sch_tab4 = st.tabs([
        f"🌟 All Matching Schemes ({len(evaluated_scholarships)})",
        "🏛️ Tamil Nadu State Welfare & Waivers",
        "🇮🇳 Central Govt & AICTE Schemes",
        "🏢 Corporate Merit & CSR Grants"
    ])

    def _render_cards(sch_list):
        if not sch_list:
            st.info("No scholarships match this specific category filter. View 'All Matching Schemes' above.")
            return

        for sc in sch_list:
            is_el = (sc.get("eligibility_status") == "eligible")
            status_chip = '<span class="chip chip-green" style="font-weight: 700; font-size: 0.8rem;">✓ 100% Eligible</span>' if is_el else '<span class="chip chip-amber" style="font-weight: 700; font-size: 0.8rem;">⚡ Potentially Eligible</span>'
            border_color = "#10B981" if is_el else "#F59E0B"
            portal_url = sc.get("portal_url", "https://scholarships.gov.in")
            portal_name = sc.get("portal_name", "National Scholarship Portal")

            docs_html = "".join(f'<li style="font-size: 0.84rem; color: #475569; margin-bottom: 4px;">{d}</li>' for d in sc.get("documents", []))
            recs_html = "".join(f'<li style="font-size: 0.84rem; color: #1E3A8A; font-weight: 500; margin-bottom: 4px;">✓ {r}</li>' for r in sc.get("why_recommended", []))

            render_html(f"""
            <div class="glass-card" style="border-left: 6px solid {border_color}; margin-bottom: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                    <div>
                        <h4 style="margin: 0; color: #0F172A; font-size: 1.2rem;">{sc.get('name')}</h4>
                        <span style="color: #64748B; font-size: 0.85rem; font-weight: 500;">🏛️ {sc.get('provider')}</span>
                    </div>
                    <div>{status_chip}</div>
                </div>

                <div style="background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 10px; padding: 12px 14px; margin-bottom: 14px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                        <div>
                            <span style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Category Match</span>
                            <div style="font-weight: 600; color: #166534; font-size: 0.88rem; margin-top: 2px;">{sc.get('category_match')}</div>
                        </div>
                        <div>
                            <span style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Income Ceiling Limit</span>
                            <div style="font-weight: 600; color: #1E40AF; font-size: 0.88rem; margin-top: 2px;">{sc.get('income_match')}</div>
                        </div>
                        <div>
                            <span style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; font-weight: 700;">State Domicile</span>
                            <div style="font-weight: 600; color: #0F172A; font-size: 0.88rem; margin-top: 2px;">{sc.get('state_match')}</div>
                        </div>
                    </div>
                </div>

                <div style="margin-bottom: 14px; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 10px 14px;">
                    <span style="font-size: 0.75rem; color: #065F46; font-weight: 700; text-transform: uppercase;">Financial Benefit & Allowance:</span>
                    <div style="font-weight: 700; color: #064E3B; font-size: 1.02rem; margin-top: 2px;">💵 {sc.get('amount')}</div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 16px;">
                    <div>
                        <div style="font-size: 0.82rem; color: #0F172A; font-weight: 700; margin-bottom: 6px;">Why This Fits Your Profile:</div>
                        <ul style="margin: 0; padding-left: 18px;">{recs_html}</ul>
                    </div>
                    <div>
                        <div style="font-size: 0.82rem; color: #0F172A; font-weight: 700; margin-bottom: 6px;">Required Documents to Keep Ready:</div>
                        <ul style="margin: 0; padding-left: 18px;">{docs_html}</ul>
                    </div>
                </div>

                <div style="border-top: 1px solid #F1F5F9; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <span style="font-size: 0.8rem; color: #64748B;">Official Application Portal: <strong>{portal_name}</strong></span>
                    <a href="{portal_url}" target="_blank" style="background: #2563EB; color: white; text-decoration: none; padding: 8px 18px; border-radius: 8px; font-weight: 600; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 6px;">
                        Apply on Official Portal ↗
                    </a>
                </div>
            </div>
            """)

    with sch_tab1:
        _render_cards(evaluated_scholarships)

    with sch_tab2:
        tn_schemes = [s for s in evaluated_scholarships if "tamil nadu" in s.get("provider", "").lower() or "tamil nadu" in s.get("name", "").lower() or "pudhumai" in s.get("name", "").lower()]
        _render_cards(tn_schemes)

    with sch_tab3:
        central_schemes = [s for s in evaluated_scholarships if "national" in s.get("portal_name", "").lower() or "aicte" in s.get("provider", "").lower() or "ministry" in s.get("provider", "").lower() or "pm-usp" in s.get("name", "").lower() or "yasasvi" in s.get("name", "").lower()]
        _render_cards(central_schemes)

    with sch_tab4:
        csr_schemes = [s for s in evaluated_scholarships if "reliance" in s.get("name", "").lower() or "tata" in s.get("name", "").lower() or "corporate" in s.get("provider", "").lower()]
        _render_cards(csr_schemes)

    # Step-by-Step Scholarship Application Guide Expander
    with st.expander("📋 Mandatory Checklist: How to Apply & Receive DBT Scholarship Funds", expanded=False):
        st.markdown("""
        ### 📌 4-Step Standard Government Scholarship Protocol
        1. **Obtain Official Tahsildar Certificates:**
           - Apply on Tamil Nadu e-Sevai / Revenue portal for valid **Permanent Community Certificate** and current financial year **Income Certificate** (< ₹2.5 Lakhs).
        2. **NPCI Aadhaar-Bank Account Seeding (DBT Enablement):**
           - All state & central scholarships are disbursed strictly via **Direct Benefit Transfer (DBT)** into an Aadhaar-seeded active savings bank account.
           - Visit your bank branch or use UIDAI Aadhaar Bank Mapping portal to ensure your bank account is active on the NPCI mapper.
        3. **National Scholarship Portal (NSP) One-Time Registration (OTR):**
           - Visit [scholarships.gov.in](https://scholarships.gov.in) and complete Face-Authentication OTR via the Aadhaar FaceRD app.
           - Apply under Central Sector Schemes (PM-USP, AICTE Pragati, PM-YASASVI, or Post-Matric).
        4. **Institutional Verification & Bonafide Submission:**
           - Once submitted online, take printouts of application along with marksheet, caste certificate, and income certificate to your College Nodal Officer / Scholarship Cell for institutional level verification.
        """)


# ---------------------------------------------------------------------------
# LANDING PAGE & LOGIN GATEWAY
# ---------------------------------------------------------------------------
if "username" not in st.session_state:
    # Check if student clicked "Login / Register" or is viewing the Landing Page
    if st.session_state.get("show_login_page", False):
        # Top bar with return link to landing page
        top_c1, top_c2 = st.columns([1.2, 5])
        with top_c1:
            if st.button("← Back to Home", key="back_to_landing", use_container_width=True):
                st.session_state["show_login_page"] = False
                st.rerun()

        col_left, col_center, col_right = st.columns([1, 1.8, 1])
        with col_center:
            render_html("""
            <div class="auth-box">
                <div style="font-size: 3.2rem; margin-bottom: 8px;">🎓</div>
                <h1 style="color: #0F172A; font-size: 1.8rem; margin: 0; font-weight: 700;">EduPath AI</h1>
                <p style="color: #64748B; font-size: 0.95rem; margin-top: 6px; margin-bottom: 24px;">
                    One-Stop Educational & Career Advisory Platform
                </p>
            </div>
            """)

            # Fast Google SSO Option
            render_html("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <svg width="20" height="20" viewBox="0 0 48 48">
                        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                        <path fill="none" d="M0 0h48v48H0z"/>
                    </svg>
                    <span style="font-weight: 600; color: #1E293B; font-size: 0.95rem;">Google Account Access</span>
                </div>
            </div>
            """)

            with st.expander("🔴 Continue with Google Account", expanded=False):
                st.caption("Sign in instantly or link your official Google student account.")
                g_email = st.text_input("Google Email Address", placeholder="student@gmail.com", key="google_email_input")
                g_name = st.text_input("Display Name (Optional)", placeholder="e.g. Eswari K", key="google_name_input")
                if st.button("Authenticate via Google", use_container_width=True, type="secondary"):
                    if g_email and "@" in g_email:
                        success, actual_user = auth.login_or_create_google_user(g_email, g_name)
                        if success:
                            st.session_state["username"] = actual_user
                            st.session_state["user_email"] = g_email
                            st.session_state["auth_provider"] = "google"
                            st.success(f"Authenticated as {actual_user} via Google!")
                            st.rerun()
                        else:
                            st.error(actual_user)
                    else:
                        st.warning("Please enter a valid Google email address.")

            st.markdown("<div style='text-align: center; color: #94A3B8; font-size: 0.85rem; margin: 12px 0;'>&mdash; OR CONTINUE WITH CREDENTIALS &mdash;</div>", unsafe_allow_html=True)

            login_tab, signup_tab, forgot_tab = st.tabs(["🔑 Sign In", "🆕 Create Account", "🔒 Forgot Password"])

            with login_tab:
                render_html("<p style='color: #64748B; font-size: 0.9rem; text-align: center; margin-bottom: 14px;'>Enter your registered username or email to access your advisory dashboard.</p>")
                login_user = st.text_input("Username or Email", key="login_user", placeholder="Enter username or email")
                login_pass = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
                if st.button("Sign In", use_container_width=True, type="primary"):
                    if login_user.strip() and login_pass:
                        if auth.verify_user(login_user, login_pass):
                            actual_username = auth.get_actual_username(login_user)
                            st.session_state["username"] = actual_username
                            st.rerun()
                        else:
                            st.error("Incorrect username/email or password.")
                    else:
                        st.warning("Please enter both username/email and password.")

            with signup_tab:
                render_html("<p style='color: #64748B; font-size: 0.9rem; text-align: center; margin-bottom: 14px;'>Register a new student profile with email for saved roadmaps & alerts.</p>")
                new_user = st.text_input("Choose Username", key="signup_user", placeholder="e.g. eswari_k")
                new_email = st.text_input("Email Address", key="signup_email", placeholder="e.g. student@gmail.com")
                new_pass = st.text_input("Choose Password", type="password", key="signup_pass", placeholder="Minimum 4 characters")
                confirm_pass = st.text_input("Confirm Password", type="password", key="signup_pass_confirm", placeholder="Re-enter password")

                if st.button("Create Account", use_container_width=True, type="primary"):
                    if not new_user.strip() or not new_pass:
                        st.warning("Please fill in username and password.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match. Please re-enter.")
                    elif len(new_pass) < 4:
                        st.warning("Password should be at least 4 characters long.")
                    else:
                        success, msg = auth.create_user(new_user, new_pass, new_email)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

            with forgot_tab:
                render_html("<p style='color: #64748B; font-size: 0.9rem; text-align: center; margin-bottom: 14px;'>Reset your password using your registered username or email address.</p>")
                reset_id = st.text_input("Username or Registered Email", key="reset_user_email", placeholder="Enter your username or email")
                new_reset_pass = st.text_input("New Password", type="password", key="reset_new_pass", placeholder="Enter new password")
                confirm_reset_pass = st.text_input("Confirm New Password", type="password", key="reset_confirm_pass", placeholder="Re-enter new password")

                if st.button("Reset Password", use_container_width=True, type="primary"):
                    if not reset_id.strip() or not new_reset_pass:
                        st.warning("Please provide your username/email and new password.")
                    elif new_reset_pass != confirm_reset_pass:
                        st.error("Passwords do not match. Please re-enter.")
                    elif len(new_reset_pass) < 4:
                        st.warning("New password must be at least 4 characters long.")
                    else:
                        success, msg = auth.reset_password(reset_id, new_reset_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
        st.stop()

    # -----------------------------------------------------------------------
    # IMMERSIVE LANDING PAGE VIEW
    # -----------------------------------------------------------------------
    # Hide sidebar on landing page for full-width presentation
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        .block-container { max-width: 1200px !important; padding-top: 1.2rem !important; padding-bottom: 4rem !important; }
        .landing-hero {
            background: linear-gradient(135deg, #0A0F1D 0%, #1E1B4B 50%, #0F172A 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 20px;
            padding: 48px 40px;
            margin-bottom: 28px;
            color: white;
            box-shadow: 0 12px 35px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
        }
        .mission-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 5px solid #2563EB;
            border-radius: 16px;
            padding: 32px 36px;
            margin-bottom: 36px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.04);
        }
        .pillar-box {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 20px;
            height: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .pillar-box:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.06);
            border-color: #93C5FD;
        }
        .video-box {
            background: #0F172A;
            border: 1px solid #1E293B;
            border-radius: 16px 16px 0 0;
            padding: 16px;
            color: white;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        }
        .stream-tag {
            display: inline-block;
            background: #EFF6FF;
            color: #1D4ED8;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 20px;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Top Navigation Header
    nav_c1, nav_c2 = st.columns([3.2, 1.3])
    with nav_c1:
        render_html("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div class="ai-orb" style="width: 44px; height: 44px;"></div>
            <div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #0F172A; font-family: 'Poppins', sans-serif; letter-spacing: -0.5px;">
                    EduPath <span style="color: #2563EB;">AI</span>
                </div>
                <div style="font-size: 0.8rem; color: #64748B; font-weight: 500;">
                    Democratizing Higher Education & Career Navigation Across India
                </div>
            </div>
        </div>
        """)
    with nav_c2:
        if st.button("🔑 Student Sign In / Register", key="nav_login_btn", use_container_width=True, type="primary"):
            st.session_state["show_login_page"] = True
            st.rerun()

    # Hero Banner
    render_html("""
    <div class="landing-hero">
        <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(59, 130, 246, 0.25); border: 1px solid rgba(96, 165, 250, 0.4); padding: 4px 14px; border-radius: 20px; margin-bottom: 18px;">
            <span style="font-size: 0.8rem; color: #93C5FD; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                ✨ SIH25094 • Multi-Stream Academic Advisory Engine
            </span>
        </div>
        <h1 style="color: #FFFFFF; font-size: 2.5rem; font-weight: 800; margin: 0 0 16px 0; line-height: 1.25; font-family: 'Poppins', sans-serif;">
            Find Your True Calling. <br>
            <span style="background: linear-gradient(135deg, #60A5FA 0%, #F59E0B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Navigate Admissions, Careers & Scholarships With AI.
            </span>
        </h1>
        <p style="color: #CBD5E1; font-size: 1.05rem; line-height: 1.6; max-width: 820px; margin-bottom: 20px;">
            EduPath AI transforms overwhelming counseling choices into clear, data-backed roadmaps. Whether you are aiming for Engineering (TNEA/JEE), Medicine (NEET), Chartered Accountancy, Corporate Law (CLAT), or Visual Communication & Media, our multi-stream intelligence guides you to your ideal college and career.
        </p>
    </div>
    """)

    # Quick Action Buttons below Hero
    hero_btn1, hero_btn2, hero_spacer = st.columns([1.5, 1.8, 2.7])
    with hero_btn1:
        if st.button("🚀 Get Started / Login", key="hero_start_btn", use_container_width=True, type="primary"):
            st.session_state["show_login_page"] = True
            st.rerun()
    with hero_btn2:
        if st.button("✨ Create Free Account", key="hero_signup_btn", use_container_width=True):
            st.session_state["show_login_page"] = True
            st.rerun()

    st.markdown("<div style='margin-bottom: 36px;'></div>", unsafe_allow_html=True)

    # MISSION OF CAREERCOMPASS
    render_html("""
    <div class="mission-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <span style="font-size: 1.8rem;">🎯</span>
            <h2 style="color: #0F172A; font-size: 1.6rem; margin: 0; font-weight: 800; font-family: 'Poppins', sans-serif;">
                The Mission of EduPath AI
            </h2>
        </div>
        <p style="color: #475569; font-size: 1.02rem; line-height: 1.7; margin-bottom: 24px;">
            In India, higher education guidance is heavily fragmented. Millions of promising high school and college students in Tier-2, Tier-3 towns and rural districts navigate crucial decisions with outdated advice, unclear cutoff expectations, and zero awareness of state welfare scholarships. 
            <br><br>
            <strong>EduPath AI was created to dismantle this opportunity divide.</strong> Our mission is to democratize institutional-grade career intelligence, ensure every academic stream is treated with deep domain respect, and provide hyper-personalized 30-day execution roadmaps so no student is left behind due to lack of guidance or funds.
        </p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px;">
            <div class="pillar-box">
                <div style="font-size: 1.6rem; margin-bottom: 8px;">🌐</div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.98rem; margin-bottom: 6px;">Multi-Stream Inclusivity</div>
                <div style="color: #64748B; font-size: 0.85rem; line-height: 1.5;">
                    Unbiased specialization across Engineering, Medical, Commerce, Law, VisCom & Arts, and Pure Sciences. No false defaults to computer science.
                </div>
            </div>
            <div class="pillar-box">
                <div style="font-size: 1.6rem; margin-bottom: 8px;">📊</div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.98rem; margin-bottom: 6px;">Community Cutoff Realism</div>
                <div style="color: #64748B; font-size: 0.85rem; line-height: 1.5;">
                    Granular cutoff matrices factoring in reservations (OC, BC, BCM, MBC, SC, ST) and Tamil Nadu 7.5% Govt School preferential quota.
                </div>
            </div>
            <div class="pillar-box">
                <div style="font-size: 1.6rem; margin-bottom: 8px;">💰</div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.98rem; margin-bottom: 6px;">Direct Financial Aid</div>
                <div style="color: #64748B; font-size: 0.85rem; line-height: 1.5;">
                    Instant discovery of 50+ government and CSR scholarships (Pudhumai Penn, AICTE Pragati, PM-USP, Reliance Foundation).
                </div>
            </div>
            <div class="pillar-box">
                <div style="font-size: 1.6rem; margin-bottom: 8px;">📅</div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.98rem; margin-bottom: 6px;">Actionable Roadmaps</div>
                <div style="color: #64748B; font-size: 0.85rem; line-height: 1.5;">
                    Translating aspirations into tangible 30-day day-by-day action schedules, portfolio checkpoints, and single-window application drills.
                </div>
            </div>
        </div>
    </div>
    """)

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # LIFE AT STUDY & INNOVATION (VIDEO SHOWCASE)
    render_html("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-size: 1.8rem;">🎬</span>
            <h2 style="color: #0F172A; font-size: 1.6rem; margin: 0; font-weight: 800; font-family: 'Poppins', sans-serif;">
                Life at Study: Focus, Discipline & Hands-On Mastery
            </h2>
        </div>
        <p style="color: #64748B; font-size: 0.95rem; margin: 0 0 20px 0;">
            Watch how modern students build deep conceptual mastery, focus through extended study sessions, and master practical technical skills:
        </p>
    </div>
    """)

    vid_col1, vid_col2, vid_col3 = st.columns(3)

    with vid_col1:
        render_html("""
        <div class="video-box">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span class="stream-tag" style="background: rgba(37,99,235,0.2); color: #93C5FD;">📖 Focused Study</span>
                <span style="font-size: 0.75rem; color: #94A3B8;">Pomodoro • Focus</span>
            </div>
            <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 6px; color: #FFFFFF;">
                Deep Study & Exam Preparation
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4; margin-bottom: 4px;">
                Cultivating uninterrupted concentration and disciplined active recall for board exams and entrance tests.
            </div>
        </div>
        """)
        st.video("https://www.youtube.com/watch?v=f02mOEt11OQ")

    with vid_col2:
        render_html("""
        <div class="video-box">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span class="stream-tag" style="background: rgba(147,51,234,0.2); color: #D8B4FE;">🎧 Study Ambience</span>
                <span style="font-size: 0.75rem; color: #94A3B8;">Library Ambience</span>
            </div>
            <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 6px; color: #FFFFFF;">
                Continuous Learning & Productivity
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4; margin-bottom: 4px;">
                Curated ambient environment for long problem-solving, revision routines, and concept visualization.
            </div>
        </div>
        """)
        st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")

    with vid_col3:
        render_html("""
        <div class="video-box">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span class="stream-tag" style="background: rgba(16,185,129,0.2); color: #6EE7B7;">💻 Practical Skills</span>
                <span style="font-size: 0.75rem; color: #94A3B8;">Coding & Labs</span>
            </div>
            <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 6px; color: #FFFFFF;">
                Engineering & Coding Innovation
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4; margin-bottom: 4px;">
                Building real-world software, algorithm optimization, and hardware robotics project portfolios.
            </div>
        </div>
        """)
        st.video("https://www.youtube.com/watch?v=8jLOx1hD3_o")

    st.markdown("<div style='margin-bottom: 36px;'></div>", unsafe_allow_html=True)

    # SIX COMPREHENSIVE ACADEMIC STREAMS
    render_html("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-size: 1.8rem;">🎓</span>
            <h2 style="color: #0F172A; font-size: 1.6rem; margin: 0; font-weight: 800; font-family: 'Poppins', sans-serif;">
                Tailored Advisory Across 6 Major Streams
            </h2>
        </div>
        <p style="color: #64748B; font-size: 0.95rem; margin: 0 0 20px 0;">
            Every student's ambition is unique. EduPath AI provides specialized college catalogs, cutoff benchmarks, and industry salary insights for each domain:
        </p>
    </div>
    """)

    st_c1, st_c2, st_c3 = st.columns(3)
    with st_c1:
        render_html("""
        <div class="glass-card" style="padding: 20px; border-left: 5px solid #2563EB;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">⚙️ Engineering & Technology</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 8px;">B.Tech / B.E • AI, Robotics, CSE, ECE, Mechanical</div>
            <div style="font-size: 0.8rem; color: #0F172A; font-weight: 600;">Top Colleges: CEG Guindy, MIT, PSG Tech, SSN</div>
            <div style="font-size: 0.8rem; color: #166534; font-weight: 700; margin-top: 6px;">Avg CTC: ₹6.0L - 18.0L PA</div>
        </div>
        <div class="glass-card" style="padding: 20px; border-left: 5px solid #8B5CF6;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">🎨 Visual Communication & Arts</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 8px;">B.Sc VisCom, B.Des, BA Media • Video Editing, UI/UX</div>
            <div style="font-size: 0.8rem; color: #0F172A; font-weight: 600;">Top Colleges: Loyola Chennai, NID, NIFT, MCC</div>
            <div style="font-size: 0.8rem; color: #166534; font-weight: 700; margin-top: 6px;">Avg CTC: ₹4.5L - 16.0L PA</div>
        </div>
        """)
    with st_c2:
        render_html("""
        <div class="glass-card" style="padding: 20px; border-left: 5px solid #10B981;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">🩺 Medical & Allied Health</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 8px;">MBBS, BDS, B.Pharm, Nursing, Allied Health</div>
            <div style="font-size: 0.8rem; color: #0F172A; font-weight: 600;">Top Colleges: MMC Chennai, Stanley, CMC Vellore</div>
            <div style="font-size: 0.8rem; color: #166534; font-weight: 700; margin-top: 6px;">Avg CTC: ₹8.0L - 28.0L PA</div>
        </div>
        <div class="glass-card" style="padding: 20px; border-left: 5px solid #0EA5E9;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">🔬 Pure & Applied Sciences</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 8px;">B.Sc Data Science, Statistics, Physics, Biotech</div>
            <div style="font-size: 0.8rem; color: #0F172A; font-weight: 600;">Top Colleges: IISc Bangalore, Loyola, PSG CAS</div>
            <div style="font-size: 0.8rem; color: #166534; font-weight: 700; margin-top: 6px;">Avg CTC: ₹6.0L - 16.0L PA</div>
        </div>
        """)
    with st_c3:
        render_html("""
        <div class="glass-card" style="padding: 20px; border-left: 5px solid #F59E0B;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">📊 Commerce & Management</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 8px;">B.Com, BBA, CA (ICAI), Finance, Corporate Tax</div>
            <div style="font-size: 0.8rem; color: #0F172A; font-weight: 600;">Top Colleges: Loyola, MCC, SRCC, Stella Maris</div>
            <div style="font-size: 0.8rem; color: #166534; font-weight: 700; margin-top: 6px;">Avg CTC: ₹7.5L - 25.0L PA</div>
        </div>
        <div class="glass-card" style="padding: 20px; border-left: 5px solid #EF4444;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">⚖️ Law & Legal Practice</div>
            <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 8px;">BA LL.B, BBA LL.B • Corporate M&A, Litigation, IPR</div>
            <div style="font-size: 0.8rem; color: #0F172A; font-weight: 600;">Top Colleges: NLSIU, GLC Chennai, School of Excellence</div>
            <div style="font-size: 0.8rem; color: #166534; font-weight: 700; margin-top: 6px;">Avg CTC: ₹7.5L - 24.0L PA</div>
        </div>
        """)

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # BOTTOM CALL TO ACTION
    render_html("""
    <div style="background: linear-gradient(135deg, #1E40AF 0%, #2563EB 50%, #1D4ED8 100%); border-radius: 20px; padding: 40px; text-align: center; color: white; box-shadow: 0 12px 30px rgba(37,99,235,0.3); margin-top: 10px;">
        <h2 style="color: #FFFFFF; font-size: 2rem; font-weight: 800; margin: 0 0 12px 0; font-family: 'Poppins', sans-serif;">
            Ready to Begin Your Educational Journey?
        </h2>
        <p style="color: #DBEAFE; font-size: 1.05rem; max-width: 680px; margin: 0 auto 24px auto; line-height: 1.6;">
            Create your student profile in under 2 minutes. Receive personalized career recommendations, verified college cutoffs, and government scholarship alerts.
        </p>
    </div>
    """)

    b_col1, b_col2, b_col3 = st.columns([1, 1.8, 1])
    with b_col2:
        if st.button("🚀 Enter EduPath AI Portal (Sign In / Register)", key="bottom_portal_btn", use_container_width=True, type="primary"):
            st.session_state["show_login_page"] = True
            st.rerun()

    # Footer
    render_html("""
    <div style="text-align: center; padding-top: 40px; color: #94A3B8; font-size: 0.82rem; border-top: 1px solid #E2E8F0; margin-top: 40px;">
        EduPath AI • Smart India Hackathon (SIH25094) • Empowering India's Next Generation of Leaders & Innovators
    </div>
    """)

    st.stop()


# ---------------------------------------------------------------------------
# AUTHENTICATED APPLICATION SHELL
# ---------------------------------------------------------------------------
with st.sidebar:
    render_html(f"""
    <div style="display: flex; align-items: center; gap: 12px; padding: 12px 8px; margin-bottom: 12px; border-bottom: 1px solid #1E293B;">
        <div class="ai-orb" style="width: 44px; height: 44px;"></div>
        <div>
            <div style="font-weight: 700; color: #FFFFFF; font-size: 1rem;">EduPath AI</div>
            <div style="font-size: 0.78rem; color: #94A3B8;">User: <strong style="color: #60A5FA;">{st.session_state.get('username', 'Student')}</strong></div>
        </div>
    </div>
    """)

    page = st.radio(
        "Explore Features",
        [
            "🏠 Dashboard",
            "👤 Profile",
            "🎯 Career Recommendations",
            "🏛️ Colleges & Institutions",
            "💰 Scholarships & Aid",
            "💻 Practice & Skills",
            "📅 30-Day Action Plan",
            "🗺️ Roadmap",
            "🗓️ Academic Schedule",
            "❓ Quick Q&A",
            "📚 Past Sessions",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.session_state.get("loaded_session"):
        session = st.session_state["loaded_session"]
        st.markdown(f"📂 **Active Session:**\n`{session['created_at'][:16]}`")
        if st.button("🆕 Start New Session", use_container_width=True):
            st.session_state.pop("loaded_session", None)
            st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# Helper DB sync
def update_schedule_db(session_id, schedule_items):
    db.update_session_schedule_json(session_id, json.dumps(schedule_items))
    if st.session_state.get("loaded_session"):
        st.session_state["loaded_session"]["schedule_json"] = json.dumps(schedule_items)


# ===========================================================================
# PAGE 1: 🏠 DASHBOARD
# ===========================================================================
if page == "🏠 Dashboard":
    render_3d_hero_canvas()

    if not st.session_state.get("loaded_session"):
        render_html("""
        <div style="background-color: #EFF6FF; border-left: 5px solid #2563EB; border-radius: 8px; padding: 16px; margin: 20px 0;">
            <p style="margin: 0; color: #1E3A8A; font-size: 0.95rem;">
                🧭 <strong>Your Journey Begins:</strong> Tell EduPath AI about your academic level, current year, board marks/CGPA, family background, and interests. Our multi-agent system will generate your complete tailored roadmap!
            </p>
        </div>
        """)

        student_text = st.text_area(
            "Describe your academic background, stream, and goals:",
            height=140,
            placeholder="e.g. I am a 12th standard student from Tamil Nadu with Maths: 95, Physics: 90, Chemistry: 88 (or 88% overall). Belong to SC category with family income 2 lakh per annum. Interested in computer science and robotics. What are my best career options and scholarships?"
        )

        if st.button("✨ Generate My Complete Advisory Plan", type="primary", use_container_width=True):
            if not student_text.strip():
                st.warning("Please enter your academic background.")
            else:
                progress_placeholder = st.empty()
                progress_bar = st.progress(0)

                agent_steps = [
                    "🧑‍🎓 [Profile Agent] Structuring education stage, category & income criteria...",
                    "🔎 [Retrieval Agent] Querying vector index for careers, institutions & welfare schemes...",
                    "💰 [Scholarship Agent] Evaluating category matches & family income ceilings...",
                    "🎯 [Recommendation Agent] Formulating prioritized pathways...",
                    "💻 [Practice Agent] Curating domain platforms & 30-Day drill plan...",
                    "🗺️ [Pathway Agent] Generating phased educational roadmap..."
                ]

                for i, step in enumerate(agent_steps):
                    progress_placeholder.markdown(f"**{step}**")
                    progress_bar.progress(int((i + 1) / len(agent_steps) * 100))

                try:
                    resp = requests.post(
                        f"{API_BASE}/advise",
                        json={"student_text": student_text},
                        timeout=240,
                    )
                    resp.raise_for_status()
                    result = resp.json()

                    milestones = parse_pathway_to_milestones(result["pathway"])
                    milestones_json = json.dumps(milestones) if milestones else None
                    scholarships_json = json.dumps(result.get("scholarships", [])) if result.get("scholarships") else None
                    practice_json = json.dumps(result.get("practice_plan", {})) if result.get("practice_plan") else None

                    session_id = db.save_session(
                        st.session_state["username"],
                        student_text,
                        result["profile"],
                        result["recommendation"],
                        result["pathway"],
                        milestones_json=milestones_json,
                        scholarships_json=scholarships_json,
                        practice_json=practice_json,
                    )

                    st.session_state["loaded_session"] = db.get_session(session_id)
                    st.rerun()

                except requests.exceptions.ConnectionError:
                    progress_bar.empty()
                    progress_placeholder.empty()
                    st.error("Cannot connect to API server. Please verify uvicorn is running on port 8000.")
                except Exception as e:
                    progress_bar.empty()
                    progress_placeholder.empty()
                    st.error(f"Error during advisory generation: {e}")

    else:
        session = st.session_state["loaded_session"]
        p = session.get("profile", {})

        render_pathway_flow_interactive(p)

        render_html(f"""
        <div style="background-color: #EFF6FF; border-left: 5px solid #2563EB; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
            <p style="margin: 0; color: #1E3A8A; font-size: 0.95rem;">
                {get_motivational_message(p)}
            </p>
        </div>
        """)

        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.markdown("### 📋 Executive Summary")
            render_html(f"""
            <div class="glass-card">
                <div style="margin-bottom: 12px;">
                    <span class="chip chip-blue">📚 {p.get('stream', 'N/A').capitalize()}</span>
                    <span class="chip chip-green">🏫 {p.get('education_stage', 'N/A').replace('_', ' ').capitalize()}</span>
                    <span class="chip chip-purple">⏳ {p.get('current_year', 'N/A').capitalize()}</span>
                    <span class="chip chip-amber">👥 {p.get('category', 'N/A').upper()}</span>
                </div>
                <p style="color: #475569; font-size: 0.95rem; font-style: italic; margin-bottom: 16px;">
                    "{session['student_text']}"
                </p>
                <div style="font-size: 0.88rem; color: #334155; line-height: 1.6;">
                    <strong>🎯 Stated Target:</strong> {p.get('goal', 'Career guidance')}<br>
                    <strong>📍 Location:</strong> {p.get('state', 'Tamil Nadu')}<br>
                    <strong>💰 Financial Status:</strong> {format_income_display(p.get('annual_income'))}
                </div>
            </div>
            """)

        with col2:
            st.markdown("### 🚀 Quick Access")
            render_html(f"""
            <div class="glass-card">
                <p style="font-size: 0.92rem; color: #475569; margin-bottom: 16px;">
                    Your personalized plan is active. Navigate to specialized sections:
                </p>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <a href="#" style="text-decoration: none; color: #1E40AF; font-weight: 600; font-size: 0.9rem;">🎯 View Career Recommendations ➔</a>
                    <a href="#" style="text-decoration: none; color: #6D28D9; font-weight: 600; font-size: 0.9rem;">🏛️ View Top 5 Colleges & Cutoffs ➔</a>
                    <a href="#" style="text-decoration: none; color: #166534; font-weight: 600; font-size: 0.9rem;">💰 View Evaluated Scholarships ➔</a>
                    <a href="#" style="text-decoration: none; color: #6B21A8; font-weight: 600; font-size: 0.9rem;">💻 View 30-Day Practice Plan ➔</a>
                    <a href="#" style="text-decoration: none; color: #92400E; font-weight: 600; font-size: 0.9rem;">🗺️ View Phased Roadmap ➔</a>
                </div>
            </div>
            """)

        # DIRECT DISPLAY OF TOP 5 COLLEGES ON DASHBOARD
        st.markdown("---")
        st.markdown("### 🎓 Top 5 Recommended Colleges for Your Marks & Cutoff")
        render_html("<p style='color: #64748B;'>Admission matching dynamically evaluated based on your board marks and reservation quota.</p>")
        render_colleges_and_institutions_view(p, key_prefix="dash")


# ===========================================================================
# PAGE 2: 👤 PROFILE
# ===========================================================================
elif page == "👤 Profile":
    if not st.session_state.get("loaded_session"):
        st.info("💡 Please create or load an advisory plan on the Dashboard first.")
    else:
        session = st.session_state["loaded_session"]
        p = session.get("profile", {})

        st.markdown("### 👤 Student Profile Attributes")
        render_html("<p style='color: #64748B;'>Parameters structured and verified by the Profile Agent.</p>")

        income_val = p.get('annual_income')
        income_str = format_income_display(income_val)

        render_html(f"""
        <div class="glass-card">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px;">
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Education Stage</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">🏫 {p.get('education_stage', 'Unknown').replace('_', ' ').capitalize()}</div>
                </div>
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Current Year / Class</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">⏳ {p.get('current_year', 'Unknown').capitalize()}</div>
                </div>
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Stream</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">📚 {p.get('stream', 'Unknown').capitalize()}</div>
                </div>
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Social Category</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">👥 {p.get('category', 'Unknown').upper()}</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px;">
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Annual Family Income</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">💰 {income_str}</div>
                </div>
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Board Score / CGPA</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">🏛️ {p.get('board_percentage', 'N/A')}%</div>
                </div>
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">State Domicile</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">📍 {p.get('state', 'Unknown').capitalize()}</div>
                </div>
                <div style="background: #F8FAFC; padding: 14px 18px; border-radius: 10px; border: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Target Goal</div>
                    <div style="font-size: 1.15rem; color: #0F172A; font-weight: 700; margin-top: 4px;">🎯 {p.get('goal', 'General').capitalize()}</div>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <div style="font-size: 0.8rem; color: #64748B; text-transform: uppercase; font-weight: 700; margin-bottom: 6px;">Interests & Domain Focus</div>
                <div>
                    {" ".join([f'<span class="chip chip-blue">💡 {i.strip()}</span>' for i in p.get('interests', [])]) if p.get('interests') else '<span class="chip chip-slate">General exploration</span>'}
                </div>
            </div>
        </div>
        """)


# ===========================================================================

# PAGE 3: 🎯 CAREER RECOMMENDATIONS (INTERACTIVE EXPLORER)
# ===========================================================================
elif page == "🎯 Career Recommendations":
    if not st.session_state.get("loaded_session"):
        st.info("💡 Please create or select an advisory plan in the **Dashboard** first.")
    else:
        session = st.session_state["loaded_session"]
        p = session.get("profile", {})
        rec_text = session.get("recommendation", "")
        parsed_rec = parse_recommendation(rec_text)

        st.markdown("### 🎯 Interactive Career & Education Explorer")
        render_html("<p style='color: #64748B;'>Explore personalized career pathways, top institutions, welfare initiatives, and compare options.</p>")

        # Top interactive search filter
        search_query = st.text_input(
            "🔍 Search within recommendations (role, skill, institution, or keyword):",
            placeholder="e.g. Robotics, Artificial Intelligence, Python, Anna University, Counseling...",
            key="rec_search_filter"
        ).strip().lower()

        # Parse structured entities
        structured_careers = parse_structured_careers(parsed_rec.get("careers", ""), p)
        structured_courses = parse_structured_courses(parsed_rec.get("courses", ""))
        structured_schemes = parse_structured_schemes(parsed_rec.get("schemes", ""))

        # Active Goal Notification Badge if student selected one
        if st.session_state.get("primary_target_goal"):
            st.success(f"🎯 **Active Target Goal:** {st.session_state['primary_target_goal']} (Set as your primary career focus)")

        # Interactive Mode Tabs
        rec_tabs = st.tabs([
            "🎯 Career Pathways & Roles",
            "🎓 Colleges & Institutions",
            "🏛️ Government Schemes",
            "🚀 Immediate Action Points",
            "⚖️ Role Comparison Matrix"
        ])

        # TAB 1: CAREER ROLES & PATHWAYS
        with rec_tabs[0]:
            st.markdown("#### 🎯 Personalized High-Fit Career Roles")
            st.markdown("<p style='color: #64748B; font-size: 0.88rem;'>Evaluated for compatibility with your academic stream, performance, and expressed interests.</p>", unsafe_allow_html=True)

            # Interactive Skills Readiness Calculator
            with st.expander("⚡ Interactive Skill Readiness Calculator (Check skills you know)", expanded=False):
                st.markdown("<p style='font-size: 0.85rem; color: #475569;'>Check the skills you have already studied or practiced to compute your real-time job readiness score:</p>", unsafe_allow_html=True)
                calc_cols = st.columns(4)
                active_stream = detect_stream_key(p)
                if active_stream == "commerce":
                    skill_options = ["Financial Accounting", "Direct & Indirect Tax (GST)", "Auditing Standards", "Corporate & Allied Laws", "TallyPrime / ERP", "Financial Modeling (Excel)", "Cost Management", "Portfolio Analysis"]
                elif active_stream == "medical":
                    skill_options = ["Human Anatomy", "Clinical Pharmacology", "Pathology & Diagnostics", "Patient Consultation", "Emergency Life Support (BLS)", "Biochemistry", "Medical Ethics", "Hospital Protocols"]
                elif active_stream == "law":
                    skill_options = ["Constitutional Law", "Legal Drafting", "Corporate Law & Contracts", "M&A Regulatory Due Diligence", "Arbitration & Mediation", "Litigation Pleadings", "Intellectual Property", "Legal Research (SCC)"]
                elif active_stream == "arts":
                    skill_options = ["Video Editing (Premiere/FCP)", "Motion Graphics (After Effects)", "Color Grading (DaVinci)", "Visual Storytelling & Pacing", "UI/UX Design (Figma)", "Digital Cinematography & Lighting", "Audio Post-Production", "Graphic Design (Photoshop)"]
                elif active_stream == "science":
                    skill_options = ["Python for Science", "Statistical Inference", "Linear Algebra", "Machine Learning", "Data Visualization", "SQL Database Queries", "Experimental Design", "Calculus"]
                else:
                    skill_options = ["Python", "C/C++", "SQL", "Data Structures & Algorithms", "ROS (Robot Operating System)", "Machine Learning", "Microcontrollers (Arduino/STM32)", "Git & GitHub"]
                user_checked_skills = []
                for s_idx, sk in enumerate(skill_options):
                    col_target = calc_cols[s_idx % 4]
                    with col_target:
                        if st.checkbox(sk, key=f"user_skill_{s_idx}"):
                            user_checked_skills.append(sk.lower())

            filtered_careers = [
                c for c in structured_careers
                if not search_query or search_query in c["title"].lower() or search_query in c["domain"].lower() or any(search_query in s.lower() for s in c["skills"])
            ]

            if not filtered_careers:
                st.info(f"No career roles matched '{search_query}'. Try a different search term.")
            else:
                for idx, c in enumerate(filtered_careers):
                    # Compute personalized readiness score based on checked skills
                    role_skills = [s.lower() for s in c.get("skills", [])]
                    matched_count = sum(1 for us in user_checked_skills if any(us in rs or rs in us for rs in role_skills))
                    total_req = len(role_skills) if role_skills else 1
                    readiness_pct = int((matched_count / total_req) * 100) if user_checked_skills else c.get("match_score", c.get("score", 92))

                    skills_chips = " ".join([f'<span class="chip chip-blue" style="font-size: 0.76rem;">{s}</span>' for s in c.get("skills", [])])
                    companies_str = ", ".join(c.get("companies", []))

                    # Build Career Card
                    render_html(f"""
                    <div class="glass-card" style="border-left: 6px solid #2563EB; margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                            <div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <h3 style="margin: 0; color: #0F172A; font-size: 1.3rem;">{c['title']}</h3>
                                    <span class="chip chip-green" style="font-size: 0.72rem;">✓ Verified Pathway</span>
                                </div>
                                <div style="color: #2563EB; font-weight: 600; font-size: 0.88rem; margin-top: 2px;">
                                    🌐 {c['domain']}
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="text-align: right;">
                                    <div style="font-weight: 800; font-size: 1.15rem; color: #1D4ED8;">{readiness_pct}% Fit</div>
                                    <div style="font-size: 0.72rem; color: #64748B;">Profile Alignment</div>
                                </div>
                                <div style="background: #EFF6FF; border: 2.5px solid #3B82F6; border-radius: 50%; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; color: #1D4ED8;">
                                    {readiness_pct}%
                                </div>
                            </div>
                        </div>

                        <p style="color: #334155; font-size: 0.92rem; line-height: 1.5; margin-bottom: 14px;">
                            {c['description']}
                        </p>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 10px; padding: 12px; margin-bottom: 14px;">
                            <div>
                                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Average Entry CTC</div>
                                <div style="font-weight: 700; color: #166534; font-size: 0.95rem; margin-top: 2px;">💵 {c['salary']}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Growth Index</div>
                                <div style="font-weight: 700; color: #92400E; font-size: 0.95rem; margin-top: 2px;">📈 {c['demand']}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Required Degree</div>
                                <div style="font-weight: 600; color: #0F172A; font-size: 0.85rem; margin-top: 2px;">🎓 {c['degree']}</div>
                            </div>
                        </div>

                        <div style="margin-bottom: 12px;">
                            <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">Essential Core Skills:</div>
                            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                                {skills_chips}
                            </div>
                        </div>
                    </div>
                    """)

                    # Interactive Streamlit widgets for each career
                    col_act1, col_act2 = st.columns([3, 1.2])
                    with col_act1:
                        with st.expander(f"📖 Deep-Dive Analysis for {c['title']}", expanded=False):
                            st.markdown(f"**🏢 Premier Recruiters in India:**\n`{companies_str}`")
                            st.markdown(f"**📜 Recommended Industry Certifications:**")
                            for cert in c["certifications"]:
                                st.markdown(f"- {cert}")
                            if user_checked_skills:
                                st.info(f"💡 **Skill Readiness:** You have matched **{matched_count} of {total_req}** core competencies for this role!")
                            if c.get("citations"):
                                st.markdown("**📄 Grounded Citations:** " + " ".join([f"`{cit}`" for cit in c["citations"]]))
                    with col_act2:
                        btn_label = "⭐ Target Goal Selected" if st.session_state.get("primary_target_goal") == c["title"] else "⭐ Set as Target Goal"
                        if st.button(btn_label, key=f"set_goal_{idx}", use_container_width=True):
                            st.session_state["primary_target_goal"] = c["title"]
                            st.rerun()

                    st.markdown("---")

        # TAB 2: COLLEGES & INSTITUTIONS (PERSONALIZED TOP 5 MATCHED BY MARKS + COMPLETE DIRECTORY)
        with rec_tabs[1]:
            render_colleges_and_institutions_view(p, key_prefix="rec_tab")

        # TAB 3: GOVERNMENT & WELFARE SCHEMES
        with rec_tabs[2]:
            st.markdown("#### 🏛️ Tamil Nadu & Central Welfare Initiatives")
            st.markdown("<p style='color: #64748B; font-size: 0.88rem;'>Government welfare, fee waivers, skill development programs, and reservation entitlements.</p>", unsafe_allow_html=True)

            for sch in structured_schemes:
                render_html(f"""
                <div class="glass-card" style="border-left: 6px solid #10B981; margin-bottom: 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <div>
                            <h4 style="margin: 0; color: #0F172A; font-size: 1.15rem;">{sch['name']}</h4>
                            <span style="font-size: 0.82rem; color: #64748B;">🏛️ {sch['authority']}</span>
                        </div>
                        <span class="chip chip-green">Active Government Scheme</span>
                    </div>
                    <div style="margin: 10px 0; font-size: 0.9rem; color: #166534; font-weight: 600;">
                        🎁 Key Benefits: {sch['benefit']}
                    </div>
                    <div style="font-size: 0.85rem; color: #475569; margin-bottom: 12px;">
                        <strong>Target Beneficiaries:</strong> {sch['eligibility']}
                    </div>
                    <div style="display: flex; justify-content: flex-end;">
                        <a href="{sch['portal']}" target="_blank" style="background: #166534; color: white; text-decoration: none; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">
                            Official Scheme Portal ↗
                        </a>
                    </div>
                </div>
                """)

        # TAB 4: IMMEDIATE ACTION POINTS
        with rec_tabs[3]:
            st.markdown("#### 🚀 Immediate Action Points")
            render_section_card(parsed_rec.get("next_steps", ""), "Recommended Action Steps", "🚀")

        # TAB 5: ROLE COMPARISON MATRIX
        with rec_tabs[4]:
            st.markdown("#### ⚖️ Side-by-Side Career Role Comparison")
            st.markdown("<p style='color: #64748B; font-size: 0.88rem;'>Compare key career options side-by-side on compensation, skill requirements, degree path, and recruiters.</p>", unsafe_allow_html=True)

            role_titles = [c["title"] for c in structured_careers]
            if len(role_titles) >= 2:
                cmp_col1, cmp_col2 = st.columns(2)
                with cmp_col1:
                    role_a_name = st.selectbox("Select Role A:", role_titles, index=0, key="cmp_role_a")
                with cmp_col2:
                    role_b_name = st.selectbox("Select Role B:", role_titles, index=min(1, len(role_titles) - 1), key="cmp_role_b")

                role_a = next((c for c in structured_careers if c.get("title") == role_a_name), structured_careers[0] if structured_careers else {})
                role_b = next((c for c in structured_careers if c.get("title") == role_b_name), structured_careers[-1] if structured_careers else {})

                c1, c2 = st.columns(2)
                with c1:
                    render_html(f"""
                    <div class="glass-card" style="border-top: 5px solid #2563EB;">
                        <h4 style="margin: 0 0 6px 0; color: #1E40AF; font-size: 1.2rem;">{role_a.get('title', 'Role A')}</h4>
                        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">{role_a.get('domain', 'Domain')}</div>
                        
                        <div style="margin-bottom: 10px;"><strong>Match Fit:</strong> <span class="chip chip-green">{role_a.get('match_score', role_a.get('score', 95))}% Fit</span></div>
                        <div style="margin-bottom: 10px;"><strong>Entry Salary:</strong> 💵 {role_a.get('salary', 'N/A')}</div>
                        <div style="margin-bottom: 10px;"><strong>Growth Rate:</strong> 📈 {role_a.get('demand', 'High')}</div>
                        <div style="margin-bottom: 10px;"><strong>Required Degree:</strong><br><small>{role_a.get('degree', 'Bachelor Degree')}</small></div>
                        <div style="margin-bottom: 10px;"><strong>Top Skills:</strong><br>{" ".join([f'<span class="chip chip-blue" style="font-size: 0.72rem;">{s}</span>' for s in role_a.get('skills', [])])}</div>
                        <div><strong>Key Employers:</strong><br><small>{", ".join(role_a.get('companies', [])[:4])}</small></div>
                    </div>
                    """)
                with c2:
                    render_html(f"""
                    <div class="glass-card" style="border-top: 5px solid #F59E0B;">
                        <h4 style="margin: 0 0 6px 0; color: #B45309; font-size: 1.2rem;">{role_b.get('title', 'Role B')}</h4>
                        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">{role_b.get('domain', 'Domain')}</div>
                        
                        <div style="margin-bottom: 10px;"><strong>Match Fit:</strong> <span class="chip chip-amber">{role_b.get('match_score', role_b.get('score', 92))}% Fit</span></div>
                        <div style="margin-bottom: 10px;"><strong>Entry Salary:</strong> 💵 {role_b.get('salary', 'N/A')}</div>
                        <div style="margin-bottom: 10px;"><strong>Growth Rate:</strong> 📈 {role_b.get('demand', 'High')}</div>
                        <div style="margin-bottom: 10px;"><strong>Required Degree:</strong><br><small>{role_b.get('degree', 'Bachelor Degree')}</small></div>
                        <div style="margin-bottom: 10px;"><strong>Top Skills:</strong><br>{" ".join([f'<span class="chip chip-amber" style="font-size: 0.72rem;">{s}</span>' for s in role_b.get('skills', [])])}</div>
                        <div><strong>Key Employers:</strong><br><small>{", ".join(role_b.get('companies', [])[:4])}</small></div>
                    </div>
                    """)
            else:
                st.info("At least two career pathways are needed for comparison.")


# ===========================================================================
# PAGE: 🏛️ COLLEGES & INSTITUTIONS (DEDICATED INSTITUTIONS PAGE)
# ===========================================================================
elif page == "🏛️ Colleges & Institutions":
    st.markdown("### 🏛️ Top Colleges & Cutoff Matching Engine")
    render_html("<p style='color: #64748B;'>Explore personalized college suggestions matched to your academic marks, TNEA single-window cutoffs, and reservation quotas.</p>")
    session = st.session_state.get("loaded_session", {})
    p = session.get("profile", {}) if session else {}
    render_colleges_and_institutions_view(p, key_prefix="page_inst")


# ===========================================================================
# PAGE 4: 💰 SCHOLARSHIPS & FINANCIAL AID (DEDICATED SECTION)
# ===========================================================================
elif page == "💰 Scholarships & Aid":
    st.markdown("### 💰 Scholarships & Financial Aid Matching Engine")
    render_html("<p style='color: #64748B;'>Intelligently evaluates tuition fee waivers, central & state scholarships, and maintenance grants based on your social category and family income ceiling.</p>")
    session = st.session_state.get("loaded_session", {})
    p = session.get("profile", {}) if session else {}
    render_scholarships_and_aid_view(p, session=session, key_prefix="page_sch")


# ===========================================================================
# PAGE 5: 💻 PRACTICE & SKILLS PLATFORMS
# ===========================================================================
elif page == "💻 Practice & Skills":
    if not st.session_state.get("loaded_session"):
        st.info("💡 Please create or select an advisory plan in the **Dashboard** first.")
    else:
        session = st.session_state["loaded_session"]
        p = session.get("profile", {})

        st.markdown("### 💻 Curated Practice & Skill Building Platforms")
        render_html("<p style='color: #64748B;'>Hands-on platforms tailored specifically to your chosen stream and technical interests.</p>")

        platforms = practice_agent.get_domain_platforms(p.get("stream", "Engineering"), p.get("interests", []))

        col1, col2 = st.columns(2)
        for i, plat in enumerate(platforms):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                render_html(f"""
                <div class="glass-card" style="height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <h4 style="margin: 0; color: #0F172A; font-size: 1.25rem;">{plat.get('platform')}</h4>
                        <span class="chip chip-blue">{plat.get('badge')}</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #475569; margin-bottom: 12px;">
                        <strong>Key Focus:</strong> {plat.get('focus')}
                    </div>
                    <div style="background: #F8FAFC; border-left: 4px solid #3B82F6; padding: 10px 14px; border-radius: 6px; font-size: 0.85rem; color: #1E293B; margin-bottom: 16px;">
                        <strong>Recommended Drill:</strong> {plat.get('practice')}
                    </div>
                    <a href="{plat.get('url')}" target="_blank" style="background: #0F172A; color: white; text-decoration: none; padding: 7px 16px; border-radius: 8px; font-weight: 600; font-size: 0.82rem; display: inline-block;">
                        Launch Platform ↗
                    </a>
                </div>
                """)


# ===========================================================================
# PAGE 6: 📅 30-DAY PERSONALIZED ACTION PLAN
# ===========================================================================
elif page == "📅 30-Day Action Plan":
    if not st.session_state.get("loaded_session"):
        st.info("💡 Please create or select an advisory plan in the **Dashboard** first.")
    else:
        session = st.session_state["loaded_session"]
        p = session.get("profile", {})
        plan = session.get("practice_plan")

        if not plan:
            plan = practice_agent.generate_30_day_plan(p, p.get("goal"))

        st.markdown(f"### 📅 {plan.get('title', '30-Day High-Impact Action Plan')}")
        render_html(f"<p style='color: #64748B;'>Target Focus: <strong>{plan.get('focus_domain')}</strong></p>")

        for week in plan.get("weeks", []):
            render_html(f"""
            <div class="glass-card" style="border-left: 6px solid #2563EB;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <span class="chip chip-blue">Week {week.get('week')} • {week.get('days')}</span>
                        <h4 style="margin: 6px 0 0 0; color: #0F172A; font-size: 1.15rem;">{week.get('theme')}</h4>
                    </div>
                    <span class="chip chip-slate">⏱️ {week.get('time_commitment')}</span>
                </div>
                <p style="color: #475569; font-size: 0.92rem; margin-bottom: 12px;"><strong>Goal:</strong> {week.get('goal')}</p>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; font-size: 0.88rem; margin-bottom: 12px;">
                    <strong>Action Step:</strong> {week.get('action')}
                </div>
                <div style="font-size: 0.84rem; color: #166534; font-weight: 600;">
                    🎯 Weekly Deliverable: {week.get('deliverable')}
                </div>
            </div>
            """)


# ===========================================================================
# PAGE 7: 🗺️ ROADMAP (INTERACTIVE & PHASED VISUAL GUIDANCE)
# ===========================================================================
elif page == "🗺️ Roadmap":
    if not st.session_state.get("loaded_session"):
        st.info("💡 Please create or select an advisory plan in the **Dashboard** first.")
    else:
        session = st.session_state["loaded_session"]
        p = session.get("profile", {})
        target_goal = st.session_state.get("primary_target_goal") or p.get("goal") or "Target Career Pathway"

        st.markdown("### 🗺️ Phased Educational & Career Roadmap")
        render_html(f"<p style='color: #64748B;'>Chronological sequence of actions for your career journey. Tailored for <strong>{p.get('current_year', 'Current Year').capitalize()}</strong> ({p.get('stream', 'Stream').capitalize()}).</p>")

        # Load or generate structured milestones
        milestones = []
        if session.get("milestones_json"):
            try:
                milestones = json.loads(session["milestones_json"])
            except Exception:
                milestones = []

        if not milestones:
            milestones = parse_pathway_to_milestones(session.get("pathway", ""))

        if not milestones:
            milestones = get_default_phased_milestones(p, target_goal)
            update_milestones_db(session["id"], milestones)

        # Compute completion statistics
        total_milestones = sum(len(ph.get("items", [])) for ph in milestones)
        completed_milestones = sum(1 for ph in milestones for it in ph.get("items", []) if it.get("completed"))
        completion_pct = int((completed_milestones / total_milestones) * 100) if total_milestones > 0 else 0

        # Stage Motivational Insight Banner
        motivational_quote = get_motivational_message(p)
        render_html(f"""
        <div style="background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%); border: 1px solid #BFDBFE; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-size: 0.85rem; color: #1E40AF; font-weight: 700; text-transform: uppercase;">🎯 Target Orientation:</span>
                <span style="font-weight: 700; color: #0F172A; font-size: 0.98rem; margin-left: 6px;">{target_goal}</span>
                <div style="font-size: 0.84rem; color: #334155; margin-top: 4px;">{motivational_quote}</div>
            </div>
            <div style="text-align: right;">
                <span class="chip chip-blue" style="margin: 0;">{p.get('education_stage', 'Stage').title()} • {p.get('current_year', 'Year').title()}</span>
            </div>
        </div>
        """)

        # Top Interactive Progress & Metric Bar
        col_m1, col_m2, col_m3, col_m4 = st.columns([1.2, 1.2, 1.2, 2.4])
        with col_m1:
            render_html(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px; text-align: center;">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Total Milestones</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin-top: 2px;">{total_milestones}</div>
            </div>
            """)
        with col_m2:
            render_html(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px; text-align: center;">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Achieved Steps</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #166534; margin-top: 2px;">{completed_milestones}</div>
            </div>
            """)
        with col_m3:
            render_html(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px; text-align: center;">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Roadmap Progress</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #2563EB; margin-top: 2px;">{completion_pct}%</div>
            </div>
            """)
        with col_m4:
            st.markdown(f"**Execution Velocity: {completed_milestones} of {total_milestones} Steps Achieved**")
            st.progress(completion_pct / 100)

        # 4-Phase Visual Stepper Diagram
        render_html("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 20px; margin: 18px 0 24px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <span style="font-size: 0.85rem; font-weight: 700; color: #1E3A8A; text-transform: uppercase; letter-spacing: 0.5px;">Phased Progression Pipeline</span>
                <span style="font-size: 0.76rem; color: #64748B;">Guidance Architecture</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px;">
                <div style="background: #F0FDF4; border: 1.5px solid #86EFAC; border-radius: 10px; padding: 10px 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 0.8rem; font-weight: 700; color: #166534;">🟢 Phase 1</span>
                        <span style="font-size: 0.7rem; background: #DCFCE7; color: #166534; font-weight: 700; padding: 2px 6px; border-radius: 6px;">0–1 Mo</span>
                    </div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.85rem;">Immediate Readiness</div>
                    <div style="font-size: 0.74rem; color: #64748B; margin-top: 2px;">Skills audit & deadlines</div>
                </div>
                <div style="background: #EFF6FF; border: 1.5px solid #93C5FD; border-radius: 10px; padding: 10px 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 0.8rem; font-weight: 700; color: #1E40AF;">🔵 Phase 2</span>
                        <span style="font-size: 0.7rem; background: #DBEAFE; color: #1E40AF; font-weight: 700; padding: 2px 6px; border-radius: 6px;">1–6 Mo</span>
                    </div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.85rem;">Core Competencies</div>
                    <div style="font-size: 0.74rem; color: #64748B; margin-top: 2px;">Mini-projects & drills</div>
                </div>
                <div style="background: #FAF5FF; border: 1.5px solid #D8B4FE; border-radius: 10px; padding: 10px 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 0.8rem; font-weight: 700; color: #6B21A8;">🟣 Phase 3</span>
                        <span style="font-size: 0.7rem; background: #F3E8FF; color: #6B21A8; font-weight: 700; padding: 2px 6px; border-radius: 6px;">6–18 Mo</span>
                    </div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.85rem;">Industry Exposure</div>
                    <div style="font-size: 0.74rem; color: #64748B; margin-top: 2px;">Internships & hackathons</div>
                </div>
                <div style="background: #FFFBEB; border: 1.5px solid #FDE68A; border-radius: 10px; padding: 10px 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 0.8rem; font-weight: 700; color: #92400E;">🟠 Phase 4</span>
                        <span style="font-size: 0.7rem; background: #FEF3C7; color: #92400E; font-weight: 700; padding: 2px 6px; border-radius: 6px;">18+ Mo</span>
                    </div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.85rem;">Career Launch</div>
                    <div style="font-size: 0.74rem; color: #64748B; margin-top: 2px;">Capstone & placements</div>
                </div>
            </div>
        </div>
        """)

        # Interactive Controls Bar: Phase Filter, Keyword Search, and Status Filter
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2.5, 2, 1.5])
        with ctrl_col1:
            phase_filter = st.selectbox(
                "Filter Timeline Horizon:",
                [
                    "All Phases (Complete 4-Stage Pathway)",
                    "🟢 Immediate (0-1 month)",
                    "🔵 Short-term (1-6 months)",
                    "🟣 Medium-term (6-18 months)",
                    "🟠 Long-term (18+ months)"
                ],
                key="rm_phase_filter"
            )
        with ctrl_col2:
            rm_search = st.text_input(
                "🔍 Search Roadmap Actions:",
                placeholder="e.g. GitHub, LeetCode, Internship, TNEA...",
                key="rm_search_query"
            ).strip().lower()
        with ctrl_col3:
            status_filter = st.selectbox(
                "Status Filter:",
                ["All Milestones", "Pending Only", "Achieved Only"],
                key="rm_status_filter"
            )

        # Milestone Cards Rendering
        phase_config = {
            "Immediate (0-1 month)": {
                "icon": "🟢",
                "class": "immediate",
                "accent": "#10B981",
                "bg": "#F0FDF4",
                "title_color": "#166534",
                "sub": "Foundational sprints, diagnostic baseline assessment, and critical eligibility deadlines.",
                "badge": "Phase 1 • Immediate Focus"
            },
            "Short-term (1-6 months)": {
                "icon": "🔵",
                "class": "short-term",
                "accent": "#3B82F6",
                "bg": "#EFF6FF",
                "title_color": "#1E40AF",
                "sub": "Core competence building, algorithmic problem drills, and demonstrable portfolio mini-projects.",
                "badge": "Phase 2 • Core Building"
            },
            "Medium-term (6-18 months)": {
                "icon": "🟣",
                "class": "medium-term",
                "accent": "#8B5CF6",
                "bg": "#FAF5FF",
                "title_color": "#6B21A8",
                "sub": "Summer industrial internships, hackathons, open-source commits, and verified certifications.",
                "badge": "Phase 3 • Industry Bridge"
            },
            "Long-term (18+ months)": {
                "icon": "🟠",
                "class": "long-term",
                "accent": "#F59E0B",
                "bg": "#FFFBEB",
                "title_color": "#92400E",
                "sub": "Comprehensive capstone engineering thesis, executive placement talk preps, and full-time hiring.",
                "badge": "Phase 4 • Culmination"
            }
        }

        displayed_count = 0
        for ph_idx, phase in enumerate(milestones):
            p_name = phase.get("phase", f"Phase {ph_idx+1}")
            cfg = phase_config.get(p_name, phase_config["Immediate (0-1 month)"])

            # Check if filtered out
            if phase_filter != "All Phases (Complete 4-Stage Pathway)" and p_name not in phase_filter:
                continue

            # Filter items in this phase
            filtered_items = []
            for it in phase.get("items", []):
                # Search filter
                if rm_search:
                    text_blob = (it.get("action", "") + " " + it.get("why_it_matters", "") + " " + it.get("skills_opportunity", "")).lower()
                    if rm_search not in text_blob:
                        continue
                # Status filter
                is_comp = it.get("completed", False)
                if status_filter == "Pending Only" and is_comp:
                    continue
                if status_filter == "Achieved Only" and not is_comp:
                    continue
                filtered_items.append(it)

            if not filtered_items:
                continue

            displayed_count += len(filtered_items)
            phase_completed_count = sum(1 for it in filtered_items if it.get("completed", False))

            # Render Phase Section Header
            render_html(f"""
            <div style="background: {cfg['bg']}; border-left: 6px solid {cfg['accent']}; border-radius: 12px; padding: 14px 20px; margin: 24px 0 16px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h4 style="margin: 0; color: {cfg['title_color']}; font-size: 1.18rem;">{cfg['icon']} {p_name}</h4>
                        <span style="background: white; color: {cfg['title_color']}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 10px; border: 1px solid {cfg['accent']};">
                            {cfg['badge']}
                        </span>
                    </div>
                    <div style="font-size: 0.82rem; color: #475569; margin-top: 3px;">{cfg['sub']}</div>
                </div>
                <div style="font-size: 0.82rem; font-weight: 700; color: {cfg['title_color']}; background: white; padding: 4px 12px; border-radius: 8px; border: 1px solid #E2E8F0;">
                    {phase_completed_count} / {len(filtered_items)} Completed
                </div>
            </div>
            """)

            # Render Milestones
            for item_idx, item in enumerate(filtered_items):
                is_done = item.get("completed", False)
                item_id = item.get("id", f"{ph_idx}_{item_idx}")
                action = item.get("action", "")
                why = item.get("why_it_matters", "")
                skills = item.get("skills_opportunity", "")

                card_bg = "#F8FAFC" if is_done else "#FFFFFF"
                border_style = "border-left: 6px solid #16A34A;" if is_done else f"border-left: 6px solid {cfg['accent']};"
                strike_style = "text-decoration: line-through; color: #64748B;" if is_done else "color: #0F172A;"
                achieve_badge = '<span class="chip chip-green" style="font-size: 0.7rem;">✓ Achieved</span>' if is_done else '<span class="chip chip-slate" style="font-size: 0.7rem;">⏳ In Progress</span>'

                skills_html = f'<span class="chip chip-blue" style="font-size: 0.74rem;">🔑 {skills}</span>' if skills else ""
                cits = "".join(f'<span class="cit-tag" style="margin-right: 6px;">📄 {c}</span>' for c in item.get("citations", []))
                links = "".join(f'<span class="link-tag" style="margin-right: 6px;">🔗 {l}</span>' for l in item.get("linked_resources", []))

                render_html(f"""
                <div class="timeline-card {cfg['class']}" style="background: {card_bg}; {border_style} margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 6px;">
                        <span style="font-size: 0.74rem; font-weight: 700; color: #64748B; text-transform: uppercase;">
                            Step {ph_idx+1}.{item_idx+1}
                        </span>
                        {achieve_badge}
                    </div>
                    <h5 style="margin: 0 0 10px 0; font-size: 1.08rem; {strike_style} line-height: 1.4;">
                        {action}
                    </h5>
                    {"<div style='background: #F1F5F9; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; font-size: 0.86rem; color: #334155;'>💡 <strong>Strategic Rationale:</strong> " + why + "</div>" if why else ""}
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
                        {skills_html}
                        {cits}
                        {links}
                    </div>
                </div>
                """)

                # Interactive toggle button for student milestone tracking
                col_btn, _ = st.columns([2.5, 5])
                with col_btn:
                    btn_text = "↩ Mark as Incomplete" if is_done else "✓ Mark Milestone as Achieved"
                    btn_type = "secondary" if is_done else "primary"
                    if st.button(btn_text, key=f"btn_done_{session['id']}_{item_id}", type=btn_type, use_container_width=True):
                        # Locate exact item in milestones
                        for ph in milestones:
                            for it_obj in ph.get("items", []):
                                if it_obj.get("id") == item_id:
                                    it_obj["completed"] = not is_done
                        update_milestones_db(session["id"], milestones)
                        st.rerun()

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if displayed_count == 0:
            st.info(f"No roadmap milestones matched your search query '{rm_search}' or current filter.")

        # Export Roadmap Section
        st.markdown("---")
        with st.expander("📥 Export Your Roadmap for Offline Study & Notion"):
            st.markdown("Download or copy your personalized roadmap as a markdown file for local study planners, Obsidian, or Notion.")

            md_content = f"# EduPath AI Phased Roadmap\n"
            md_content += f"**Student Profile:** {p.get('education_stage', 'Stage').title()} ({p.get('current_year', 'Year').title()}) - {p.get('stream', 'Stream').title()}\n"
            md_content += f"**Target Goal:** {target_goal}\n\n"

            for ph in milestones:
                md_content += f"## {ph.get('phase')}\n"
                for it in ph.get("items", []):
                    chk = "[x]" if it.get("completed") else "[ ]"
                    md_content += f"- {chk} **{it.get('action')}**\n"
                    if it.get("why_it_matters"):
                        md_content += f"  - *Why:* {it.get('why_it_matters')}\n"
                    if it.get("skills_opportunity"):
                        md_content += f"  - *Skills:* {it.get('skills_opportunity')}\n"
                md_content += "\n"

            st.download_button(
                label="📄 Download Roadmap (.md)",
                data=md_content,
                file_name=f"EduPath_AI_Roadmap_{p.get('stream', 'Stream')}.md",
                mime="text/markdown",
                use_container_width=False
            )
            st.code(md_content, language="markdown")


# ===========================================================================
# PAGE 8: 🗓️ ACADEMIC SCHEDULE
# ===========================================================================
elif page == "🗓️ Academic Schedule":
    if not st.session_state.get("loaded_session"):
        st.info("💡 Please create or select an advisory plan in the **Dashboard** first.")
    else:
        session = st.session_state["loaded_session"]
        st.markdown("### 🗓️ Academic Schedule & Timeline")
        render_html("<p style='color: #64748B;'>Visual Gantt chart timeline and monthly milestones.</p>")

        if not session.get("schedule"):
            st.markdown("#### Assign Deadlines to Milestones")
            target_date = st.date_input("Target Goal Date (e.g., college counseling / admission deadline):", value=date(2027, 8, 15))

            if st.button("📅 Generate Monthly Schedule", type="primary", use_container_width=True):
                with st.spinner("Assigning monthly deadlines via Schedule Agent..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/schedule",
                            json={"pathway": session.get("pathway", ""), "target_date": target_date.isoformat()},
                            timeout=90,
                        )
                        resp.raise_for_status()
                        sched_text = resp.json()["schedule"]
                        sched_items = parse_schedule_table(sched_text)

                        conn = db.sqlite3.connect(db.DB_PATH)
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE sessions SET schedule = ?, schedule_json = ? WHERE id = ?",
                            (sched_text, json.dumps(sched_items), session["id"])
                        )
                        conn.commit()
                        conn.close()

                        st.session_state["loaded_session"] = db.get_session(session["id"])
                        st.rerun()
                    except Exception as err:
                        st.error(f"Failed to generate schedule: {err}")
        else:
            sched_items = []
            if session.get("schedule_json"):
                sched_items = json.loads(session["schedule_json"])
            else:
                sched_items = parse_schedule_table(session.get("schedule", ""))

            # Gantt Chart
            st.markdown("#### 📊 Gantt Timeline Chart")
            gantt_html = render_gantt_chart(sched_items)
            if gantt_html:
                components.html(gantt_html, height=480, scrolling=True)

            # Monthly Cards
            st.markdown("#### 📅 Monthly Action Cards")
            grouped = {}
            for item in sched_items:
                m = item["month"]
                if m not in grouped:
                    grouped[m] = []
                grouped[m].append(item)

            for m, items in grouped.items():
                st.markdown(f"##### 🗓️ {m}")
                for item in items:
                    idx = next(i for i, x in enumerate(sched_items) if x["id"] == item["id"])
                    cb_key = f"cb_{session['id']}_{item['id']}"

                    prio_badge = "🔴 High" if "high" in item["priority"].lower() else "🟡 Medium" if "med" in item["priority"].lower() else "🟢 Low"

                    checked = st.checkbox(
                        f"[{prio_badge}] {item['action']}",
                        value=item.get("completed", False),
                        key=cb_key
                    )

                    if checked != item.get("completed", False):
                        sched_items[idx]["completed"] = checked
                        update_schedule_db(session["id"], sched_items)
                        st.rerun()


# ===========================================================================
# PAGE 9: ❓ QUICK Q&A
# ===========================================================================
elif page == "❓ Quick Q&A":
    st.markdown("### ❓ Quick Institutional Q&A")
    render_html("<p style='color: #64748B;'>Ask any question regarding scholarships, cutoffs, schemes, or institutions directly to the grounded Q&A Agent.</p>")

    question = st.text_input("Type your question:", placeholder="e.g. Who is eligible for the PRAGATI scholarship scheme?")
    cat_filter = st.selectbox("Category filter:", ["Any", "scholarship", "course", "career", "scheme"])

    if st.button("🔍 Search & Formulate Answer", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please type a question.")
        else:
            with st.spinner("Searching official records..."):
                try:
                    payload = {"question": question}
                    if cat_filter != "Any":
                        payload["category"] = cat_filter

                    resp = requests.post(f"{API_BASE}/qa", json=payload, timeout=60)
                    resp.raise_for_status()
                    answer = resp.json()["answer"]

                    cits = re.findall(r"\((?:source|citation):\s*([^)]+)\)", answer, re.IGNORECASE)
                    clean_ans = re.sub(r"\((?:source|citation):\s*[^)]+\)", "", answer, re.IGNORECASE).strip()

                    with st.container(border=True):
                        st.markdown(f"**Answer:**\n\n{clean_ans}")
                        if cits:
                            st.markdown("---")
                            st.markdown("**Grounded Sources:**")
                            for c in set(cits):
                                render_html(f'<span class="cit-tag">📄 {c}</span>')
                except Exception as e:
                    st.error(f"Error querying Q&A agent: {e}")


# ===========================================================================
# PAGE 10: 📚 PAST SESSIONS
# ===========================================================================
elif page == "📚 Past Sessions":
    st.markdown("### 📚 Saved Advisory Archives")
    sessions = db.get_all_sessions(st.session_state["username"])

    if not sessions:
        st.info("No saved sessions found. Create your first plan on the **Dashboard**!")
    else:
        for s in sessions:
            with st.container(border=True):
                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**📅 Date:** `{s['created_at'][:16]}`")
                    preview = s['student_text'][:120] + ("..." if len(s['student_text']) > 120 else "")
                    st.markdown(f"*{preview}*")
                with col_btn:
                    if st.button("📂 Open", key=f"btn_open_{s['id']}"):
                        st.session_state["loaded_session"] = db.get_session(s["id"])
                        st.rerun()
