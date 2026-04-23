# ============================================================
# app.py — EcoLift Landing Page & Authentication
# ============================================================
# Entry point for the Streamlit app.
# Run with: streamlit run app.py
#
# Demo credentials (mock mode, no Firebase needed):
#   admin@ecolift.com     / demo1234
#   donor@ecolift.com     / demo1234
#   receiver@ecolift.com  / demo1234
#   logistics@ecolift.com / demo1234
# ============================================================

import streamlit as st
from datetime import datetime, timezone

from firebase_config import sign_in_with_email_password, get_user
from styles import get_css

# ── Page config (must be first Streamlit call) ────────────────
st.set_page_config(
    page_title="EcoLift — Food Rescue Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Antigravity CSS ────────────────────────────────────
st.markdown(get_css(), unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────
def _init_session():
    defaults = {
        "authenticated": False,
        "id_token":      None,
        "uid":           None,
        "user_role":     None,
        "user_name":     None,
        "user_email":    None,
        "sub_tier":      "basic",
        "cart":          [],          # claimed rescue IDs in this session
        "notifications": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# ════════════════════════════════════════════════════════════
# ── AUTHENTICATED SIDEBAR ────────────────────────────────────
# ════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 1.5rem;">
            <div style="font-size:2.4rem;filter:drop-shadow(0 0 12px rgba(0,229,160,0.5));">🌿</div>
            <div style="font-size:1.3rem;font-weight:800;background:linear-gradient(135deg,#00E5A0,#7C6EFA);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                EcoLift
            </div>
            <div style="font-size:0.7rem;color:rgba(232,240,254,0.4);letter-spacing:0.12em;text-transform:uppercase;">
                Food Rescue Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        # User info card
        role_icon = {"admin": "🛡️", "donor": "🍽️", "receiver": "🤝", "logistics": "🚚"}.get(st.session_state.user_role, "👤")
        tier_label = "⭐ Pro" if st.session_state.sub_tier == "pro" else "Basic"
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="su-name">{role_icon} {st.session_state.user_name}</div>
            <div class="su-role">{st.session_state.user_role}</div>
            <div class="su-tier">{tier_label} Plan</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation links (Streamlit handles multipage automatically)
        st.markdown("**Navigate**")
        st.page_link("app.py",                        label="🏠 Home",               )
        st.page_link("pages/01_Marketplace.py",        label="🛒 Rescue Marketplace"  )
        st.page_link("pages/02_Donor_Predictions.py",  label="📊 Donor Predictions"   )
        st.page_link("pages/03_CSR_Portal.py",         label="🌍 CSR Portal"          )
        if st.session_state.user_role == "admin":
            st.page_link("pages/04_Admin_Revenue.py", label="💰 Revenue Dashboard"   )

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ════════════════════════════════════════════════════════════
# ── LOGIN PAGE ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════

def render_login():
    import os
    from firebase_config import sign_up_with_email_password, FIREBASE_WEB_API_KEY

    is_mock = (FIREBASE_WEB_API_KEY == "DEMO_KEY")

    # Animated background particles (CSS only)
    st.markdown("""
    <style>
    @keyframes drift { 0%{transform:translateY(0) rotate(0deg);opacity:.6}
                      100%{transform:translateY(-100vh) rotate(720deg);opacity:0} }
    .particle { position:fixed; border-radius:50%; pointer-events:none; z-index:0;
                background:rgba(0,229,160,0.12); animation:drift linear infinite; }
    </style>
    <div class="particle" style="width:8px;height:8px;left:15%;bottom:-20px;animation-duration:18s;animation-delay:0s;"></div>
    <div class="particle" style="width:5px;height:5px;left:35%;bottom:-20px;animation-duration:22s;animation-delay:3s;"></div>
    <div class="particle" style="width:10px;height:10px;left:60%;bottom:-20px;animation-duration:16s;animation-delay:6s;"></div>
    <div class="particle" style="width:6px;height:6px;left:80%;bottom:-20px;animation-duration:20s;animation-delay:1s;"></div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        # Logo
        st.markdown("""
        <div style="text-align:center;padding:2rem 0 1.5rem;">
            <div style="font-size:3.2rem;filter:drop-shadow(0 0 16px rgba(0,229,160,0.5));">🌿</div>
            <div style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,#00E5A0,#7C6EFA);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">EcoLift</div>
            <div style="font-size:0.85rem;color:rgba(232,240,254,0.5);margin-top:0.3rem;">Rescue food. Build community. Generate impact.</div>
        </div>
        """, unsafe_allow_html=True)

        # Mock mode banner
        if is_mock:
            st.markdown("""
            <div style="background:rgba(0,229,160,0.07);border:1px solid rgba(0,229,160,0.2);
                        border-radius:12px;padding:0.8rem 1rem;margin-bottom:1rem;font-size:0.8rem;color:rgba(232,240,254,0.7);">
                🔑 <b style="color:#00E5A0;">Demo Mode</b> — use password <code>demo1234</code> with:<br>
                <code>admin@ecolift.com</code> &nbsp;·&nbsp; <code>donor@ecolift.com</code> &nbsp;·&nbsp; <code>receiver@ecolift.com</code>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(124,110,250,0.07);border:1px solid rgba(124,110,250,0.2);
                        border-radius:12px;padding:0.8rem 1rem;margin-bottom:1rem;font-size:0.8rem;color:rgba(232,240,254,0.7);">
                🔥 <b style="color:#7C6EFA;">Live Mode</b> — Connected to Firebase. Sign in or create a new account below.
            </div>
            """, unsafe_allow_html=True)

        # ── Sign In / Register tabs ────────────────────────────
        tab_signin, tab_register = st.tabs(["🔐 Sign In", "✨ Create Account"])

        # ── SIGN IN TAB ────────────────────────────────────────
        with tab_signin:
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("Email Address", placeholder="you@example.com", key="si_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="si_pass")
                submitted = st.form_submit_button("Sign In →", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    with st.spinner("Authenticating…"):
                        result = sign_in_with_email_password(email, password)

                    if "error" in result:
                        err = result["error"]
                        st.error(f"❌ {err}")
                        # Helpful context for common Firebase errors
                        if "INVALID_LOGIN_CREDENTIALS" in err or "EMAIL_NOT_FOUND" in err:
                            st.info(
                                "💡 **No account found.** Switch to the **✨ Create Account** tab "
                                "to register a new account, or check your email/password.",
                                icon="ℹ️"
                            )
                        elif "TOO_MANY_ATTEMPTS" in err:
                            st.warning("Too many failed attempts. Please wait a few minutes before trying again.", icon="⚠️")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.id_token   = result.get("idToken")
                        st.session_state.uid        = result.get("localId")
                        st.session_state.user_role  = result.get("role", "receiver")
                        st.session_state.user_name  = result.get("name", email.split("@")[0])
                        st.session_state.user_email = email
                        st.session_state.sub_tier   = "basic"
                        st.success(f"Welcome back, {st.session_state.user_name}! 🎉")
                        st.rerun()

        # ── REGISTER TAB ───────────────────────────────────────
        with tab_register:
            if is_mock:
                st.info(
                    "Account creation requires a real Firebase project. "
                    "Add your `FIREBASE_WEB_API_KEY` to `.env` and restart.",
                    icon="🔒"
                )
            else:
                with st.form("register_form", clear_on_submit=True):
                    reg_name  = st.text_input("Full Name", placeholder="Jane Doe", key="reg_name")
                    reg_email = st.text_input("Email Address", placeholder="you@example.com", key="reg_email")
                    reg_role  = st.selectbox(
                        "I am a…",
                        options=["receiver", "donor", "logistics"],
                        format_func=lambda r: {
                            "receiver":  "🤝 Receiver (NGO / Shelter / Individual)",
                            "donor":     "🍽️ Donor (Restaurant / Grocery / Caterer)",
                            "logistics": "🚚 Logistics Partner (Delivery Driver)",
                        }[r],
                        key="reg_role"
                    )
                    reg_pass  = st.text_input("Password", type="password",
                                              placeholder="Min. 6 characters", key="reg_pass")
                    reg_pass2 = st.text_input("Confirm Password", type="password",
                                              placeholder="Repeat password", key="reg_pass2")
                    reg_submit = st.form_submit_button("Create My Account →", use_container_width=True)

                if reg_submit:
                    if not all([reg_name, reg_email, reg_pass, reg_pass2]):
                        st.error("Please fill in all fields.")
                    elif reg_pass != reg_pass2:
                        st.error("Passwords do not match.")
                    elif len(reg_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        with st.spinner("Creating your account…"):
                            result = sign_up_with_email_password(
                                reg_email, reg_pass, reg_name, reg_role
                            )
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                            if "EMAIL_EXISTS" in result["error"]:
                                st.info("This email is already registered. Please Sign In instead.", icon="ℹ️")
                        else:
                            st.session_state.authenticated = True
                            st.session_state.id_token   = result.get("idToken")
                            st.session_state.uid        = result.get("localId")
                            st.session_state.user_role  = reg_role
                            st.session_state.user_name  = reg_name
                            st.session_state.user_email = reg_email
                            st.session_state.sub_tier   = "basic"
                            st.success(f"🎉 Account created! Welcome to EcoLift, {reg_name}!")
                            st.rerun()

        # Features row
        st.markdown("<br>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("""<div class="glass-card" style="text-align:center;padding:1rem;">
                <div style="font-size:1.8rem;">🤝</div>
                <div style="font-size:0.75rem;font-weight:600;color:#00E5A0;margin-top:0.4rem;">Community</div>
                <div style="font-size:0.7rem;color:rgba(232,240,254,0.45);">Connect donors &amp; receivers</div>
            </div>""", unsafe_allow_html=True)
        with f2:
            st.markdown("""<div class="glass-card" style="text-align:center;padding:1rem;">
                <div style="font-size:1.8rem;">🤖</div>
                <div style="font-size:0.75rem;font-weight:600;color:#7C6EFA;margin-top:0.4rem;">AI-Powered</div>
                <div style="font-size:0.7rem;color:rgba(232,240,254,0.45);">Predictive surplus alerts</div>
            </div>""", unsafe_allow_html=True)
        with f3:
            st.markdown("""<div class="glass-card" style="text-align:center;padding:1rem;">
                <div style="font-size:1.8rem;">💚</div>
                <div style="font-size:0.75rem;font-weight:600;color:#00E5A0;margin-top:0.4rem;">Impact</div>
                <div style="font-size:0.7rem;color:rgba(232,240,254,0.45);">Meals saved, CO₂ reduced</div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# ── HOME DASHBOARD (post-login) ──────────────────────────────
# ════════════════════════════════════════════════════════════

def render_home():
    render_sidebar()

    from firebase_config import get_active_rescues, get_revenue_stats
    from waste_api import fetch_waste_predictions

    stats  = get_revenue_stats()
    now_str = datetime.now(timezone.utc).strftime("%b %d, %Y · %H:%M UTC")

    # Page header
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem;flex-wrap:wrap;gap:1rem;">
        <div>
            <div class="section-title">Good to see you, {st.session_state.user_name} 👋</div>
            <div class="section-sub">Here's your EcoLift impact overview · {now_str}</div>
        </div>
        <div class="live-badge"><span class="pulse-dot"></span>LIVE DATA</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Active Rescues</div>
            <div class="kpi-value">{len(get_active_rescues())}</div>
            <div class="kpi-sub">Available now</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Meals Rescued</div>
            <div class="kpi-value">{stats["meals_rescued"]:,}</div>
            <div class="kpi-sub">All-time</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">CO₂ Offset</div>
            <div class="kpi-value">{stats["co2_offset_kg"]} kg</div>
            <div class="kpi-sub">Estimated</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Platform Revenue</div>
            <div class="kpi-value">${stats["total_revenue"]:,.0f}</div>
            <div class="kpi-sub">Total generated</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent predictions + Quick Actions
    col_pred, col_action = st.columns([1.6, 1])

    with col_pred:
        st.markdown("""<div class="section-title" style="font-size:1.1rem;">🔮 Latest Surplus Predictions</div>
        <div class="section-sub">AI-generated alerts from the Waste Management System</div>""",
        unsafe_allow_html=True)

        preds = fetch_waste_predictions(4)
        for p in preds[:4]:
            conf = p.get("confidence_score", 0)
            conf_pct = int(conf * 100)
            badge = "🔥 High Confidence" if conf >= 0.85 else "Monitoring"
            badge_cls = "badge-green" if conf >= 0.85 else "badge-orange"
            pulse = '<span class="pulse-dot"></span>' if conf >= 0.90 else ""
            st.markdown(f"""
            <div class="rescue-card" style="margin-bottom:0.7rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="food-title">{p.get('icon','📦')} {p.get('business_name')}</span>
                    <span class="badge {badge_cls}">{badge}</span>
                </div>
                <div class="food-meta">{p.get('food_type')} · {p.get('predicted_waste_kg')} kg predicted</div>
                <div style="font-size:0.73rem;color:rgba(232,240,254,0.45);margin-top:0.4rem;">
                    {pulse}Confidence: <b style="color:#00E5A0;">{conf_pct}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_action:
        st.markdown("""<div class="section-title" style="font-size:1.1rem;">⚡ Quick Actions</div>
        <div class="section-sub">Jump straight in</div>""", unsafe_allow_html=True)

        st.markdown("""<div class="glass-card" style="margin-bottom:0.8rem;">
            <div style="font-size:1.4rem;">🛒</div>
            <div style="font-weight:600;font-size:0.95rem;margin-top:0.4rem;">Browse Marketplace</div>
            <div style="font-size:0.78rem;color:rgba(232,240,254,0.5);">Claim available food rescues</div>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/01_Marketplace.py", label="→ Open Marketplace")

        st.markdown("""<div class="glass-card" style="margin-bottom:0.8rem;">
            <div style="font-size:1.4rem;">📊</div>
            <div style="font-weight:600;font-size:0.95rem;margin-top:0.4rem;">Donor Dashboard</div>
            <div style="font-size:0.78rem;color:rgba(232,240,254,0.5);">Accept rescue predictions</div>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/02_Donor_Predictions.py", label="→ View Predictions")

        st.markdown("""<div class="glass-card">
            <div style="font-size:1.4rem;">🌍</div>
            <div style="font-weight:600;font-size:0.95rem;margin-top:0.4rem;">CSR Portal</div>
            <div style="font-size:0.78rem;color:rgba(232,240,254,0.5);">Buy Food Rescue Credits</div>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/03_CSR_Portal.py", label="→ Buy Credits")


# ════════════════════════════════════════════════════════════
# ── MAIN ROUTER ──────────────────────────────────────────────
# ════════════════════════════════════════════════════════════

if st.session_state.authenticated:
    render_home()
else:
    render_login()
