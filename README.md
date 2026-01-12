# Banking-Management-System-DB-Project

🏦 FinFlow Pro – Core Banking System (Database Course Project)

FinFlow Pro is a Core Banking System (CBS) developed as part of a Database Systems course project. The project demonstrates the practical implementation of database concepts, transactions, and GUI-based application development using Python, PyQt5, and MySQL.

The system supports Admin and Customer modes, enabling secure banking operations such as account management, deposits, withdrawals, fund transfers, and transaction history tracking, all backed by a relational database.

# 🚀 Features

🔐 Authentication

Admin login

Customer login

Role-based access control

👨‍💼 Admin Module

Manage customers

Manage bank accounts

Monitor transactions

Maintain audit logs

👤 Customer Module

View account details

Deposit money

Withdraw money

Transfer funds to other accounts

View transaction history with filters

📊 Database Functionality

Relational schema with proper normalization

Use of primary keys & foreign keys

Transaction management

Audit logging for database operations

🖥️ User Interface

Desktop GUI built using PyQt5

Modern, responsive design

Light and dark theme support

# 🗄️ Database Schema

The database schema is provided in a separate .txt file and includes tables such as:

Customer

Account

Transaction

AppUser

AuditLog

Related constraints (PK, FK, relationships)

This schema reflects real-world banking database design principles.

# 🛠️ Technologies Used
Programming & Tools

Python 3

PyQt5 (GUI)

MySQL

MySQL Connector for Python

Database Concepts Implemented

ER Modeling

Normalization

Transactions

Constraints (Primary Key, Foreign Key)

Audit Logging

# 📂 Project Structure
📁 FinFlow-Pro-CBS

 ├── BankSystem.py        # Main Python application (GUI + DB logic)
 
 ├── database_schema.sql # Database schema & table structure
 
 └── README.md           # Project documentation

# ⚙️ Requirements
Software

Python 3.x

MySQL Server

MySQL Workbench (optional)

Python Libraries
PyQt5
mysql-connector-python


Install dependencies using:

pip install PyQt5 mysql-connector-python

# ▶️ How to Run

Create the database in MySQL using the provided schema file.

Update database credentials in BankSystem.py.

Run the application:

python BankSystem.py

# 🎓 Academic Purpose

This project is developed strictly for educational purposes to demonstrate database design, implementation, and integration with a Python-based application.
