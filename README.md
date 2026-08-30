# 🤖 Loglan Dictionary Telegram Bot & Web Service

[![CI](https://github.com/torrua/loglan_bot/actions/workflows/ci.yml/badge.svg)](https://github.com/torrua/loglan_bot/actions/workflows/ci.yml)
[![GitHub license](https://img.shields.io/github/license/torrua/loglan_bot)](https://github.com/torrua/loglan_bot/blob/master/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

Async service providing a **Telegram Bot** ([@LoglanBot](http://t.me/LoglanBot)) and **Web Dictionary** for the Loglan constructed language.

Built with **Python 3.12+**, **Quart**, **Hypercorn**, **SQLAlchemy 2.0 (AsyncIO)**, **Loglan-Core**, and **pyTelegramBotAPI**.

---

## 🚀 Features

- **Telegram Bot**:
  - Direct translation of Loglan words to English and vice-versa.
  - Commands `/log` (search by Loglan word) and `/gle` (search by English key).
  - Interactive inline keyboards for navigating word parents, complexes, and affixes (djifoa).
  - Secure webhook handler with secret token validation.
- **Loglan-Online Web Interface**:
  - Interactive dictionary search with case-sensitivity and edition/event filters.
  - Proxy reader for Loglan texts, articles, and columns with automated caching.
  - Clean HTML exports and responsive Bootstrap layout.

---

## 🛠️ Quick Start

### 1. Requirements
- Python 3.11+ (recommended: 3.12)
- PostgreSQL (e.g. Neon.tech) with Loglan LOD database schema.

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure your settings:
```bash
cp .env.example .env
```

Key environment variables:
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from @BotFather.
- `TELEGRAM_ADMIN_ID`: Admin user ID for notifications.
- `LOD_DATABASE_URL`: Async PostgreSQL URL (e.g. `postgresql+asyncpg://user:pass@host/dbname`).
- `WEBHOOK_SECRET`: Secret token for webhook verification.

### 3. Installation
```bash
pip install -r requirements-dev.txt
```

### 4. Running the Web App & Webhook Server
```bash
hypercorn -b 0.0.0.0:8080 main:app
```

### 5. Running Bot Locally in Polling Mode (for development)
```bash
python -m app.bot.local_run
```

---

## 🧪 Testing & Code Quality

Run tests:
```bash
pytest tests/ -v
```

Check types:
```bash
mypy app tests
```

Check code style and linting:
```bash
ruff check .
ruff format --check .
```

---

## 🐳 Docker Deployment

Build and run container:
```bash
docker build -t loglan-bot .
docker run -p 8080:8080 --env-file .env loglan-bot
```