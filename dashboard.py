import html
import sqlite3
import textwrap
import time
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Safe import with fallback to prevent Streamlit process caching errors
try:
    from database import get_recent_alerts, get_price_history_for_product, DB_PATH
except ImportError:
    from database import get_recent_alerts, DB_PATH
    def get_price_history_for_product(url):
        with sqlite3.connect(DB_PATH) as con:
            return con.execute("""
                SELECT price, mrp, discount, scraped_at
                FROM price_history
                WHERE url = ?
                ORDER BY id ASC
            """, (url,)).fetchall()

from scraper import run_scraper

st.set_page_config(
    page_title="DropAlert | Audio Price Tracker",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Elegant Modern Dark Aesthetics & Micro-Animations CSS
st.markdown(
    textwrap.dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

    :root {
        --bg-main: #080c14;
        --bg-card: rgba(17, 24, 39, 0.75);
        --bg-card-hover: rgba(26, 36, 56, 0.9);
        --border-color: rgba(255, 255, 255, 0.08);
        --accent-indigo: #6366f1;
        --accent-sky: #38bdf8;
        --accent-emerald: #10b981;
        --accent-rose: #f43f5e;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .stApp {
        background: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    header, [data-testid="stHeader"], [data-testid="stAppHeader"] {
        display: none !important;
        height: 0px !important;
        visibility: hidden !important;
    }

    [data-testid="stToolbar"], #MainMenu, footer {
        visibility: hidden !important;
        display: none !important;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1.8rem !important;
        padding-bottom: 4rem !important;
    }

    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(18px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
        }
        50% {
            box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
        }
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.9rem 1.6rem;
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        margin-bottom: 1.6rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.4s ease-out;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .brand-logo {
        width: 3.2rem;
        height: 3.2rem;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, var(--accent-indigo), var(--accent-sky));
        border-radius: 14px;
        font-size: 1.8rem;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
    }

    .brand-text {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
    }

    .brand-badge {
        display: inline-block;
        padding: 0.22rem 0.65rem;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        color: #818cf8;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-left: 0.5rem;
    }

    .status-container {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.45rem 0.95rem;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 30px;
        color: var(--accent-emerald) !important;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-emerald);
        animation: pulseGlow 2s infinite;
    }

    /* Elegant Hero Landing Wrap */
    .hero-landing-wrap {
        padding: 2.2rem 2.4rem;
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(30, 41, 59, 0.75));
        border: 1px solid var(--border-color);
        border-radius: 24px;
        margin-bottom: 1.8rem;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(20px);
        animation: fadeInUp 0.5s ease-out;
    }

    .hero-pill-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.85rem;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 30px;
        color: #818cf8;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
    }

    .hero-main-title {
        margin: 0 0 0.9rem;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.25;
        color: #ffffff;
        letter-spacing: -0.03em;
    }

    .hero-highlight-text {
        color: var(--accent-sky);
    }

    .hero-subtext {
        margin: 0 0 1.6rem;
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
        max-width: 800px;
    }

    /* Hero Feature Cards Grid */
    .hero-feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.1rem;
        margin-bottom: 1.5rem;
    }

    .hero-feature-card {
        padding: 1.15rem 1.25rem;
        background: rgba(8, 12, 20, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .hero-feature-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(17, 24, 39, 0.85);
        transform: translateY(-4px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3);
    }

    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 0.4rem;
    }

    .feature-title {
        color: #ffffff;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .feature-desc {
        color: var(--text-secondary);
        font-size: 0.78rem;
        line-height: 1.45;
    }

    /* Hero Trust Footer Bar */
    .hero-trust-bar {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        color: var(--text-secondary);
        font-size: 0.8rem;
        font-weight: 600;
        padding-top: 1rem;
        border-top: 1px dashed rgba(255, 255, 255, 0.08);
        flex-wrap: wrap;
    }

    .hero-trust-bar span.bullet {
        color: var(--accent-indigo);
    }

    /* Scrape Action Card */
    .scrape-action-card {
        padding: 1.5rem;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        animation: fadeInUp 0.5s ease-out;
    }

    .scrape-action-card h3 {
        margin: 0 0 0.4rem;
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
    }

    .scrape-action-card p {
        margin: 0 0 1.2rem;
        color: var(--text-secondary);
        font-size: 0.82rem;
        line-height: 1.45;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 20px !important;
        padding: 1.1rem 1.3rem !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
        backdrop-filter: blur(16px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        animation: fadeInUp 0.5s ease-out;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(99, 102, 241, 0.35) !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.3) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
    }

    /* Section Headers */
    .section-title-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 2rem 0 1.1rem;
        animation: fadeInUp 0.4s ease-out;
    }

    .section-kicker {
        color: var(--accent-indigo);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .section-h2 {
        margin: 0.15rem 0 0;
        font-size: 1.35rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }

    /* Price Alert Cards */
    .alert-card-glow {
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.9rem;
        border-radius: 18px;
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        backdrop-filter: blur(12px);
        transition: all 0.25s ease;
        animation: fadeInUp 0.4s ease-out;
    }

    .alert-card-glow:hover {
        transform: translateX(4px);
        border-color: rgba(255, 255, 255, 0.15);
    }

    .alert-card-glow.drop {
        border-left: 5px solid var(--accent-emerald);
    }

    .alert-card-glow.increase {
        border-left: 5px solid var(--accent-rose);
    }

    .alert-tag {
        display: inline-block;
        padding: 0.28rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .alert-tag.drop { background: rgba(16, 185, 129, 0.12); color: var(--accent-emerald); border: 1px solid rgba(16, 185, 129, 0.25); }
    .alert-tag.increase { background: rgba(244, 63, 94, 0.12); color: var(--accent-rose); border: 1px solid rgba(244, 63, 94, 0.25); }

    /* Modern Product Deal Cards */
    .student-card {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 1.2rem;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        backdrop-filter: blur(14px);
        animation: fadeInUp 0.5s ease-out;
    }

    .student-card:hover {
        transform: translateY(-6px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.35);
        background: var(--bg-card-hover);
    }

    .card-badges {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.8rem;
    }

    .student-deal-badge {
        padding: 0.3rem 0.7rem;
        background: linear-gradient(135deg, var(--accent-indigo), var(--accent-sky));
        color: #ffffff;
        font-size: 0.7rem;
        font-weight: 800;
        border-radius: 8px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
    }

    .trend-indicator {
        font-size: 0.76rem;
        font-weight: 700;
        color: var(--accent-emerald);
        padding: 0.2rem 0.55rem;
        background: rgba(16, 185, 129, 0.1);
        border-radius: 16px;
    }

    .trend-indicator.up { color: var(--accent-rose); background: rgba(244, 63, 94, 0.1); }
    .trend-indicator.flat { color: var(--text-secondary); background: rgba(255, 255, 255, 0.05); }

    .product-img-box {
        width: 100%;
        height: 160px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(8, 12, 20, 0.5);
        border-radius: 14px;
        margin-bottom: 1rem;
        padding: 0.8rem;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }

    .product-img-box img {
        max-height: 135px;
        max-width: 100%;
        object-fit: contain;
        transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .student-card:hover .product-img-box img {
        transform: scale(1.07);
    }

    .product-title {
        color: #ffffff;
        font-size: 0.94rem;
        font-weight: 700;
        line-height: 1.4;
        margin-bottom: 1rem;
        min-height: 52px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .price-box {
        margin-top: auto;
        padding-top: 0.85rem;
        border-top: 1px dashed rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: baseline;
        justify-content: space-between;
    }

    .student-price {
        font-size: 1.65rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }

    .original-mrp {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-decoration: line-through;
    }

    .savings-pill {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--accent-emerald);
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.2);
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        margin-top: 0.4rem;
    }

    .deal-button {
        display: block;
        margin-top: 0.9rem;
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, var(--accent-indigo), #4f46e5);
        color: #ffffff !important;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-align: center;
        text-decoration: none !important;
        border-radius: 12px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.25s ease;
    }

    .deal-button:hover {
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
    }

    .all-time-low-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.6rem 1.2rem;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid var(--accent-emerald);
        border-radius: 30px;
        color: var(--accent-emerald);
        font-size: 0.84rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        padding: 0.35rem 0.75rem !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        border-color: var(--accent-indigo) !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.2) !important;
    }

    label[data-testid="stWidgetLabel"] p {
        color: var(--text-secondary) !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    [data-testid="stDataFrame"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 18px !important;
    }

    @media (max-width: 900px) {
        .hero-feature-grid { grid-template-columns: 1fr; }
        .hero-main-title { font-size: 1.8rem; }
        .topbar { flex-direction: column; align-items: flex-start; }
    }
    </style>

    <!-- Top Brand Header -->
    <div class="topbar">
        <div class="brand-lockup">
            <div class="brand-logo">🎧</div>
            <div>
                <span class="brand-text">DropAlert</span>
                <span class="brand-badge">Student Edition</span>
            </div>
        </div>
        <div class="status-container">
            <div class="status-pill"><span class="pulse-dot"></span> Price Engine Active</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

# ── Elegant Human-Designed Landing Hero Showcase Section
col_hero, col_action = st.columns([3.2, 1.2])

with col_hero:
    st.markdown(
        textwrap.dedent("""
        <div class="hero-landing-wrap">
            <div class="hero-pill-tag">
                <span class="pulse-dot"></span> REAL-TIME AUDIO DEAL TRACKER • UPDATED LIVE
            </div>
            <h1 class="hero-main-title">
                Stop Overpaying for Audio Gear.<br/>
                <span class="hero-highlight-text">Track Price Drops in Real Time.</span>
            </h1>
            <p class="hero-subtext">
                DropAlert continuously monitors Flipkart for budget TWS earbuds, neckbands, over-ear headphones, and gaming headsets. Compare historic Camel price trends and snag verified all-time low student deals.
            </p>
            
            <div class="hero-feature-grid">
                <div class="hero-feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Automated Proxy Scraper</div>
                    <div class="feature-desc">Fetches live Flipkart prices continuously without IP blocks or stale cache.</div>
                </div>
                <div class="hero-feature-card">
                    <div class="feature-icon">📉</div>
                    <div class="feature-title">Camel Price History</div>
                    <div class="feature-desc">Tracks historic price points to verify true discounts vs fake price markups.</div>
                </div>
                <div class="hero-feature-card">
                    <div class="feature-icon">🎓</div>
                    <div class="feature-title">Student Budget Focus</div>
                    <div class="feature-desc">Curated deals under ₹999 & ₹1,499 with 50%+ discount alerts for students.</div>
                </div>
            </div>
            
            <div class="hero-trust-bar">
                <span>🔒 100% Free & Open Tracker</span>
                <span class="bullet">•</span>
                <span>⚡ Scraped Live from Flipkart</span>
                <span class="bullet">•</span>
                <span>📊 Verified Price Analytics</span>
            </div>
        </div>
        """), unsafe_allow_html=True)

with col_action:
    st.markdown(
        textwrap.dedent("""
        <div class="scrape-action-card">
            <h3>⚡ Live Scraper Trigger</h3>
            <p>Fetch current audio product prices directly from Flipkart and update the deal database instantly.</p>
        </div>
        """), unsafe_allow_html=True)
    if st.button("🚀 Trigger Live Scrape Now", use_container_width=True, type="primary"):
        with st.spinner("Scraping Flipkart using automated proxy rotation..."):
            st.cache_data.clear()
            res = run_scraper()
            st.cache_data.clear()
            if res["status"] == "success":
                st.success(f"Scraped {res['products_count']} products! {res['alerts_triggered']} price alerts logged.")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Scrape failed: {res.get('message')}")

# ── DB Queries & Data Handling
@st.cache_data(ttl=30)
def get_products():
    with sqlite3.connect(DB_PATH) as con:
        return con.execute(
            """
            SELECT p.name, p.url, p.price, p.mrp, p.discount, p.image, p.scraped_at
            FROM price_history AS p
            INNER JOIN (
                SELECT url, MAX(scraped_at) AS latest_at
                FROM price_history
                WHERE price <= 6000
                GROUP BY url
            ) AS latest
                ON p.url = latest.url AND p.scraped_at = latest.latest_at
            WHERE p.price <= 6000
            ORDER BY p.price ASC
            """
        ).fetchall()

@st.cache_data(ttl=30)
def previous_price(url):
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(
            """
            SELECT price
            FROM price_history
            WHERE url = ?
            ORDER BY id DESC
            LIMIT 2
            """,
            (url,),
        ).fetchall()
    return rows[1][0] if len(rows) >= 2 else None

def clean_mrp(price, mrp, discount):
    mrp_text = str(mrp)
    discount_text = str(discount)
    if mrp > price * 10 and mrp_text.endswith(discount_text):
        candidate = mrp_text[: -len(discount_text)]
        if candidate.isdigit() and int(candidate) >= price:
            return int(candidate)
    return mrp

try:
    products = get_products()
    recent_alerts = get_recent_alerts(limit=10)
    if not products or not recent_alerts:
        from database import seed_initial_data
        seed_initial_data()
        st.cache_data.clear()
        products = get_products()
        recent_alerts = get_recent_alerts(limit=10)
except Exception as exc:
    st.error(f"Error loading database: {exc}")
    st.stop()

# ── Student Analytics Metric Cards
if products:
    total = len(products)
    avg_price = int(sum(row[2] for row in products) / total)
    cheapest = min(products, key=lambda row: row[2])
    max_discount = max(products, key=lambda row: row[4])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tracked Student Deals", total)
    m2.metric("Average Price", f"₹{avg_price:,}")
    m3.metric("Cheapest Deal Today", f"₹{cheapest[2]:,}")
    m4.metric("Max Discount", f"{max_discount[4]}% OFF")

# ── Price Drop & Hike Alerts Feed
st.markdown(
    textwrap.dedent("""
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Live Feed</div>
            <h2 class="section-h2">🔥 Price Drop & Hike Alerts</h2>
        </div>
    </div>
    """), unsafe_allow_html=True)

if recent_alerts:
    for alert in recent_alerts:
        _, name, url, old_p, new_p, change, pct, a_type, img_url, t_time = alert
        is_drop = a_type == "DROP"
        card_cls = "drop" if is_drop else "increase"
        icon = "🔥 PRICE DROP" if is_drop else "⚠️ PRICE INCREASE"
        diff_str = f"-₹{abs(change):,}" if is_drop else f"+₹{change:,}"

        st.markdown(
            textwrap.dedent(f"""
            <div class="alert-card-glow {card_cls}">
                <div>
                    <span class="alert-tag {card_cls}">{icon} ({pct}% OFF)</span>
                    <strong style="margin-left: 0.8rem; color:#ffffff;">{html.escape(name[:75])}</strong>
                    <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 0.35rem;">
                        Was: <del>₹{old_p:,}</del> ➔ <strong>Now: ₹{new_p:,}</strong> ({diff_str}) | Detected: {t_time}
                    </div>
                </div>
                <div>
                    <a href="{html.escape(url)}" target="_blank" style="text-decoration:none; font-size:0.82rem; font-weight:800; color:var(--accent-sky);">Grab Deal ↗</a>
                </div>
            </div>
            """), unsafe_allow_html=True)
else:
    st.info("💡 No price drops recorded yet. Automated price changes will pop up here!")

# ── CAMELCAMELCAMEL STYLE INTERACTIVE PRICE HISTORY GRAPH SECTION
st.markdown(
    textwrap.dedent("""
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Camel Price Analytics</div>
            <h2 class="section-h2">📈 Interactive Price History Graph</h2>
        </div>
    </div>
    """), unsafe_allow_html=True)

if products:
    product_options = {row[0]: row[1] for row in products}
    product_names = list(product_options.keys())
    
    default_index = 0
    if "selected_product_url" in st.session_state:
        target_url = st.session_state["selected_product_url"]
        for idx, (p_name, p_url) in enumerate(product_options.items()):
            if p_url == target_url:
                default_index = idx
                break

    selected_name = st.selectbox(
        "Select a product to view Camel price history chart",
        product_names,
        index=default_index
    )

    selected_url = product_options[selected_name]
    history_data = get_price_history_for_product(selected_url)

    if history_data:
        df_history = pd.DataFrame(history_data, columns=["Price", "MRP", "Discount", "Scraped At"])
        
        prices_list = df_history["Price"].tolist()
        current_p = prices_list[-1]
        all_time_low = min(prices_list)
        all_time_high = max(prices_list)
        avg_hist_p = int(sum(prices_list) / len(prices_list))

        if current_p == all_time_low:
            st.markdown(
                textwrap.dedent("""
                <div class="all-time-low-badge">
                    🏆 ALL-TIME LOW RECORD PRICE! Best time to buy right now!
                </div>
                """), unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹{current_p:,}")
        c2.metric("All-Time Lowest", f"₹{all_time_low:,}")
        c3.metric("All-Time Highest", f"₹{all_time_high:,}")
        c4.metric("Historical Average", f"₹{avg_hist_p:,}")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_history["Scraped At"],
            y=df_history["Price"],
            mode="lines+markers",
            name="Price (₹)",
            line=dict(color="#38bdf8", width=3),
            marker=dict(size=7, color="#10b981", symbol="circle"),
            hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> ₹%{y:,}<extra></extra>"
        ))

        fig.add_shape(
            type="line",
            x0=df_history["Scraped At"].iloc[0],
            y0=all_time_low,
            x1=df_history["Scraped At"].iloc[-1],
            y1=all_time_low,
            line=dict(color="#10b981", width=1.5, dash="dash"),
        )

        fig.update_layout(
            paper_bgcolor="rgba(8, 12, 20, 0.6)",
            plot_bgcolor="rgba(17, 24, 39, 0.85)",
            font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
            margin=dict(l=20, r=20, t=30, b=30),
            height=330,
            xaxis=dict(
                title="Timestamp / Scrape Date",
                type="category",
                gridcolor="rgba(255, 255, 255, 0.05)",
                showline=True,
                linecolor="rgba(255,255,255,0.08)"
            ),
            yaxis=dict(
                title="Price in ₹",
                gridcolor="rgba(255, 255, 255, 0.05)",
                showline=True,
                linecolor="rgba(255,255,255,0.08)",
                tickprefix="₹",
                tickformat="d"
            ),
            hoverlabel=dict(
                bgcolor="#1e293b",
                font_size=13,
                font_family="Plus Jakarta Sans"
            )
        )

        if all_time_low == all_time_high:
            fig.update_yaxes(range=[max(0, all_time_low - 100), all_time_high + 100])

        st.plotly_chart(fig, use_container_width=True)

