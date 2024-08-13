'''
use command:

python query.py {project_name} query/prompt {query}
'''


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



def query_chatbot(query, db, docstore, llm):


    # get relevant summaries
    query_docs = db.similarity_search(query)

    # get original documents
    source_docs = []
    for doc in query_docs:
        source_docs.append(docstore[doc.metadata['doc_id']])

    prompt = "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.\
    Question: {question}\
    Context: {context}\
    Answer:"

    context = " ".join([doc.page_content for doc in source_docs])


    prompt_template = PromptTemplate.from_template(prompt)

    chain = (prompt_template | llm | StrOutputParser())

    answer = chain.invoke({"question" : query, "context" : context})

    sources = [doc.metadata['source'] for doc in source_docs]

    return answer, sources

def load_db(db_dir, embedding_function):

    with open(f"{db_dir}/docstore.pkl", "rb") as f:
        docstore = pickle.load(f)

    db = Chroma(persist_directory=f"{db_dir}/chroma_db", embedding_function=embedding_function)

    return db, docstore

def save_answer_and_sources(answer_path, query, answer, sources):

    with open(answer_path, "w") as f:
        f.write("# Query:\n")
        f.write(query)
        f.write("\n\n")

        f.write("# Answer:\n")
        f.write(answer)
        f.write("\n\n")

        f.write("## Sources:\n")
        for s in sources:
            f.write(f"* {s}\n")


def get_prompt(query, db, docstore):
    # get relevant summaries
    query_docs = db.similarity_search(query)

    # get original documents
    source_docs = []
    for doc in query_docs:
        source_docs.append(docstore[doc.metadata['doc_id']])

    prompt = "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.\
    Question: {question}\
    Context: {context}\
    Answer:"

    context = " ".join([doc.page_content for doc in source_docs])


    prompt_template = PromptTemplate.from_template(prompt)

    prompt = prompt_template.invoke({"question" : query, "context" : context})

    sources = [doc.metadata['source'] for doc in source_docs]

    return prompt.text, sources

def copy_prompt(prompt, sources):
    pyperclip.copy(prompt)
    print("Prompt copied to clipboard\n")
    print("Sources:")
    for s in sources:
        print(f"{s}")

def print_answer(answer, sources, answer_path):

    print("==========================")
    print("Answer:")
    print(answer)
    print("\n\n")

    print("==========================")
    print("Sources:")
    for s in sources:
        print(s)
    print("\n\n")

    print(f"Saved to {answer_path}")

if __name__ == "__main__":

    os.environ["OPENAI_API_KEY"] = input("What is your OpenAI API key?")

    embedding_function = OpenAIEmbeddings()
    llm = ChatOpenAI(model = "gpt-4o-mini")

    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=str, help="Name of the db directory e.g. 'online_rl'")
    parser.add_argument("type", type=str, help="Specify whether to get full answer (query) or just copy prompt (prompt)")
    parser.add_argument('query', type=str, help="Query for chatbot to answer")
    args = parser.parse_args()

    root_dir = f"dbs/{args.project}"
    db_dir = f"{root_dir}/db"

    if args.type == "query":
        answer_path = f"{root_dir}/answers/{str(uuid.uuid4())}.md"
        os.makedirs(f"{root_dir}/answers", exist_ok=True)

        db, docstore = load_db(db_dir, embedding_function)
        answer, sources = query_chatbot(args.query, db, docstore, llm)
        save_answer_and_sources(answer_path, args.query, answer, sources)

        print_answer(answer, sources, answer_path)

    elif args.type == "prompt":
        db, docstore = load_db(db_dir, embedding_function)
        prompt, sources = get_prompt(args.query, db, docstore)
        copy_prompt(prompt, sources)
    else:
        print("No such type. Enter either 'query' or 'prompt'")