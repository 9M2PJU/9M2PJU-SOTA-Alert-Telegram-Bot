from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from dataclasses import asdict
from typing import Iterable

from .models import Subscriber


class Store:
    def __init__(self, path: str) -> None:
        self.path = path
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with closing(self.connect()) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS subscribers (
                    chat_id INTEGER PRIMARY KEY,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    notify_spots INTEGER NOT NULL DEFAULT 1,
                    notify_alerts INTEGER NOT NULL DEFAULT 1,
                    association_filter TEXT NOT NULL DEFAULT '',
                    callsign_filter TEXT NOT NULL DEFAULT '',
                    mode_filter TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS sent_items (
                    chat_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    item_id INTEGER NOT NULL,
                    sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chat_id, item_type, item_id)
                );
                """
            )
            conn.commit()

    def upsert_subscriber(self, chat_id: int, active: bool = True) -> Subscriber:
        with closing(self.connect()) as conn:
            conn.execute(
                """
                INSERT INTO subscribers (chat_id, is_active)
                VALUES (?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET is_active = excluded.is_active
                """,
                (chat_id, int(active)),
            )
            conn.commit()
        return self.get_subscriber(chat_id)

    def get_subscriber(self, chat_id: int) -> Subscriber:
        with closing(self.connect()) as conn:
            row = conn.execute("SELECT * FROM subscribers WHERE chat_id = ?", (chat_id,)).fetchone()
        if row is None:
            return self.upsert_subscriber(chat_id)
        return _subscriber_from_row(row)

    def list_active_subscribers(self) -> list[Subscriber]:
        with closing(self.connect()) as conn:
            rows = conn.execute("SELECT * FROM subscribers WHERE is_active = 1").fetchall()
        return [_subscriber_from_row(row) for row in rows]

    def set_active(self, chat_id: int, active: bool) -> None:
        self.upsert_subscriber(chat_id, active=active)

    def set_filter(self, chat_id: int, key: str, value: str) -> Subscriber:
        columns = {
            "association": "association_filter",
            "callsign": "callsign_filter",
            "mode": "mode_filter",
        }
        column = columns.get(key)
        if column is None:
            raise ValueError("filter key must be association, callsign, or mode")
        self.upsert_subscriber(chat_id)
        with closing(self.connect()) as conn:
            conn.execute(
                f"UPDATE subscribers SET {column} = ? WHERE chat_id = ?",
                (value.strip().upper(), chat_id),
            )
            conn.commit()
        return self.get_subscriber(chat_id)

    def clear_filters(self, chat_id: int) -> Subscriber:
        self.upsert_subscriber(chat_id)
        with closing(self.connect()) as conn:
            conn.execute(
                """
                UPDATE subscribers
                SET association_filter = '', callsign_filter = '', mode_filter = ''
                WHERE chat_id = ?
                """,
                (chat_id,),
            )
            conn.commit()
        return self.get_subscriber(chat_id)

    def mark_sent(self, chat_id: int, item_type: str, item_id: int) -> bool:
        with closing(self.connect()) as conn:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO sent_items (chat_id, item_type, item_id)
                VALUES (?, ?, ?)
                """,
                (chat_id, item_type, item_id),
            )
            conn.commit()
            return cursor.rowcount == 1

    def bootstrap_sent(self, subscribers: Iterable[Subscriber], item_type: str, item_ids: Iterable[int]) -> None:
        rows = [(subscriber.chat_id, item_type, item_id) for subscriber in subscribers for item_id in item_ids]
        if not rows:
            return
        with closing(self.connect()) as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO sent_items (chat_id, item_type, item_id)
                VALUES (?, ?, ?)
                """,
                rows,
            )
            conn.commit()


def _subscriber_from_row(row: sqlite3.Row) -> Subscriber:
    return Subscriber(
        chat_id=int(row["chat_id"]),
        is_active=bool(row["is_active"]),
        notify_spots=bool(row["notify_spots"]),
        notify_alerts=bool(row["notify_alerts"]),
        association_filter=str(row["association_filter"]),
        callsign_filter=str(row["callsign_filter"]),
        mode_filter=str(row["mode_filter"]),
    )


def describe_filters(subscriber: Subscriber) -> str:
    data = asdict(subscriber)
    filters = {
        "association": data["association_filter"] or "any",
        "callsign": data["callsign_filter"] or "any",
        "mode": data["mode_filter"] or "any",
    }
    return "\n".join(f"{key}: {value}" for key, value in filters.items())