# ── Student Quick Budget Filters
st.markdown(
    textwrap.dedent("""
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Student Budget Filters</div>
            <h2 class="section-h2">Find Deals in Your Budget</h2>
        </div>
    </div>
    """), unsafe_allow_html=True)

filter_col, search_col, sort_col = st.columns([2, 2, 1])

with filter_col:
    budget_filter = st.selectbox(
        "Student Budget Bracket",
        ["All Student Deals", "💸 Under ₹999", "🎧 Under ₹1,499", "🔥 50%+ Discount"]
    )

with search_col:
    search_query = st.text_input("Search Brand or Model", placeholder="boAt, Sony, Noise, JBL...")

with sort_col:
    sort_option = st.selectbox("Sort Deals", ["Price: Low to High", "Price: High to Low", "Biggest Discount %"])

filtered = list(products)

if budget_filter == "💸 Under ₹999":
    filtered = [p for p in filtered if p[2] <= 999]
elif budget_filter == "🎧 Under ₹1,499":
    filtered = [p for p in filtered if p[2] <= 1499]
elif budget_filter == "🔥 50%+ Discount":
    filtered = [p for p in filtered if p[4] >= 50]

if search_query:
    filtered = [p for p in filtered if search_query.casefold() in str(p[0]).casefold()]

