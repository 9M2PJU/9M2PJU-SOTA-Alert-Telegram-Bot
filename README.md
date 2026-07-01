# 9M2PJU SOTA Bot

Telegram bot for SOTA chasers and activators. It watches SOTAwatch spots and alerts, then sends matching updates to subscribed Telegram users.

## Features

- Latest SOTA spots from `https://api2.sota.org.uk/api/spots/-1/all`
- Upcoming SOTA alerts from `https://api2.sota.org.uk/api/alerts`
- Per-user subscriptions in SQLite
- Filters by association, callsign, and mode
- Commands for quick lookup and subscription management
- Polling worker with deduplication so users do not receive repeated posts

## Telegram Bot Setup

1. Open Telegram and message `@BotFather`.
2. Create a bot named `9M2PJU SOTA Bot`.
3. Choose a username ending in `bot`, for example `9M2PJU_SOTA_Bot`.
4. Copy the token from BotFather.

## Local Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
export TELEGRAM_BOT_TOKEN="123456:your-token"
sota-telegram-bot
```

Optional settings:

```bash
export SOTA_DB_PATH="./data/bot.sqlite3"
export SOTA_SPOTS_POLL_SECONDS="45"
export SOTA_ALERTS_POLL_SECONDS="300"
```

## Commands

- `/start` - subscribe and show help
- `/help` - show commands
- `/subscribe` - enable notifications
- `/unsubscribe` - disable notifications
- `/spots` - show latest matching spots
- `/alerts` - show upcoming matching alerts
- `/filter` - show active filters
- `/filter association 9M`
- `/filter callsign 9M2PJU`
- `/filter mode CW`
- `/clearfilters` - remove all filters

Filters are matched case-insensitively. Association filters match SOTA association prefixes such as `9M`, `W4C`, `JA`, or `VK3`. Callsign filters match activator and poster/spotter callsigns.

## systemd Example

Create `/etc/systemd/system/9m2pju-sota-bot.service`:

```ini
[Unit]
Description=9M2PJU SOTA Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/opt/9M2PJU-SOTA-Alert-Telegram-Bot
Environment=TELEGRAM_BOT_TOKEN=replace-me
Environment=SOTA_DB_PATH=/var/lib/9m2pju-sota-bot/bot.sqlite3
ExecStart=/opt/9M2PJU-SOTA-Alert-Telegram-Bot/.venv/bin/sota-telegram-bot
Restart=always
RestartSec=10
User=sota-bot

[Install]
WantedBy=multi-user.target
```

## Development Checks

```bash
python -m unittest
python -m compileall sota_telegram_bot tests
```
