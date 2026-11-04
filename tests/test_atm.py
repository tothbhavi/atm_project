import tempfile
import unittest
from pathlib import Path

from atm import ATM, ATMError


class ATMTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "account.json"
        self.atm = ATM(self.data_file)
        self.atm.initialize("4826")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pin_is_not_stored_in_plaintext(self):
        stored = self.data_file.read_text(encoding="utf-8")
        self.assertNotIn('"4826"', stored)
        self.assertTrue(self.atm.authenticate("4826"))
        self.assertFalse(self.atm.authenticate("1111"))

    def test_balance_persists_after_reload(self):
        self.atm.deposit(500)
        reloaded = ATM(self.data_file)
        self.assertEqual(reloaded.get_balance(), 10_500)

    def test_deposit_and_withdraw(self):
        self.assertEqual(self.atm.deposit(250), 10_250)
        self.assertEqual(self.atm.withdraw(1_000), 9_250)

    def test_rejects_zero_and_negative_amounts(self):
        for amount in (0, -10):
            with self.subTest(amount=amount):
                with self.assertRaises(ATMError):
                    self.atm.deposit(amount)

    def test_rejects_withdrawal_above_balance(self):
        with self.assertRaises(ATMError):
            self.atm.withdraw(10_001)
        self.assertEqual(self.atm.get_balance(), 10_000)

    def test_rejects_invalid_pin_format(self):
        with self.assertRaises(ATMError):
            ATM(Path(self.temp_dir.name) / "other.json").initialize("12")

    def test_prevents_double_initialization(self):
        with self.assertRaises(ATMError):
            self.atm.initialize("1234")


if __name__ == "__main__":
    unittest.main()
