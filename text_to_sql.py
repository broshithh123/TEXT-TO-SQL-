import streamlit as st
import sqlite3
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.sql_database import SQLDatabase
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool
from sqlalchemy import create_engine
import os
import tempfile

api_key = ""

with open("key.txt", "r") as file:
    api_key = file.read()

# Initialize Streamlit session state for messages and file paths
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "temp_file_path" not in st.session_state:
    st.session_state["temp_file_path"] = None
if "temp_db_path" not in st.session_state:
    st.session_state["temp_db_path"] = None

# Streamlit UI Title
st.title("SQL Query Bot with Google Generative AI")

# Function to display chat messages
def display_chat_messages():
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Function to clean up temporary files
def cleanup_temp_files():
    if st.session_state["temp_file_path"] and os.path.exists(st.session_state["temp_file_path"]):
        try:
            os.unlink(st.session_state["temp_file_path"])
            st.session_state["temp_file_path"] = None
        except PermissionError:
            pass
    if st.session_state["temp_db_path"] and os.path.exists(st.session_state["temp_db_path"]):
        try:
            os.unlink(st.session_state["temp_db_path"])
            st.session_state["temp_db_path"] = None
        except PermissionError:
            pass

# Call cleanup function
cleanup_temp_files()

# File uploader for SQLite database or SQL file
uploaded_file = st.file_uploader("Choose a SQLite database file or SQL file", type=["db", "sqlite", "sql"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
        temp_file.write(uploaded_file.read())
        st.session_state["temp_file_path"] = temp_file.name

    if file_extension in ['db', 'sqlite']:
        # For SQLite database files
        engine = create_engine(f"sqlite:///{st.session_state['temp_file_path']}")
    elif file_extension == 'sql':
        # For SQL files, create a new SQLite database and execute the script
        st.session_state["temp_db_path"] = tempfile.NamedTemporaryFile(delete=False, suffix='.db').name
        engine = create_engine(f"sqlite:///{st.session_state['temp_db_path']}")
        
        with open(st.session_state["temp_file_path"], 'r') as sql_file:
            sql_script = sql_file.read()
        
        with engine.connect() as conn:
            conn.executescript(sql_script)
    else:
        st.error("Unsupported file type")
        st.stop()

    # Initialize SQLDatabase and QuerySQLDataBaseTool
    db = SQLDatabase(engine)
    query_tool = QuerySQLDataBaseTool(db=db)

    # Define prompt template for SQL query generation
    sql_prompt = PromptTemplate(
        input_variables=["input"],
        template="""
        Given an input question, create a syntactically correct SQL query to retrieve the requested information.
        
        Question: {input}
        SQL Query:
        """,
    )

    # Initialize LLMChain with Google Generative AI model for SQL query generation
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key = api_key, temperature=0.5)
    sql_chain = LLMChain(llm=llm, prompt=sql_prompt)

    def generate_and_execute_query(question):
        # Generate the SQL query
        sql_query = sql_chain.run(question)
        sql
        # Execute the query and get the result
        try:
            result = query_tool.run(sql_query)
            return f"Query: {sql_query}\nResult: {result}"
        except Exception as e:
            return f"Error executing query: {str(e)}\nQuery attempted: {sql_query}"

    # Chat input for user query
    if user_query := st.chat_input("Enter your question or query:"):
        st.session_state["messages"].append({"role": "user", "content": user_query})
        display_chat_messages()

        response = generate_and_execute_query(user_query)

        st.session_state["messages"].append({"role": "assistant", "content": response})
        display_chat_messages()

else:
    st.warning("Please upload a SQLite database file (.db/.sqlite) or SQL file (.sql) to begin.")
