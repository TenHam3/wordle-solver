'''
Simulator to run all possible guesses against all possible words and generate
a lookup table of results for fast access during solving
'''

import numpy as np
import pandas as pd
import math
import json
import time
import itertools as it
import os
from wordle import *

test_words = np.loadtxt('./data/test.txt', dtype=str)
all_words = np.loadtxt('./data/allowed_words.txt', dtype=str)
possible_words = np.loadtxt('./data/solutions.txt', dtype=str)

if not os.path.exists('./data/word_indices.json'):
    with open('./data/word_indices.json', 'w') as f:
        word_indices = {word: i for i, word in enumerate(all_words)}
        json.dump(word_indices, f)

NUM_ALLOWED = len(all_words)
NUM_POSSIBLE = len(possible_words)

def main():
    # Get pattern matrix (check if already saved in file first)
    if os.path.exists('./data/pattern_matrix.npy'):
        pattern_matrix = np.load('./data/pattern_matrix.npy')
    else:
        pattern_matrix = generate_pattern_matrix(all_words, all_words)
        np.save('./data/pattern_matrix.npy', pattern_matrix)

    # Get entropies (check if already saved in file first)
    if os.path.exists('./data/entropies.json'):
        with open('./data/entropies.json', 'r') as f:
            entropies = json.load(f)
    else:
        entropies = {}
        for i, word in enumerate(all_words):
            entropies[word] = get_entropy(i, pattern_matrix)
        
        with open('./data/entropies.json', 'w') as f:
            json.dump(entropies, f)

    # Get relative frequencies
    frequencies = {}
    if os.path.exists('./data/word_freq_updated.json'):
        with open('./data/word_freq_updated.json', 'r') as f:
            frequencies = json.load(f)
    else:
        print("Need relative word frequency data")
        return

    sorted_by_freqs = sorted(frequencies.keys(), key=frequencies.get)

    # entropy_df = pd.DataFrame.from_dict(entropies, orient='index', columns=['expected_info_gain'])
    # print(entropy_df.sort_values(by='expected_info_gain', ascending=False).head(10))
    
    return

def safe_log(x):
    return math.log2(x) if x > 0 else 0

def words_to_int_arrays(words):
    return np.array([[ord(c) for c in w] for w in words], dtype=np.uint8)


def generate_pattern_matrix(words1, words2):
    """
    A pattern for two words represents the wordle-similarity
    pattern (grey -> 0, yellow -> 1, green -> 2) but as an integer
    between 0 and 3^5. Reading this integer in ternary gives the
    associated pattern.

    This function computes the pairwise patterns between two lists
    of words, returning the result as a grid of hash values. Since
    this can be time-consuming, many operations are vectorized
    (perhaps at the expense of easier readibility), and the result
    is saved to a file so that this only needs to be evaluated once, and
    all remaining pattern matching is a lookup.
    """

    # Number of letters/words
    nl = len(words1[0])
    nw1 = len(words1)  # Number of words
    nw2 = len(words2)  # Number of words

    # Convert word lists to integer arrays
    word_arr1, word_arr2 = map(words_to_int_arrays, (words1, words2))

    # equality_grid keeps track of all equalities between all pairs
    # of letters in words. Specifically, equality_grid[a, b, i, j]
    # is true when words[a][i] == words[b][j]
    equality_grid = np.zeros((nw1, nw2, nl, nl), dtype=bool)
    for i, j in it.product(range(nl), range(nl)):
        equality_grid[:, :, i, j] = np.equal.outer(word_arr1[:, i], word_arr2[:, j])

    # full_pattern_matrix[a, b] should represent the 5-color pattern
    # for guess a and answer b, with 0 -> grey, 1 -> yellow, 2 -> green
    full_pattern_matrix = np.zeros((nw1, nw2, nl), dtype=np.uint8)

    # Green pass
    for i in range(nl):
        matches = equality_grid[:, :, i, i].flatten()  # matches[a, b] is true when words[a][i] = words[b][i]
        full_pattern_matrix[:, :, i].flat[matches] = EXACT

        for k in range(nl):
            # If it's a match, mark all elements associated with
            # that letter, both from the guess and answer, as covered.
            # That way, it won't trigger the yellow pass.
            equality_grid[:, :, k, i].flat[matches] = False
            equality_grid[:, :, i, k].flat[matches] = False

    # Yellow pass
    for i, j in it.product(range(nl), range(nl)):
        matches = equality_grid[:, :, i, j].flatten()
        full_pattern_matrix[:, :, i].flat[matches] = MISPLACED
        for k in range(nl):
            # Similar to above, we want to mark this letter
            # as taken care of, both for answer and guess
            equality_grid[:, :, k, j].flat[matches] = False
            equality_grid[:, :, i, k].flat[matches] = False

    # Rather than representing a color pattern as a list of integers,
    # store it as a single integer, whose ternary representation corresponds
    # to that list of integers.
    pattern_matrix = np.dot(
        full_pattern_matrix,
        (3**np.arange(nl)[::-1]).astype(np.uint8)
    )

    return pattern_matrix

def get_entropy(guess, pattern_matrix, remaining_indices=None):
    patterns = pattern_matrix[guess, remaining_indices]
    patterns, counts = np.unique(patterns, return_counts=True)
    probs = counts / counts.sum()
    return -np.sum(probs * np.log2(probs))

def sigmoid(x):
    return 1 / (1 + np.exp(-x))
    
if __name__ == "__main__":
    main()