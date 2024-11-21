# Website Monitoring Bot 🕵️‍♂️🌐

A powerful and flexible Telegram bot designed to monitor websites for changes, notify users of updates, and provide comprehensive management tools. This bot leverages Python's asynchronous capabilities, SQLite, and Telegram's Bot API to deliver a seamless monitoring experience.

## Features 🚀

### Website Monitoring
- **Add Websites**: Monitor any website by providing its URL and the interval (in hours) for checks.
- **Real-time Change Detection**: Compares the current content of a website with its initial state and detects changes, line by line.
- **Notifications**: Sends notifications to users when changes are detected, with the option to stop monitoring.

### User Management
- **User-specific Monitoring**: Each user can monitor their own set of websites without interference from others.
- **Custom Intervals**: Specify the frequency of checks for each website in hours.

### Admin Tools
- **Statistics Command**: Admins can view:
  - Total users actively monitoring websites.
  - Total websites being monitored across all users.
- **Bot Control**: Fully manage the bot's features and monitored websites from Telegram commands.

### Website Content Processing
- **Header Skipping**: Automatically skips headers and irrelevant metadata while comparing website content.
- **Content Cleaning**: Removes special characters like `\xad` and filters out cookie-related banners or scripts before processing.

### Database Integration
- **SQLite Persistence**: All website and user data is securely stored in an SQLite database for persistence and reliability.
- **Hash-based Identification**: Each monitored website is assigned a unique hash ID for easy identification and management.

### Advanced Scheduling
- **Threaded Scheduling**: Uses `schedule` and multithreading for efficient periodic checks.
- **Dynamic Management**: Automatically adds and removes monitoring tasks based on user commands.

### Performance Optimizations
- **Async Execution**: Combines `asyncio` with `pyTelegramBotAPI` to ensure smooth performance, even under heavy loads.
- **Scalability**: Supports up to 1000 monitored websites with minimal resource usage.

### Command List 📝
- `/start` – Start the bot and get usage instructions.
- `/add <url> <interval_in_hours>` – Add a website to monitor.
- `/stop <hash_id>` – Stop monitoring a website using its unique hash ID.
- `/list` – List all websites you're monitoring along with their intervals and IDs.
- `/stat` – Admin-only command to view user and website statistics.

### Example Use Case
1. Add a website to monitor:  
   `/add https://example.com 6`  
   *(Monitor `https://example.com` every 6 hours).*

2. Stop monitoring:  
   `/stop abc12345`
   *(Stop monitoring the website with hash ID `abc12345`).*
   **OR**
   `/stop https://example.com`

4. View all monitored websites:  
   `/list`

5. Admin retrieves bot statistics:  
   `/stat`

## Technologies Used 🛠️
- **Languages**: Python
- **Libraries**: `telebot`, `sqlite3`, `beautifulsoup4`, `schedule`, `asyncio`, `difflib`
- **Database**: SQLite
- **Web Scraping**: BeautifulSoup and subprocess-based page fetching.

---

This bot is perfect for anyone who needs to monitor website content for updates or changes, whether it's for research, competitive analysis, or personal projects.

## Contributions 🤝
Feel free to fork the repository and contribute by submitting pull requests. Suggestions and bug reports are also welcome!
