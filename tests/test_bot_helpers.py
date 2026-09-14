import unittest

from signalbot.bot import methods_keyboard, start_keyboard, welcome_text


class BotHelperTests(unittest.TestCase):
    def test_start_keyboard_has_preorder_action(self):
        keyboard = start_keyboard()
        self.assertEqual(keyboard.inline_keyboard[0][0].callback_data, "begin")

    def test_welcome_contains_requested_sales_copy(self):
        text = welcome_text()
        self.assertIn("Vous avez découvert le trading sur les réseaux sociaux", text)
        self.assertIn("Une progression pensée pour les vrais débutants", text)
        self.assertIn("Précommandez maintenant votre exemplaire", text)
        self.assertIn("12 500 FCFA", text)
        self.assertIn("25 USDT", text)

    def test_methods_keyboard_has_four_payment_methods(self):
        keyboard = methods_keyboard()
        self.assertEqual([row[0].callback_data for row in keyboard.inline_keyboard], [
            "method:wave", "method:orange", "method:taptap", "method:crypto", "restart"
        ])


if __name__ == "__main__":
    unittest.main()
