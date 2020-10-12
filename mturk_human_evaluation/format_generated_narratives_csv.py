"""
Input file format:
<id>,<prompt>,<response>

Output file format:
<id_0>,<prompt_0>,<response_0>,...<id_n>,<prompt_n>,<response_n>

Author: Alexandra DeLucia
"""
# Imports
import os
import re
import csv
import random
import logging
import pandas as pd

# Settings
logging.basicConfig(level=logging.INFO)
random.seed(20)
tasks_per_row = 5 # Not including attention check

input_file = "/home/aadelucia/gpt/mturk/random_prompts_antilm_all.csv"
output_file = "/home/aadelucia/gpt/mturk/random_prompts_survey_format_antilm.csv"

# Formatting
SPLIT_RE = re.compile("(?:\[RESPONSE\])")
PROMPT_RE = re.compile("(\[WP\]\s*)")
SPECIAL_TOKEN_RE = re.compile("(?:\[RESPONSE\])|(\[WP\]\s*)|<\|endoftext\|>")
NEWLINE_RE = re.compile("(<newline>)")
FRONT_QUOTE_RE = re.compile(r"(``\s?)")
BACK_QUOTE_RE = re.compile("(\s)*''")
#response = re.sub("[~\*\-]{3,}", "\n", response)


def format_for_html(text):
    text = text.strip()
    # Remove [WP]/[RESPONSE] tokens
    text = SPECIAL_TOKEN_RE.sub("", text)
    # Fix weird quotes
    text = re.sub(" ’ ", "'", text)
    text = re.sub("``", "\"", text)
    text = re.sub("''", "\"", text)
    # Replace newline characters with HTML linebreaks
    text = NEWLINE_RE.sub("<br/>", text)
    return text


# Load the input_file
df = pd.read_csv(input_file)
if len(df) % tasks_per_row != 0:
    num_fillers = tasks_per_row - len(df) % tasks_per_row
    logging.warning(f"Not enough stories, need {num_fillers} more. Filling with dummy values.")
    temp = [{"id": "dummy", "prompt": "This is a filler story.", "response": "This is not a story, put any value."} for i in range(num_fillers)]
    df = df.append(temp)
logging.info(f"Loaded {len(df)} stories. Creating {len(df)//tasks_per_row} HITs with {tasks_per_row} tasks each.")

# Create output CSV and write header
f = open(output_file, "w+", newline="")
writer = csv.writer(f, quoting=csv.QUOTE_ALL)
header = []
for i in range(tasks_per_row + 1):  # +1 for attention check
    header.extend([f"id_{i}", f"prompt_{i}", f"response_{i}"])
writer.writerow(header)

# Write output tasks_per_row at a time
# Shuffle the rows first
shuffled_data = list(df.sample(frac=1).itertuples(index=False))
num_prompts = len(shuffled_data)

for n in range(0, num_prompts, tasks_per_row):
    # Choose a position for the attention check
    check_pos = random.randint(0, tasks_per_row-1)
    row = []
    for i, item in enumerate(shuffled_data[n:n+tasks_per_row]):
        # Add current story
        row.extend([item.id, format_for_html(item.prompt), format_for_html(item.response)])
        # Add attention check
        if i == check_pos:
            row.extend([f"{item.id}-check", "attention check", "This is not a story. Please select the same answers as you did for the previous story."])
    writer.writerow(row)
f.close()


# Now split into batches with 20 HITs each
batch_size = 20
df = pd.read_csv(output_file, index_col=0)
if len(df) % batch_size != 0:
    num_batches = (len(df) // batch_size) + 1
else:
    num_batches = len(df) // batch_size
for i in range(num_batches):
    start = i * batch_size
    end = start + batch_size
    if end > len(df):
        end = -1
    df.iloc[start:end].to_csv(f"{output_file}-{i+1}", quoting=csv.QUOTE_ALL)



