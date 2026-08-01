import html
import sqlite3
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

# ── Clean Light Theme CSS System
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --border-color: #e2e8f0;
    --border-hover: #cbd5e1;
    --accent-primary: #4f46e5;
    --accent-hover: #4338ca;
    --accent-light: #eef2ff;
    --accent-emerald: #059669;
    --accent-emerald-bg: #ecfdf5;
    --accent-rose: #dc2626;
    --accent-rose-bg: #fef2f2;
    --text-primary: #0f172a;
    --text-secondary: #64748b;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 20px rgba(0,0,0,0.06);
    --shadow-hover: 0 12px 30px rgba(79, 70, 229, 0.12);
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .stApp {
    background: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

/* Hide Streamlit UI Chrome */
header, [data-testid="stHeader"], [data-testid="stAppHeader"],
[data-testid="stToolbar"], #MainMenu, footer,
.viewerBadge_container__1t5np, [data-testid="manage-app-button"] {
    display: none !important;
    height: 0px !important;
    visibility: hidden !important;
}

.block-container {
    max-width: 1280px;
    padding-top: 1.8rem !important;
    padding-bottom: 4rem !important;
}

/* Top Navigation Header */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.8rem;
}

.brand-lockup {
    display: flex;
    align-items: center;
    gap: 0.9rem;
}

.brand-logo {
    width: 3rem;
    height: 3rem;
    display: grid;
    place-items: center;
    background: var(--accent-primary);
    color: #ffffff;
    border-radius: 12px;
    font-size: 1.6rem;
}

.brand-text {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
}

.brand-badge {
    padding: 0.2rem 0.6rem;
    background: var(--accent-light);
    border: 1px solid rgba(79, 70, 229, 0.2);
    border-radius: 9999px;
    color: var(--accent-primary);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-left: 0.5rem;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.85rem;
    background: var(--accent-emerald-bg);
    border: 1px solid rgba(5, 150, 105, 0.2);
    border-radius: 9999px;
    color: var(--accent-emerald);
    font-size: 0.78rem;
    font-weight: 700;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent-emerald);
}

/* Hero Section */
.hero-card {
    padding: 1.8rem 2rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-left: 5px solid var(--accent-primary);
    border-radius: 18px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.8rem;
}

.hero-card h1 {
    margin: 0 0 0.5rem;
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.hero-card p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.55;
}

/* Stat Metric Strip */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.4rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: var(--accent-primary) !important;
    box-shadow: var(--shadow-md) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.75rem !important;
    font-weight: 800 !important;
}

/* Section Headings */
.section-title-wrap {
    margin: 2.2rem 0 1.2rem;
}

