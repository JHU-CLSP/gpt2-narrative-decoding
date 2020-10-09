"""
Generates responses with the given GPT-2 model and list of prompts.

Output is a CSV file in the format:
<id>,<prompt>,<response>

Where "id" is the line number of the prompt in the original file.

Author: Lisa Li
Modified: Alexandra DeLucia
"""
# Standard imports
import sys
import argparse
import logging
import csv
import time

# Third-party imports
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Configure logging
logging.basicConfig(level=logging.INFO)


def batchify_old(sents, bsz):
    """Lisa's version. Groups prompts by length to avoid padding issue"""
    sents, sorted_idxs = zip(*sorted(zip(sents, range(len(sents))), key=lambda x: len(x[0])))
    minibatches, mb2linenos = [], []
    curr_batch = []
    curr_linenos = []
    for i in range(len(sents)):
        if len(curr_batch) == bsz:
            minibatches.append(curr_batch)
            mb2linenos.append(curr_linenos)

            curr_batch = [sents[i]]
            curr_linenos = [sorted_idxs[i]]
        else:
            curr_batch.append(sents[i])
            curr_linenos.append(sorted_idxs[i])
    return minibatches, mb2linenos


def batchify(prompts, batch_size):
    # Edge case: 1 prompt per batch
    if len(prompts) == batch_size:
        return [[p] for p in prompts], [[i] for i in range(len(prompts))]
    # Edge case: batch size of 1 (all prompts at once)
    if batch_size == 1:
        return [prompts], list(range(len(prompts)))

    minibatches = []
    minibatches_idx = []
    curr_batch = []
    curr_batch_idx = []
    for i, prompt in enumerate(prompts):
        if len(curr_batch) == batch_size:
            minibatches.append(curr_batch)
            minibatches_idx.append(curr_batch_idx)
            curr_batch = [prompt]
            curr_batch_idx = [i]
        else:
            curr_batch.append(prompt)
            curr_batch_idx.append(i)
    # Check if extra prompts
    if len(prompts) % batch_size != 0:
        minibatches.append(curr_batch)
        minibatches_idx.append(curr_batch_idx)
    return minibatches, minibatches_idx


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-path", type=str, default="/home/aadelucia/gpt/writing_prompts/test.wp.src")
    parser.add_argument("--output-path", type=str, default="output.txt")
    parser.add_argument("--model-name-or-path", type=str, default=None, help="path to our model")
    parser.add_argument("--length", type=int, default=200)
    parser.add_argument("--bsz", type=int, default=20)
    
    parser.add_argument("--seed", type=int, default=42, help="random seed for initialization")
    parser.add_argument("--no-cuda", action="store_true", help="Avoid using CUDA when available")

    args = parser.parse_args()
    args.device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
    return args


if __name__ == "__main__":
    # Load training parameters
    args = parse_args()

    # Claim the GPU
    try:
        torch.ones(1).to(args.device)
    except RuntimeError as err:
        logging.error(err)
        sys.exit(1)

    # Load pre-trained OpenAI GPT-2 model
    tokenizer = GPT2Tokenizer.from_pretrained(args.model_name_or_path)
    model = GPT2LMHeadModel.from_pretrained(args.model_name_or_path)
    model.to(args.device)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"  # Hack to be able to batch generate

    logging.info(f"Loading prompts from {args.prompt_path}")
    prompt_lst = []
    with open(args.prompt_path, 'r') as f:
        prompt_lst = [f"{line.strip()} [RESPONSE]" for line in f.readlines()]

    # Batch the prompts for quicker generation
    logging.info("total number of sentences = {}".format(len(prompt_lst)))
    prompt_lst_batch, prompt_lst_batch_idx = batchify(prompt_lst, args.bsz)
    logging.info("total batch size = {}".format(len(prompt_lst_batch)))

    # Start the output file
    f = open(args.output_path, "w+", newline="")
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["id", "prompt", "response"])

    for i, (prompts, prompts_idx) in enumerate(zip(prompt_lst_batch, prompt_lst_batch_idx)):
        # Log progress
        if i % 100 == 0:
            logging.info(f"On batch {i} out of {len(prompt_lst_batch)}")
    
        # Encode prompts
        encoded_prompt_dict = tokenizer.batch_encode_plus(prompts, return_tensors="pt", pad_to_max_length=True)
        encoded_prompt = encoded_prompt_dict['input_ids'].to(args.device)
        encoded_mask = encoded_prompt_dict['attention_mask'].to(args.device)
        end_of_prompt_idx = len(encoded_prompt[0])

        for p in [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 1.0]:
            # Greedy decoding
            if p == 0.0:
                output_sequences = model.generate(
                    input_ids=encoded_prompt,
                    max_length=args.length + len(encoded_prompt[0]),
                    temperature=1.0,
                    top_k=0,
                    top_p=0,
                    pad_token_id=50256,
                    repetition_penalty=1.0,
                    do_sample=False,
                    num_beams=1,
                    num_return_sequences=1,
                    attention_mask=encoded_mask
                )
            # Use nucleus sampling decoding
            else:
                output_sequences = model.generate(
                    input_ids=encoded_prompt,
                    max_length=args.length + len(encoded_prompt[0]),
                    temperature=1.0,
                    top_k=0,
                    top_p=p,
                    pad_token_id=50256,
                    repetition_penalty=1.0,
                    do_sample=True,
                    num_beams=1,
                    num_return_sequences=1,
                    attention_mask=encoded_mask
                )

            # Remove the batch dimension when returning multiple sequences
            if len(output_sequences.shape) > 2:
                output_sequences.squeeze_()

            for prompt_id, prompt, generated_sequence in zip(prompts_idx, prompts, output_sequences):
                # Only decode the generated response, skip the prompt
                generated_sequence = generated_sequence.tolist()[end_of_prompt_idx:]
                response = tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)
                
                # Write upprocessed output
                writer.writerow([f"{prompt_id}_{p}", prompt, response])

# Close file
f.close()


