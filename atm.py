"""Local, educational ATM CLI. Not suitable for real financial use."""
from __future__ import annotations

import base64
import getpass
import hashlib
import hmac
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

PBKDF2_ITERATIONS = 310_000
INITIAL_BALANCE = 10_000


class ATMError(Exception):
    """Expected ATM operation error."""


def _derive_pin_hash(pin: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", pin.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )


def _validate_pin(pin: str) -> None:
    if not re.fullmatch(r"\d{4,8}", pin):
        raise ATMError("PIN must contain 4 to 8 digits.")


class ATM:
    """A single-user ATM simulation backed by a local JSON file."""

    def __init__(self, data_file: str | Path = "atm_data.json") -> None:
        self.data_file = Path(data_file)
        self._data: dict[str, Any] | None = None
        if self.data_file.exists():
            self._load()

    @property
    def is_initialized(self) -> bool:
        return self._data is not None

    def initialize(self, pin: str, initial_balance: int = INITIAL_BALANCE) -> None:
        if self.is_initialized:
            raise ATMError("ATM account is already initialized.")
        _validate_pin(pin)
        if not isinstance(initial_balance, int) or isinstance(initial_balance, bool) or initial_balance < 0:
            raise ATMError("Initial balance must be a non-negative whole number.")

        salt = os.urandom(16)
        self._data = {
            "version": 1,
            "pin_salt": base64.b64encode(salt).decode("ascii"),
            "pin_hash": base64.b64encode(_derive_pin_hash(pin, salt)).decode("ascii"),
            "balance": initial_balance,
        }
        self._save()

    def authenticate(self, pin: str) -> bool:
        if not self.is_initialized:
            raise ATMError("Initialize the account before signing in.")
        try:
            _validate_pin(pin)
            salt = base64.b64decode(self._data["pin_salt"], validate=True)
            expected = base64.b64decode(self._data["pin_hash"], validate=True)
            actual = _derive_pin_hash(pin, salt)
            return hmac.compare_digest(actual, expected)
        except (ATMError, ValueError, KeyError):
            return False

    def get_balance(self) -> int:
        self._require_initialized()
        return int(self._data["balance"])

    def deposit(self, amount: int) -> int:
        self._validate_amount(amount)
        self._require_initialized()
        self._data["balance"] += amount
        self._save()
        return self.get_balance()

    def withdraw(self, amount: int) -> int:
        self._validate_amount(amount)
        self._require_initialized()
        if amount > self._data["balance"]:
            raise ATMError("Insufficient funds.")
        self._data["balance"] -= amount
        self._save()
        return self.get_balance()

    def _require_initialized(self) -> None:
        if not self.is_initialized:
            raise ATMError("Initialize the account first.")

    @staticmethod
    def _validate_amount(amount: int) -> None:
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ATMError("Amount must be a positive whole number of rupees.")

    def _load(self) -> None:
        try:
            data = json.loads(self.data_file.read_text(encoding="utf-8"))
            if data.get("version") != 1 or not isinstance(data.get("balance"), int):
                raise ValueError("Unsupported or invalid account data.")
            base64.b64decode(data["pin_salt"], validate=True)
            base64.b64decode(data["pin_hash"], validate=True)
            self._data = data
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ATMError(f"Could not read account data: {exc}") from exc

    def _save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{self.data_file.name}.", dir=self.data_file.parent, text=True
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self._data, handle, indent=2)
                handle.write("\n")
            os.replace(temporary_name, self.data_file)
            try:
                self.data_file.chmod(0o600)
            except OSError:
                pass  # File permissions are platform-dependent.
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)


def run() -> None:
    atm = ATM()
    print("\n=== Local ATM Simulator ===")
    try:
        if not atm.is_initialized:
            print("First run: create a 4–8 digit demo PIN.")
            while True:
                pin = getpass.getpass("Create PIN: ")
                confirmation = getpass.getpass("Confirm PIN: ")
                if pin != confirmation:
                    print("PINs do not match. Try again.")
                    continue
                try:
                    atm.initialize(pin)
                    print("Account created. Your starting balance is ₹10,000.")
                    break
                except ATMError as exc:
                    print(exc)
        authenticated = False
        for attempt in range(3):
            if atm.authenticate(getpass.getpass("Enter PIN: ")):
                authenticated = True
                break
            print(f"Incorrect PIN. {2 - attempt} attempt(s) remaining.")
        if not authenticated:
            print("Too many failed attempts. Session ended.")
            return

        while True:
            print("\n1. Check balance\n2. Deposit\n3. Withdraw\n4. Exit")
            choice = input("Choose an option: ").strip()
            try:
                if choice == "1":
                    print(f"Balance: ₹{atm.get_balance():,}")
                elif choice in {"2", "3"}:
                    amount_text = input("Amount in whole rupees: ").strip()
                    if not amount_text.isdigit():
                        raise ATMError("Enter a positive whole number.")
                    amount = int(amount_text)
                    balance = atm.deposit(amount) if choice == "2" else atm.withdraw(amount)
                    print(f"Transaction successful. Balance: ₹{balance:,}")
                elif choice == "4":
                    print("Thank you. Session ended.")
                    return
                else:
                    print("Choose 1, 2, 3 or 4.")
            except ATMError as exc:
                print(f"Transaction failed: {exc}")
    except (ATMError, KeyboardInterrupt, EOFError) as exc:
        print(f"\nSession ended: {exc or 'interrupted'}")


if __name__ == "__main__":
    run()
