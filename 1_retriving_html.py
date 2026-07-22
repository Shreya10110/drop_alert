import requests
import time
from fake_useragent import UserAgent
url="https://www.flipkart.com/audio-video/headset/earphones/pr?sid=0pm,fcn,821&p[]=facets.connectivity%255B%255D%3DBluetooth&p[]=facets.rating%255B%255D%3D3%25E2%2598%2585%2B%2526%2Babove&p[]=facets.price_range.from%3D699&p[]=facets.price_range.to%3DMax&otracker=categorytreeua = UserAgent()"
session = requests.Session()
headers={
    "User-Agent":UserAgent().random,
    "Accept-Language":"en-US,en;q=0.9,mr;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/", 
}
proxy_auth ='35277792966eba78ea2b:232bae6b020dcb6a@gw.dataimpulse.com:823'
proxies = {
    "http": f"http://{proxy_auth}",
    "https": f"https://{proxy_auth}"
}
time.sleep(2)
r = session.get(url,proxies=proxies,headers=headers)
print(r.text)
with open("flipkart.html", "w", encoding="utf-8") as f:
    f.write(r.text)