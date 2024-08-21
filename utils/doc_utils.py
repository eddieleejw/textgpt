'''
all functions in this file are concerned with making `doc` files, which have form:

[
    {'page_content' : ..., 'source' : ...},
    {'page_content' : ..., 'source' : ...},
    ...
]
'''

from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
import os
import tqdm
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

    # print(f"Generated {len(docs)} chunks")

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

    # print(f"Generated {len(docs)} chunks")

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

    # print(f"Generated {len(docs)} chunks")

    return docs


def pkl_to_doc(directory):
    '''
    Note: will automatically split documents that are too long
    '''

    splitter = RecursiveCharacterTextSplitter()

    pkl_paths = []

    for file_name in os.listdir(directory):
        if file_name.endswith(".pkl"):
            pkl_file = os.path.join(directory, file_name)
            pkl_paths.append(pkl_file)

    docs = []

    for pkl_file in tqdm.tqdm(pkl_paths):
        with open(pkl_file, "rb") as f:
            temp_docs = pickle.load(f)

        # split docs
        for doc in temp_docs:
            page_content = doc['page_content']

            split_texts = splitter.split_text(page_content)

            for text in split_texts:
                docs.append({'page_content': text, 'source': doc['source']})
        
    return docs


def new_data_to_doc(directory):
    docs = []
    docs += pdf_txt_to_doc(directory)
    docs += pkl_to_doc(directory)
    print(f"Generated {len(docs)} chunks")
    return docs

def uploaded_files_to_doc(uploaded_files):
    docs = []
    splitter = RecursiveCharacterTextSplitter()

    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith("txt"):
            loader = UnstructuredPDFLoader(uploaded_file)
            pages = loader.load_and_split()
            for page in pages:
                docs.append({'page_content' : page.page_content, 'source' : uploaded_file.name})
        elif uploaded_file.name.endswith(".pdf"):
            loader = TextLoader(uploaded_file)
            pages = loader.load_and_split()
            for page in pages:
                docs.append({'page_content' : page.page_content, 'source' : uploaded_file.name})
        elif uploaded_file.name.endswith(".pkl"):
            with open(uploaded_file, "rb") as f:
                temp_docs = pickle.load(f)

            # split docs
            for doc in temp_docs:
                page_content = doc['page_content']

                split_texts = splitter.split_text(page_content)

                for text in split_texts:
                    docs.append({'page_content': text, 'source': doc['source']})

    print(f"Generated {len(docs)} chunks")
    return docs



if __name__ == "__main__":
    docs = pkl_to_doc("dbs/gprMax/data/new_data")
    
    pass