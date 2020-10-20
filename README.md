# Decoding Methods for Neural Narrative Generation
Alexandra DeLucia\*, Aaron Mueller\*, Xiang "Lisa" Li, João Sedoc

This repository contains code for replicating the approach and results of the paper [Decoding Strategies for Neural Narrative Generation](https://arxiv.org/abs/2010.07375).

### TODO:
- Add job scripts
- Describe preprocessing procedure
- Describe training and generation procedures
	- baseline (done)
	- GPT-2

## Preprocessing
Our preprocessing script may be found in `data/preproc.py`. To replicate our setup, download the [writingPrompts dataset](https://dl.fbaipublicfiles.com/fairseq/data/writingPrompts.tar.gz) and unzip the .tar into  the `data` folder.

This script will generate a series of prompts and responses of various lengths. All outputs with the `.comb*` suffix contain the prompt and response together; `.src*` files contain only prompts, and `.trg*` files contain only responses. If there is no number after the suffix, it is the large dataset (full responses). `*.1` files are short datasets (1 paragraph), and `*.3` files are medium datasets (3 paragraphs). While this script does not impose a token cutoff, we impose a cutoff in the training script by thresholding the maximum sequence length.

We also include a `count_length.py` script which calculates the average length of prompt/response pairs per-dataset as well as the total number of tokens per-dataset (replicating the results of our Table 2).

## Training

## Generation

## Baseline
We use the [fusion model](https://github.com/pytorch/fairseq/blob/master/examples/stories/README.md) from fairseq. We download and apply their dataset and their trained model. We only modify the generation scripts to generate outputs of different lengths and using different p-values. As p=0 was not a valid hyperparameter, we use a separate script to generate in that case (`generate_argmax.sh`). These may be found in the `baselines` folder.
