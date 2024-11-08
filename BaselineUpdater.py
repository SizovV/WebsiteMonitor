import requests
import sqlite3
from bs4 import BeautifulSoup
from requests_html import HTMLSession

DATABASE_PATH = "website_monitor.db"  # Replace with the path to your database


def get_page_content(url):
    """Fetches and parses the HTML content of a URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    # 2 approach, instant download of web-page
    response = requests.get(url)
    response.raise_for_status()
    soup_2 = BeautifulSoup(response.text, 'html.parser')

    soup = soup_2.get_text().strip()
    return soup

def update_baseline_content():
    """Updates the baseline content for all monitored websites."""
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Retrieve all monitored websites
    cursor.execute("SELECT id, url FROM websites")
    websites = cursor.fetchall()

    for site_id, url in websites:
        try:
            content = get_page_content(url)

            # Update the baseline content and hash in the database for each website
            cursor.execute(
                "UPDATE websites SET initial_content = ? WHERE  id = ? and url = ?",
                (content, site_id, url)
            )

            print(f"Updated baseline for {url}")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Baseline update complete.")


# Run the baseline update
if __name__ == "__main__":
    update_baseline_content()
