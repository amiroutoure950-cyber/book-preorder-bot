from __future__ import annotations

import logging
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import Config
from .domain import BOOK, METHODS, format_amount, payment_instructions, validate_username
from .store import Store

logger = logging.getLogger(__name__)

WELCOME_TEMPLATE = """📖 *LE FOREX SANS ILLUSION*

Comprendre le marché des changes, protéger son capital et apprendre à trader avec méthode.

Un livre de Hamma Dit Amirou Toure pour sortir des promesses faciles et construire une vraie compréhension du trading.

✅ Le Forex expliqué avec des mots simples
✅ Psychologie, discipline et habitudes du trader
✅ Gestion du risque et protection du capital
✅ Prix, volume, sentiment et macroéconomie
✅ Méthode, journal de trading et progression durable

Ce livre ne promet pas de gains garantis. Il vous aide à développer un cadre de réflexion plus lucide, plus discipliné et plus professionnel.

💰 *Précommande : {fcfa} FCFA ou {usdt} USDT*

Remplissez vos informations pour réserver votre exemplaire :"""


def welcome_text() -> str:
    return WELCOME_TEMPLATE.format(fcfa=format_amount(BOOK.fcfa), usdt=BOOK.usdt)


def methods_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"method:{code}")]
        for code, label in METHODS.items()
    ] + [[InlineKeyboardButton("⬅️ Recommencer", callback_data="restart")]])


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Précommander maintenant", callback_data="begin")]])


def admin_keyboard(preorder_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Valider", callback_data=f"approve:{preorder_id}"),
        InlineKeyboardButton("❌ Refuser", callback_data=f"reject:{preorder_id}"),
    ]])


def begin_collection(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = "full_name"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_photo(
        photo=Path(context.application.bot_data["config"].cover_path).open("rb"),
        caption=welcome_text(),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=start_keyboard(),
    )


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    if data == "begin":
        await query.answer()
        begin_collection(context)
        await query.message.reply_text("1/4 — Quel est votre nom et prénom ?")
        return
    if data == "restart":
        await query.answer()
        begin_collection(context)
        await query.edit_message_text("1/4 — Quel est votre nom et prénom ?")
        return
    if data.startswith("method:"):
        await query.answer()
        method = data.split(":", 1)[1]
        if method not in METHODS or context.user_data.get("step") != "method":
            return
        context.user_data["method"] = method
        context.user_data["step"] = "receipt"
        cfg: Config = context.application.bot_data["config"]
        await query.edit_message_text(payment_instructions(method, cfg.payment_phone, cfg.usdt_address), parse_mode=ParseMode.MARKDOWN)
        await query.message.reply_text("📸 Envoyez maintenant la capture du reçu dans cette conversation.")
        return
    if data.startswith("approve:") or data.startswith("reject:"):
        await decide_preorder(update, context)


async def collect_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step not in {"full_name", "country", "phone", "username"}:
        await update.message.reply_text("Utilisez /start pour commencer une précommande.")
        return
    value = (update.message.text or "").strip()
    if len(value) < 2:
        await update.message.reply_text("Merci d'indiquer une information valide.")
        return
    context.user_data[step] = value
    prompts = {
        "full_name": ("country", "2/4 — Dans quel pays résidez-vous ?"),
        "country": ("phone", "3/4 — Quel est votre numéro de téléphone avec l'indicatif pays ?"),
        "phone": ("username", "4/4 — Quel est votre username Telegram ? Exemple : @username"),
    }
    if step in prompts:
        next_step, prompt = prompts[step]
        context.user_data["step"] = next_step
        await update.message.reply_text(prompt)
        return
    context.user_data["telegram_username"] = validate_username(value)
    context.user_data["step"] = "method"
    await update.message.reply_text(
        f"Merci. Choisissez votre moyen de paiement pour la précommande de *{BOOK.title}* :",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=methods_keyboard(),
    )


async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") != "receipt":
        await update.message.reply_text("Utilisez /start pour commencer une précommande.")
        return
    cfg: Config = context.application.bot_data["config"]
    store: Store = context.application.bot_data["store"]
    if update.message.photo:
        receipt_file_id = update.message.photo[-1].file_id
    elif update.message.document and (update.message.document.mime_type or "").startswith("image/"):
        receipt_file_id = update.message.document.file_id
    else:
        await update.message.reply_text("Veuillez envoyer une image du reçu.")
        return
    user = update.effective_user
    preorder_id = store.create_preorder(
        telegram_user_id=user.id,
        telegram_username=context.user_data.get("telegram_username"),
        full_name=context.user_data["full_name"],
        country=context.user_data["country"],
        phone=context.user_data["phone"],
        method=context.user_data["method"],
        receipt_file_id=receipt_file_id,
    )
    caption = (
        f"🔔 PRÉCOMMANDE À VÉRIFIER #{preorder_id}\n\n"
        f"Livre : {BOOK.title}\n"
        f"Nom et prénom : {context.user_data['full_name']}\n"
        f"Pays de résidence : {context.user_data['country']}\n"
        f"Téléphone : {context.user_data['phone']}\n"
        f"Username Telegram : {context.user_data['telegram_username'] or 'non renseigné'}\n"
        f"ID Telegram : {user.id}\n"
        f"Paiement : {METHODS[context.user_data['method']]}\n"
        f"Montant : {format_amount(BOOK.fcfa)} FCFA / {BOOK.usdt} USDT"
    )
    await context.bot.send_photo(cfg.admin_chat_id, receipt_file_id, caption=caption, reply_markup=admin_keyboard(preorder_id))
    context.user_data.clear()
    await update.message.reply_text("✅ Votre précommande a été enregistrée. Le reçu est en cours de vérification manuelle.")


async def decide_preorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cfg: Config = context.application.bot_data["config"]
    if query.from_user.id != cfg.admin_chat_id:
        await query.answer("Action réservée à l'administrateur.", show_alert=True)
        return
    action, raw_id = (query.data or "").split(":", 1)
    preorder_id = int(raw_id)
    store: Store = context.application.bot_data["store"]
    preorder = store.get_preorder(preorder_id)
    if not preorder:
        await query.answer("Précommande introuvable.", show_alert=True)
        return
    status = "approved" if action == "approve" else "rejected"
    if not store.decide_preorder(preorder_id, status, query.from_user.id):
        await query.answer("Cette précommande a déjà été traitée.", show_alert=True)
        return
    if status == "approved":
        message = "✅ Votre précommande du livre *Le Forex Sans Illusion* est confirmée. Nous vous contacterons pour la livraison dès sa sortie."
        suffix = "\n\n✅ PRÉCOMMANDE VALIDÉE"
    else:
        message = "❌ Votre reçu n'a pas pu être validé. Contactez le support avec votre numéro de précommande."
        suffix = "\n\n❌ PRÉCOMMANDE REFUSÉE"
    await context.bot.send_message(preorder["telegram_user_id"], message, parse_mode=ParseMode.MARKDOWN)
    await query.edit_message_caption(caption=(query.message.caption or "") + suffix, reply_markup=None)
    await query.answer("Décision enregistrée.")


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg: Config = context.application.bot_data["config"]
    await update.effective_message.reply_text(f"Support : @{cfg.admin_username}")


def build_application(cfg: Config) -> Application:
    cfg.database_path.parent.mkdir(parents=True, exist_ok=True)
    store = Store(cfg.database_path)
    store.initialize()
    app = Application.builder().token(cfg.bot_token).build()
    app.bot_data["config"] = cfg
    app.bot_data["store"] = store
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, collect_text))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & (filters.PHOTO | filters.Document.IMAGE), receive_receipt))
    return app
