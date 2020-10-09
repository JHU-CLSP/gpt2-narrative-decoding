import csv
import math
from collections import defaultdict
from sklearn.metrics import cohen_kappa_score as cohen_kappa

def print_kappas(reviewer_kappas, reviewer_id):
    """
    Pretty-print method for displaying a reviewer's average cohen kappa with all
    other reviewers.
    """
    print("Reviewer {}:".format(reviewer_id))
    int_sum, coh_sum, flu_sum, rel_sum, denom = (0, 0, 0, 0, 0)
    for kappas in reviewer_kappas[reviewer_id]:
        int_sum += kappas[0] * kappas[4]
        coh_sum += kappas[1] * kappas[4]
        flu_sum += kappas[2] * kappas[4]
        rel_sum += kappas[3] * kappas[4]
        denom += kappas[4]
    print("\tInterestingness: {:.3f}".format(int_sum / denom))
    print("\tCoherence: {:.3f}".format(coh_sum / denom))
    print("\tFluency: {:.3f}".format(flu_sum / denom))
    print("\tRelevance: {:.3f}".format(rel_sum / denom))
    print("\tMean: {:.3f}".format((int_sum+coh_sum+flu_sum+rel_sum) / (4.0*denom)))

# If you have a file of line-separated reviewers who seem suspect, load it here.
reviewers_to_verify = set()
with open("fast_reviewers_b5.txt", "r") as fast_reviewers:
    for reviewer in fast_reviewers:
        reviewers_to_verify.update([reviewer.strip()])

CSV_FILE = "trial_results_b5.csv"
reviewer = defaultdict(list)

turkscore_lines = open(CSV_FILE)
int_idx = set(); rel_idx = set(); coh_idx = set(); flu_idx = set()
header = turkscore_lines.readline()
reviewer_ids = []
curr_reviewer = ""
for i, column in enumerate(header.split(",")):
    if i == 0:
        continue
    reviewer_id = column.split("_")[0].strip()
    if reviewer_id != curr_reviewer:
        curr_reviewer = reviewer_id
        reviewer_ids.append(reviewer_id)

    if "interesting" in column:
        int_idx.update([i])
    elif "coheren" in column:
        coh_idx.update([i])
    elif "fluen" in column:
        flu_idx.update([i])
    elif "relevan" in column:
        rel_idx.update([i])

turkscores = csv.reader(turkscore_lines)
for i, row in enumerate(turkscores):
    reviewer_num = 0
    interesting, coherent, fluent, relevant = (None, None, None, None)
    for j, col in enumerate(row):
        if j == 0:
            continue
        elif len(col) >= 1:
            score = int(float(col))
        else:
            score = None
        
        if j in int_idx:
            interesting = score
        elif j in coh_idx:
            coherent = score
        elif j in flu_idx:
            fluent = score
        elif j in rel_idx:
            relevant = score

        if (j - 1) % 4 == 3:
            reviewer_id = reviewer_ids[reviewer_num]
            if relevant is not None:
                reviewer[reviewer_id].append((interesting, coherent, fluent, relevant))
            else:
                reviewer[reviewer_id].append(None)
            # move to next reviewer and reset scores
            reviewer_num += 1
            interesting, coherent, fluent, relevant = (None, None, None, None)

turkscore_lines.close()

reviewer_kappas = defaultdict(list)

"""
Obtain Cohen's kappas for all reviewers against all other reviewers. For any given reviewer,
their average Cohen's kappa with all other users acts as their mean Cohen's kappa, which we use
to evaluate the general agreement of a particular reviewer with others.
"""
for reviewer_i in reviewer.keys():
    for reviewer_j in reviewer.keys():
        # skip if same reviewer
        if reviewer_i == reviewer_j:
            continue

        in_common = 0
        int_1, coh_1, flu_1, rel_1 = ([], [], [], [])
        int_2, coh_2, flu_2, rel_2 = ([], [], [], [])
        for scores_i, scores_j in zip(reviewer[reviewer_i], reviewer[reviewer_j]):
            if scores_i is not None and scores_j is not None:
                in_common += 1
                int_1.append(scores_i[0]); int_2.append(scores_j[0])
                coh_1.append(scores_i[1]); coh_2.append(scores_j[1])
                flu_1.append(scores_i[2]); flu_2.append(scores_j[2])
                rel_1.append(scores_i[3]); rel_2.append(scores_j[3])
        if in_common > 0:
            int_kappa = cohen_kappa(int_1, int_2)
            coh_kappa = cohen_kappa(coh_1, coh_2)
            flu_kappa = cohen_kappa(flu_1, flu_2)
            rel_kappa = cohen_kappa(rel_1, rel_2)
            reviewer_kappas[reviewer_i].append((int_kappa, coh_kappa, flu_kappa, rel_kappa, in_common))

# Print non-suspicious reviewers first, then suspicious reviewers for easier comparison
for reviewer_id in sorted(reviewer_kappas.keys()):
    if reviewer_id not in reviewers_to_verify:
        print_kappas(reviewer_kappas, reviewer_id)

print("\n----------------\nReviewers to verify:")
for reviewer_id in sorted(reviewers_to_verify):
    print_kappas(reviewer_kappas, reviewer_id)
