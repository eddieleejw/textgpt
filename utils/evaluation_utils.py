'''
Module for functions used in evaluation
'''

import pickle
import random
from .query_utils import query_chatbot
from bert_score import BERTScorer
import statistics

DEBUG = True
def c_log(s):
    if DEBUG:
        print(s)



def generate_answers(qa_pairs, db, docstore, llm, n = 50):
    '''
    n: number of answers to generate. will default to 50
    '''
    n = min(len(qa_pairs), n)
    qa_pairs = random.sample(qa_pairs, n)

    c_log(f"Chat bot answering {n} evaluation question")

    chatbot_answers = []
    for qa in qa_pairs:
        query = qa['Question']
        target = qa['Answer']
        chatbot_answers.append((query, query_chatbot(query, db, docstore, llm)[0], target))
    
    c_log("Finished answering evaluation question")

    return chatbot_answers

def get_bertscores(chatbot_answers):
    '''
    chatbot_answers: list of tuples (query, chatbot answer, target answer)

    returns `bert_scores`, a list of tuples (precision, recall, f1 score) for each query-answer pair
    '''
    bert_scores = []
    scorer = BERTScorer(model_type='bert-base-uncased')

    for query, chatbot_answer, target in chatbot_answers:
        candidate = chatbot_answer
        reference = target
        P, R, F1 = scorer.score([candidate], [reference])

        bert_scores.append((P,R,F1))

    return bert_scores

def process_bertscores(bert_scores) -> dict:
    '''
    takes bert_scores, and returns a dictionary with keys "p", "r", and "f1" (for precision, recall, f1 score)
    the values are dictionaries, with keys "mean", "std", "max", "mean
    '''

    bertscores_dict = {}

    for i, score_type in enumerate(["p", "r", "f1"]):
        temp_scores = [score[i].item() for score in bert_scores]

        bertscores_dict[score_type] = {}

        bertscores_dict[score_type]["mean"] = statistics.mean(temp_scores)
        bertscores_dict[score_type]["std"] = statistics.stdev(temp_scores)
        bertscores_dict[score_type]["max"] = max(temp_scores)
        bertscores_dict[score_type]["min"] = min(temp_scores)

    return bertscores_dict

def evaluate_bertscore(db, docstore, llm, qa_pairs = None, load_path = None, n = 50):
    '''
    Requires one of qa_pairs or a load_path to a 'qa_pairs.pkl' file to be supplied

    If both are supplied, will default to using 'qa_pairs'

    n: number of answers to generate. will default to 50

    returns a `bertscores_dict` object
    '''

    if not qa_pairs and not load_path:
        raise TypeError("`evaluate` missing qa_pairs inputs")
    
    if not qa_pairs:
        with open(load_path, "rb") as f:
            qa_pairs = pickle.load(f)

    chatbot_answers = generate_answers(qa_pairs, db, docstore, llm, n)
    bert_scores = get_bertscores(chatbot_answers)
    bertscores_dict = process_bertscores(bert_scores)

    return bertscores_dict

    


    




