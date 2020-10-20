#!/bin/bash

export LD_LIBRARY_PATH=/opt/NVIDIA/cuda-9.0/lib64
export CUDA_VISIBLE_DEVICES=`free-gpu`

source /home/amueller/miniconda3/bin/activate
conda activate fairseq


fairseq-generate stories_test \
	--source-lang wp_source \
	--target-lang wp_target \
	--path models/fusion_checkpoint.pt \
	--beam 1 \
	--batch-size 4 \
	--sampling \
	--sampling-topp $1 \
	--nbest 1 \
	--model-overrides "{'pretrained_checkpoint':'models/pretrained_checkpoint.pt'}" \
	--max-len-b 256		# 768 for large outputs; 100 for small
