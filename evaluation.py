"""
Automatic evaluation of generated narratives. 

Uses distinct-1,2 and sentBERT for evaluating diversity.

Author: Alexandra DeLucia
"""
# Standard imports
import os
import argparse
import logging
import regex
import pandas as pd
from csv import QUOTE_ALL

# Third-party
from sentence_transformers import SentenceTransformer
import torch
from scipy.spatial.distance import pdist
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global SentBERT
sentbert_model = None 


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-files", nargs="+", required=True, 
        help="List of model response output files in CSV form with columns <id>,<prompt>,<response>, where ID is <prompt id>_<top-p>. The filename should be gpt2_{model size}_{dataset size}.csv")
    parser.add_argument("--output-file", type=str, required=True)
    parser.add_argument("--baseline", action="store_true", help="Filename format is baseline_dummy_{dataset size}_{p}.txt and content is assumed to be on the responses.")
    parser.add_argument("--antilm", action="store_true")

    parser.add_argument("--metrics", nargs="+", default=set(["dist-n", "sentBERT"]), 
        choices=["dist-n", "sentBERT"], help="Evaluation metrics")

    parser.add_argument("--cpu", help="Use CPU even if GPU is available")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def sentBERT(responses):
    """
    Compute average pairwise cosine distance between BERT representations

    Note: Diversity paper uses cosine similarity and then negates it, here
    we just use cosine distance
    """
    embeddings = sentbert_model.encode(responses)
    distances = pdist(embeddings, metric="cosine")
    return np.average(distances)


def distinct_1(lines):
    '''
    Computes the number of distinct words divided by the total number of words.
    Input:
    lines: List of strings.

    Written by Joao Sedoc
    '''
    words = ' '.join(lines).split(' ')
    num_distinct_words = len(set(words))
    return float(num_distinct_words) / len(words)


def distinct_2(lines):
    '''Computes the number of distinct bigrams divided by the total number of words.

    Input:
    lines: List of strings.

    Written by Joao Sedoc
    '''
    all_bigrams = []
    num_words = 0

    for line in lines:
        line_list = line.split(' ')
        num_words += len(line_list)
        bigrams = zip(line_list, line_list[1:])
        all_bigrams.extend(list(bigrams))

    return len(set(all_bigrams)) / float(num_words)


def clean_response(response):
    """
    Remove special tokens from the response
    """
    og_response = response
    # Remove extra characters
    response = response.strip()
    # Remove special tokens
    response = regex.sub("<\|endoftext\|>|<newline>|\[RESPONSE\]", "", response)
    # Lowercase
    response = response.lower()
    # Add spaces in front of punctuation
    logging.debug(regex.findall("(\p{P})", response))
    response = regex.sub("(\p{P})", " \\1", response)
    # Remove excess spacing
    response = regex.sub("\s+", " ", response)
    logging.debug(f"OG: {og_response}\nNew: {response}")
    return response


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
 
    # Write header to output CSV file
    columns = ["model_size", "dataset_size", "top_p", "lambda"]
    if "dist-n" in args.metrics:
        columns.extend(["dist1", "dist2"])
    if "sentBERT" in args.metrics:
        columns.append("sentBERT")
        if args.cpu:
            device = "cpu"
        else:
            device = "cuda"
            # Claim GPU
            torch.ones(1).to(device)
        # Instantiate model
        sentbert_model = SentenceTransformer("bert-large-nli-stsb-mean-tokens").to(device)
    
    automatic_results = []
    for input_file in args.input_files:
        logging.info(f"On file {input_file}")
        
        if args.baseline:
            # Get model and training info from filename
            # Example format: /path/to/baseline_dummy_med_0.5.txt
            dataset_size, top_p = input_file.split("/")[-1][:-4].split("_")[-2:]
            if top_p == "argmax":
                top_p = 0.0
            model = "fusion"
            model_size = "NA"
            lamb = 0.0
            with open(input_file) as f:
                responses = [clean_response(i) for i in f.readlines()]
            
            row = [model_size, dataset_size, top_p, lamb]
            logging.info(f"Calculating for model: {model_size}\tdataset: {dataset_size}\ttop-p: {top_p}\tlambda: {lamb}")
            
            if "dist-n" in args.metrics:
                logging.info(f"\tComputing distinct-1")
                dist1 = distinct_1(responses)

                logging.info(f"\tComputing distinct-2")
                dist2 = distinct_2(responses)
                row.extend([dist1, dist2])
            
            if "sentBERT" in args.metrics:
                logging.info(f"\tComputing SentBERT")
                sentBERT_score = sentBERT(responses)
                row.append(sentBERT_score)
            
            automatic_results.append(row)

            if args.debug:
                break
        
        else:
            # Get model and training info from filename
            # Example format: /path/to/gpt2_med_med.csv
            model, model_size, dataset_size = input_file.split("/")[-1].split(".")[0].split("_")
            
            # Load and clean/tokenize the responses
            df = pd.read_csv(input_file, index_col=0, quoting=QUOTE_ALL)
            df["clean_response"] = df.response.map(lambda x: clean_response(x))
            
            df["prompt_id"] = df.index.map(lambda x: x.split("_")[0])
            df["top_p"] = df.index.map(lambda x: x.split("_")[1])
            if args.antilm:
                df["lambda"] = df.index.map(lambda x: x.split("_")[2])
            else:        
                df["lambda"] = df.index.map(lambda x: 0.0)

            for (top_p, lamb), temp in df.groupby(["top_p", "lambda"]):
                row = [model_size, dataset_size, top_p, lamb]
                logging.info(f"Calculating for model: {model_size}\tdataset: {dataset_size}\ttop-p: {top_p}\tlambda: {lamb}")
                
                responses = temp.clean_response.tolist()

                if "dist-n" in args.metrics:
                    logging.info(f"\tComputing distinct-1")
                    dist1 = distinct_1(responses)

                    logging.info(f"\tComputing distinct-2")
                    dist2 = distinct_2(responses)
                    row.extend([dist1, dist2])
                
                if "sentBERT" in args.metrics:
                    logging.info(f"\tComputing SentBERT")
                    sentBERT_score = sentBERT(responses)
                    row.append(sentBERT_score)
                
                automatic_results.append(row)

                if args.debug:
                    break
        
    logging.info(f"Saving results.")
    result_df = pd.DataFrame(automatic_results, columns=columns)
    result_df.to_csv(args.output_file)
    logging.info(result_df.head())


