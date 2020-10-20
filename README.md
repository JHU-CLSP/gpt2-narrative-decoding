# Decoding Methods for Neural Narrative Generation
Alexandra DeLucia\*, Aaron Mueller\*, Xiang "Lisa" Li, João Sedoc

This repository contains code for replicating the approach and results of the paper [Decoding Strategies for Neural Narrative Generation](https://arxiv.org/abs/2010.07375).

### TODO:
- Add job scripts
- Describe preprocessing procedure
- Describe training and generation procedures
	- baseline (done)
	- GPT-2

## Models
Our models are on the Hugging Face library. Only the GPT-2 medium model fine-tuned on the medium and large datasets are available on the library. If you would like the small model, please reach out to us (the authors).

```python
model = AutoModel.from_pretrained("aadelucia/GPT2_medium_narrative_finetuned_medium")
```

## Preprocessing
Our preprocessing script may be found in `data/preproc.py`. To replicate our setup, download the [writingPrompts dataset](https://dl.fbaipublicfiles.com/fairseq/data/writingPrompts.tar.gz) and unzip the .tar into  the `data` folder.

This script will generate a series of prompts and responses of various lengths. All outputs with the `.comb*` suffix contain the prompt and response together; `.src*` files contain only prompts, and `.trg*` files contain only responses. If there is no number after the suffix, it is the large dataset (full responses). `*.1` files are short datasets (1 paragraph), and `*.3` files are medium datasets (3 paragraphs). While this script does not impose a token cutoff, we impose a cutoff in the training script by thresholding the maximum sequence length.

We also include a `count_length.py` script which calculates the average length of prompt/response pairs per-dataset as well as the total number of tokens per-dataset (replicating the results of our Table 2).

## Training

## Generation
TODO: write-up our basic generation procedure. Alexandra: point to specific scripts (incl. antiLM scripts)

The generation script is `script_generate_medium_responses.sh`, which calls the `generate_responses.py` script to generate the responses from the fine-tuned GPT-2 model on all responses lengths (small, medium, large). This script can be used with GPT-2 small by changing the `--model-name-or-path` option. 

The script was run on the Center for Language and Speech Processing (CLSP) cluster at Johns Hopkins University, where we had access to special features such as "job arrays" (`$SGE_TASK_ID`). 

We include our Maximum Mutual Information (MMI) antiLM generation scripts. Note however that this runs on a modified version of the huggingface transformers generation code. We have submitted a [pull request](https://github.com/huggingface/transformers/pull/7931) to include diverse decoding. You may find our implementation there.

## Baseline
We use the [fusion model](https://github.com/pytorch/fairseq/blob/master/examples/stories/README.md) from fairseq. We download and apply their dataset and their trained model. We only modify the generation scripts to generate outputs of different lengths and using different p-values. As p=0 was not a valid hyperparameter, we use a separate script to generate in that case (`generate_argmax.sh`). These may be found in the `baselines` folder.
