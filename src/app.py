import streamlit as st
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
# To avoid deprecation warnings, consider using the recommended packages:
# pip install -U langchain-community langchain-openai
from langchain.llms import OpenAI  
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Construct the absolute path to your SQLite database file.
db = SQLDatabase.from_uri("sqlite:///../data/bank.db")

# Initialize your language model.
llm = OpenAI(api_key=api_key, temperature=0)

# Create the SQL query chain.
sql_chain = create_sql_query_chain(llm, db)

# --- Helper Functions ---
def run_query(question: str):
    try:
        generated_query = sql_chain.invoke({"question": question})
        st.write("**Generated SQL:**")
        st.code(generated_query)
        with db._engine.connect() as conn:
            result = conn.execute(generated_query)
            rows = result.fetchall()
        return rows
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

def run_write_operation(instruction: str):
    try:
        generated_query = sql_chain.invoke({"question": instruction})
        st.write("**Generated Write Query:**")
        st.code(generated_query)
        if st.button("Confirm Write Operation"):
            with db._engine.connect() as conn:
                trans = conn.begin()
                conn.execute(generated_query)
                trans.commit()
            st.success("Write operation successful.")
            return "Write operation executed successfully."
        else:
            st.info("Waiting for confirmation...")
            return None
    except Exception as e:
        st.error(f"Error during write operation: {e}")
        return None

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_write" not in st.session_state:
    st.session_state.pending_write = None

st.title("Bank SQL Chatbot")
st.write("Interact with the bank database using natural language.")

operation = st.radio("Select Operation", ["Query", "Write Operation"])

st.markdown("### Chat History")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**User:** {msg['message']}")
    else:
        st.markdown(f"**Bot:** {msg['message']}")

user_input = st.text_input("Enter your instruction:")

if st.button("Send"):
    if user_input:
        st.session_state.messages.append({"role": "user", "message": user_input})
        if operation == "Query":
            rows = run_query(user_input)
            if rows is not None:
                response = "**Query Results:**\n"
                if rows:
                    for row in rows:
                        response += f"- {row}\n"
                else:
                    response += "No results found."
                st.session_state.messages.append({"role": "bot", "message": response})
        else:  # Write Operation
            generated_write = run_write_operation(user_input)
            st.session_state.messages.append({"role": "bot", "message": "Write query generated. Use the confirmation button above to execute."})
        # No explicit st.experimental_rerun() here
