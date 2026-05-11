# Telegram Gmail Notifier Bot

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: python-telegram-bot](https://img.shields.io/badge/Framework-python--telegram--bot-green.svg)](https://python-telegram-bot.org/)

A professional, high-security Python-based Telegram bot that monitors your Gmail inbox and delivers instant notifications only for emails from a curated whitelist of senders. 

Unlike other bots, this project is built with **security-first principles**, ensuring your email content remains private and your inbox stays untouched.

## ✨ Key Features

* **Selective Alerts:** Get notified only for what matters. Add or remove senders in real-time via Telegram commands.
* **Zero-Impact Security:** Operates on a **Read-Only** Gmail scope. The bot cannot delete, send, or mark emails as read.
* **Idempotent Notifications:** Uses a local persistence layer to track processed Email IDs, preventing duplicate alerts even after server restarts.
* **Dual-Layer Persistence:** Manages your whitelist (`config.json`) and processed history (`processed.json`) independently.
* **Cloud Optimized:** Specifically designed to run within the GCP Free Tier (`e2-micro`) using `APScheduler`.

## 🏗️ Clean Architecture

The project follows SOLID principles to separate concerns, making it easy to test and extend:

* `main.py`: The **Composition Root**. Orchestrates dependency injection and initializes the bot.
* `gmail_service.py`: Encapsulates the **Google OAuth2 flow** and Gmail API interactions.
* `bot_handlers.py`: Acts as the **Controller** layer, handling user commands and Telegram interactions.
* `storage.py`: The **Data Access Object (DAO)**. Manages JSON persistence with error handling.
* `config.py`: Centralized **Configuration** using environment variables for sensitive data.
* `logger.py`: Standardized logging for production monitoring and debugging.

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher.
* A Google Cloud Project with the **Gmail API** enabled.
* A Telegram Bot token (from [@BotFather](https://t.me/botfather)).

### Installation
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/aljanue/gmail-filter-bot.git](https://github.com/aljanue/gmail-filter-bot.git)
    cd gmail-filter-bot
    ```

2.  **Set up the environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Credentials:**
    * Place your `credentials.json` (from Google Cloud Console) in the root directory.
    * Create a `.env` file:
    ```env
    TELEGRAM_TOKEN=your_bot_token_here
    SECURE_USER_ID=your_telegram_user_id
    CHECK_INTERVAL=120
    ```

4.  **Initial Run:**
    ```bash
    python3 main.py
    ```
    *A browser window will open for the initial OAuth2 authorization. After this, a `token.json` will be generated for headless operation.*

## 🛠️ Bot Commands

* `/add <email>`: Add a new sender to the priority notification list.
* `/remove <email>`: Stop receiving notifications for a specific sender.
* `/list`: Show all currently monitored senders.
* `/help`: View available commands.

## ☁️ Deployment (GCP)

This bot is designed to run as a `systemd` service on a Debian/Ubuntu Linux server:

1.  Upload the project to your VM.
2.  Configure a service file at `/etc/systemd/system/gmailbot.service`.
3.  Enable and start the service:
    ```bash
    sudo systemctl enable gmailbot && sudo systemctl start gmailbot
    ```

## 🔒 Security Disclaimer
This application uses the `https://www.googleapis.com/auth/gmail.readonly` scope. It can only see your messages and settings; it **cannot** send emails, delete them, or change your password. Your `token.json` and `.env` contain sensitive access keys—**never commit them to version control.**

---
*Developed with ❤️ for privacy and productivity.*