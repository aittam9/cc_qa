import os 
import re 
import pandas as pd
from tqdm import tqdm
from collections import Counter
from utils import get_completion, num_tokens_from_string, compute_token_price
import pickle


with open("../qa_results/all_dfs.pkl", "rb") as infile:
    dfs = pickle.load(infile)

evaluation_prompt = open("../prompts/eval_prompt.txt", "r").read()


if __name__ == "__main__":
    eval_dfs = []
    for n,book in enumerate(dfs, 1):
        print(f"Processing qas of book_{n}")

    answ = []
    for row in tqdm(book.itertuples()):
        query = re.sub(" secondo il testo?", "", row.Query[2:]).strip()
        passage = row.Passage.strip()
        prompt =  re.sub(r"\{query\}", query, re.sub(r"\{text\}", passage, evaluation_prompt))
        answ.append(re.sub(r"\"", "", get_completion(prompt, "gpt-4o")).strip())
        

    print(f"\nResults for book {n}: {Counter(answ)}")
    book["IsQueryRelevant"] = answ
    eval_dfs.append(book)
    book.to_csv(f"../automatic_eval_results/autoeval_qabook_{n}.tsv", sep = "\t")

    with open("../automatic_eval_results/all_autoeval_dfs.pkl", "wb") as outfile:
        pickle.dump(eval_dfs, outfile)