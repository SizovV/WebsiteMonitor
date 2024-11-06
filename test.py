import difflib
from bs4 import BeautifulSoup
import requests
import hashlib
import time
from pyppeteer import launch
import asyncio

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}
async def fetch_content(url):
    """Fetches and parses the HTML content of a URL."""
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(url)
    await asyncio.sleep(0.6)  # Give time for JavaScript to load
    html_content = await page.content()
    await browser.close()
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    print(requests.head(url, timeout=5))
    return soup.get_text().strip()


#url = "https://huutokaupat.com/ilmoittaja/helsingin-kaupunki-kaupunkiympariston-toimiala-tontit-yksikko "
#print(hashlib.md5(url.encode()).hexdigest()[:8] )
async def main():
    url = "https://huutokaupat.com/ilmoittaja/cityvarasto-oy"
    url = "https://huutokaupat.com/ilmoittaja/rinta-joupin-autoliike-oy"
    url = "https://huutokaupat.com/ilmoittaja/bilar99e-oy"
    url = "https://huutokaupat.com/ilmoittaja/rawest"
    url = "https://huutokaupat.com/ilmoittaja/kone-keltto-oy"
    soup_1 = await fetch_content(url)
    print(soup_1)

asyncio.run(main())


# Check for changes
#additions, deletions = check_content_changes(old_content, new_content)

#print("Additions:", additions)
#print("Deletions:", deletions)


