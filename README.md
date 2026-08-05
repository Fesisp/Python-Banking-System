# Python Banking System (Fesisbank) 🏦

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Security](https://img.shields.io/badge/Security-SHA--256-green)]()
[![Build Status](https://img.shields.io/badge/Tests-Passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A robust CLI banking engine built with **Object-Oriented Programming (OOP)**, **SQLite data persistence**, **SHA-256 credential security**, and **atomic transaction processing**. Zero external dependencies required.

---

## 📋 Overview

The **Python Banking System (Fesisbank)** simulates a full-featured retail banking lifecycle in a secure, structured environment. It addresses the common limitations of in-memory banking prototypes by introducing relational persistence, secure authentication, overdraft management, and atomic money transfers across customer accounts.

Designed with clean architecture and OOP design patterns, it serves as an enterprise-grade reference implementation for Python standard library capabilities.

---

## ✨ Key Features

* **🔐 Secure Authentication:** User login via CPF and password with salted **SHA-256 password hashing** (`Security` module) and password management.
* **🏦 Account Diversity:**
  * **Checking Account (Conta Corrente):** Supports overdraft limits and daily withdrawal caps with automatic date-based limit resets.
  * **Savings Account (Conta Poupança):** Supports periodic interest yield applications on positive balances.
* **💸 Atomic Financial Operations:**
  * **Deposits & Withdrawals:** Enforces positive amount constraints and overdraft/limit validation.
  * **Pix / Wire Transfers:** Implements atomic `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK` database operations for safe inter-account fund transfers.
  * **Savings Yield:** Computes and applies compound interest yield.
* **📜 Transaction History & Statements:** Complete audit logging stored in SQLite and formatted for console display.
* **💾 Local Persistence:** Auto-initializes and syncs state to `fesisbank_users.db`.

---

## 🛠️ Tech Stack

* **Language:** Python 3.8+
* **Database:** SQLite 3 (`sqlite3` standard library module)
* **Security:** `hashlib` (SHA-256 with salt)
* **Testing:** `unittest` standard library framework

---

## 🏛️ System Architecture & OOP Design

The codebase strictly adheres to core OOP principles:

```
[ Domain Models (models.py) ] <---> [ Service Layer (banking_service.py) ] <---> [ Persistence (db.py) ]
                                                ^
                                                |
                                    [ Interactive CLI (main.py) ]
```

* **Abstraction:** Abstract base classes `Cliente`, `Conta`, and `Transacao`.
* **Encapsulation:** Protected properties (`_saldo`, `_numero`, `_historico`) for transactional state integrity.
* **Inheritance:** `ContaCorrente` and `ContaPoupanca` extend `Conta`; `PessoaFisica` extends `Cliente`.
* **Polymorphism:** Unified `registrar()` contract across `Deposito`, `Saque`, `Transferencia`, and `Rendimento`.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.8 or higher installed on your system.
* No external third-party packages (`pip`) required.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Fesisp/Python-Banking-System.git
   cd Python-Banking-System
   ```

2. **Run the CLI application:**
   ```bash
   python main.py
   ```
   *(The database file `fesisbank_users.db` will be created automatically on first run).*

---

## 💡 Usage

Launch the CLI interface to interact with the system:

```text
============================================================
🏦               FESISBANK - DIGITAL BANK               🏦
============================================================

[1] 👤 Register New Customer
[2] 🔐 Login
[3] 📋 List All Accounts (Admin Overview)
[4] ℹ️  About Fesisbank
[5] 🚪 Exit
------------------------------------------------------------
Select an option => 
```

### Main CLI Workflows

1. **Customer Registration:** Enter CPF, full name, birth date, address, phone number, and account password.
2. **Account Opening:** Choose between Checking Account (*Conta Corrente*) or Savings Account (*Conta Poupança*).
3. **Banking Dashboard:** Perform deposits, withdrawals, Pix transfers to other accounts, view statements, or apply savings yield.

---

## 🧪 Running Automated Tests

Run the comprehensive unit test suite to verify business logic, database migrations, and transaction atomicity:

```bash
python -m unittest test_banking_system.py
```

```text
Ran 6 tests in 0.116s

OK
```

---

## 📂 Project Structure

```text
Python-Banking-System/
├── main.py                 # Interactive CLI interface & menu navigation
├── banking_service.py      # Business logic & database operations layer
├── models.py               # OOP domain models (Users, Accounts, Transactions)
├── db.py                   # SQLite connection manager & schema initializer
├── fesisbank_users.db      # SQLite database file (Auto-generated)
├── test_banking_system.py  # Unit test suite using unittest
├── requirements.txt        # Dependency statement (Standard Library only)
└── README.md               # Project documentation
```

---

## 👤 Author

Developed and maintained by **Felipe da Silva Spinola ([Fesisp](https://github.com/Fesisp))**.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
