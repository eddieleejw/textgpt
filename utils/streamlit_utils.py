import streamlit as st
import os

def db_error_check(new_data_directory, session_state):
    if not os.path.exists(new_data_directory):
        st.error("New data directory does not exist")
        return False
    elif not os.listdir(new_data_directory):
        st.error("New data directory is empty")
        return False
    elif not session_state["db_project"]:
        st.error("Project not specified")
        return False
    elif not session_state["openai_api_key"]:
        st.error("Please enter an OpenAI API key")
        return False
    
    return True