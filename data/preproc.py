import sys

# Given a fold {train,dev,test}, generate short, medium, and long versions of each prompt.
fold = sys.argv[1]

# 1 -> 1 paragraph (short). 3 -> 3 paragraphs (medium). Full -> entire response (long).
# src = prompt. trg = response. comb = both together.
with open(fold+".wp_source", "r") as src, open(fold+".wp_target", "r") as trg, \
        open(fold+".wp.src", "w") as src_out, open(fold+".wp.trg.1", "w") as trg_out1, \
        open(fold+".wp.trg.3", "w") as trg_out3, open(fold+".wp.trg", "w") as trg_out_full, \
        open(fold+".wp.comb.1", "w") as together_1, open(fold+".wp.comb.3", "w") as together_3, \
        open(fold+".wp.comb", "w") as together_full:
    for src_line, trg_line in zip(src, trg):
        if not src_line.startswith("[ WP ]"):
            continue

        # combine consecutive newlines
        tokens = trg_line.split(" ")
        new_tokens = []
        new_tokens.append(tokens[0])
        for idx, token in enumerate(tokens[1:]):
            i = idx + 1
            if tokens[i] == "<newline>" and tokens[i-1] == tokens[i]:
                continue
            new_tokens.append(token)
        trg_line_combined = " ".join(new_tokens)
        
        # make [ WP ] tag into one token
        src_line_tokens = src_line.split(" ")
        src_line_tokens.pop(2)
        src_line_tokens.pop(1)
        src_line_tokens[0] = "[WP]"
        new_src_line = " ".join(src_line_tokens)

        src_out.write(new_src_line.strip() + "\n")
        trg_split = trg_line_combined.strip().split("<newline>")
        trg_out1.write(trg_split[0] + "\n")
        trg_out3.write("<newline> <newline>".join(trg_split[:3]) + "\n")
        trg_out_full.write("<newline> <newline>".join(trg_split) + "\n")

        together_prefix = "<|startoftext|> " + new_src_line.strip() + " [RESPONSE] "
        together_1.write(together_prefix + trg_split[0].strip() + " <|endoftext|>\n")
        together_3.write(together_prefix + "<newline> <newline>".join(trg_split[:3]).strip() + \
                " <|endoftext|>\n")
        together_full.write(together_prefix + "<newline> <newline>".join(trg_split).strip() + \
                " <|endoftext|>\n")

