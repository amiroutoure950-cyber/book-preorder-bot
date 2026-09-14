from __future__ import annotations

from signalbot.bot import build_application
from signalbot.config import Config


if __name__ == "__main__":
    config = Config.from_env()
    application = build_application(config)
    application.run_polling(drop_pending_updates=True)
