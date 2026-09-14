from __future__ import annotations

import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path: Path | str):
        self.path = str(path)

    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS preorders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_user_id INTEGER NOT NULL,
                    telegram_username TEXT,
                    full_name TEXT NOT NULL,
                    country TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    method TEXT NOT NULL,
                    receipt_file_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    admin_id INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    decided_at TEXT
                );
                """
            )

    def create_preorder(self, *, telegram_user_id: int, telegram_username: str | None,
                        full_name: str, country: str, phone: str, method: str,
                        receipt_file_id: str) -> int:
        with self.connect() as db:
            cursor = db.execute(
                """INSERT INTO preorders
                (telegram_user_id, telegram_username, full_name, country, phone, method, receipt_file_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (telegram_user_id, telegram_username, full_name, country, phone, method, receipt_file_id),
            )
            return int(cursor.lastrowid)

    def get_preorder(self, preorder_id: int):
        with self.connect() as db:
            row = db.execute("SELECT * FROM preorders WHERE id = ?", (preorder_id,)).fetchone()
            return dict(row) if row else None

    def decide_preorder(self, preorder_id: int, status: str, admin_id: int) -> bool:
        with self.connect() as db:
            cursor = db.execute(
                """UPDATE preorders SET status = ?, admin_id = ?, decided_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'pending'""",
                (status, admin_id, preorder_id),
            )
            return cursor.rowcount == 1
