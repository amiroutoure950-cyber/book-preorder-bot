from pathlib import Path

root = Path(__file__).parent
config = (root / "signalbot/config.py").read_text()
domain = (root / "signalbot/domain.py").read_text()
store = (root / "signalbot/store.py").read_text()
bot = (root / "signalbot/bot.py").read_text()

parts = []
for text in (config, domain, store, bot):
    lines = []
    for line in text.splitlines():
        if line == "from __future__ import annotations":
            continue
        if line.startswith("from .config import") or line.startswith("from .domain import") or line.startswith("from .store import"):
            continue
        lines.append(line)
    parts.append("\n".join(lines))

entry = '''

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)

if __name__ == "__main__":
    application = build_application(Config.from_env())
    application.run_polling(allowed_updates=["message", "callback_query", "chat_member"])
'''
output = "from __future__ import annotations\n\n" + "\n\n".join(parts) + entry
(root / "main_standalone.py").write_text(output)
print(root / "main_standalone.py")
