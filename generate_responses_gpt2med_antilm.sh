#!/bin/bash

#$ -wd /home/aadelucia/gpt/logs
#$ -N med-gen-antilm
#$ -j y -o $JOB_NAME-$JOB_ID.out
#$ -M aadelucia@jhu.edu
#$ -m e
#$ -l ram_free=10G,mem_free=10G,gpu=1,hostname=b1[123456789]|c0*|c1[12345789]
#$ -q g.q
#$ -t 1-3

# Activate dev environments and call programs
#eval "$(/home/lisali/anaconda3/bin/conda shell.bash hook)"
source /home/aadelucia/miniconda3/bin/activate gpt-antilm
export LD_LIBRARY_PATH=:/opt/NVIDIA/cuda-10/lib64/
export CUDA_VISIBLE_DEVICES=$(free-gpu)

PROJECT_HOME=/home/aadelucia/gpt
TEST_PROMPTS="$PROJECT_HOME/writing_prompts/test.wp.src"
OUTPUT_BASE="$PROJECT_HOME/regenerated_narratives_antilm"
mkdir -p $OUTPUT_BASE
MODEL_BASE="$PROJECT_HOME/models/gpt_med_wp"
OUTPUT_FILE_BASE="${OUTPUT_BASE}/gpt2_med"
DATASETS=("med" "large" "small")
MAX_LENGTH=(256 768 128)
BATCH_SIZE=20


i=$(($SGE_TASK_ID - 1))
dataset=${DATASETS[$i]}
max_length=${MAX_LENGTH[$i]}
OUTPUT_FILE="${OUTPUT_FILE_BASE}_${dataset}.csv"

echo "Generating for response length $dataset on GPU ${CUDA_VISIBLE_DEVICES}"
python $PROJECT_HOME/code/generate_batch_padded_antilm.py \
    --prompt-path ${TEST_PROMPTS} \
    --model-name-or-path "${MODEL_BASE}_${dataset}" \
    --output-path "${OUTPUT_FILE}" \
    --length "${max_length}" \
    --bsz "${BATCH_SIZE}" \
    --lambdas 0.1 0.2 0.35 0.5 \
    --p 0.7

# Check exit status
status=$?
if [ "$status" -ne 0 ]
then
    echo "Task $SGE_TASK_ID failed"
    exit 1
fi

