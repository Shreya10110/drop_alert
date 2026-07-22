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
    page_title="DropAlert | Student Edition Price Tracker",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Student Neo-Modern Dark Glassmorphism CSS Design
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800;900&display=swap');

    :root {
        --bg-main: #0b0f19;
        --bg-card: rgba(18, 24, 38, 0.85);
        --bg-card-hover: rgba(26, 35, 56, 0.95);
        --border-color: rgba(255, 255, 255, 0.08);
        --border-glow: rgba(0, 242, 254, 0.3);
        --neon-cyan: #00f2fe;
        --neon-green: #00ff87;
        --neon-purple: #7928ca;
        --flame-red: #ff3366;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .stApp {
        background: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
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
        max-width: 1280px;
        padding-top: 2.5rem !important;
        padding-bottom: 4rem !important;
    }

    /* Top Brand Bar */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.8rem 1.2rem;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-green));
        border-radius: 14px;
        font-size: 1.8rem;
        box-shadow: 0 0 20px rgba(0, 255, 135, 0.4);
    }

    .brand-text {
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        background: linear-gradient(135deg, #ffffff 30%, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        background: linear-gradient(90deg, #7928ca, #ff0080);
        border-radius: 20px;
        color: #ffffff;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.08em;
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
        gap: 0.5rem;
        padding: 0.45rem 0.85rem;
        background: rgba(0, 255, 135, 0.08);
        border: 1px solid rgba(0, 255, 135, 0.25);
        border-radius: 30px;
        color: var(--neon-green) !important;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--neon-green);
        box-shadow: 0 0 10px var(--neon-green);
        animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 255, 135, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0); }
    }

    /* Hero Banner */
    .hero-banner {
        padding: 1.4rem 1.8rem;
        background: linear-gradient(135deg, rgba(18, 24, 38, 0.9), rgba(30, 41, 59, 0.8));
        border: 1px solid var(--border-color);
        border-left: 5px solid var(--neon-cyan);
        border-radius: 20px;
        margin-bottom: 1.5rem;
    }

    .hero-banner h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }

    .hero-banner p {
        margin: 0.3rem 0 0;
        color: var(--text-secondary);
        font-size: 0.88rem;
    }

    /* Custom Streamlit Metrics */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 18px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
        backdrop-filter: blur(12px);
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.75rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #ffffff, var(--neon-cyan));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Section Headers */
    .section-title-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 2rem 0 1rem;
    }

    .section-kicker {
        color: var(--neon-cyan);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .section-h2 {
        margin: 0.1rem 0 0;
        font-size: 1.3rem;
        font-weight: 800;
        color: #ffffff;
    }

    /* Alert Cards */
    .alert-card-glow {
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.9rem;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }

    .alert-card-glow.drop {
        border-left: 5px solid var(--neon-green);
        box-shadow: 0 0 20px rgba(0, 255, 135, 0.12);
    }

    .alert-card-glow.increase {
        border-left: 5px solid var(--flame-red);
        box-shadow: 0 0 20px rgba(255, 51, 102, 0.12);
    }

    .alert-tag {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 30px;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .alert-tag.drop { background: rgba(0, 255, 135, 0.15); color: var(--neon-green); border: 1px solid rgba(0, 255, 135, 0.3); }
    .alert-tag.increase { background: rgba(255, 51, 102, 0.15); color: var(--flame-red); border: 1px solid rgba(255, 51, 102, 0.3); }

    /* Student Product Cards */
    .student-card {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 1.3rem;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(12px);
    }

    .student-card:hover {
        transform: translateY(-5px);
        border-color: var(--neon-cyan);
        box-shadow: 0 12px 30px rgba(0, 242, 254, 0.18);
        background: var(--bg-card-hover);
    }

    .card-badges {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.9rem;
    }

    .student-deal-badge {
        padding: 0.35rem 0.65rem;
        background: linear-gradient(135deg, var(--neon-green), var(--neon-cyan));
        color: #0b0f19;
        font-size: 0.7rem;
        font-weight: 900;
        border-radius: 8px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .trend-indicator {
        font-size: 0.75rem;
        font-weight: 800;
        color: var(--neon-green);
    }

    .trend-indicator.up { color: var(--flame-red); }
    .trend-indicator.flat { color: var(--text-secondary); }

    .product-title {
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.4;
        margin-bottom: 1rem;
        min-height: 52px;
    }

    .price-box {
        margin-top: auto;
        padding-top: 0.8rem;
        border-top: 1px dashed rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: baseline;
        justify-content: space-between;
    }

    .student-price {
        font-size: 1.65rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -0.03em;
    }

    .original-mrp {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-decoration: line-through;
    }

    .savings-pill {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 800;
        color: var(--neon-green);
        background: rgba(0, 255, 135, 0.1);
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        margin-top: 0.4rem;
    }

    .deal-button {
        display: block;
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, var(--neon-cyan), #00b4db);
        color: #0b0f19 !important;
        font-size: 0.8rem;
        font-weight: 900;
        letter-spacing: 0.06em;
        text-align: center;
        text-decoration: none !important;
        border-radius: 12px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
        transition: all 0.2s ease;
    }

    .deal-button:hover {
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5);
        transform: scale(1.02);
    }

    /* All time low badge styling */
    .all-time-low-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.2rem;
        background: linear-gradient(135deg, rgba(0, 255, 135, 0.2), rgba(0, 242, 254, 0.2));
        border: 1px solid var(--neon-green);
        border-radius: 30px;
        color: var(--neon-green);
        font-size: 0.85rem;
        font-weight: 900;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 0 0 20px rgba(0, 255, 135, 0.3);
        margin-bottom: 1rem;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2) !important;
    }

    label[data-testid="stWidgetLabel"] p {
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    [data-testid="stDataFrame"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 18px !important;
    }

    @media (max-width: 768px) {
        .topbar { flex-direction: column; align-items: flex-start; }
        .status-container { margin-top: 0.5rem; }
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
            <div class="status-pill"><span class="pulse-dot"></span> Auto Proxy Engine Active</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Hero Section & Scraper Trigger
col_hero, col_action = st.columns([3, 1])

with col_hero:
    st.markdown(
        """
        <div class="hero-banner">
            <h1>🎓 Student Electronics Deal & Price Drop Tracker</h1>
            <p>Monitors Flipkart budget headphones, ear-buds, and audio gear continuously with automated proxy rotation and desktop drop alerts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_action:
    if st.button("⚡ Scrape Fresh Deals", use_container_width=True, type="primary"):
        with st.spinner("Scraping Flipkart using automated proxy rotation..."):
            st.cache_data.clear()
            res = run_scraper()
            st.cache_data.clear()
            if res["status"] == "success":
                st.success(f"Scraped {res['products_count']} products! {res['alerts_triggered']} price alerts triggered.")
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
            SELECT p.name, p.url, p.price, p.mrp, p.discount, p.scraped_at
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
            ORDER BY scraped_at DESC
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
    """
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Live Feed</div>
            <h2 class="section-h2">🔥 Price Drop & Hike Alerts</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if recent_alerts:
    for alert in recent_alerts:
        _, name, url, old_p, new_p, change, pct, a_type, _, t_time = alert
        is_drop = a_type == "DROP"
        card_cls = "drop" if is_drop else "increase"
        icon = "🔥 PRICE DROP" if is_drop else "⚠️ PRICE INCREASE"
        diff_str = f"-₹{abs(change):,}" if is_drop else f"+₹{change:,}"

        st.markdown(
            f"""
            <div class="alert-card-glow {card_cls}">
                <div>
                    <span class="alert-tag {card_cls}">{icon} ({pct}% OFF)</span>
                    <strong style="margin-left: 0.8rem; color:#ffffff;">{html.escape(name[:75])}</strong>
                    <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 0.35rem;">
                        Was: <del>₹{old_p:,}</del> ➔ <strong>Now: ₹{new_p:,}</strong> ({diff_str}) | Detected: {t_time}
                    </div>
                </div>
                <div>
                    <a href="{html.escape(url)}" target="_blank" style="text-decoration:none; font-size:0.82rem; font-weight:900; color:var(--neon-cyan);">Grab Deal ↗</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("💡 No price drops recorded yet. Automated price changes will pop up here and trigger desktop notifications!")

# ── CAMELCAMELCAMEL STYLE INTERACTIVE PRICE HISTORY GRAPH SECTION
st.markdown(
    """
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Camel Price Analytics</div>
            <h2 class="section-h2">📈 Interactive Price History Graph</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
                """
                <div class="all-time-low-badge">
                    🏆 ALL-TIME LOW RECORD PRICE! Best time to buy right now!
                </div>
                """,
                unsafe_allow_html=True,
            )

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
            line=dict(color="#00f2fe", width=3.5),
            marker=dict(size=8, color="#00ff87", symbol="circle"),
            hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> ₹%{y:,}<extra></extra>"
        ))

        fig.add_shape(
            type="line",
            x0=df_history["Scraped At"].iloc[0],
            y0=all_time_low,
            x1=df_history["Scraped At"].iloc[-1],
            y1=all_time_low,
            line=dict(color="#00ff87", width=1.5, dash="dash"),
        )

        fig.update_layout(
            paper_bgcolor="rgba(11, 15, 25, 0.6)",
            plot_bgcolor="rgba(18, 24, 38, 0.8)",
            font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
            margin=dict(l=20, r=20, t=30, b=30),
            height=320,
            xaxis=dict(
                title="Timestamp / Scrape Date",
                type="category",
                gridcolor="rgba(255, 255, 255, 0.06)",
                showline=True,
                linecolor="rgba(255,255,255,0.1)"
            ),
            yaxis=dict(
                title="Price in ₹",
                gridcolor="rgba(255, 255, 255, 0.06)",
                showline=True,
                linecolor="rgba(255,255,255,0.1)",
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
    """
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Student Budget Filters</div>
            <h2 class="section-h2">Find Deals in Your Budget</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
    f"""
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Curated Deals</div>
            <h2 class="section-h2">Student Deal Showcase ({len(filtered)} Products)</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

def render_student_card(name, url, price, mrp, discount):
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

    st.markdown(
        f"""
        <div class="student-card">
            <div class="card-badges">
                <span class="student-deal-badge">{discount}% OFF</span>
                <span class="trend-indicator {trend_class}">{trend_text}</span>
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
        """,
        unsafe_allow_html=True,
    )

if filtered:
    card_cols = st.columns(3)
    for idx, item in enumerate(filtered):
        p_name, p_url, p_price, p_mrp, p_discount, _ = item
        with card_cols[idx % 3]:
            render_student_card(p_name, p_url, p_price, p_mrp, p_discount)
else:
    st.info("No deals found matching your selected budget bracket or search query. Try choosing 'All Student Deals'!")

# ── Data Table View
st.markdown(
    """
    <div class="section-title-wrap">
        <div>
            <div class="section-kicker">Database View</div>
            <h2 class="section-title">Tracked Price Database</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered:
    table = pd.DataFrame(
        filtered,
        columns=["Name", "URL", "Price", "MRP", "Discount", "Updated"],
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
