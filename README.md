# 9M2PJU SOTA Bot

Telegram bot for SOTA chasers and activators. It watches SOTAwatch spots and alerts, then sends matching updates to subscribed Telegram users.

## Features

- Latest SOTA spots from `https://api2.sota.org.uk/api/spots/-1/all`
- Upcoming SOTA alerts from `https://api2.sota.org.uk/api/alerts`
- Per-user subscriptions in SQLite
- Filters by association, callsign, and mode
- Commands for quick lookup and subscription management
- Polling worker with deduplication so users do not receive repeated posts
- Docker and Docker Compose support

## Bot Token

1. Open Telegram and message `@BotFather`.
2. Create a bot named `9M2PJU SOTA Bot`.
3. Choose a username ending in `bot`, for example `9M2PJU_SOTA_Bot`.
4. Paste the token into `.env`.

Example `.env`:

```bash
TELEGRAM_BOT_TOKEN="123456:your-token"
SOTA_DB_PATH="/app/data/bot.sqlite3"
SOTA_SPOTS_POLL_SECONDS="45"
SOTA_ALERTS_POLL_SECONDS="300"
```

## Docker

```bash
docker compose up -d --build
docker compose logs -f sota-bot
docker compose down
```

The bot stores its SQLite database in the `sota-bot-data` Docker volume.

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

## Verification

```bash
docker compose build
docker compose run --rm sota-bot python -m unittest
```
