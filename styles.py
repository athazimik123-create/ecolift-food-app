# ============================================================
# styles.py — EcoLift "Antigravity Ide" Design System
# ============================================================
# All custom CSS is centralized here and injected via
# st.markdown(get_css(), unsafe_allow_html=True)
# ============================================================

def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
/* ── RESET & BASE ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0A0F1E 0%, #0D2137 50%, #0A1628 100%) !important;
    min-height: 100vh;
    font-family: 'Inter', sans-serif !important;
    color: #E8F0FE !important;
}

/* ── HIDE DEFAULT STREAMLIT CHROME ───────────────────────── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"]      { display: none !important; }
[data-testid="collapsedControl"]    { display: none !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

/* ── SCROLLBAR ───────────────────────────────────────────── */
::-webkit-scrollbar              { width: 6px; }
::-webkit-scrollbar-track        { background: transparent; }
::-webkit-scrollbar-thumb        { background: rgba(0,229,160,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover  { background: rgba(0,229,160,0.6); }

/* ── GLASS SIDEBAR ───────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.4) !important;
}
section[data-testid="stSidebar"] * { color: #E8F0FE !important; }

/* ── MAIN CONTENT AREA ───────────────────────────────────── */
[data-testid="stMainBlockContainer"] {
    padding: 2rem 2.5rem !important;
    max-width: 1300px !important;
    margin: 0 auto !important;
}

/* ── GLASS CARD ──────────────────────────────────────────── */
.glass-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 1.8rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.37), inset 0 1px 0 rgba(255,255,255,0.1);
    transition: transform 0.3s cubic-bezier(.25,.8,.25,1),
                box-shadow 0.3s cubic-bezier(.25,.8,.25,1);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,160,0.4), transparent);
}
.glass-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 60px rgba(0,229,160,0.15), 0 8px 32px rgba(0,0,0,0.5);
}

/* ── RESCUE / FOOD CARD ──────────────────────────────────── */
.rescue-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    cursor: pointer;
}
.rescue-card:hover {
    transform: translateY(-5px) scale(1.01);
    border-color: rgba(0,229,160,0.35);
    box-shadow: 0 16px 48px rgba(0,229,160,0.12), 0 4px 24px rgba(0,0,0,0.4);
}
.rescue-card .food-icon  { font-size: 2.4rem; margin-bottom: 0.5rem; display: block; }
.rescue-card .food-title { font-size: 1.05rem; font-weight: 600; color: #fff; }
.rescue-card .food-meta  { font-size: 0.82rem; color: rgba(232,240,254,0.6); margin-top: 0.3rem; }
.rescue-card .food-kg    { font-size: 1.3rem; font-weight: 700; color: #00E5A0; }

/* ── KPI METRIC CARD ─────────────────────────────────────── */
.kpi-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,229,160,0.1); }
.kpi-card .kpi-label { font-size: 0.78rem; font-weight: 500; color: rgba(232,240,254,0.55); text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-card .kpi-value { font-size: 2rem; font-weight: 800; color: #00E5A0; margin: 0.35rem 0 0; line-height: 1; }
.kpi-card .kpi-sub   { font-size: 0.75rem; color: rgba(232,240,254,0.4); margin-top: 0.3rem; }

/* ── PULSE GLOW (live data indicator) ───────────────────── */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,229,160,0.5); }
    50%       { box-shadow: 0 0 0 10px rgba(0,229,160,0); }
}
.pulse-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #00E5A0;
    animation: pulse-glow 2s infinite;
    vertical-align: middle;
    margin-right: 6px;
}
.live-badge {
    display: inline-flex; align-items: center;
    background: rgba(0,229,160,0.1);
    border: 1px solid rgba(0,229,160,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem; font-weight: 600;
    color: #00E5A0;
    letter-spacing: 0.05em;
}

/* ── CONFIDENCE BAR ──────────────────────────────────────── */
.conf-bar-wrap { background: rgba(255,255,255,0.08); border-radius: 8px; height: 8px; overflow: hidden; margin: 0.5rem 0; }
.conf-bar-fill { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #00E5A0, #7C6EFA); transition: width 0.6s ease; }

/* ── BUTTONS ─────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00E5A0, #00C87A) !important;
    color: #0A0F1E !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1.6rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(0,229,160,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,229,160,0.45) !important;
    background: linear-gradient(135deg, #00FFBE, #00E5A0) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── FAB (Floating Action Button) ────────────────────────── */
.fab {
    position: fixed; bottom: 2rem; right: 2rem; z-index: 9999;
    width: 58px; height: 58px;
    background: linear-gradient(135deg, #00E5A0, #7C6EFA);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,229,160,0.4);
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(.25,.8,.25,1), box-shadow 0.3s ease;
    animation: float 4s ease-in-out infinite;
}
.fab:hover { transform: scale(1.12) translateY(-4px); box-shadow: 0 16px 48px rgba(0,229,160,0.55); }

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-6px); }
}

