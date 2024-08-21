import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import os
import uuid
from utils.query_utils import load_db, query_chatbot
from utils.db_utils import add_data_to_db, data_to_db, add_uploaded_files_to_db, uploaded_files_to_db
from utils.streamlit_utils import cleanup_uploaded_files, db_error_check, print_bertscores, generate_qna_streamlit, rescan_projects, write_uploaded_files_to_disk
from utils.evaluation_utils import evaluate_bertscore
import uuid


# read in available projects once
if "available_projects" not in st.session_state:
    # available_projects = []

    # for file_name in os.listdir("dbs"):
    #     if file_name not in [".DS_Store"]:
    #         available_projects.append(file_name)
    
    # st.session_state["available_projects"] = tuple(available_projects)
    rescan_projects(st.session_state)
    


st.title("TextGPT")

st.session_state["openai_api_key"] = st.text_input("OpenAI API key here")
os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]

st.divider()



st.header("Build")

st.session_state["db_type"] = st.selectbox("Database operation", ["Build new", "Update existing"])

# st.session_state["db_data_path"] = st.text_input("Path to new data directory")
st.session_state["uploaded_files"] = st.file_uploader("Upload files to build/update database", accept_multiple_files = True)

if st.session_state["db_type"] == "Update existing":
    st.session_state["db_project"] = st.selectbox("Select project", st.session_state["available_projects"], key = "1")

    if st.button("Rescan projects", type = "primary", key = "2"):
        rescan_projects(st.session_state)
        st.rerun()
    
    
else:
    st.session_state["db_project"] = st.text_input("Name of project")





root_dir = f"dbs/{st.session_state["db_project"]}"

if st.session_state["db_type"] == "Update existing":
    st.write(f"NOTE: Existing database must be at`{root_dir}/db`")
else:
    st.write(f"NOTE: Writing database to `{root_dir}/db`")


if st.button("Go!"):

    if db_error_check(st.session_state):

        # write the uploaded files to temporary storage
        temp_data_dir = "f8d0ca0"
        if os.path.exists(temp_data_dir):
            cleanup_uploaded_files(temp_data_dir)
        write_uploaded_files_to_disk(st.session_state["uploaded_files"], temp_data_dir)


        if st.session_state["db_type"] == "Update existing":
            with st.spinner("Updating database..."):
                # add_uploaded_files_to_db(
                #     db_dir = f"{root_dir}/db",
                #     embedding_function = OpenAIEmbeddings(),
                #     uploaded_files = st.session_state["uploaded_files"],
                #     llm = ChatOpenAI(model="gpt-4o-mini")
                # )
                add_data_to_db(
                    db_dir = f"{root_dir}/db",
                    embedding_function = OpenAIEmbeddings(),
                    new_data_directory= temp_data_dir,
                    llm = ChatOpenAI(model="gpt-4o-mini")
                )
            st.success("Database updated!")
        else:
            with st.spinner("Creating database..."):
                # uploaded_files_to_db(
                #     uploaded_files = st.session_state["uploaded_files"],
                #     embedding_function = OpenAIEmbeddings(), 
                #     llm = ChatOpenAI(model="gpt-4o-mini"), 
                #     save_dir = f"{root_dir}/db"
                # )

                data_to_db(
                    new_data_directory=temp_data_dir,
                    embedding_function = OpenAIEmbeddings(), 
                    llm = ChatOpenAI(model="gpt-4o-mini"), 
                    save_dir = f"{root_dir}/db"
                )

            st.success("Database created!")

        # clean up temp storage
        cleanup_uploaded_files(temp_data_dir)
    

st.divider()


st.header("Evaluate")

st.session_state["query_project"] = st.selectbox("Select project", st.session_state["available_projects"], key = "4")
if st.button("Rescan projects", type = "primary", key = "7"):
    rescan_projects(st.session_state)
    st.rerun()
