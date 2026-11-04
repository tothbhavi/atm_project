# ATM Simulator (Python)

A small, local, single-user ATM simulation built with Python's standard library. It demonstrates credential verification, input validation, persistent state and basic transaction handling.

## Features

- First-run PIN setup (4–8 digits) with confirmation; no PIN is hard-coded in the source.
- PIN verifier stored using PBKDF2-HMAC-SHA256 with a random per-account salt.
- Constant-time verifier comparison via `hmac.compare_digest`.
- Three PIN attempts per program run.
- Persistent balance stored in a local JSON data file.
- Deposit and withdrawal validation, including insufficient-funds checks.
- Atomic file replacement to reduce the chance of a partially written account file.
- Unit tests using Python's built-in `unittest`.

## Run

Requires Python 3.10+.

```bash
python atm.py
```

On first run, create and confirm a demo PIN. The program creates `atm_data.json` in the current working directory. This file is ignored by Git. Do not commit it or share it.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Authentication and request flow

1. The user enters a PIN through `getpass`, so it is not echoed in a normal terminal.
2. The program reads the random salt and PBKDF2 verifier from the local account file.
3. It derives a candidate verifier from the entered PIN and stored salt.
4. `hmac.compare_digest` compares the candidate and stored verifier.
5. After successful verification, the CLI exposes the transaction menu.

This is a local CLI demo. It has no network requests, user database, access tokens, refresh tokens, server-side sessions or multi-user authorization.

## Security limitations

This project is an educational exercise, **not real banking software**. A short numeric PIN has limited entropy. Anyone who obtains the local data file can attempt offline PIN guessing. The JSON balance is not protected against a user who can edit the file, and the attempt counter resets when the program restarts. There is no concurrent-user or multi-process transaction locking, audit ledger, hardware security module, secure server, or regulated financial controls.

For a production system, authentication, account state and transaction authorization must be enforced by a properly secured backend. Never use this project to store real credentials or money.

## Project structure

```text
atm_project/
├── atm.py
├── README.md
├── .gitignore
└── tests/
    └── test_atm.py
```
