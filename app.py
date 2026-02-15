import streamlit as st
from pathlib import Path #Helps work with file paths in a platform-independent way
from langchain_community.agent_toolkits.sql.base import create_sql_agent #to build an agent that can query SQL databases
from langchain_community.utilities import SQLDatabase #Wrapper class that lets LangChain interact with SQL databases.
from langgraph.prebuilt import create_react_agent
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler #Handles streaming token-by-token output from the LLM to stdout
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine #SQLAlchemy engine lets Python connect to SQL databases.
import sqlite3
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
import os
os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="LangChain: Chat with SQL DB")
st.title("LangChain: Chat with SQL DB")

INJECTION_WARNING="""
                  SQL agent can be vulnerable to prompt injection.
                  Use a DB role with limited permissions.
                  """
#Constants used to identify database type.
LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_opt=["use SQLite 3 Database-Student.db","Connect to your MySQL Database"]
selected_opt=st.sidebar.radio(label="Choose the db which you want to chat with",options=radio_opt)

if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("Provide MySQL Host")
    mysql_user=st.sidebar.text_input("MySQL User")
    mysql_password=st.sidebar.text_input("MySQL password",type="password")
    mysql_db=st.sidebar.text_input("MySQL Database")
else:
    db_uri=LOCALDB

api_key=st.sidebar.text_input(label="Groq API Key",type="password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please enter your Groq API Key")

##LLM model
llm=ChatGroq(groq_api_key=api_key,model_name="llama-3.3-70b-versatile",streaming=True)
#Caches DB connection for 2 hours
#Prevents reconnecting on every refresh
@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri==LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute() #Gets absolute path of student.db
        creator=lambda:sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True) #Connects in read-only mode
        return SQLDatabase(create_engine("sqlite:///",creator=creator)) #Wraps database into LangChain SQLDatabase
    elif db_uri==MYSQL:
        if not(mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db=configure_db(db_uri)


##toolkit  
toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent="zero-shot-react-description"
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"]=[{"role":"assistant","content":"How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamingStdOutCallbackHandler()
        response=agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)

 
