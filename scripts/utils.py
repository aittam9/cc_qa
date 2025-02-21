import os
import re
import csv 
from itertools import islice 

import pandas as pd
from tqdm import tqdm

import spacy 
from spacy.symbols import ORTH

from typing import List, Dict, Tuple

import tiktoken
from openai import OpenAI 

# \n\n([^(Art!Sez|Cap|Tit|§)]) 
#(\[.*Art.*\]).*  #to remove [abrogat etc]

ABBREVIATIONS_PATH = "./abbreviazioni_extended.csv"

with open(ABBREVIATIONS_PATH, "r") as infile:
    ABBREVIATIONS = [tuple(i) for i in csv.reader(infile, delimiter= ",")]


class SpecialTokenizer():
    def __init__(self, ab_path = ABBREVIATIONS):
        self.nlp = spacy.load("it_core_news_sm")
        for ab in ABBREVIATIONS:
            formatted_ab = ab[0].replace(".", ". ").strip()
            formatted_ab = re.sub(r"\s{2:}", " ", formatted_ab)
            base_ab_tokens = ab[0].split()
            ab_tokens = list(set(base_ab_tokens + [formatted_ab] + formatted_ab.split()))
            
            for token in ab_tokens:
                self.nlp.tokenizer.add_special_case(token.lower(), [{ORTH: token.lower()}])
                self.nlp.tokenizer.add_special_case(token.title(), [{ORTH: token.title()}])
                self.nlp.tokenizer.add_special_case(token.upper(), [{ORTH: token.upper()}])
                self.nlp.tokenizer.add_special_case(token.capitalize(), [{ORTH: token.capitalize()}])
        self.tokenizer = self.nlp.tokenizer
        self.abbreviations = ABBREVIATIONS

    def word_tokenize(self, text):
        tokens = [t.text for t in self.tokenizer(text)]
        return tokens 
    def sentence_tokenize(self, text):
        sentences = [s for s in self.nlp(text).sents]
        return sentences


# remove titoli, sezioni, capi, indici and abrogated articles
#TODO delete abrogated signaled with square brackets
def get_arts_dict_clean(file_path):  
    art_regex = re.compile(r"(\nArt.*\n)")
    raw_text = open(file_path, "r").read()
    raw_text1 = re.sub("\n\n\n", "\n\n", raw_text)
    raw_text1 = re.sub(r"(\nCapo|\nCAPO|Titolo|Sezione|Libro|\nIndice|§)(.+\n)?", "", raw_text)
    raw_text1 = re.sub(r"(Art|Artt)\..+ \((abrogat(o|i)|omissis)\)", "", raw_text1)
    titles = re.findall(art_regex, raw_text1)
    bodies = re.sub(art_regex, "ART_TITLE\n", raw_text1).split("ART_TITLE\n")

    titles = [t.strip() for t in titles]
    bodies = [b.strip() for b in bodies[1:]]
    arts_final = dict(zip(titles, bodies))
    assert len(titles) == len(bodies), "Something went wrong"
    return arts_final
    

# openai tokens count
def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens



client = OpenAI()
def get_completion(prompt, model):
    num_gen_per_prompt = 1
    completion = client.chat.completions.create(
            model=model,
            temperature=0,
            messages = [{'role': 'user', 'content': prompt}],
            n = num_gen_per_prompt)
                                    
    generated_answer = completion.choices[0].message.content

    return generated_answer


def generate_queries(data, prompt, tokenizer, subset = None):
    #slice the data if subset is passed
    if subset:
            data = dict(islice(data.items(), subset))
    query_passage = []
    # get completion for each article
    for k in tqdm(data):
        #TODO logic to decide number of queries
        # n_questions = decide_n_queries(data[k])
        # prompt = re.sub(r"\{\}", str(n_questions), prompt)
        
        p = align_prompt2_n_queries(data[k], tokenizer, prompt)
        answ = get_completion(p + data[k], "gpt-4o")
        #query_passage.append((k, answ, data[k]))
        #loop over the generated queries and separate them
        for query in answ.split("\n"):
            query_passage.append((k, query, data[k]))

    #build a dataframe
    columns = ["Articolo di riferimento", "Query", "Passage"]
    df = pd.DataFrame(query_passage, columns = columns)
    return df 


def align_prompt2_n_queries(art, tokenizer, prompt):
    sents = tokenizer.sentence_tokenize(art)
    if len(sents) ==1:
        #TODO take into account the number of tokens
        if  num_tokens_from_string(sents[0].text) > 50:
            n_questions = 2
        n_questions = 1
    
    elif len(sents) >= 2 < 8:
        n_questions = len(sents)

    elif len(sents) > 8:
        n_questions = 8
    p = re.sub(r"\{\}", str(n_questions), prompt)
    return p 


def compute_token_price(data, prompt, from_dict_or_df = "dict"):
    if from_dict_or_df == "dict":
        input_tok_book1 = num_tokens_from_string("".join(list(data.values())))
        input_tok_prompt_book1 = num_tokens_from_string(prompt) * len(data)
    # elif from_dict_or_df == "df":
    #     input_tok_book1 = data["Passage"].unique().tolist()
    #     input_tok_book1 = num_tokens_from_string("".join(list(input_tok_book1)))
    #     input_queries = 

    return (input_tok_book1 + input_tok_prompt_book1) * 5e-06