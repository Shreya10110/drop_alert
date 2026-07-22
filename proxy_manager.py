import sys
import random
import time
import requests
from fake_useragent import UserAgent

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class ProxyManager:
    """
    Automated Proxy Manager:
    - Auto-fetches and tests free proxies from public sources.
    - Supports dynamic rotating session proxy (e.g. DataImpulse).
    - Auto-rotates proxy on failed requests or blocks.
    """

    def __init__(self, static_auth="35277792966eba78ea2b:232bae6b020dcb6a@gw.dataimpulse.com:823"):
        self.static_auth = static_auth
        self.ua = UserAgent()
        self.proxy_pool = []
        self.current_index = 0

    def get_dynamic_session_proxy(self):
        """Generates a dynamic rotating session proxy URL for DataImpulse/similar services."""
        if not self.static_auth:
            return None
        user_pass, host_port = self.static_auth.split("@")
        user, password = user_pass.split(":")
        session_id = f"session-{random.randint(10000, 99999)}"
        proxy_url = f"http://{user}_session_{session_id}:{password}@{host_port}"
        return {"http": proxy_url, "https": proxy_url}

    def fetch_free_proxies(self):
        """Fetches fresh public HTTP proxies if paid proxy is not available or as fallback."""
        sources = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        ]
        proxies = []
        for src in sources:
            try:
                res = requests.get(src, timeout=5)
                if res.status_code == 200:
                    lines = [line.strip() for line in res.text.splitlines() if line.strip() and ":" in line]
                    proxies.extend(lines[:30])
                    if len(proxies) >= 50:
                        break
            except Exception:
                continue
        random.shuffle(proxies)
        self.proxy_pool = proxies
        print(f"[ProxyManager] Fetched {len(self.proxy_pool)} free proxies into rotation pool.")

    def get_next_proxy(self):
        """Returns next proxy dictionary from proxy pool or dynamic proxy."""
        if self.static_auth:
            return self.get_dynamic_session_proxy()
        
        if not self.proxy_pool:
            self.fetch_free_proxies()
        
        if not self.proxy_pool:
            return None
        
        proxy_str = self.proxy_pool[self.current_index % len(self.proxy_pool)]
        self.current_index += 1
        return {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}"
        }

    def fetch_page(self, url, max_retries=5, delay=2):
        """
        Fetches URL with automatic proxy rotation, user-agent randomization, and retries.
        """
        for attempt in range(1, max_retries + 1):
            proxy = self.get_next_proxy()
            headers = {
                "User-Agent": self.ua.random,
                "Accept-Language": "en-US,en;q=0.9,mr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://www.google.com/",
            }

            try:
                print(f"[ProxyManager] Attempt {attempt}/{max_retries}: Scraping page via proxy...")
                session = requests.Session()
                response = session.get(url, headers=headers, proxies=proxy, timeout=12)
                
                if response.status_code == 200 and len(response.text) > 5000:
                    print("[ProxyManager] Successfully fetched page HTML!")
                    return response.text
                else:
                    print(f"[ProxyManager] Response invalid (Status {response.status_code}, length {len(response.text)}). Rotating proxy...")
            except Exception as e:
                print(f"[ProxyManager] Request failed: {e}. Rotating proxy...")
            
            time.sleep(delay)
        
        print("[ProxyManager] All proxy attempts failed. Attempting direct request fallback...")
        try:
            headers = {"User-Agent": self.ua.random}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.text
        except Exception as err:
            print(f"[ProxyManager] Direct request fallback failed: {err}")
            
        return None

if __name__ == "__main__":
    pm = ProxyManager()
    test_url = "https://httpbin.org/ip"
    print("Testing Proxy Manager...")
    html = pm.fetch_page(test_url, max_retries=2)
    if html:
        print("Result snippet:", html[:200])
