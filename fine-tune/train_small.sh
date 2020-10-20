#!/bin/bash

source /home/amueller/miniconda3/bin/activate
conda activate parlai
export LD_LIBRARY_PATH=/opt/NVIDIA/cuda-10/lib64
export CUDA_VISIBLE_DEVICES=`free-gpu`

TRAIN_FILE=/export/b02/amueller/discourse-data/writingPrompts/train.wp.comb.1
VALID_FILE=/export/b02/amueller/discourse-data/writingPrompts/valid.wp.comb.1

python run_language_modeling.py \
	--output_dir wp_small \
	--model_type gpt2 \
	--model_name_or_path gpt2-medium \
	--do_train \
	--train_data_file $TRAIN_FILE \
	--per_gpu_train_batch_size 4 \
	--add_wp_vocab \
	--do_eval \
	--eval_data_file $VALID_FILE \
	--block_size 100 \
	--save_steps 5000 \
	--save_total_limit 4
#	--evaluate_during_training
