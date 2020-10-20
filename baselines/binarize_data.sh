#!/bin/bash

source /home/amueller/miniconda3/bin/activate
conda activate fairseq

TEXT=/export/b02/amueller/discourse-data/writingPrompts

fairseq-preprocess --source-lang wp.src --target-lang wp.trg \
	--trainpref $TEXT/train --validpref $TEXT/valid --testpref $TEXT/test \
	--destdir data-bin/writingPrompts \
	--padding-factor 1 \
	--thresholdtgt 10 --thresholdsrc 10
