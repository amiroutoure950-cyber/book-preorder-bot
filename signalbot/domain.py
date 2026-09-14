from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BookOffer:
    title: str
    author: str
    fcfa: int
    usdt: int


BOOK = BookOffer(
    title="Le Forex Sans Illusion",
    author="Hamma Dit Amirou Toure",
    fcfa=12_500,
    usdt=25,
)

METHODS = {
    "wave": "Wave",
    "orange": "Orange Money",
    "taptap": "TapTap Send",
    "crypto": "Crypto — USDT BEP-20",
}


def format_amount(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


def payment_instructions(method: str, phone: str, usdt_address: str) -> str:
    common = (
        f"📖 {BOOK.title}\n"
        f"💵 Montant : {format_amount(BOOK.fcfa)} FCFA\n"
        "Après le paiement, envoyez ici une capture claire du reçu. "
        "La précommande sera confirmée après vérification manuelle.\n\n"
    )
    if method in {"wave", "orange", "taptap"}:
        label = METHODS[method]
        extra = f"📱 Numéro de paiement : `{phone}`"
        if method == "taptap":
            extra += "\n👤 Bénéficiaire : Amirou Toure"
        return common + f"🟠 Moyen choisi : {label}\n" + extra
    if method == "crypto":
        return (
            common.replace(f"{format_amount(BOOK.fcfa)} FCFA", f"{BOOK.usdt} USDT")
            + "🪙 Réseau obligatoire : BEP-20 (BSC)\n"
            + f"📍 Adresse USDT : `{usdt_address}`\n\n"
            + "Vérifiez impérativement le réseau et l’adresse avant l’envoi."
        )
    raise ValueError("Méthode de paiement inconnue")


def validate_username(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    return value if value.startswith("@") else "@" + value
