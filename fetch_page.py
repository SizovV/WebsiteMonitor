# fetch_page.py
import asyncio
from pyppeteer import launch
import sys
import json

async def fetch_page_content(url):
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(url)
    await asyncio.sleep(0.6)
    html_content = await page.content()
    await browser.close()
    return html_content

async def main(url):
    html_content = await fetch_page_content(url)
    print(html_content)

if __name__ == "__main__":
    url = sys.argv[1]
    asyncio.run(main(url))
