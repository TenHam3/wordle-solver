'''
Simulator to run all possible guesses against all possible words and generate
a lookup table of results for fast access during solving
'''

import numpy as np
import pandas as pd
import math
from wordle import *

all_words = np.loadtxt('./data/allowed_words.txt', dtype=str)
possible_words = np.loadtxt('./data/possible_words.txt', dtype=str)

NUM_ALLOWED = len(all_words)
NUM_POSSIBLE = len(possible_words)

# Compute a pattern matrix that maps (target, guess) pairs to evaluation patterns

def main():
    return

def safe_log(x):
    return math.log2(x) if x > 0 else 0

def expected_info_gain():
    info_gain = 0.0

    # Iterate through each possible pattern and add its contribution to info gain

    return info_gain

# Calculate expected information gain for each guess in allowed words

# Store results in a DataFrame and export to JSON for easy lookup during solving
# Maps guesses to expected info gain



if __name__ == "__main__":
    main()