.section-kicker {
    color: var(--accent-primary);
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.section-h2 {
    margin: 0.2rem 0 0;
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

/* Alert Cards */
.alert-card {
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.9rem;
    border-radius: 14px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    box-shadow: var(--shadow-sm);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.alert-card:hover {
    transform: translateX(4px);
    border-color: var(--border-hover);
}

.alert-card.drop { border-left: 4px solid var(--accent-emerald); }
.alert-card.increase { border-left: 4px solid var(--accent-rose); }

.alert-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.alert-pill.drop { background: var(--accent-emerald-bg); color: var(--accent-emerald); border: 1px solid rgba(5, 150, 105, 0.2); }
.alert-pill.increase { background: var(--accent-rose-bg); color: var(--accent-rose); border: 1px solid rgba(220, 38, 38, 0.2); }

.alert-meta {
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
}

/* Product Deal Cards */
.product-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 1.4rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    box-shadow: var(--shadow-sm);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.product-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent-primary);
    box-shadow: var(--shadow-hover);
}

.card-badges {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.deal-badge {
    padding: 0.3rem 0.7rem;
    background: var(--accent-light);
    color: var(--accent-primary);
    font-size: 0.72rem;
    font-weight: 800;
    border-radius: 9999px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    border: 1px solid rgba(79, 70, 229, 0.2);
}

.trend-indicator {
    font-size: 0.76rem;
    font-weight: 700;
    color: var(--accent-emerald);
    padding: 0.2rem 0.6rem;
    background: var(--accent-emerald-bg);
    border-radius: 9999px;
}

.trend-indicator.up { color: var(--accent-rose); background: var(--accent-rose-bg); }
.trend-indicator.flat { color: var(--text-secondary); background: #f1f5f9; }

/* Fixed Uniform Image Box */
.product-img-box {
    width: 100%;
    height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8fafc;
    border-radius: 12px;
    margin-bottom: 1.1rem;
    padding: 0.8rem;
    border: 1px solid #f1f5f9;
}

.product-img-box img {
    max-height: 130px;
    max-width: 100%;
    object-fit: contain;
    transition: transform 0.25s ease;
}

.product-card:hover .product-img-box img {
    transform: scale(1.05);
}

.product-title {
    color: var(--text-primary);
    font-size: 0.95rem;
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
    padding-top: 0.9rem;
    border-top: 1px dashed var(--border-color);
    display: flex;
    align-items: baseline;
    justify-content: space-between;
}

.student-price {
    font-size: 1.65rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.original-mrp {
    font-size: 0.88rem;
    color: var(--text-secondary);
    text-decoration: line-through;
}

.savings-pill {
    display: inline-block;
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--accent-emerald);
    background: var(--accent-emerald-bg);
    border: 1px solid rgba(5, 150, 105, 0.2);
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    margin-top: 0.4rem;
}

/* Unified Accent Buttons */
.deal-button {
    display: block;
    margin-top: 1rem;
    padding: 0.8rem 1rem;
    background: var(--accent-primary);
    color: #ffffff !important;
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-align: center;
    text-decoration: none !important;
    border-radius: 12px;
    text-transform: uppercase;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    transition: all 0.2s ease;
}

.deal-button:hover {
    background: var(--accent-hover);
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.4);
    transform: translateY(-1px);
}

div.stButton > button[kind="primary"] {
    background: var(--accent-primary) !important;
    border-color: var(--accent-primary) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
    transition: all 0.2s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.4) !important;
}

/* All Time Low Badge */
.all-time-low-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.2rem;
    background: var(--accent-emerald-bg);
    border: 1px solid var(--accent-emerald);
    border-radius: 9999px;
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
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
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
    border-radius: 16px !important;
}

