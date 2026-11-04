"""A small, menu-driven ATM simulator for learning Python fundamentals.

This is an educational project, not production banking software. The PIN is
provided when the ATM object is created; the demo CLI uses a sample PIN.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, List, Optional


@dataclass
class Transaction:
    """A single account operation recorded in the session."""

    kind: str
    amount: Decimal
    balance_after: Decimal
    timestamp: datetime


class BankAccount:
    """Stores an account balance and a simple in-memory transaction history."""

    def __init__(self, opening_balance: Decimal = Decimal("10000.00")) -> None:
        if opening_balance < 0:
            raise ValueError("Opening balance cannot be negative.")
        self._balance = opening_balance.quantize(Decimal("0.01"))
        self.transactions: List[Transaction] = []

    @property
    def balance(self) -> Decimal:
        return self._balance

    def deposit(self, amount: Decimal) -> Decimal:
        self._validate_amount(amount)
        self._balance += amount
        self._record("DEPOSIT", amount)
        return self._balance

    def withdraw(self, amount: Decimal) -> Decimal:
        self._validate_amount(amount)
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount
        self._record("WITHDRAWAL", amount)
        return self._balance

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Enter an amount greater than zero.")
        if amount != amount.quantize(Decimal("0.01")):
            raise ValueError("Use no more than two decimal places.")

    def _record(self, kind: str, amount: Decimal) -> None:
        self.transactions.append(
            Transaction(kind, amount, self._balance, datetime.now())
        )


class ATM:
    """Handles authentication and the interactive ATM menu."""

    def __init__(
        self,
        account: Optional[BankAccount] = None,
        pin: str = "1234",
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        if not pin.isdigit() or len(pin) != 4:
            raise ValueError("The PIN must contain exactly four digits.")
        self.account = account or BankAccount()
        self.pin = pin
        self.input = input_fn
        self.output = output_fn

    def authenticate(self) -> bool:
        for attempt in range(3):
            entered_pin = self.input("Enter your 4-digit PIN: ").strip()
            if entered_pin == self.pin:
                self.output("\nAuthentication successful.")
                return True
            remaining = 2 - attempt
            if remaining:
                self.output(f"Incorrect PIN. {remaining} attempt(s) remaining.")
        self.output("Too many incorrect attempts. Your session has been locked.")
        return False

    def run(self) -> None:
        self._show_header()
        if not self.authenticate():
            return

        while True:
            self._show_menu()
            choice = self.input("Select an option (1-5): ").strip()

            if choice == "1":
                self._show_balance()
            elif choice == "2":
                self._handle_deposit()
            elif choice == "3":
                self._handle_withdrawal()
            elif choice == "4":
                self._show_transactions()
            elif choice == "5":
                self.output("\nThank you for using Gnosis ATM. Have a nice day!")
                break
            else:
                self.output("Invalid selection. Please choose a number from 1 to 5.")

    def _show_header(self) -> None:
        self.output("\n" + "=" * 42)
        self.output("              GNOSIS ATM")
        self.output("          Secure Banking Demo")
        self.output("=" * 42)

    def _show_menu(self) -> None:
        self.output("\nMAIN MENU")
        self.output("-" * 30)
        self.output("1. Check balance")
        self.output("2. Deposit money")
        self.output("3. Withdraw money")
        self.output("4. Transaction history")
        self.output("5. Exit")

    def _show_balance(self) -> None:
        self.output(f"Available balance: ₹{self.account.balance:,.2f}")

    def _read_amount(self, prompt: str) -> Optional[Decimal]:
        raw_amount = self.input(prompt).strip().replace(",", "")
        try:
            amount = Decimal(raw_amount)
            self.account._validate_amount(amount)
            return amount
        except (InvalidOperation, ValueError):
            self.output("Invalid amount. Enter a positive number with up to 2 decimals.")
            return None

    def _handle_deposit(self) -> None:
        amount = self._read_amount("Amount to deposit (₹): ")
        if amount is None:
            return
        new_balance = self.account.deposit(amount)
        self.output(f"Deposit successful: ₹{amount:,.2f}")
        self.output(f"New balance: ₹{new_balance:,.2f}")

    def _handle_withdrawal(self) -> None:
        amount = self._read_amount("Amount to withdraw (₹): ")
        if amount is None:
            return
        try:
            new_balance = self.account.withdraw(amount)
        except ValueError as error:
            self.output(str(error))
            return
        self.output(f"Please collect your cash: ₹{amount:,.2f}")
        self.output(f"Remaining balance: ₹{new_balance:,.2f}")

    def _show_transactions(self) -> None:
        self.output("\nTRANSACTION HISTORY")
        self.output("-" * 58)
        if not self.account.transactions:
            self.output("No transactions have been made in this session.")
            return
        for item in self.account.transactions:
            stamp = item.timestamp.strftime("%d %b %Y, %I:%M:%S %p")
            self.output(
                f"{stamp} | {item.kind:<10} | ₹{item.amount:>10,.2f} "
                f"| Balance: ₹{item.balance_after:,.2f}"
            )


def main() -> None:
    """Run the demo ATM. The sample PIN is 1234."""
    ATM(pin="1234").run()


if __name__ == "__main__":
    main()