/* ── GRADIENT BADGE ──────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-green  { background: rgba(0,229,160,0.15); color: #00E5A0; border: 1px solid rgba(0,229,160,0.3); }
.badge-purple { background: rgba(124,110,250,0.15); color: #7C6EFA; border: 1px solid rgba(124,110,250,0.3); }
.badge-orange { background: rgba(255,159,67,0.15); color: #FF9F43; border: 1px solid rgba(255,159,67,0.3); }
.badge-red    { background: rgba(255,71,87,0.15);  color: #FF4757; border: 1px solid rgba(255,71,87,0.3); }

/* ── FORM INPUTS ─────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 10px !important;
    color: #E8F0FE !important;
    font-family: 'Inter', sans-serif !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(0,229,160,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,229,160,0.12) !important;
}
label { color: rgba(232,240,254,0.75) !important; font-size: 0.85rem !important; font-weight: 500 !important; }

/* ── SLIDER ──────────────────────────────────────────────── */
[data-testid="stSlider"] .st-ey  { background: #00E5A0 !important; }
[data-testid="stSlider"] .st-f8  { background: rgba(255,255,255,0.1) !important; }

/* ── SELECTBOX ───────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 10px !important;
    color: #E8F0FE !important;
}

/* ── TOGGLE / CHECKBOX ───────────────────────────────────── */
[data-testid="stCheckbox"] span { color: rgba(232,240,254,0.8) !important; }

/* ── PLOTLY CHARTS ───────────────────────────────────────── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── DIVIDER ─────────────────────────────────────────────── */
hr { border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.5rem 0; }

/* ── SECTION HEADER ──────────────────────────────────────── */
.section-title {
    font-size: 1.5rem; font-weight: 700;
    background: linear-gradient(135deg, #00E5A0, #7C6EFA);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.section-sub { font-size: 0.88rem; color: rgba(232,240,254,0.5); margin-bottom: 1.5rem; }

/* ── LOGIN CARD ──────────────────────────────────────────── */
.login-wrap {
    max-width: 420px; margin: 6vh auto 0;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 24px;
    padding: 2.8rem 2.4rem;
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    box-shadow: 0 24px 64px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
}
.login-logo {
    text-align: center; margin-bottom: 1.8rem;
}
.login-logo .logo-icon {
    font-size: 3.2rem;
    filter: drop-shadow(0 0 16px rgba(0,229,160,0.5));
}
.login-logo h1 {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #00E5A0, #7C6EFA);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-top: 0.5rem;
}
.login-logo p { font-size: 0.85rem; color: rgba(232,240,254,0.5); margin-top: 0.3rem; }

/* ── SIDEBAR NAV ITEM ────────────────────────────────────── */
.sidebar-user {
    background: rgba(0,229,160,0.08);
    border: 1px solid rgba(0,229,160,0.2);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin-bottom: 1.2rem;
}
.sidebar-user .su-name  { font-weight: 700; font-size: 0.95rem; color: #fff; }
.sidebar-user .su-role  { font-size: 0.75rem; color: #00E5A0; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }
.sidebar-user .su-tier  { font-size: 0.72rem; color: rgba(232,240,254,0.45); margin-top: 2px; }

/* ── STATUS BADGES ───────────────────────────────────────── */
.status-pending    { color: #FF9F43; }
.status-accepted   { color: #00E5A0; }
.status-in_transit { color: #7C6EFA; }
.status-delivered  { color: rgba(232,240,254,0.5); }

/* ── SPONSOR CARD ────────────────────────────────────────── */
.sponsor-card {
    background: rgba(124,110,250,0.06);
    border: 1px solid rgba(124,110,250,0.18);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.sponsor-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(124,110,250,0.15); }
.sponsor-rank { font-size: 1.4rem; font-weight: 800; color: rgba(124,110,250,0.6); }
.sponsor-name { font-size: 1rem; font-weight: 700; color: #fff; }
.sponsor-credits { font-size: 0.82rem; color: rgba(232,240,254,0.5); margin-top: 2px; }
</style>
"""


def render_page_header(title: str, subtitle: str, icon: str = "") -> str:
    """Returns HTML for a standardized page header."""
    return f"""
    <div style="margin-bottom:2rem;">
        <div class="section-title">{icon} {title}</div>
        <div class="section-sub">{subtitle}</div>
    </div>
    """


def render_kpi(label: str, value: str, sub: str = "") -> str:
    """Returns HTML for a KPI metric card."""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
    </div>
    """


def render_rescue_card(rescue: dict) -> str:
    """Returns HTML for a food rescue listing card."""
    food = rescue.get("food_details", {})
    status = rescue.get("status", "pending")
    conf = rescue.get("confidence_score", 0)
    is_premium = rescue.get("premium_delivery", False)

    conf_pct = int(conf * 100)
    badge_html = '<span class="badge badge-orange">⚡ Premium</span>' if is_premium else ""
    pulse_html = '<span class="pulse-dot"></span>' if conf >= 0.90 else ""

    return f"""
    <div class="rescue-card">
        <span class="food-icon">{rescue.get("icon", "📦")}</span>
        <div class="food-title">{rescue.get("business_name", "Unknown")}</div>
        <div class="food-meta">{food.get("type", "Mixed")} · {food.get("description","")[:60]}</div>
        <div style="margin:0.7rem 0;display:flex;align-items:center;gap:0.6rem;">
            <div class="food-kg">{food.get("quantity_kg", 0)} kg</div>
            <span class="badge badge-{'green' if status=='pending' else 'purple'}">{status}</span>
            {badge_html}
        </div>
        <div style="font-size:0.76rem;color:rgba(232,240,254,0.5);margin-bottom:0.4rem;">
            {pulse_html}AI Confidence: {conf_pct}%
        </div>
        <div class="conf-bar-wrap">
            <div class="conf-bar-fill" style="width:{conf_pct}%;"></div>
        </div>
    </div>
    """


def render_prediction_card(pred: dict, already_converted: bool = False) -> str:
    """Returns HTML for a waste prediction card."""
    wd = pred.get("waste_data", pred)
    conf = pred.get("confidence", pred.get("confidence_score", 0))
    conf_pct = int(conf * 100)
    color = "#00E5A0" if conf >= 0.85 else "#FF9F43"
    status_label = "✓ Converted to Rescue" if already_converted else ("🔥 High Confidence" if conf >= 0.85 else "Monitoring")
    status_badge = "badge-green" if already_converted else ("badge-orange" if conf >= 0.85 else "badge-purple")

    return f"""
    <div class="rescue-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.8rem;">
            <div>
                <div class="food-title">🏢 {wd.get("business_name","Unknown")}</div>
                <div class="food-meta">{wd.get("food_type","Mixed")} · Location {wd.get("location_id","")}</div>
            </div>
            <span class="badge {status_badge}">{status_label}</span>
        </div>
        <div class="food-kg">{wd.get("predicted_waste_kg",0)} kg predicted</div>
        <div style="font-size:0.76rem;color:rgba(232,240,254,0.5);margin:0.5rem 0 0.3rem;">
            AI Confidence: <span style="color:{color};font-weight:700;">{conf_pct}%</span>
        </div>
        <div class="conf-bar-wrap">
            <div class="conf-bar-fill" style="width:{conf_pct}%;background:linear-gradient(90deg,{color},{color}99);"></div>
        </div>
    </div>
    """
