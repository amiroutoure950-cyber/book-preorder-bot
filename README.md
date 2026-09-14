# Bot de précommande — Le Forex Sans Illusion

Bot Telegram de précommande pour **Le Forex Sans Illusion**, par Hamma Dit Amirou Toure.

## Parcours client

1. Présentation du livre et de la couverture.
2. Saisie du nom et prénom, pays de résidence, téléphone et username Telegram.
3. Choix du paiement : Wave, Orange Money, TapTap Send ou USDT BEP-20.
4. Affichage des instructions exactes.
5. Envoi d'une capture du reçu.
6. Vérification manuelle par l'administrateur avec boutons Valider/Refuser.

Prix : **12 500 FCFA** ou **25 USDT**.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
BOT_TOKEN='...' ADMIN_CHAT_ID='...' .venv/bin/python main.py
```

Ne mettez jamais le token dans Git. Le token fourni dans une conversation doit être révoqué et remplacé via BotFather avant la mise en production.

## Variables

Voir `.env.example`. `ADMIN_CHAT_ID` est obligatoire et doit être l'ID numérique du compte qui recevra les demandes et validera les paiements.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
