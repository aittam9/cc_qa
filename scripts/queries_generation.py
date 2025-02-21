import os 
import re
from utils import SpecialTokenizer, num_tokens_from_string, get_completion, align_prompt2_n_queries
import json
from itertools import islice
from tqdm import tqdm
import pickle
import pandas as pd


data = json.load(open("../data/cc_books_clean_whole2_nonum.json", "r"))
tokenizer = SpecialTokenizer()


prompt = open("../prompts/generation_prompt.txt", "r").read()
#process book

if __name__ == "__main__":
    
    dfs = []
    for n, book in enumerate(data, 1):
        print(f"Processing {book}...\n")
        #process articles
        query_passage = []
        for k in tqdm(data[book]):
            try:
                p = align_prompt2_n_queries(data[book][k], tokenizer, prompt)
                answ = get_completion(p + data[book][k], "gpt-4o")
                #loop over the generated queries and separate them
                for query in answ.split("\n"):
                    query_passage.append((k, query, data[book][k].replace("\n", " ")))
            except:
                print(f"Failed to generate queries for {k}")

        #build and save a dataframe for each book
        columns = ["Articolo di riferimento", "Query", "Passage"]
        df = pd.DataFrame(query_passage, columns = columns)
        df.to_csv(f"../qa_results/cc_book{n}_qa.tsv", sep = "\t")
        dfs.append(df) 
        assert len(df["Articolo di riferimento"].unique()) == len(book), "Number of unique articles does not match number of inputs"
    
    #save a binary file of all the dataframes
    with open("../results/all_qa_dfs.pkl", "wb") as outfile:
        pickle.dump(dfs, outfile)