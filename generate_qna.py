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
from utils import generate_qna_utils

if __name__ == "__main__":
    generate_qna_utils.main()