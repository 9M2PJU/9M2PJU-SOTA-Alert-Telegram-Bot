from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes

from .config import load_settings
from .filters import alert_matches, spot_matches
from .formatting import format_alert, format_spot, help_text
from .sotawatch import SotawatchClient, SotawatchError
from .storage import Store, describe_filters

LOGGER = logging.getLogger(__name__)


class SotaBot:
    def __init__(self, store: Store, client: SotawatchClient) -> None:
        self.store = store
        self.client = client

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or update.message is None:
            return
        self.store.upsert_subscriber(update.effective_chat.id)
        await update.message.reply_html(help_text())

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is not None:
            await update.message.reply_html(help_text())

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or update.message is None:
            return
        self.store.set_active(update.effective_chat.id, True)
        await update.message.reply_text("Subscribed. I will send matching SOTA spots and alerts.")

    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or update.message is None:
            return
        self.store.set_active(update.effective_chat.id, False)
        await update.message.reply_text("Unsubscribed. Use /subscribe to enable notifications again.")

    async def filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or update.message is None:
            return
        chat_id = update.effective_chat.id
        args = context.args or []
        if not args:
            subscriber = self.store.get_subscriber(chat_id)
            await update.message.reply_text("Current filters:\n" + describe_filters(subscriber))
            return
        if len(args) < 2:
            await update.message.reply_text("Usage: /filter association 9M, /filter callsign 9M2PJU, or /filter mode CW")
            return
        key = args[0].lower()
        value = " ".join(args[1:])
        try:
            subscriber = self.store.set_filter(chat_id, key, value)
        except ValueError as exc:
            await update.message.reply_text(str(exc))
            return
        await update.message.reply_text("Updated filters:\n" + describe_filters(subscriber))

    async def clearfilters(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or update.message is None:
            return
        subscriber = self.store.clear_filters(update.effective_chat.id)
        await update.message.reply_text("Filters cleared:\n" + describe_filters(subscriber))

    async def spots(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or update.message is None:
            return
        subscriber = self.store.get_subscriber(update.effective_chat.id)
        try:
            spots = await asyncio.to_thread(self.client.fetch_spots)
        except SotawatchError as exc:
            LOGGER.warning("spots lookup failed: %s", exc)
            await update.message.reply_text("Could not fetch SOTAwatch spots right now.")
            return
        matches = [spot for spot in spots if spot_matches(subscriber, spot)][:5]
        if not matches:
            await update.message.reply_text("No matching spots found.")
            return
        for spot in matches:
            await update.message.reply_html(format_spot(spot), disable_web_page_preview=True)

    async def alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or update.message is None:
            return
        subscriber = self.store.get_subscriber(update.effective_chat.id)
        try:
            alerts = await asyncio.to_thread(self.client.fetch_alerts)
        except SotawatchError as exc:
            LOGGER.warning("alerts lookup failed: %s", exc)
            await update.message.reply_text("Could not fetch SOTAwatch alerts right now.")
            return
        matches = [alert for alert in alerts if alert_matches(subscriber, alert)][:5]
        if not matches:
            await update.message.reply_text("No matching alerts found.")
            return
        for alert in matches:
            await update.message.reply_html(format_alert(alert), disable_web_page_preview=True)


async def poll_spots(application: Application, store: Store, client: SotawatchClient, interval: int) -> None:
    while True:
        try:
            spots = await asyncio.to_thread(client.fetch_spots)
            subscribers = store.list_active_subscribers()
            for spot in reversed(spots):
                for subscriber in subscribers:
                    if spot_matches(subscriber, spot) and store.mark_sent(subscriber.chat_id, "spot", spot.id):
                        await _send(application, subscriber.chat_id, format_spot(spot))
        except Exception:
            LOGGER.exception("spot polling failed")
        await asyncio.sleep(interval)


async def poll_alerts(application: Application, store: Store, client: SotawatchClient, interval: int) -> None:
    while True:
        try:
            alerts = await asyncio.to_thread(client.fetch_alerts)
            subscribers = store.list_active_subscribers()
            for alert in alerts:
                for subscriber in subscribers:
                    if alert_matches(subscriber, alert) and store.mark_sent(subscriber.chat_id, "alert", alert.id):
                        await _send(application, subscriber.chat_id, format_alert(alert))
        except Exception:
            LOGGER.exception("alert polling failed")
        await asyncio.sleep(interval)


async def _send(application: Application, chat_id: int, text: str) -> None:
    try:
        await application.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except TelegramError:
        LOGGER.exception("telegram send failed for chat_id=%s", chat_id)


async def bootstrap_existing(store: Store, client: SotawatchClient) -> None:
    subscribers = store.list_active_subscribers()
    if not subscribers:
        return
    try:
        spots = await asyncio.to_thread(client.fetch_spots)
        alerts = await asyncio.to_thread(client.fetch_alerts)
    except SotawatchError:
        LOGGER.exception("could not bootstrap existing SOTAwatch items")
        return
    store.bootstrap_sent(subscribers, "spot", (spot.id for spot in spots))
    store.bootstrap_sent(subscribers, "alert", (alert.id for alert in alerts))


async def post_init(application: Application) -> None:
    settings = application.bot_data["settings"]
    store = application.bot_data["store"]
    client = application.bot_data["client"]
    if settings.bootstrap_existing_items:
        await bootstrap_existing(store, client)
    application.create_task(poll_spots(application, store, client, settings.spots_poll_seconds))
    application.create_task(poll_alerts(application, store, client, settings.alerts_poll_seconds))


def build_application() -> Application:
    settings = load_settings()
    store = Store(settings.db_path)
    client = SotawatchClient(settings.request_timeout_seconds)
    sota_bot = SotaBot(store, client)

    application = Application.builder().token(settings.telegram_bot_token).post_init(post_init).build()
    application.bot_data["settings"] = settings
    application.bot_data["store"] = store
    application.bot_data["client"] = client

    application.add_handler(CommandHandler("start", sota_bot.start))
    application.add_handler(CommandHandler("help", sota_bot.help))
    application.add_handler(CommandHandler("subscribe", sota_bot.subscribe))
    application.add_handler(CommandHandler("unsubscribe", sota_bot.unsubscribe))
    application.add_handler(CommandHandler("filter", sota_bot.filter))
    application.add_handler(CommandHandler("clearfilters", sota_bot.clearfilters))
    application.add_handler(CommandHandler("spots", sota_bot.spots))
    application.add_handler(CommandHandler("alerts", sota_bot.alerts))
    return application


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    build_application().run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
