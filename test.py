import difflib
from bs4 import BeautifulSoup
import requests
import hashlib
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}
def fetch_content(url):
    """Fetches and parses the HTML content of a URL."""
    response = requests.get(url, headers=headers)
    time.sleep(3)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    print(requests.head(url, timeout=5))
    print(response.text)
    return soup.get_text().strip()

url = "https://huutokaupat.com/ilmoittaja/cityvarasto-oy"
url = "https://huutokaupat.com/ilmoittaja/rinta-joupin-autoliike-oy"
url = "https://huutokaupat.com/ilmoittaja/bilar99e-oy"
url = "https://huutokaupat.com/ilmoittaja/rawest"
url = "https://huutokaupat.com/ilmoittaja/kone-keltto-oy"
#url = "https://huutokaupat.com/ilmoittaja/helsingin-kaupunki-kaupunkiympariston-toimiala-tontit-yksikko "
#print(hashlib.md5(url.encode()).hexdigest()[:8] )
#print(fetch_content(url))



from requests_html import HTMLSession


session = HTMLSession()
response = session.get(url, headers=headers)
response.html.render(sleep=0.6)  # Renders the JavaScript
content = response.html.text  # Get the fully rendered HTML content

soup = BeautifulSoup(content, 'html.parser')

print(soup)


# Check for changes
#additions, deletions = check_content_changes(old_content, new_content)

#print("Additions:", additions)
#print("Deletions:", deletions)


