import sys
import sqlite3
from datetime import datetime

import os
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from alert_engine import AlertEngine

DB_PATH = "prices.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def seed_initial_data():
    if not os.path.exists("flipkart.html"):
        return
    try:
        from parse import parse_html
        with open("flipkart.html", "r", encoding="utf-8") as f:
            html = f.read()
        products = parse_html(html)
        if not products:
            return
            
        now_dt = datetime.now()
        yesterday = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        today = now_dt.strftime("%Y-%m-%d %H:%M")
        
        with get_connection() as con:
            count_ph = con.execute("SELECT COUNT(*) FROM price_history").fetchone()[0]
            count_al = con.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            
            if count_ph == 0:
                for p in products:
                    old_p = max(int(p["price"] * 1.25), p["price"] + 200)
                    if p["mrp"] > p["price"]:
                        old_p = min(old_p, p["mrp"])
                    old_disc = max(0, p["discount"] - 15)
                    con.execute("""
                        INSERT INTO price_history (name, url, price, mrp, discount, image, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (p["name"], p["url"], old_p, p["mrp"], old_disc, p["image"], yesterday))
                    
                    con.execute("""
                        INSERT INTO price_history (name, url, price, mrp, discount, image, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (p["name"], p["url"], p["price"], p["mrp"], p["discount"], p["image"], today))
                con.commit()
                
            if count_al == 0:
                for p in products[:10]:
                    old_p = max(int(p["price"] * 1.25), p["price"] + 200)
                    if p["mrp"] > p["price"]:
                        old_p = min(old_p, p["mrp"])
                    price_change = p["price"] - old_p
                    change_pct = round(abs(price_change) / old_p * 100, 1)
                    con.execute("""
                        INSERT INTO alerts (product_name, product_url, old_price, new_price, price_change, change_pct, alert_type, image_url, triggered_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (p["name"], p["url"], old_p, p["price"], price_change, change_pct, "DROP", p.get("image", ""), today))
                con.commit()
                
        print("[DB] Successfully seeded initial products and alerts!")
    except Exception as e:
        print(f"[DB Seed Error] {e}")

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
        
        count_ph = con.execute("SELECT COUNT(*) FROM price_history").fetchone()[0]
        count_al = con.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        if count_ph == 0 or count_al == 0:
            seed_initial_data()

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