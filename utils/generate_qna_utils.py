'''
Generate question-answer pairs based on a given collection of documents
'''

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import pickle
import utils.doc_utils as doc_utils

def generate_qna(contents, llm):
    '''
    Generate qnas
    contents: a list of texts. list(str)
    llm: a language model
    '''

    ret = []

    prompt_template = PromptTemplate.from_template(
        "You are a teacher preparing questions and answers for an exam based on the given document. \
        For the following document, generate 3 question and answer pairs that are as general as possible \
        Format the question and answer pairs with each question and answer being in consecutive lines, e.g. \
        Question: ... \
        Answer: ... \
        Text: {doc}"
    )

    chain = ({"doc" : lambda x : x} | prompt_template | llm | StrOutputParser())

    qnas = chain.batch(contents)

    return qnas


def process_text(qnas):

    '''
    takes output from `generate_qna` and processes them into individual pairs of questions and answers
    '''

    qa_pairs = []

    # Initialize lists to hold questions and answers

    for i, text in enumerate(qnas):
        questions = []
        answers = []

        # Split the text into lines
        lines = text.split('\n')

        # Iterate through the lines
        for line in lines:
            if line.startswith("Question:"):
                questions.append(line.replace("Question:", "").strip())
            elif line.startswith("Answer:"):
                answers.append(line.replace("Answer:", "").strip())
            elif line != "":
                answers[-1] += "\n" + line

        try:
            qa_pairs += [{"Question": q, "Answer": a} for q, a in zip(questions, answers)]
        except:
            print(f"Problem processing text {i}")
            continue

    return qa_pairs


def save_qa_pairs(qa_pairs, directory):

    inp = input(f"Saving to directory {directory} [Y/N]")
    if inp in ["Y", "y"]:
        with open(f"{directory}/qa_pairs.pkl", "wb") as f:
            pickle.dump(qa_pairs, f)

def load_contents(directory):
    doc_list = doc_utils.new_data_to_doc(directory)
    contents = [doc['page_content'] for doc in doc_list]
    return contents

def main():
    contents_directory = "dbs/gprMax/data/old_data/pkl"
    
    if input(f"Loading contents form {contents_directory} [Y/N]") in ["Y", "y"]:
        contents = load_contents(contents_directory)

        if input(f"Truncate contents for testing? [Y/N]") in ["Y", "y"]:
            contents = contents[:5]
    else:
        print("Change `contents_directory` in `generate_qna.py` to the correct directory")
        exit()

    

    llm = ChatOpenAI(model = "gpt-4o-mini")

    qnas = generate_qna(contents, llm)
    qa_pairs = process_text(qnas)
    save_qa_pairs(qa_pairs, "dbs/gprMax/eval")
    


# if __name__ == "__main__":
#     os.environ["OPENAI_API_KEY"] = input("What is your OpenAI API key?")
#     contents_directory = "dbs/gprMax/data/old_data/pkl"
    
#     if input(f"Loading contents form {contents_directory} [Y/N]") in ["Y", "y"]:
#         contents = load_contents(contents_directory)
#     else:
#         print("Change `contents_directory` in `generate_qna.py` to the correct directory")
#         exit()

#     llm = ChatOpenAI(model = "gpt-4o-mini")

#     qnas = generate_qna(contents, llm)
#     qa_pairs = process_text(qnas)
#     save_qa_pairs(qa_pairs, "dbs/gprMax/eval")
