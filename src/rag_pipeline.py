from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
# To avoid deprecation warnings, install and import from the recommended package:
# pip install -U langchain-community langchain-openai
from langchain.llms import OpenAI  
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Construct an absolute path to your database file.
# Replace the path below with the actual absolute path to your bank.db file.
db = SQLDatabase.from_uri("sqlite:///../data/bank.db")

# Initialize your language model.
llm = OpenAI(api_key=api_key, temperature=0)

# Create the SQL query chain for generating SQL from natural language.
sql_chain = create_sql_query_chain(llm, db)

def run_query(question: str):
    """Generates a SELECT SQL query from natural language and executes it."""
    try:
        generated_query = sql_chain.invoke({"question": question})
        print(f"Generated SQL:\n{generated_query}\n")
        with db._engine.connect() as conn:
            result = conn.execute(generated_query)
            rows = result.fetchall()
        return rows
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def run_write_operation(instruction: str):
    """
    Generates a write operation SQL query (e.g., UPDATE, INSERT, DELETE) from natural language,
    and executes it. **Caution:** Validate and confirm operations in a production setting.
    """
    try:
        generated_query = sql_chain.invoke({"question": instruction})
        print(f"Generated Write Query:\n{generated_query}\n")
        # Confirm before executing a write operation.
        confirm = input("Do you want to execute this write operation? (yes/no): ")
        if confirm.lower() != "yes":
            print("Write operation cancelled.")
            return

        with db._engine.connect() as conn:
            trans = conn.begin()  # Start a transaction
            conn.execute(generated_query)
            trans.commit()
        print("Write operation successful.")
    except Exception as e:
        print(f"Error during write operation: {e}")

if __name__ == "__main__":
    # Example SELECT query
    query_text = "Show me all customers with a savings account balance above 5000"
    rows = run_query(query_text)
    if rows is not None:
        print("Query Results:")
        for row in rows:
            print(row)

    # Example write operation (for demonstration purposes only)
    # e.g., "Increase the balance of account 1 by 200"
    write_instruction = "Increase the balance of account with account_id 1 by 200"
    run_write_operation(write_instruction)
