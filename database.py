import sys
import sqlite3
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from alert_engine import AlertEngine

DB_PATH = "prices.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT,
                url        TEXT,
                price      INTEGER,
                mrp        INTEGER,
                discount   INTEGER,
                image      TEXT,
                scraped_at TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name  TEXT,
                product_url   TEXT,
                old_price     INTEGER,
                new_price     INTEGER,
                price_change  INTEGER,
                change_pct    REAL,
                alert_type    TEXT,
                image_url     TEXT,
                triggered_at  TEXT
            )
        """)
        con.commit()

init_db()

def save_products(products):
    """
    1. Triggers price change detection & alerts.
    2. Saves products into price_history table.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    alert_engine = AlertEngine(db_path=DB_PATH)
    alerts = alert_engine.process_price_changes(products)
    
    with get_connection() as con:
        for p in products:
            con.execute("""
                INSERT INTO price_history (name, url, price, mrp, discount, image, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (p["name"], p["url"], p["price"], p["mrp"], p["discount"], p["image"], now))
        con.commit()
    
    print(f"[DB] Saved {len(products)} products at {now}")
    return alerts

def get_recent_alerts(limit=20):
    """Fetches recent price drop & increase alerts."""
    with get_connection() as con:
        rows = con.execute("""
            SELECT id, product_name, product_url, old_price, new_price, price_change, change_pct, alert_type, image_url, triggered_at
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return rows

def get_price_history_for_product(url):
    """Fetches chronological price history points for a specific product URL."""
    with get_connection() as con:
        rows = con.execute("""
            SELECT price, mrp, discount, scraped_at
            FROM price_history
            WHERE url = ?
            ORDER BY id ASC
        """, (url,)).fetchall()
    return rows

def show_all():
    with get_connection() as con:
        rows = con.execute("""
            SELECT name, price, discount, scraped_at 
            FROM price_history 
            ORDER BY price ASC
        """).fetchall()
        print(f"\n[DB] {len(rows)} records in database:\n")
        for r in rows[:10]:
            print(f"  {r[0][:45]:<45} | ₹{r[1]:<6} | {r[2]}% off | {r[3]}")

if __name__ == "__main__":
    init_db()
    show_all()