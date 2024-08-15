import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate
from IPython.display import display, Image, Markdown
from langchain_core.documents import Document
import os
import tqdm
import uuid
import pickle
import argparse
import pyperclip
from query import load_db, query_chatbot

# read in available projects once
if "available_projects" not in st.session_state:
    st.write("Adding available projects...")

    available_projects = []

    for file_name in os.listdir("dbs"):
        if file_name not in [".DS_Store"]:
            available_projects.append(file_name)
    
    st.session_state["available_projects"] = tuple(available_projects)
    


st.title("TextGPT")

st.session_state["openai_api_key"] = st.text_input("OpenAI API key here")

# st.session_state["project"] = st.text_input("Project here")
st.session_state["project"] = st.selectbox("Select project", st.session_state["available_projects"])

st.session_state["query"] = st.text_input("Query here")

st.button("Reset", type = "primary")

# if st.button("Display"):
#     st.write("openai_api_key" in st.session_state)
#     st.write("project" in st.session_state)
#     st.write("query" in st.session_state)

if st.button("Run"):
    if st.session_state["openai_api_key"] == "":
        st.write("Please enter an OpenAI API key")
        st.stop()
    elif st.session_state["project"] == "":
        st.write("Please enter a project")
        st.stop()
    elif st.session_state["query"] == "":
        st.write("Please enter a query")
        st.stop()
    

    with st.spinner("Running"):

        os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]

        embedding_function = OpenAIEmbeddings()
        llm = ChatOpenAI(model = "gpt-4o-mini")


        root_dir = f"dbs/{st.session_state["project"]}"
        db_dir = f"{root_dir}/db"

        # check if db exists
        if not os.path.exists(root_dir):
            st.error(f"Project does not exist, or is in the incorrect location. Make sure that the project exists and has path `{root_dir}`")
            st.stop()
        elif not os.path.exists(db_dir):
            st.error(f"Database does not exist, or is in the incorrect location. Make sure that the database exists and has path `{db_dir}`")
            st.stop()

        answer_path = f"{root_dir}/answers/{str(uuid.uuid4())}.md"
        os.makedirs(f"{root_dir}/answers", exist_ok=True)

        db, docstore = load_db(db_dir, embedding_function)

        try:
            answer, sources = query_chatbot(st.session_state["query"], db, docstore, llm)
        except:
            st.error("Unable to generate answer. Please check OpenAI API key, or try again later")
            st.stop()

        st.header("Answer:")
        st.markdown(answer)

        st.header("Sources:")
        for s in sources:
            st.write(s)
        