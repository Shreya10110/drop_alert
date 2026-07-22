import os
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from proxy_manager import ProxyManager
from parse import parse_html
from database import save_products

DEFAULT_URL = "https://www.flipkart.com/audio-video/headset/earphones/pr?sid=0pm,fcn,821&p[]=facets.connectivity%255B%255D%3DBluetooth&p[]=facets.rating%255B%255D%3D3%25E2%2598%2585%2B%2526%2Babove&p[]=facets.price_range.from%3D699&p[]=facets.price_range.to%3DMax&otracker=categorytree"

def run_scraper(target_url=DEFAULT_URL, use_fallback_file=True):
    """
    Automated scraper pipeline:
    1. Fetches target web page using automated proxy rotation.
    2. Parses product names, prices, discounts, and images.
    3. Saves data into SQLite DB and automatically triggers price change alerts.
    """
    print(f"\n[Scraper] Starting automated product scrape at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    pm = ProxyManager()
    
    html = pm.fetch_page(target_url, max_retries=3)
    
    if html and len(html) > 5000:
        with open("flipkart.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[Scraper] Saved latest HTML response to flipkart.html")
    elif use_fallback_file and os.path.exists("flipkart.html"):
        print("[Scraper] Live fetch unsuccessful. Falling back to cached flipkart.html...")
        with open("flipkart.html", "r", encoding="utf-8") as f:
            html = f.read()
    else:
        print("[Scraper Error] Unable to retrieve page content.")
        return {"status": "error", "message": "Failed to fetch content", "products_count": 0, "alerts": []}

    products = parse_html(html)
    if not products:
        print("[Scraper Warning] 0 products parsed from HTML.")
        return {"status": "warning", "message": "No products parsed", "products_count": 0, "alerts": []}

    print(f"[Scraper] Successfully parsed {len(products)} products.")
    alerts = save_products(products)
    
    return {
        "status": "success",
        "products_count": len(products),
        "alerts_triggered": len(alerts) if alerts else 0,
        "alerts": alerts
    }

if __name__ == "__main__":
    result = run_scraper()
    print("\n[Scraper Finished]", result)
