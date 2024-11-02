import os
import telebot
import Config
import requests
from bs4 import BeautifulSoup
import difflib
import sqlite3
import time
import schedule
from datetime import datetime
from threading import Thread


class WebsiteMonitor:
    def __init__(self, db_path='website_monitor.db'):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Initializes the database with a table for tracking websites."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS websites (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                url TEXT UNIQUE,
                                hash_id TEXT UNIQUE,
                                initial_content TEXT,
                                check_interval INTEGER,
                                user_id INTEGER,
                                last_checked TIMESTAMP
                            )''')

        print("dataset created")
        cursor.execute("SELECT * FROM websites")
        resa = cursor.fetchall()
        for j in resa:
            print(j)

        conn.commit()
        conn.close()

    def add_website(self, url, check_interval, user_id):
        import hashlib
        """Adds a new website with its initial content and check interval to the database."""
        if self.is_reachable(url):
            content = self.fetch_content(url)
            hash_id = hashlib.md5(url.encode()).hexdigest()[:8]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT OR IGNORE INTO websites (url, hash_id, initial_content, check_interval, user_id, last_checked)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (url, hash_id, content, check_interval, user_id, datetime.now()))
            conn.commit()
            conn.close()
            schedule.every(check_interval).seconds.do(self.check_website, url=url, user_id=user_id)
            return hash_id  # Return the hash_id to notify the user
        else:
            return None

    def is_reachable(self, url):
        """Checks if the URL is reachable."""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def fetch_content(self, url):
        """Fetches and parses the HTML content of a URL."""
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text().strip()

    def compare_content(self, new_content, initial_content):
        """Compares new content with the initial content and logs the differences."""
        return list(difflib.unified_diff(initial_content.splitlines(), new_content.splitlines(), lineterm=""))

    def check_website(self, url, user_id):
        """Checks a website for changes and notifies the user if changes are detected."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT initial_content FROM websites WHERE url = ?", (url,))
        row = cursor.fetchone()

        if row:
            initial_content = row[0]
            new_content = self.fetch_content(url)

            changes = self.compare_content(new_content, initial_content)

            additions = []

            # Parse the diff output
            for line in changes:
                if line.startswith('+') and not line.startswith('+++'):  # Exclude file header line with '+++'
                    additions.append(line[1:])

            if additions:
                # Send a notification to the user about the change
                bot.send_message(user_id,
                                 f"Website {url} has changed. Do you want to continue monitoring? Reply with /stop {url} to stop.")

                # Update the initial content after notifying the user
                cursor.execute("UPDATE websites SET initial_content = ?, last_checked = ? WHERE url = ?",
                               (new_content, datetime.now(), url))
            conn.commit()
        conn.close()

    def remove_website(self, url):
        """Removes a website from the database and stops monitoring."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM websites WHERE url = ?", (url,))
        conn.commit()
        conn.close()

    def run_scheduled_checks(self):
        """Runs scheduled checks in a separate thread."""
        while True:
            schedule.run_pending()
            time.sleep(1)

    def list_user_websites(self, user_id):
        """Retrieve a list of websites being monitored for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, check_interval, hash_id FROM websites WHERE user_id = ?", (user_id,))
        websites = cursor.fetchall()
        conn.close()
        return websites

    def remove_website_by_hash(self, hash_id):
        """Removes a website from the database using its hash_id and stops monitoring."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM websites WHERE hash_id = ?", (hash_id,))
        rows_deleted = cursor.rowcount  # Check if a row was deleted
        conn.commit()
        conn.close()
        return rows_deleted > 0


# apihelper.proxy = {'http': 'http://catalog.live.ovh:8080'}
API_KEY = os.getenv("API_KEY")  # Fetch API_KEY from environment variable
bot = telebot.TeleBot(API_KEY)
# id_admin = 275457031

monitor = WebsiteMonitor()


# Function to start monitoring
def start_monitoring():
    monitoring_thread = Thread(target=monitor.run_scheduled_checks)
    monitoring_thread.daemon = True
    monitoring_thread.start()


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "Welcome to the Website Monitor Bot! Use /add <url> <interval_in_seconds> to start monitoring a website.")
    # bot.send_message(message.chat.id, "Кстати, если найдешь баг или фичу срузу пиши @ghusty_dab")


@bot.message_handler(commands=['add'])
def add_website(message):
    """Add a website to be monitored."""
    try:
        parts = message.text.split()
        url = parts[1]
        interval = int(parts[2])
        user_id = message.chat.id
        hash_id = monitor.add_website(url, interval, user_id)

        if hash_id:
            bot.reply_to(message, f"Website {url} added with a check interval of {interval} seconds.\n"
                                  f"Use this ID to manage it: {hash_id}")
        else:
            bot.reply_to(message, f"Could not reach {url}. Please check the URL and try again.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /add <url> <interval_in_seconds>")


@bot.message_handler(commands=['stop'])
def stop_website(message):
    """Stop monitoring a website by its unique hash ID."""
    try:
        hash_id = message.text.split()[1]
        if monitor.remove_website_by_hash(hash_id):
            bot.reply_to(message, f"Monitoring for website with ID {hash_id} has been stopped.")
        else:
            bot.reply_to(message, f"No website found with ID {hash_id}.")
    except IndexError:
        bot.reply_to(message, "Usage: /stop <hash_id>")


@bot.message_handler(commands=['list'])
def list_websites(message):
    """List all currently monitored websites for the user, showing their hash ID."""
    user_id = message.chat.id
    websites = monitor.list_user_websites(user_id)

    if websites:
        response = "Your monitored websites:\n"
        for url, interval, hash_id in websites:
            response += f"- {url} (check every {interval} seconds), ID: {hash_id}\n"
    else:
        response = "You are not currently monitoring any websites."

    bot.reply_to(message, response)

# Start the bot and website monitoring
start_monitoring()
# Runing
bot.polling(none_stop=True, interval=1, timeout=30)
