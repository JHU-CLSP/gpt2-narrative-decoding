import sys
import numpy as np

fold = sys.argv[1]

# get average number of tokens per-response for each size dataset
with open(fold+".wp.comb.1", "r") as small, open(fold+".wp.comb.3", "r") as medium, \
        open(fold+".wp.comb", "r") as _long:
    num_lines = 0
    s_list = []
    s_sum = 0
    m_list = []
    m_sum = 0
    l_list = []
    l_sum = 0
    for s_line, m_line, l_line in zip(small, medium, _long):
        s_tokens = s_line.strip().split()
        m_tokens = m_line.strip().split()
        l_tokens = l_line.strip().split()

        s_sum += len(s_tokens)
        s_list.append(len(s_tokens))
        m_sum += len(m_tokens)
        m_list.append(len(m_tokens))
        l_sum += len(l_tokens)
        l_list.append(len(l_tokens))
        num_lines += 1

    print("small avg. length: {}".format(s_sum / num_lines))
    print("\tsmall std. dev.: {}".format(np.std(s_list)))
    print("medium avg. length: {}".format(m_sum / num_lines))
    print("\tmedium std. dev.: {}".format(np.std(m_list)))
    print("large avg. length: {}".format(l_sum / num_lines))
    print("\tlarge std. dev.: {}".format(np.std(l_list)))
