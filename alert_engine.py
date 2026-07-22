import os
import sys
import sqlite3
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

class AlertEngine:
    """
    Alert Engine:
    - Analyzes price changes (drops and increases) when products are scraped.
    - Saves alerts into SQLite database 'alerts' table.
    - Triggers desktop notifications & Telegram alerts.
    """

    def __init__(self, db_path="prices.db", telegram_token=None, telegram_chat_id=None):
        self.db_path = db_path
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self._init_alert_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_alert_table(self):
        with self._get_connection() as con:
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

    def send_desktop_notification(self, title, message):
        """Triggers OS-level desktop notification."""
        try:
            if HAS_PLYER:
                notification.notify(
                    title=title,
                    message=message[:250],
                    app_name="DropAlert",
                    timeout=7
                )
                print(f"[AlertEngine] Desktop Notification sent: {title}")
            else:
                ps_script = f"""
                [reflection.assembly]::loadwithpartialname('System.Windows.Forms')
                $notify = new-object system.windows.forms.notifyicon
                $notify.icon = [system.drawing.systemicons]::information
                $notify.visible = $true
                $notify.showballoontip(5000, '{title}', '{message.replace("'", "")}', [system.windows.forms.tooltipicon]::info)
                """
                os.system(f'powershell -Command "{ps_script}"')
                print(f"[AlertEngine] PowerShell Notification sent: {title}")
        except Exception as e:
            print(f"[AlertEngine] Desktop notification notice: {e}")

    def send_telegram_notification(self, text):
        """Sends notification to Telegram Bot if credentials exist."""
        if not self.telegram_token or not self.telegram_chat_id:
            return
        import requests
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            requests.post(url, json={"chat_id": self.telegram_chat_id, "text": text, "parse_mode": "Markdown"}, timeout=5)
            print("[AlertEngine] Telegram alert sent!")
        except Exception as e:
            print(f"[AlertEngine] Telegram alert failed: {e}")

    def process_price_changes(self, products):
        """
        Compares incoming scraped products against DB to find price drops/increases.
        Returns list of newly generated alerts.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_alerts = []

        with self._get_connection() as con:
            for p in products:
                url = p["url"]
                new_price = p["price"]
                name = p["name"]

                if not new_price or new_price <= 0:
                    continue

                row = con.execute("""
                    SELECT price FROM price_history 
                    WHERE url = ? 
                    ORDER BY scraped_at DESC 
                    LIMIT 1
                """, (url,)).fetchone()

                if row and row[0] is not None:
                    old_price = row[0]
                    if old_price != new_price:
                        price_change = new_price - old_price
                        change_pct = round(abs(price_change) / old_price * 100, 1)

                        if new_price < old_price:
                            alert_type = "DROP"
                            title = "PRICE DROP ALERT!"
                            msg = f"'{name[:50]}' price dropped by ₹{abs(price_change):,} ({change_pct}% OFF)!\nOld: ₹{old_price:,} -> New: ₹{new_price:,}"
                        else:
                            alert_type = "INCREASE"
                            title = "PRICE INCREASE ALERT"
                            msg = f"'{name[:50]}' price increased by ₹{price_change:,}!\nOld: ₹{old_price:,} -> New: ₹{new_price:,}"

                        con.execute("""
                            INSERT INTO alerts (product_name, product_url, old_price, new_price, price_change, change_pct, alert_type, image_url, triggered_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (name, url, old_price, new_price, price_change, change_pct, alert_type, p.get("image", ""), now))
                        
                        alert_item = {
                            "product_name": name,
                            "url": url,
                            "old_price": old_price,
                            "new_price": new_price,
                            "change": price_change,
                            "change_pct": change_pct,
                            "alert_type": alert_type,
                            "triggered_at": now
                        }
                        new_alerts.append(alert_item)

                        self.send_desktop_notification(title, msg)
                        self.send_telegram_notification(f"*{title}*\n{msg}")

            con.commit()

        if new_alerts:
            print(f"[AlertEngine] Processed & logged {len(new_alerts)} price alerts!")
        else:
            print("[AlertEngine] No price changes detected in this scrape.")

        return new_alerts

if __name__ == "__main__":
    engine = AlertEngine()
    print("Alert Engine initialized successfully!")
