import csv
import numpy as np
from collections import defaultdict
from matplotlib import pyplot as plt

k = 4

# M: a matrix of dim. N x k, where N is # of items and k is # of categories
def fleiss_kappa(M):
    N, k = M.shape
    n_annotators = float(np.sum(M[0, :]))

    p = np.sum(M, axis=0) / (N * n_annotators)
    P = (np.sum(np.multiply(M, M), axis=1) - n_annotators) / (n_annotators * (n_annotators - 1))
    Pbar = np.sum(P) / N
    PbarE = np.sum(np.multiply(p, p))

    kappa = (Pbar - PbarE) / (1 - PbarE)
    return kappa

# Figure out which rows correspond with which metrics. Order can vary for each MTurk batch
def get_idxs(header_row):
    int_idx = set(); coh_idx = set(); flu_idx = set(); rel_idx = set()
    for i, column in enumerate(header.split(",")):
        if "interesting" in column:
            int_idx.update([i])
        elif "coheren" in column:
            coh_idx.update([i])
        elif "fluen" in column:
            flu_idx.update([i])
        elif "relevan" in column:
            rel_idx.update([i])
    return (int_idx, coh_idx, flu_idx, rel_idx)

# Load data. N = number of stories, k = number of possible ratings
CSV_FILE = "combined_results_new.csv"
N = sum(1 for line in open("combined_results_new.csv")) - 1
M_int = np.zeros((N, k))
M_coh = np.zeros((N, k))
M_flu = np.zeros((N, k))
M_rel = np.zeros((N, k))
int_counter = defaultdict(int)
coh_counter = defaultdict(int)
flu_counter = defaultdict(int)
rel_counter = defaultdict(int)

interesting = defaultdict(list)
coherent = defaultdict(list)
fluent = defaultdict(list)
relevant = defaultdict(list)

turkscore_lines = open(CSV_FILE)
header = turkscore_lines.readline()
int_idx, coh_idx, flu_idx, rel_idx = get_idxs(header)

turkscores = csv.reader(turkscore_lines)
adj_i = -1

"""
Get nucleus sampling scores across p-values. For diverse decoding scores,
uncomment the lines containing the lamda variable and comment out the
corresponding lines with only the p_val variable.
"""
for i, row in enumerate(turkscores):
    adj_i += 1
    if len(row[0]) < 1 and "_" in row[1]:
        int_idx, coh_idx, flu_idx, rel_idx = get_idxs(row)
        adj_i -= 1
        continue
    for j, col in enumerate(row):
        # skip if blank
        if len(col) < 1:
            continue

        if j == 0:
            print(col)
            # story_id, p_val, lamda = col.split('_')
            story_id, p_val = col.split('_')
            continue
        else:
            score = int(float(col))

        if j in int_idx:
            M_int[adj_i, score-1] += 1
            # interesting[lamda].append(score)
            interesting[p_val].append(score)
            int_counter[score] += 1
        elif j in coh_idx:
            M_coh[adj_i, score-1] += 1
            # coherent[lamda].append(score)
            coherent[p_val].append(score)
            coh_counter[score] += 1
        elif j in flu_idx:
            M_flu[adj_i, score-1] += 1
            # fluent[lamda].append(score)
            fluent[p_val].append(score)
            flu_counter[score] += 1
        elif j in rel_idx:
            M_rel[adj_i, score-1] += 1
            # relevant[lamda].append(score)
            relevant[p_val].append(score)
            rel_counter[score] += 1


turkscore_lines.close()

x = []
y_int = []; y_int_err = []
y_coh = []; y_coh_err = []
y_flu = []; y_flu_err = []
y_rel = []; y_rel_err = []

print('Interestingness: ({:.3f})'.format(fleiss_kappa(M_int)))
for judgment in sorted(int_counter.keys()):
    print(str(judgment)+': '+str(int_counter[judgment]), end='. ')
print('')
for p_val in sorted(interesting.keys()):
    x.append(float(p_val))
    print('\t{}: {:.3f} ({:.3f}) -- {}'.format(p_val, np.mean(interesting[p_val]), np.std(interesting[p_val]), len(interesting[p_val])))
    y_int.append(np.mean(interesting[p_val]))
    y_int_err.append(np.std(interesting[p_val]))

print('Coherence: ({:.3f})'.format(fleiss_kappa(M_coh)))
for judgment in sorted(coh_counter.keys()):
    print(str(judgment)+': '+str(coh_counter[judgment]), end='. ')
print('')
for p_val in sorted(coherent.keys()):
    print('\t{}: {:.3f} ({:.3f}) -- {}'.format(p_val, np.mean(coherent[p_val]), np.std(coherent[p_val]), len(coherent[p_val])))
    y_coh.append(np.mean(coherent[p_val]))
    y_coh_err.append(np.std(coherent[p_val]))


print('Fluency: ({:.3f})'.format(fleiss_kappa(M_flu)))
for judgment in sorted(flu_counter.keys()):
    print(str(judgment)+': '+str(coh_counter[judgment]), end='. ')
print('')
for p_val in sorted(fluent.keys()):
    print('\t{}: {:.3f} ({:.3f}) -- {}'.format(p_val, np.mean(fluent[p_val]), np.std(fluent[p_val]), len(fluent[p_val])))
    y_flu.append(np.mean(fluent[p_val]))
    y_flu_err.append(np.std(fluent[p_val]))


print('Relevance: ({:.3f})'.format(fleiss_kappa(M_rel)))
for judgment in sorted(rel_counter.keys()):
    print(str(judgment)+': '+str(rel_counter[judgment]), end='. ')
print('')
for p_val in sorted(relevant.keys()):
    print('\t{}: {:.3f} ({:.3f}) -- {}'.format(p_val, np.mean(relevant[p_val]), np.std(relevant[p_val]), len(relevant[p_val])))
    y_rel.append(np.mean(relevant[p_val]))
    y_rel_err.append(np.std(relevant[p_val]))

"""
Plot nucleus sampling results. To plot diverse decoding results, uncomment the
commented lines. Comment out the corresponding line above each commented line
to replace the parameters for nucleus sampling plotting.
"""
'''
# plt.style.use("ggplot")
plt.plot(x, y_int, label="Interesting", color="red", linestyle="-", marker="o")
plt.plot(x, y_coh, label="Coherent", color="blue", linestyle="--", marker="*")
plt.plot(x, y_flu, label="Fluent", color="purple", linestyle="-.", marker="+")
plt.plot(x, y_rel, label="Relevant", color="black", linestyle=":", marker="s")
plt.xlabel("p")
# plt.xlabel("λ")
plt.axis([0.0, 1.0, 1.5, 3.5])
# plt.axis([0.0, 0.5, 1.5, 3.5])
plt.xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
# plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
plt.yticks([1.5, 2.5, 3.5])
plt.ylabel("Mean Rating")
plt.legend()
plt.savefig("p_val_graph_new.pdf", bbox_inches="tight")
'''
