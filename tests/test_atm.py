import unittest
from decimal import Decimal

from ATM import ATM, BankAccount


class BankAccountTests(unittest.TestCase):
    def setUp(self):
        self.account = BankAccount(Decimal("1000.00"))

    def test_deposit_updates_balance_and_history(self):
        self.assertEqual(self.account.deposit(Decimal("250.50")), Decimal("1250.50"))
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0].kind, "DEPOSIT")

    def test_withdrawal_updates_balance_and_history(self):
        self.assertEqual(self.account.withdraw(Decimal("200.00")), Decimal("800.00"))
        self.assertEqual(self.account.transactions[0].kind, "WITHDRAWAL")

    def test_withdrawal_rejects_insufficient_funds(self):
        with self.assertRaisesRegex(ValueError, "Insufficient funds"):
            self.account.withdraw(Decimal("1000.01"))
        self.assertEqual(self.account.balance, Decimal("1000.00"))

    def test_deposit_rejects_zero_and_negative_amounts(self):
        for amount in (Decimal("0"), Decimal("-1")):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.account.deposit(amount)

    def test_amount_rejects_more_than_two_decimal_places(self):
        with self.assertRaisesRegex(ValueError, "two decimal places"):
            self.account.deposit(Decimal("1.234"))


class ATMTests(unittest.TestCase):
    def test_authentication_locks_after_three_wrong_pins(self):
        answers = iter(["0000", "1111", "2222"])
        messages = []
        atm = ATM(
            account=BankAccount(),
            pin="1234",
            input_fn=lambda _prompt: next(answers),
            output_fn=messages.append,
        )
        self.assertFalse(atm.authenticate())
        self.assertTrue(any("locked" in message for message in messages))

    def test_authentication_accepts_correct_pin(self):
        messages = []
        atm = ATM(
            pin="1234",
            input_fn=lambda _prompt: "1234",
            output_fn=messages.append,
        )
        self.assertTrue(atm.authenticate())
        self.assertTrue(any("successful" in message for message in messages))

    def test_importable_module_does_not_start_cli(self):
        # Importing ATM is safe because execution is guarded by __main__.
        import ATM as atm_module
        self.assertTrue(callable(atm_module.main))


if __name__ == "__main__":
    unittest.main()