if sort_option == "Price: Low to High":
    filtered.sort(key=lambda p: p[2])
elif sort_option == "Price: High to Low":
    filtered.sort(key=lambda p: p[2], reverse=True)
else:
    filtered.sort(key=lambda p: p[4], reverse=True)

# ── Student Deal Cards Display
st.markdown(
    textwrap.dedent(f"""
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Curated Deals</div>
            <h2 class="section-h2">Student Deal Showcase ({len(filtered)} Products)</h2>
        </div>
    </div>
    """), unsafe_allow_html=True)

def render_student_card(name, url, price, mrp, discount, image_url):
    old_price = previous_price(url)
    display_mrp = clean_mrp(price, mrp, discount)
    savings = display_mrp - price if display_mrp > price else 0

    if old_price and price < old_price:
        trend_text = f"↓ ₹{old_price - price:,} drop"
        trend_class = ""
    elif old_price and price > old_price:
        trend_text = f"↑ ₹{price - old_price:,} higher"
        trend_class = "up"
    else:
        trend_text = "Price steady"
        trend_class = "flat"

    safe_name = html.escape(str(name))
    short_name = safe_name if len(safe_name) <= 80 else f"{safe_name[:77]}..."
    safe_url = html.escape(str(url), quote=True)
    safe_img = html.escape(str(image_url), quote=True) if image_url else "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop"

    st.markdown(
        textwrap.dedent(f"""
        <div class="student-card">
            <div class="card-badges">
                <span class="student-deal-badge">{discount}% OFF</span>
                <span class="trend-indicator {trend_class}">{trend_text}</span>
            </div>
            <div class="product-img-box">
                <img src="{safe_img}" alt="{short_name}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop';"/>
            </div>
            <div class="product-title">{short_name}</div>
            <div style="margin-top:auto;">
                {"<div class='savings-pill'>Saved ₹" + f"{savings:,}" + "</div>" if savings > 0 else ""}
                <div class="price-box">
                    <span class="student-price">₹{price:,}</span>
                    <span class="original-mrp">₹{display_mrp:,}</span>
                </div>
                <a class="deal-button" href="{safe_url}" target="_blank" rel="noopener noreferrer">
                    Grab Student Deal ↗
                </a>
            </div>
        </div>
        """), unsafe_allow_html=True)

