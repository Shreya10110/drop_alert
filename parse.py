import re
import json
import sys
from bs4 import BeautifulSoup

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def extract_card_details(card):
    """Extracts selling price, MRP, discount %, and image URL cleanly from a product card element."""
    # Find price tags
    price_tags = card.find_all(lambda tag: tag.name in ["div", "span"] and "₹" in tag.text and len(tag.text.strip()) < 30)
    prices = []
    for pt in price_tags:
        found = re.findall(r'₹([\d,]+)', pt.text)
        for f in found:
            val = int(f.replace(",", ""))
            if val > 0 and val not in prices:
                prices.append(val)
    
    if not prices:
        raw = re.findall(r'₹([\d,]+)', card.get_text())
        prices = [int(p.replace(",", "")) for p in raw]

    price = prices[0] if prices else 0
    mrp = prices[1] if len(prices) > 1 else price

    disc_match = re.search(r'(\d{1,2})%\s*off', card.get_text(), re.I)
    discount = int(disc_match.group(1)) if disc_match else 0

    # Repair MRP if concatenated with discount digits
    if discount > 0 and mrp > price * 4:
        mrp_str = str(mrp)
        disc_str = str(discount)
        if mrp_str.endswith(disc_str):
            cand = mrp_str[:-len(disc_str)]
            if cand.isdigit() and int(cand) >= price:
                mrp = int(cand)

    img = card.find("img")
    img_url = img["src"] if img and img.has_attr("src") else ""

    return price, mrp, discount, img_url

def parse_html(html):
    """Parses product details accurately using URL canonical path matching to avoid index offsets."""
    soup = BeautifulSoup(html, "html.parser")
    jsonld = soup.find("script", type="application/ld+json")
    items = []

    if jsonld:
        try:
            parsed_data = json.loads(jsonld.get_text())
            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                items = parsed_data[0].get("itemListElement", [])
        except Exception as e:
            print(f"[Parse Notice] JSON-LD error: {e}")

    products = []
    seen_urls = set()

    if items:
        for item in items:
            name = item.get("name", "")
            full_url = item.get("url", "")
            if not full_url or full_url in seen_urls:
                continue

            path_snippet = full_url.split("flipkart.com")[-1].split("?")[0]
            
            # Find the exact link tag in HTML
            link = soup.find("a", href=lambda h: h and path_snippet in h)
            if link:
                # Find the surrounding product card container
                card = link.find_parent(lambda tag: tag.name == "div" and ("₹" in tag.get_text()) and len(tag.get_text()) < 1200)
                if card:
                    price, mrp, discount, img_url = extract_card_details(card)
                    if price > 0:
                        products.append({
                            "name": name,
                            "url": full_url,
                            "price": price,
                            "mrp": mrp,
                            "discount": discount,
                            "image": img_url
                        })
                        seen_urls.add(full_url)
    
    # Fallback if no JSON-LD items matched
    if not products:
        cards = soup.find_all("div", {"data-id": True}) or soup.find_all(lambda tag: tag.name == "div" and ("₹" in tag.get_text()) and len(tag.get_text()) < 800)
        for card in cards:
            link = card.find("a", href=True)
            if not link:
                continue
            url = link["href"] if link["href"].startswith("http") else "https://www.flipkart.com" + link["href"]
            if url in seen_urls:
                continue

            price, mrp, discount, img_url = extract_card_details(card)
            name = card.get_text()[:60].strip()

            if price > 0:
                products.append({
                    "name": name,
                    "url": url,
                    "price": price,
                    "mrp": mrp,
                    "discount": discount,
                    "image": img_url
                })
                seen_urls.add(url)

    return products

if __name__ == "__main__":
    try:
        with open("flipkart.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        parsed = parse_html(html_content)
        print(f"[Parse] Successfully parsed {len(parsed)} products from flipkart.html:")
        for p in parsed[:10]:
            print(f"  {p['name'][:42]:<42} | Price: ₹{p['price']:<5} | MRP: ₹{p['mrp']:<5} | {p['discount']}% off")
    except Exception as err:
        print(f"[Parse Error] {err}")