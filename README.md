# Decoding Methods for Neural Narrative Generation
Alexandra DeLucia\*, Aaron Mueller\*, Xiang "Lisa" Li, João Sedoc

This repository contains code for replicating the approach and results of the paper [Decoding Strategies for Neural Narrative Generation](https://arxiv.org/abs/2010.07375).

### TODO:
- Add job scripts
- Describe preprocessing procedure
- Describe training and generation procedures
	- baseline
	- GPT-2
- add `requirements.txt` file

## Preprocessing

## Training

## Generation

## Baseline
We use the [fusion model](https://github.com/pytorch/fairseq/blob/master/examples/stories/README.md) from fairseq. We download and apply their model and dataset. We only modify the generation scripts to generate outputs of different lengths and using different p-values. As p=0 was not a valid hyperparameter, we use a separate script to generate in that case (`generate_argmax.sh`). These may be found in the `baselines` folder.
