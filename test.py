import difflib
from bs4 import BeautifulSoup
import requests
import hashlib
import time
import sqlite3
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

db_path = 'website_monitor.db'
url = 'https://huutokaupat.com/ilmoittaja/cityvarasto-oy?jarjestys=paattyvat&sivu=1'
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT last_checked, url, initial_content FROM websites")
    resa = cursor.fetchall()
    for last_checked, url, initial_content in resa:
        print(last_checked, url)
    initial_content = resa[2][2]

import unicodedata

def remove_control_characters(s):
    return ''.join(c for c in s if unicodedata.category(c)[0] != 'C')
def split_into_chunks_and_write_to_file(text, file_path, chunk_size=30):
    with open(file_path, 'w') as file:
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            file.write(chunk + '\n')  # Write each chunk on a new line

# Example usage
initial_content = remove_control_characters(initial_content)
file_path = "test1.txt"
split_into_chunks_and_write_to_file(initial_content, file_path)



import subprocess
output = subprocess.run(['python3', 'fetch_page.py', url], capture_output=True, text=True)
new_content = BeautifulSoup(output.stdout, 'html.parser').get_text().strip()
print(new_content)


new_content = remove_control_characters(new_content)
file_path = "test2.txt"
split_into_chunks_and_write_to_file(new_content, file_path)


changes = list(difflib.unified_diff(initial_content.splitlines(), new_content.splitlines(), lineterm=""))
print(changes)

#compare_content(new_content, initial_content)

# Check for changes
#additions, deletions = check_content_changes(old_content, new_content)

#print("Additions:", additions)
#print("Deletions:", deletions)


