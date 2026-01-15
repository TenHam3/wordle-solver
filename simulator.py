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
from scipy.stats import entropy
from wordle import *

all_words = np.loadtxt('./data/allowed_words.txt', dtype=str)
possible_words = np.loadtxt('./data/solutions.txt', dtype=str)

if os.path.exists('./data/word_indices.json'):
    with open('./data/word_indices.json', 'r') as f:
        word_indices = json.load(f)
else:
    with open('./data/word_indices.json', 'w') as f:
        word_indices = {word: i for i, word in enumerate(all_words)}
        json.dump(word_indices, f)

NUM_ALLOWED = len(all_words)
NUM_POSSIBLE = len(possible_words)
PATTERN_MATRIX = None

def main():
    # Get pattern matrix
    # pattern_matrix = get_pattern_matrix(all_words, all_words)

    # Get relative frequencies
    frequencies = get_freqs()

    # Get expected scores
    if not os.path.exists('./data/initial_expected_scores.json'):
        with open('./data/initial_expected_scores.json', 'w') as f:
            freq_probs = get_freq_probs(frequencies)
            weights = get_weights(all_words, freq_probs)
            scores = get_expected_scores(all_words, all_words, weights)
            scores = {word: float(score) for word, score in zip(all_words, scores)}
            json.dump(scores, f)
    else:
        with open('./data/initial_expected_scores.json', 'r') as f:
            scores = json.load(f)
    score_df = pd.DataFrame.from_dict(scores, orient='index', columns=['expected_score'])
    print(score_df.sort_values(by='expected_score', ascending=True).head(10))
    
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

def get_pattern_matrix(words1, words2):
    global PATTERN_MATRIX
    words1_indices = [word_indices[word] for word in words1]
    words2_indices = [word_indices[word] for word in words2]

    if PATTERN_MATRIX is None:
        if os.path.exists('./data/pattern_matrix.npy'):
            PATTERN_MATRIX = np.load('./data/pattern_matrix.npy')
        else:
            PATTERN_MATRIX = generate_pattern_matrix(all_words, all_words)
            np.save('./data/pattern_matrix.npy', PATTERN_MATRIX)
    
    return PATTERN_MATRIX[np.ix_(words1_indices, words2_indices)]

# Calculates entropy for a given guess from pattern matrix
# Only considers potential answers given by remaining indices
def get_entropy(guess, pattern_matrix, remaining_indices=None):
    patterns = pattern_matrix[guess, remaining_indices]
    patterns, counts = np.unique(patterns, return_counts=True)
    probs = counts / counts.sum()
    return -np.sum(probs * np.log2(probs))

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def get_freqs():
    frequencies = {}
    if os.path.exists('./data/word_freq_updated.json'):
        with open('./data/word_freq_updated.json', 'r') as f:
            frequencies = json.load(f)
    else:
        print("Need relative word frequency data")
        return
    return frequencies

# Possible cutoff point at line 6489 (PIKER) of sorted_by_freqs.txt, BASSY (next word) not in solutions
def get_freq_probs(freqs, n=3000, width=10):
    sorted_words = sorted(freqs.keys(), key=freqs.get)
    center = width * ( -0.5 + (n / len(sorted_words)) )
    linspace = np.linspace(center - width / 2, center + width / 2, len(sorted_words))

    freq_probs = {}
    for word, x in zip(sorted_words, linspace):
        freq_probs[word.upper()] = sigmoid(x)
    
    return freq_probs

def get_weights(remaining_words, freq_probs):
    weights = np.array([freq_probs[str(word)] for word in remaining_words])
    total = weights.sum()
    return weights / total if total != 0 else np.zeros(weights.shape)

def get_distributions(all_words, remaining_words, weights):
    # Distributions holds the probability distributions of each word's patterns
    # Rows - allowed words (same order as pattern matrix), Cols - patterns
    distributions = np.zeros( (len(all_words), 3**5) )
    pattern_matrix = get_pattern_matrix(all_words, remaining_words)

    n = np.arange(len(all_words))
    for i, weight in enumerate(weights):
        distributions[n, pattern_matrix[:,i]] += weight

    return distributions

def get_entropy_with_freqs(distributions):  
    axis = len(distributions.shape) - 1
    return entropy(distributions, base=2, axis=axis)

def get_entropies(all_words, remaining_words, weights):
    if weights.sum() == 0:
        return np.zeros(len(all_words))
    distributions = get_distributions(all_words, remaining_words, weights)
    return get_entropy_with_freqs(distributions)

# Maximize the expected score instead of expected information gain
# E[score] = P(word) * guess_# + 
# (1 - P(word)) * (guess_# + f(entropy after prev guess - expected entropy of word))

# Regrssion-based heuristic for how many guesses remain given the entropy (from 3B1B)
def guesses_from_entropy(entropy):
    min_score = 2**(-entropy) + 2 * (1 - 2**(-entropy))
    return min_score + 1.5 * entropy / 11.5

# Expected scores for remaining words given their weights/probs of being the answer
def get_expected_scores(all_words, remaining_words, weights):
    curr_entropy = get_entropy_with_freqs(weights)
    expected_entropies = get_entropies(all_words, remaining_words, weights)
    word_weights = dict(zip(remaining_words, weights))
    probs = np.array([word_weights.get(word, 0) for word in all_words])
    return probs + (1 - probs) * (1 + guesses_from_entropy(curr_entropy - expected_entropies))

if __name__ == "__main__":
    main()