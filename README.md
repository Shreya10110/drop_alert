# 🎧 DropAlert - Student Edition Price Drop & Tracker

**DropAlert** is a web scraping and price monitoring application designed for students to track electronics, headphones, and ear-buds on Flipkart. It features **Automated Proxy Rotation**, **Desktop System Notifications** for price drops & price hikes, and an interactive **CamelCamelCamel-style Price History Graph**.

---

## 🌟 Key Features

- **🔄 Automated Proxy Rotation (`proxy_manager.py`)**: Rotates proxies dynamically per request with fallback support.
- **🚨 Instant Price Drop & Hike Alerts (`alert_engine.py`)**: Detects price changes automatically and triggers OS desktop notifications.
- **📈 Interactive Price History Graph**: CamelCamelCamel-style Plotly line charts displaying historical price trends, All-Time Low records, and price analytics.
- **🎓 Student Budget Quick Filters**: Filter deals by budget brackets (`Under ₹999`, `Under ₹1,499`, `50%+ OFF`).
- **⚡ One-Click Scraper Control**: Manual scraper trigger directly from the Streamlit UI.

---

## 📁 Project Structure

```text
├── dashboard.py        # Streamlit Neo-Modern Glassmorphism UI
├── scraper.py          # End-to-end automated scraping controller
├── proxy_manager.py    # Automated proxy rotation & pool manager
├── alert_engine.py      # Price change detection & desktop notifications
├── database.py         # SQLite database schema & price history storage
├── parse.py            # HTML parser with canonical URL card matching
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the Repository & Install Dependencies

```bash
git clone https://github.com/<your-username>/drop-alert.git
cd drop-alert
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
python scraper.py
```

### 3. Launch the Dashboard

```bash
streamlit run dashboard.py
```

Open your browser at `http://localhost:8501`.

---

## 🛠️ Built With

- **Python 3.x**
- **Streamlit** (UI Dashboard)
- **BeautifulSoup4 & Requests** (Web Scraping)
- **Plotly** (Interactive Price History Graphs)
- **SQLite3** (Price History & Alerts Database)
- **Plyer** (Desktop Notifications)
