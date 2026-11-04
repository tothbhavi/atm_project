# Gnosis ATM Banking System

A menu-driven ATM simulator built with Python. This project demonstrates object-oriented programming, input validation, decimal-based money handling, authentication flow, and transaction history.

## Features

- **PIN authentication** with a maximum of three attempts
- **Balance enquiry** with currency formatting
- **Cash deposits** with positive-amount validation
- **Cash withdrawals** with insufficient-funds protection
- **Transaction history** with timestamps and running balances
- **Interactive menu** that stays active until the user exits
- **Safe money arithmetic** using Python's `Decimal` type rather than floating-point numbers
- **Testable design** with input/output functions that can be injected

## Requirements

- Python 3.9 or newer
- No third-party packages required

## Run the application

Clone the repository and run:

```bash
python ATM.py
```

The educational demo PIN is `1234`.

> **Security note:** This is a learning simulator. The demo PIN is hardcoded, the account is stored only in memory, and authentication is not suitable for real banking. Do not use real credentials or financial data.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
atm_project/
├── ATM.py
├── README.md
└── tests/
    └── test_atm.py
```

## Design overview

- `BankAccount` owns the balance and enforces deposit/withdrawal rules.
- `Transaction` represents an auditable operation in the current session.
- `ATM` manages the user interface, PIN attempts, and menu flow.
- `main()` is the executable entry point, so importing the module does not start an interactive session.

## Learning outcomes

This project is intended to practise classes, dataclasses, type hints, exception handling, loops, functions, dependency injection, unit testing, and the `decimal` module.
