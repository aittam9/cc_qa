import os 
import re 
import pandas as pd

import numpy as np
from tqdm import tqdm
from collections import Counter
from utils import get_completion, num_tokens_from_string, compute_token_price
import pickle
import random 

import argparse




def filter_rows_by_values(df, col, values):
    return df[df[col].isin(values)]

def aggregate_and_filter(dfs):
    #from list of dfs to single df
    concat = pd.concat(dfs)
    before = concat.shape[0]
    concat= filter_rows_by_values(concat, "IsQueryRelevant", ["SI", "NO"])
    after = concat.shape[0]
    print(f"Removed {before-after} items with invalid answers")

    return concat


def format4manualeval(concat):
    #create a new dataframe with the template of the questions to be evaluated by humans
    man_eval_inputs = []
    man_input_template = "{title}\n{text}\n\nDomanda:\n{question}"
    for row in concat.itertuples():
        q = re.sub(r" secondo il testo\?", "?", row.Query[2:]).strip()
        example = re.sub(r"\{title\}", row._1  , re.sub(r"\{text\}", row.Passage, re.sub(r"\{question\}", q, man_input_template)))
        man_eval_inputs.append(example)

    man_eval_df = pd.DataFrame(zip(concat["Articolo di riferimento"].tolist(), man_eval_inputs,concat["IsQueryRelevant"].tolist() ),
                                columns = ["Art.", "Quesito", "AutomaticEvaluation"])
    return man_eval_df


def make_random_split(man_eval_df):
    shuffled = man_eval_df.sample(frac = 1)
    sampled_dfs = []
    for step in range(0,8000, 100):
        sampled_dfs.append(shuffled.iloc[step:step+100])
        print(f"Sampled {step}-{step+100}")
    return sampled_dfs

def get_ids_random2add(stored_ids, n):
    sample_from = list(set(range(80)) -set(stored_ids))
    new_ids = random.choices(sample_from, k = n)
    return new_ids


def build_split_from_scratch():
     # read input (list of dfs i binary)
    with open("../automatic_eval_results/all_autoeval_dfs.pkl", "rb") as infile:
        dfs = pickle.load(infile)

    concat = aggregate_and_filter(dfs)
    manual_eval = format4manualeval(concat)
    sampled_dfs = make_random_split(manual_eval)

    #print 
    print(f"Total entries in starting dataframe: {len(set(manual_eval.index.tolist()))}") 
    print(f"Number of sampled dataframe: {len(sampled_dfs)}")
    print(f"Length of each dataframe: {len(sampled_dfs[-1])}")


    #sanity check if ids overlap
    total_ids = []
    for d in sampled_dfs:
        for i in d.index.to_list():
            total_ids.append(i)
    assert len(total_ids) == len(set(total_ids)), "Ids overlap!"
    print(f"Sanity check for ids overalapping: OK")

    #save output in binary format
    with open("../manual_evaluation/all_rand_subsets.pkl", "wb") as outfile:
        pickle.dump(sampled_dfs, outfile)
    

def add_splits(n):
    manual_eval_dir = "../manual_evaluation/evaluated_input"
        #check already saampled subsets
    stored_idx = [int(i.split("_")[-1].split(".")[0]) for i in os.listdir(manual_eval_dir)] 
    # n = int(args.select)
    ids2add = get_ids_random2add(stored_idx, n)
    assert sorted(stored_idx) != sorted(ids2add), "Something wrong with the sampling. Already present id has been sampled again."
    
    #load the binary randomized subsets
    print("Loading all randomized subsets:")
    with open("../manual_evaluation/all_rand_subsets.pkl", "rb") as infile:
        sampled_dfs = pickle.load(infile)
    
    #select additional random subsets and add them to the pool
    for id in ids2add:
        print(f"Saving random sampled dataframe {id}")
        sampled_dfs[id].to_csv(f"../manual_evaluation/input2eval/man_eval_randss_{id}.tsv", sep = "\t")
        
        with open("../manual_evaluation/2eval_log.txt", "a") as f:
            f.write(str(id) +": added to inputs2eval\n")
            
    print(f"Already evaluated df ids: {stored_idx}\nNew ids added to be evaluated {ids2add}")
    




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--build", "-b", action= "store_true", help= "build the random splits from scratch")
    parser.add_argument("--select", "-s",  help= "select n random subset to add to the pool to evaluatemanually. ")

    args = parser.parse_args()

    if args.build:
        
        build_split_from_scratch()
    
    elif args.select:
      #TODO add a function to clean the input2eval directory first
        n = int(args.select)
        add_splits(n)

    else:
        print("Invalid argument. please provide a valid argument.\nType --build to generate random subsets from scratch\nType --select <n> to add n subset to manual evaluation")
    


    