# st.session_state["eval_data_path"] = st.text_input("Specify path to directory holding evaluation data. The chatbot will be evaluated on its performance on these documents. It is recommended to evaluate on the documents the chatbot was trained on.")
st.session_state["eval_uploaded_files"] = st.file_uploader("Upload files to evaluate database", accept_multiple_files = True)
st.session_state["eval_number"] = st.text_input("How many evaluation data points to use. Higher yields more accurate results but will take longer and use more API requests. Leave blank to use all available data")

if st.button("Go!", key = "5"):
    if st.session_state["openai_api_key"] == "":
        st.error("Please enter an OpenAI API key")
        st.stop()
    elif st.session_state["query_project"] == "":
        st.error("Please enter a project")
        st.stop()
    elif not os.path.exists(f"dbs/{st.session_state['query_project']}/db"):
        st.error(f"Could not find database (expected at `dbs/{st.session_state['query_project']}/db`)")
        st.stop()
    
    if not os.path.exists(f"dbs/{st.session_state['query_project']}/db/chroma_db") or not os.path.exists(f"dbs/{st.session_state['query_project']}/db/docstore.pkl") or not os.path.exists(f"dbs/{st.session_state['query_project']}/db/document_data.pkl"):
        st.error("Database missing files:")
        if not os.path.exists(f"dbs/{st.session_state['query_project']}/db/chroma_db"):
            st.error(f"missing directory `dbs/{st.session_state['query_project']}/db/chroma_db`")
        
        if not os.path.exists(f"dbs/{st.session_state['query_project']}/db/docstore.pkl"):
            st.error(f"missing file `dbs/{st.session_state['query_project']}/db/docstore.pkl`")
        
        if not os.path.exists(f"dbs/{st.session_state['query_project']}/db/document_data.pkl"):
            st.error(f"missing file `dbs/{st.session_state['query_project']}/db/document_data.pkl`")

        st.stop()
    
    

    with st.spinner("Generating evaluation dataset"):

        temp_eval_data_dir = "1def5f1b"
        if os.path.exists(temp_eval_data_dir):
            cleanup_uploaded_files(temp_eval_data_dir)
        write_uploaded_files_to_disk(st.session_state["eval_uploaded_files"], temp_eval_data_dir)

        embedding_function = OpenAIEmbeddings()
        llm = ChatOpenAI(model = "gpt-4o-mini")

        qa_pairs = generate_qna_streamlit(temp_eval_data_dir)
        cleanup_uploaded_files(temp_eval_data_dir)


    with st.spinner("Evaluating"):

        embedding_function = OpenAIEmbeddings()
        llm = ChatOpenAI(model = "gpt-4o-mini")

        db, docstore = load_db(f"dbs/{st.session_state['query_project']}/db", embedding_function)

        if st.session_state["eval_number"] == "":
            n = len(qa_pairs)
        else:
            n = int(st.session_state["eval_number"])

        bertscores_dict = evaluate_bertscore(db, docstore, llm, qa_pairs = qa_pairs, n = n)

        print_bertscores(bertscores_dict)



st.divider()

st.header("Query")



# st.session_state["project"] = st.text_input("Project here")
st.session_state["query_project"] = st.selectbox("Select project", st.session_state["available_projects"], key = "3")
if st.button("Rescan projects", type = "primary", key = "6"):
    rescan_projects(st.session_state)
    st.rerun()

st.session_state["query"] = st.text_input("Query here")

# if st.button("Display"):
#     st.write("openai_api_key" in st.session_state)
#     st.write("project" in st.session_state)
#     st.write("query" in st.session_state)

if st.button("Go!", key = "8"):
    if st.session_state["openai_api_key"] == "":
        st.error("Please enter an OpenAI API key")
        st.stop()
    elif st.session_state["query_project"] == "":
        st.error("Please enter a project")
        st.stop()
    elif st.session_state["query"] == "":
        st.error("Please enter a query")
        st.stop()
    

    with st.spinner("Running"):

        embedding_function = OpenAIEmbeddings()
        llm = ChatOpenAI(model = "gpt-4o-mini")


        root_dir = f"dbs/{st.session_state["query_project"]}"
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
        
