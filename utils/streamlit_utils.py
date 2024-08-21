from langchain_openai import ChatOpenAI
import streamlit as st
import os
from utils.db_utils import create_document_data, db_update, load_db_and_artifcats, save_artifacts
from utils.doc_utils import uploaded_files_to_doc
from utils.generate_qna_utils import load_contents, generate_qna, process_text
from langchain_core.documents import Document
import shutil

def db_error_check(session_state):
    if not session_state["uploaded_files"]:
        st.error("No files uploaded")
        return False
    elif not session_state["db_project"]:
        st.error("Project not specified")
        return False
    elif not session_state["openai_api_key"]:
        st.error("Please enter an OpenAI API key")
        return False
    
    return True


def print_bertscores(bertscores_dict):
    for score_type in ["p", "r", "f1"]:

        
        if score_type == "p":
            score_type_long = "Precision"
        elif score_type == "r":
            score_type_long = "Recall"
        else:
            score_type_long = "F1 score"

        st.write(f"{score_type_long}: Mean = {bertscores_dict[score_type]["mean"]:.2f} (std = {bertscores_dict[score_type]["std"]:.2f})")

        # st.write(f"Mean: {bertscores_dict[score_type]["mean"]:.2f}")
        # st.write(f"Std: {bertscores_dict[score_type]["std"]:.2f}")
        # st.write(f"Max: {bertscores_dict[score_type]["max"]:.2f}")
        # st.write(f"Min: {bertscores_dict[score_type]["min"]:.2f}")
        # st.write("\n\n")

def generate_qna_streamlit(contents_directory):

    if not os.path.exists(contents_directory):
        st.error("Given directory does not exist")
        st.stop()

    contents = load_contents(contents_directory)

    llm = ChatOpenAI(model = "gpt-4o-mini")

    qnas = generate_qna(contents, llm)
    qa_pairs = process_text(qnas)
    return qa_pairs


def rescan_projects(session_state):
    available_projects = []

    # make dbs directory if it DNE
    if not os.path.exists("dbs"):
        os.makedirs("dbs", exist_ok=True)

    for file_name in os.listdir("dbs"):
        if file_name not in [".DS_Store"]:
            available_projects.append(file_name)
    
    session_state["available_projects"] = tuple(available_projects)


def write_uploaded_files_to_disk(uploaded_files, dir):

    os.makedirs(dir)

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_value = uploaded_file.getvalue()

        with open(f"{dir}/{file_name}", "wb") as f:
            f.write(file_value)

            print(f"DEBUG: writing to {dir}/{file_name}")

def cleanup_uploaded_files(dir):
    shutil.rmtree(dir)