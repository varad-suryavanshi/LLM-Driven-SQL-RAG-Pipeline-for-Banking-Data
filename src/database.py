# src/database.py
import sqlite3

def create_connection(db_file="../data/bank.db"):
    conn = sqlite3.connect(db_file)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            address TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            account_type TEXT,
            balance REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            account_id INTEGER,
            date TEXT,
            amount REAL,
            transaction_type TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and tables created.")
