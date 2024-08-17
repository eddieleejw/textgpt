import os
from utils.evaluation_utils import evaluate_bertscore
from utils.query_utils import load_db
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


def main():
    os.environ["OPENAI_API_KEY"] = input("What is your OpenAI API key?")
    embedding_function = OpenAIEmbeddings()
    llm = ChatOpenAI(model = "gpt-4o-mini")
    project = input("What is the name of the project?")

    db, docstore = load_db(f"dbs/{project}/db", embedding_function)
    bertscores_dict = evaluate_bertscore(db, docstore, llm, load_path = "dbs/gprMax/eval/qa_pairs.pkl", n = 5)
    print(bertscores_dict)


if __name__ == "__main__":
    main()
    

