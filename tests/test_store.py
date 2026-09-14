import tempfile
import unittest
from pathlib import Path

from signalbot.store import Store


class StoreTests(unittest.TestCase):
    def test_preorder_decision_is_one_shot(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "test.db")
            store.initialize()
            preorder_id = store.create_preorder(
                telegram_user_id=10,
                telegram_username="@user",
                full_name="Test User",
                country="Mali",
                phone="+22300000000",
                method="wave",
                receipt_file_id="file-1",
            )
            self.assertTrue(store.decide_preorder(preorder_id, "approved", 99))
            self.assertFalse(store.decide_preorder(preorder_id, "rejected", 99))
            self.assertEqual(store.get_preorder(preorder_id)["status"], "approved")


if __name__ == "__main__":
    unittest.main()
