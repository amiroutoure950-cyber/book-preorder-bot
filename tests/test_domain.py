from __future__ import annotations

import unittest

from signalbot.domain import BOOK, METHODS, format_amount, payment_instructions, validate_username


class DomainTests(unittest.TestCase):
    def test_book_offer_is_fixed_to_requested_price(self):
        self.assertEqual(BOOK.title, "Le Forex Sans Illusion")
        self.assertEqual(BOOK.fcfa, 12500)
        self.assertEqual(BOOK.usdt, 25)

    def test_payment_methods_are_exactly_the_supported_rails(self):
        self.assertEqual(list(METHODS), ["wave", "orange", "taptap", "crypto"])

    def test_fiat_instructions_use_new_payment_number(self):
        text = payment_instructions("wave", "+22383149995", "address")
        self.assertIn("12 500 FCFA", text)
        self.assertIn("+22383149995", text)
        self.assertIn("Wave", text)

    def test_crypto_instructions_use_bep20_and_address(self):
        text = payment_instructions("crypto", "phone", "0xe89c4c190c8ceb4088182bc133b3454e5a1e827a")
        self.assertIn("25 USDT", text)
        self.assertIn("BEP-20", text)
        self.assertIn("0xe89c4c190c8ceb4088182bc133b3454e5a1e827a", text)

    def test_username_is_normalized_without_changing_user_value(self):
        self.assertEqual(validate_username("amirou"), "@amirou")
        self.assertEqual(validate_username("@amirou"), "@amirou")

    def test_amount_formatting(self):
        self.assertEqual(format_amount(12500), "12 500")


if __name__ == "__main__":
    unittest.main()