if filtered:
    card_cols = st.columns(3)
    for idx, item in enumerate(filtered):
        p_name, p_url, p_price, p_mrp, p_discount, p_image, _ = item
        with card_cols[idx % 3]:
            render_student_card(p_name, p_url, p_price, p_mrp, p_discount, p_image)
else:
    st.info("No deals found matching your selected budget bracket or search query. Try choosing 'All Student Deals'!")

# ── Data Table View
st.markdown(
    textwrap.dedent("""
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Database View</div>
            <h2 class="section-h2">Tracked Price Database</h2>
        </div>
    </div>
    """), unsafe_allow_html=True)

if filtered:
    table = pd.DataFrame(
        filtered,
        columns=["Name", "URL", "Price", "MRP", "Discount", "Image", "Updated"],
    )
    table["MRP"] = table.apply(lambda r: clean_mrp(r["Price"], r["MRP"], r["Discount"]), axis=1)
    table["Price"] = table["Price"].map(lambda v: f"₹{v:,}")
    table["MRP"] = table["MRP"].map(lambda v: f"₹{v:,}")
    table["Discount"] = table["Discount"].map(lambda v: f"{v}%")

    st.dataframe(
        table[["Name", "Price", "MRP", "Discount", "Updated"]],
        width="stretch",
        hide_index=True,
    )
