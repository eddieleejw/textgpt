'''
all functions in this file are concerned with making `doc` files, which have form:

[
    {'page_content' : ..., 'source' : ...},
    {'page_content' : ..., 'source' : ...},
    ...
]
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


def pdf_to_doc(directory):
    pdf_paths = []

    for file_name in os.listdir(directory):
        if file_name.endswith(".pdf"):
            pdf_file = os.path.join(directory, file_name)
            pdf_paths.append((pdf_file, file_name))

    docs = []
    for pdf_file, file_name in tqdm.tqdm(pdf_paths):
        loader = UnstructuredPDFLoader(pdf_file)
        pages = loader.load_and_split()
        for page in pages:
            # docs.append({'page_content' : page.page_content, 'metadata' : {'source' : file_name}})
            docs.append({'page_content' : page.page_content, 'source' : file_name})

    print(f"Generated {len(docs)} chunks")

    return docs

def txt_to_doc(directory):
    txt_paths = []

    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            txt_file = os.path.join(directory, file_name)
            txt_paths.append((txt_file, file_name))
    
    docs = []
    for txt_file, file_name in tqdm.tqdm(txt_paths):
        loader = TextLoader(txt_file)
        pages = loader.load_and_split()
        for page in pages:
            docs.append({'page_content' : page.page_content, 'source' : file_name})

    print(f"Generated {len(docs)} chunks")

    return docs

def pdf_txt_to_doc(directory):
    txt_paths = []
    pdf_paths = []

    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            txt_file = os.path.join(directory, file_name)
            txt_paths.append((txt_file, file_name))
        elif file_name.endswith(".pdf"):
            pdf_file = os.path.join(directory, file_name)
            pdf_paths.append((pdf_file, file_name))

    
    docs = []

    for pdf_file, file_name in tqdm.tqdm(pdf_paths):
        loader = UnstructuredPDFLoader(pdf_file)
        pages = loader.load_and_split()
        for page in pages:
            docs.append({'page_content' : page.page_content, 'source' : file_name})

    for txt_file, file_name in tqdm.tqdm(txt_paths):
        loader = TextLoader(txt_file)
        pages = loader.load_and_split()
        for page in pages:
            docs.append({'page_content' : page.page_content, 'source' : file_name})

    print(f"Generated {len(docs)} chunks")

    return docs

if __name__ == "__main__":
    docs = pdf_txt_to_doc("dbs/lookahead/data/new_data")

    with open("temp.txt", "w") as f:
        for doc in docs:
            f.write(f"Source: {doc['source']}\n\n{doc['page_content']}")
            f.write("\n\n=================================\n\n")
            print(len(doc['page_content']))