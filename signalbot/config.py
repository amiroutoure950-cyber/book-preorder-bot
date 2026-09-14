from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_username: str
    admin_chat_id: int
    payment_phone: str
    usdt_address: str
    database_path: Path
    cover_path: Path

    @classmethod
    def from_env(cls) -> "Config":
        required = ["BOT_TOKEN", "ADMIN_CHAT_ID"]
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError("Variables manquantes : " + ", ".join(missing))
        return cls(
            bot_token=os.environ["BOT_TOKEN"],
            admin_username=os.getenv("ADMIN_USERNAME", "touramirou").lstrip("@"),
            admin_chat_id=int(os.environ["ADMIN_CHAT_ID"]),
            payment_phone=os.getenv("PAYMENT_PHONE", "+223" + "83149995").strip(),
            usdt_address=os.getenv("USDT_ADDRESS", "0xe89c4c190c8ceb4088182bc133b3454e5a1e827a"),
            database_path=Path(os.getenv("DATABASE_PATH", "data/book_preorders.db")),
            cover_path=Path(os.getenv("COVER_PATH", "cover.png")),
        )