@media (max-width: 900px) {
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
    <div class="status-pill"><span class="pulse-dot"></span> Price Engine Active</div>
</div>
""", unsafe_allow_html=True)

# ── Clean Hero Showcase Section
col_hero, col_action = st.columns([3.2, 1.2])

with col_hero:
    st.markdown("""
<div class="hero-card">
    <h1>🎓 Student Electronics Deal & Price Tracker</h1>
    <p>Monitors Flipkart budget headphones, TWS earbuds, and audio gear continuously with automated proxy rotation and real-time drop tracking.</p>
</div>
""", unsafe_allow_html=True)

with col_action:
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
st.markdown("""
<div class="section-title-wrap">
    <div class="section-kicker">Live Feed</div>
    <h2 class="section-h2">🔥 Price Drop & Hike Alerts</h2>
</div>
""", unsafe_allow_html=True)

if recent_alerts:
    for alert in recent_alerts:
        _, name, url, old_p, new_p, change, pct, a_type, img_url, t_time = alert
        is_drop = a_type == "DROP"
        card_cls = "drop" if is_drop else "increase"
        icon = "🔥 PRICE DROP" if is_drop else "⚠️ PRICE INCREASE"
        diff_str = f"-₹{abs(change):,}" if is_drop else f"+₹{change:,}"

        st.markdown(f"""
<div class="alert-card {card_cls}">
    <div>
        <span class="alert-pill {card_cls}">{icon} ({pct}% OFF)</span>
        <strong style="margin-left: 0.8rem; color:#0f172a;">{html.escape(name[:75])}</strong>
        <div class="alert-meta">
            Was: <del>₹{old_p:,}</del> ➔ <strong>Now: ₹{new_p:,}</strong> ({diff_str}) | Detected: {t_time}
        </div>
    </div>
    <div>
        <a href="{html.escape(url)}" target="_blank" style="text-decoration:none; font-size:0.82rem; font-weight:800; color:var(--accent-primary);">Grab Deal ↗</a>
    </div>
</div>
""", unsafe_allow_html=True)
else:
    st.info("💡 No price drops recorded yet. Automated price changes will pop up here!")

# ── CAMELCAMELCAMEL STYLE INTERACTIVE PRICE HISTORY GRAPH SECTION
st.markdown("""
<div class="section-title-wrap">
    <div class="section-kicker">Camel Price Analytics</div>
    <h2 class="section-h2">📈 Interactive Price History Graph</h2>
</div>
""", unsafe_allow_html=True)

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
            st.markdown("""
<div class="all-time-low-badge">
    🏆 ALL-TIME LOW RECORD PRICE! Best time to buy right now!
</div>
""", unsafe_allow_html=True)

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
            line=dict(color="#4f46e5", width=3),
            marker=dict(size=7, color="#059669", symbol="circle"),
            hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> ₹%{y:,}<extra></extra>"
        ))

        fig.add_shape(
            type="line",
            x0=df_history["Scraped At"].iloc[0],
            y0=all_time_low,
            x1=df_history["Scraped At"].iloc[-1],
            y1=all_time_low,
            line=dict(color="#059669", width=1.5, dash="dash"),
        )

        fig.update_layout(
            paper_bgcolor="#f8fafc",
            plot_bgcolor="#ffffff",
            font=dict(color="#0f172a", family="Plus Jakarta Sans"),
            margin=dict(l=20, r=20, t=30, b=30),
            height=330,
            xaxis=dict(
                title="Timestamp / Scrape Date",
                type="category",
                gridcolor="#e2e8f0",
                showline=True,
                linecolor="#cbd5e1"
            ),
            yaxis=dict(
                title="Price in ₹",
                gridcolor="#e2e8f0",
                showline=True,
                linecolor="#cbd5e1",
                tickprefix="₹",
                tickformat="d"
            ),
            hoverlabel=dict(
                bgcolor="#0f172a",
                font_size=13,
                font_family="Plus Jakarta Sans",
                font_color="#ffffff"
            )
        )

        if all_time_low == all_time_high:
            fig.update_yaxes(range=[max(0, all_time_low - 100), all_time_high + 100])

        st.plotly_chart(fig, use_container_width=True)

# ── Student Quick Budget Filters
st.markdown("""
<div class="section-title-wrap">
    <div class="section-kicker">Student Budget Filters</div>
    <h2 class="section-h2">Find Deals in Your Budget</h2>
</div>
""", unsafe_allow_html=True)

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
st.markdown(f"""
<div class="section-title-wrap">
    <div class="section-kicker">Curated Deals</div>
    <h2 class="section-h2">Student Deal Showcase ({len(filtered)} Products)</h2>
</div>
""", unsafe_allow_html=True)

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

    st.markdown(f"""
<div class="product-card">
    <div class="card-badges">
        <span class="deal-badge">{discount}% OFF</span>
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
""", unsafe_allow_html=True)

if filtered:
    card_cols = st.columns(3)
    for idx, item in enumerate(filtered):
        p_name, p_url, p_price, p_mrp, p_discount, p_image, _ = item
        with card_cols[idx % 3]:
            render_student_card(p_name, p_url, p_price, p_mrp, p_discount, p_image)
else:
    st.info("No deals found matching your selected budget bracket or search query. Try choosing 'All Student Deals'!")

# ── Data Table View
st.markdown("""
<div class="section-title-wrap">
    <div class="section-kicker">Database View</div>
    <h2 class="section-h2">Tracked Price Database</h2>
</div>
""", unsafe_allow_html=True)

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
