# src/generate_data.py
from faker import Faker
import random
import sqlite3

fake = Faker()

def populate_data():
    conn = sqlite3.connect("../data/bank.db")
    c = conn.cursor()

    # Insert synthetic customers, accounts, and transactions
    for _ in range(50):
        name = fake.name()
        age = random.randint(18, 90)
        address = fake.address().replace("\n", ", ")
        c.execute("INSERT INTO customers (name, age, address) VALUES (?, ?, ?)", (name, age, address))
        customer_id = c.lastrowid

        # Create 1-3 accounts per customer
        for _ in range(random.randint(1, 3)):
            account_type = random.choice(["Checking", "Savings"])
            balance = round(random.uniform(100, 10000), 2)
            c.execute("INSERT INTO accounts (customer_id, account_type, balance) VALUES (?, ?, ?)",
                      (customer_id, account_type, balance))
            account_id = c.lastrowid

            # Create transactions
            for _ in range(random.randint(1, 5)):
                date = fake.date_this_year().isoformat()
                amount = round(random.uniform(-500, 500), 2)
                transaction_type = "credit" if amount >= 0 else "debit"
                c.execute("INSERT INTO transactions (account_id, date, amount, transaction_type) VALUES (?, ?, ?, ?)",
                          (account_id, date, amount, transaction_type))
    
    conn.commit()
    conn.close()
    print("Data populated successfully.")

if __name__ == "__main__":
    populate_data()
