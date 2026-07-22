from requests_html import HTMLSession
session = HTMLSession()
r = session.get('https://flipkart.com/')
print(r.html.links)