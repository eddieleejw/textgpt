from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import os
import tqdm
import uuid
import pickle
# from docs import pdf_to_doc, pdf_txt_to_doc, pkl_to_doc, new_data_to_doc
from utils.doc_utils import pdf_to_doc, pdf_txt_to_doc, pkl_to_doc, new_data_to_doc, uploaded_files_to_doc



def summarize_texts(texts, llm):

    summaries = []

    prompt_template = PromptTemplate.from_template(
        "You are to summarize the following document for retrieval for RAG. Include some helpful keywords to aid in retrieval. \
        Text: {doc}"
    )

    chain = ({"doc" : lambda x : x} | prompt_template | llm | StrOutputParser())

    # batch 100 at a time
    print("Batching 100 queries at a time")
    for i in tqdm.tqdm(range((len(texts)//100)+1), "batches"):
        summaries += chain.batch(texts[100*i:100*(i+1)])

    assert len(summaries) == len(texts)

    # for _ in tqdm.tqdm(range(1)):
    #     summaries = chain.batch(texts)

    return summaries


def create_document_data(docs, llm):
    # pdf_paths = []

    # for file_name in os.listdir(directory):
    #     if file_name.endswith(".pdf"):
    #         pdf_file = os.path.join(directory, file_name)
    #         pdf_paths.append((pdf_file, file_name))

    # docs = []
    # for pdf_file, file_name in tqdm.tqdm(pdf_paths):
    #     loader = UnstructuredPDFLoader(pdf_file)
    #     pages = loader.load_and_split()
    #     for page in pages:
    #         # docs.append({'page_content' : page.page_content, 'metadata' : {'source' : file_name}})
    #         docs.append({'page_content' : page.page_content, 'source' : file_name})

    # print(f"Generated {len(docs)} chunks")

    texts_to_summarize = [doc['page_content'] for doc in docs]

    summaries = summarize_texts(texts_to_summarize, llm)

    document_data = []

    for i in range(len(docs)):
        document_data.append({
            'page_content' : docs[i]['page_content'],
            'source' : docs[i]['source'],
            'summary' : summaries[i],
            'doc_id' : str(uuid.uuid4())
        })
    
    return document_data

def create_db(document_data, save_dir, embedding_function):
    summary_docs = [Document(page_content = doc['summary'], metadata = {'doc_id' : doc['doc_id']}) for doc in document_data]

    db = Chroma.from_documents(summary_docs, embedding_function, persist_directory=f"{save_dir}/chroma_db")
    docstore = {doc['doc_id'] : Document(page_content = doc['page_content'], metadata = {'source' : doc['source']}) for doc in document_data}

    return db, docstore

def save_artifacts(document_data, docstore, save_dir):
    
    with open(f"{save_dir}/document_data.pkl", "wb") as f:
        pickle.dump(document_data, f)

    with open(f"{save_dir}/docstore.pkl", "wb") as f:
        pickle.dump(docstore, f)


def load_db_and_artifcats(db_dir, embedding_function):

    with open(f"{db_dir}/docstore.pkl", "rb") as f:
        docstore = pickle.load(f)

    with open(f"{db_dir}/document_data.pkl", "rb") as f:
        document_data = pickle.load(f)

    db = Chroma(persist_directory=f"{db_dir}/chroma_db", embedding_function=embedding_function)


    return db, docstore, document_data





def db_update(db, new_document_data):
    '''
    update existing db with new document_data
    '''
    summary_docs = [Document(page_content = doc['summary'], metadata = {'doc_id' : doc['doc_id']}) for doc in new_document_data]
    db.add_documents(summary_docs)


def pdf_to_db(pdf_directory, embedding_function, llm, save_dir):
    os.makedirs(save_dir, exist_ok = False)

    # load in pdf as "docs"
    docs = pdf_to_doc(pdf_directory)

    # create summarise and id, save to document_data
    document_data = create_document_data(docs, llm)

    # embed to database and create docstore
    db, docstore = create_db(document_data, save_dir, embedding_function = embedding_function)

    # save artifacts
    save_artifacts(document_data = document_data, docstore = docstore, save_dir = save_dir)

def data_to_db(new_data_directory, embedding_function, llm, save_dir):
    os.makedirs(save_dir, exist_ok = True)

    # load in pdf and txts as "docs"
    docs = new_data_to_doc(new_data_directory)

    # create summarise and id, save to document_data
    document_data = create_document_data(docs, llm)

    # embed to database and create docstore
    db, docstore = create_db(document_data, save_dir, embedding_function = embedding_function)

    # save artifacts
    save_artifacts(document_data = document_data, docstore = docstore, save_dir = save_dir)



def add_pdfs_to_db(db_dir, embedding_function, new_pdf_directory, llm):
    # load old db
    db, docstore, document_data = load_db_and_artifcats(db_dir, embedding_function)

    # generate new document_data (summaries)
    new_docs = pdf_to_doc(new_pdf_directory)
    new_document_data = create_document_data(new_docs, llm)

    # add documents
    db_update(db, new_document_data)

    # make new docstore and document_data
    merged_document_data = document_data + new_document_data
    new_docstore = {doc['doc_id'] : Document(page_content = doc['page_content'], metadata = {'source' : doc['source']}) for doc in new_document_data}
    merged_docstore = docstore
    merged_docstore.update(new_docstore)

    save_artifacts(document_data = merged_document_data, docstore = merged_docstore, save_dir = db_dir)


def add_data_to_db(db_dir, embedding_function, new_data_directory, llm):
    # load old db
    db, docstore, document_data = load_db_and_artifcats(db_dir, embedding_function)

    # generate new document_data (summaries)
    new_docs = new_data_to_doc(new_data_directory)

    new_document_data = create_document_data(new_docs, llm)

    # add documents
    db_update(db, new_document_data)

    # make new docstore and document_data
    merged_document_data = document_data + new_document_data
    new_docstore = {doc['doc_id'] : Document(page_content = doc['page_content'], metadata = {'source' : doc['source']}) for doc in new_document_data}
    merged_docstore = docstore
    merged_docstore.update(new_docstore)

    save_artifacts(document_data = merged_document_data, docstore = merged_docstore, save_dir = db_dir)



def add_uploaded_files_to_db(db_dir, embedding_function, uploaded_files, llm):
    # load old db
    db, docstore, document_data = load_db_and_artifcats(db_dir, embedding_function)

    # generate new document_data (summaries)
    # new_docs = new_data_to_doc(new_data_directory)
    new_docs = uploaded_files_to_doc(uploaded_files)

    new_document_data = create_document_data(new_docs, llm)

    # add documents
    db_update(db, new_document_data)

    # make new docstore and document_data
    merged_document_data = document_data + new_document_data
    new_docstore = {doc['doc_id'] : Document(page_content = doc['page_content'], metadata = {'source' : doc['source']}) for doc in new_document_data}
    merged_docstore = docstore
    merged_docstore.update(new_docstore)

    save_artifacts(document_data = merged_document_data, docstore = merged_docstore, save_dir = db_dir)


def uploaded_files_to_db(uploaded_files, embedding_function, llm, save_dir):
    os.makedirs(save_dir, exist_ok = True)

    # load in pdf and txts as "docs"
    # docs = new_data_to_doc(new_data_directory)
    docs = uploaded_files_to_doc(uploaded_files)

    # create summarise and id, save to document_data
    document_data = create_document_data(docs, llm)

    # embed to database and create docstore
    db, docstore = create_db(document_data, save_dir, embedding_function = embedding_function)

    # save artifacts
    save_artifacts(document_data = document_data, docstore = docstore, save_dir = save_dir)