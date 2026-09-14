import unittest

from signalbot.bot import methods_keyboard, start_keyboard, welcome_text


class BotHelperTests(unittest.TestCase):
    def test_start_keyboard_has_preorder_action(self):
        keyboard = start_keyboard()
        self.assertEqual(keyboard.inline_keyboard[0][0].callback_data, "begin")

    def test_welcome_mentions_book_and_price(self):
        text = welcome_text()
        self.assertIn("LE FOREX SANS ILLUSION", text)
        self.assertIn("12 500 FCFA", text)
        self.assertIn("25 USDT", text)

    def test_methods_keyboard_has_four_payment_methods(self):
        keyboard = methods_keyboard()
        self.assertEqual([row[0].callback_data for row in keyboard.inline_keyboard], [
            "method:wave", "method:orange", "method:taptap", "method:crypto", "restart"
        ])


if __name__ == "__main__":
    unittest.main()
