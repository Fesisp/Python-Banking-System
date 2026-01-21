# Banking System with OOP & SQLite 🏦

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Status-Completed-success)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A robust console-based banking application that demonstrates the practical application of **Object-Oriented Programming (OOP)** and **SQL Database Persistence**.

## 📋 Project Overview

This project was developed to simulate core banking operations in a secure and structured environment. Unlike simple scripts, this system implements a full user lifecycle (Registration -> Login -> Transaction) and persists all data to a local **SQLite database**, ensuring that records are maintained even after the application closes.

It serves as a reference implementation for:
* **Class-based Architecture** (User, Account, Transaction classes).
* **Database Management** using raw SQL queries within Python.
* **Secure Authentication** logic.

## ✨ Key Features

* **🔐 User Authentication:** Secure Login and Registration system preventing unauthorized access.
* **💸 Core Transactions:** Perform Deposits, Withdrawals, and Transfers between accounts.
* **📜 Statement History:** View detailed transaction logs retrieved directly from the database.
* **💾 Data Persistence:** Automatic saving of users and balances using `sqlite3`.
* **🛡️ Error Handling:** Validations for insufficient funds, negative values, and invalid user inputs.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Database:** SQLite3 (Standard Library)
* **Paradigm:** Object-Oriented Programming (OOP)

## 🚀 How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Fesisp/python-banking-system.git](https://github.com/Fesisp/python-banking-system.git)
    cd python-banking-system
    ```

2.  **Run the application:**
    ```bash
    python main.py
    ```
    *(The database file `fesisbank_users.db` will be created/connected automatically)*.

3.  **Follow the on-screen menu:**
    * Select **[1]** to Register a new user.
    * Select **[2]** to Login and access banking features.

## 📂 Project Structure

```text
python-banking-system/
├── main.py              # Application entry point and logic
├── fesisbank_users.db   # SQLite Database file (Auto-generated)
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```
## 👤 Autor

Felipe da Silva Spinola
Projeto desenvolvido por [Fesisp](https://github.com/Fesisp).
