from telebot import TeleBot

import Config
import requests
from bs4 import BeautifulSoup
import difflib
import sqlite3
import time
import schedule
from datetime import datetime
from threading import Thread
import asyncio
from telebot.async_telebot import AsyncTeleBot
import subprocess
import hashlib

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


def compare_content(new_content, initial_content):
    """Compares new content with the initial content and logs the differences."""
    return list(difflib.unified_diff(initial_content.splitlines(), new_content.splitlines(), lineterm=""))


class WebsiteMonitor:
    def __init__(self, db_path='website_monitor.db'):
        self.db_path = db_path
        self.jobs = {}  # Store scheduled jobs here by hash_id
        self.initialize_database()

    # Function to start monitoring
    async def start_monitoring(self):
        monitoring_thread = Thread(target=self.run_scheduled_checks)
        monitoring_thread.daemon = True
        monitoring_thread.start()

    def initialize_database(self):
        """Initializes the database with a table for tracking websites."""

        asyncio.run(self.start_monitoring())

        def wrapper(url, user_id):
            asyncio.run(self.check_website(url, user_id))

        with sqlite3.connect(self.db_path) as conn:
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

            cursor.execute("SELECT url, check_interval, user_id FROM websites")
            resa = cursor.fetchall()
            for url, check_interval, user_id in resa:
                print(url, check_interval, user_id)
                # schedule.every(check_interval).seconds.do(self.check_website, url=url, user_id=user_id)
                job = schedule.every(check_interval).seconds.do(wrapper, url=url, user_id=user_id)
                hash_id = hashlib.md5(url.encode()).hexdigest()[:8]
                self.jobs[hash_id] = job  # Save the job to remove later

            conn.commit()

    def add_website(self, url, interval, user_id):
        """Adds a new website with its initial content and check interval to the database."""
        if self.is_reachable(url):
            output = subprocess.run(['python3', 'fetch_page.py', url], capture_output=True, text=True)
            content = BeautifulSoup(output.stdout, 'html.parser').get_text().strip()

            hash_id = hashlib.md5(url.encode()).hexdigest()[:8]

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                check_interval = interval * 60  # Convert hours into seconds
                cursor.execute('''INSERT OR IGNORE INTO websites (url, hash_id, initial_content, check_interval, user_id, last_checked)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                               (url, hash_id, content, check_interval, user_id, datetime.now()))
                conn.commit()

            def wrapper():
                asyncio.run(self.check_website(url, user_id))

            # Schedule the wrapper function
            job = schedule.every(check_interval).seconds.do(wrapper)
            self.jobs[hash_id] = job  # Save the job to remove later
            return hash_id  # Return the hash_id to notify the user
        else:
            return None

    @staticmethod
    def is_reachable(url):
        """Checks if the URL is reachable."""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    async def check_website(self, url, user_id):
        """Checks a website for changes and notifies the user if changes are detected."""

        additions = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT initial_content FROM websites WHERE url = ? and user_id = ?", (url, user_id))
            row = cursor.fetchone()

            if row:
                initial_content = row[0]
                output = subprocess.run(['python3', 'fetch_page.py', url], capture_output=True, text=True)
                new_content = BeautifulSoup(output.stdout, 'html.parser').get_text().strip()
                changes = compare_content(new_content, initial_content)

                # Parse the diff output
                for line in changes:
                    if line.startswith('+') and not line.startswith('+++'):  # Exclude file header line with '+++'
                        additions.append(line[1:])

                if len(additions):
                    # Update the initial content after notifying the user
                    cursor.execute(
                        "UPDATE websites SET initial_content = ?, last_checked = ? WHERE url = ? and user_id = ?",
                        (new_content, datetime.now(), url, user_id))

                    bot.send_message(user_id, f"Website {url} has changed. Do you want to continue monitoring? Reply "
                                              f"with /stop {url} to stop.")

                conn.commit()

    def remove_website(self, url, user_id):
        """Removes a website from the database and stops monitoring."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM websites WHERE url = ? and user_id = ?", (url, user_id))
            rows_deleted = cursor.rowcount  # Check if a row was deleted
            conn.commit()

        hash_id = hashlib.md5(url.encode()).hexdigest()[:8]
        # Unschedule the job if it exists
        if hash_id in self.jobs:
            schedule.cancel_job(self.jobs[hash_id])
            del self.jobs[hash_id]  # Remove job reference
        return rows_deleted > 0

    def run_scheduled_checks(self):
        """Runs scheduled checks in a separate thread."""
        while True:
            schedule.run_pending()
            time.sleep(1)

    def list_user_websites(self, user_id):
        """Retrieve a list of websites being monitored for a specific user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url, check_interval, hash_id FROM websites WHERE user_id = ?", (user_id,))
            websites = cursor.fetchall()

        return websites

    def remove_website_by_hash(self, hash_id, user_id):
        """Removes a website from the database using its hash_id and stops monitoring."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM websites WHERE hash_id = ? and user_id = ?", (hash_id, user_id))
            rows_deleted = cursor.rowcount  # Check if a row was deleted
            conn.commit()

        # Unschedule the job if it exists
        if hash_id in self.jobs:
            schedule.cancel_job(self.jobs[hash_id])
            del self.jobs[hash_id]  # Remove job reference

        return rows_deleted > 0


# apihelper.proxy = {'http': 'http://catalog.live.ovh:8080'}
# API_KEY = os.getenv("API_KEY")  # Fetch API_KEY from environment variable
API_KEY = Config.TOKEN

bot = TeleBot(API_KEY)

ADMIN_ID = 275457031


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "Welcome to the Website Monitor Bot! Use /add <url> <interval_in_hours> to start monitoring a website.")
    # bot.send_message(message.chat.id, "Кстати, если найдешь баг или фичу срузу пиши @ghusty_dab")


@bot.message_handler(commands=['add'])
def add_website_orig(message):
    """Add a website to be monitored."""
    try:
        parts = message.text.split()
        url = parts[1]
        interval = int(parts[2])
        user_id = message.chat.id

        hash_id = monitor.add_website(url, interval, user_id)

        if hash_id:
            bot.reply_to(message, f"Website {url} added with a check interval of {interval} hours.\n"
                                  f"Use this ID to manage it: {hash_id}")
        else:
            bot.reply_to(message, f"Could not reach {url}. Please check the URL and try again.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /add <url> <interval_in_hours>")


@bot.message_handler(commands=['stop'])
def stop_website(message):
    """Stop monitoring a website by its unique hash ID."""
    try:
        hash_id = message.text.split()[1]
        url = message.text.split()[1]
        if monitor.remove_website_by_hash(hash_id, message.chat.id):
            bot.reply_to(message, f"Monitoring for website with ID {hash_id} has been stopped.")
        elif monitor.remove_website(url, message.chat.id):
            bot.reply_to(message, f"Monitoring for website with url {url} has been stopped.")
        else:
            bot.reply_to(message, f"No website found with {url}.")
    except IndexError:
        bot.reply_to(message, "Usage: /stop <hash_id> or <url>")


@bot.message_handler(commands=['list'])
def list_websites(message):
    """List all currently monitored websites for the user, showing their hash ID."""
    user_id = message.chat.id
    websites = monitor.list_user_websites(user_id)

    if websites:
        response = "Your monitored websites:\n"
        for url, interval, hash_id in websites:
            response += f"- {url} (check every {interval / (60 * 60)} hours), ID: {hash_id}\n"
    else:
        response = "You are not currently monitoring any websites."
    bot.reply_to(message, response)


@bot.message_handler(commands=['stat'])
def send_statistics(message):
    try:
        if message.from_user.id == ADMIN_ID:
            # Connect to the database
            DATABASE_PATH = "website_monitor.db"
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()

                # Get total subjects
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM websites")
                total_subjects = cursor.fetchone()[0]

                # Get number of tracking sites
                cursor.execute("SELECT COUNT(DISTINCT id) FROM websites")
                tracking_sites = cursor.fetchone()[0]

            # Format the statistics message
            stats_message = (
                f"📊 **Statistics**\n"
                f"Total Subjects: {total_subjects}\n"
                f"Tracking Sites: {tracking_sites}"
            )
            bot.send_message(ADMIN_ID, stats_message)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"An error occurred while fetching statistics: {e}")


# Start website monitoring
monitor = WebsiteMonitor()


def main():
    # Start the bot
    bot.polling(none_stop=True, interval=1, timeout=30)

# Run the bot
asyncio.run(main())
