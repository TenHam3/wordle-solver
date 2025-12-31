'''
Solver application for user to utilize during a Wordle game
'''

import numpy as np
import os
import random
from wordle import *
from simulator import *

# Each tile's aria-label uses the format:
# nth letter, [letter], [color]
# color = "correct" (green), "present in another position" (yellow), "absent" (gray)

test_words = np.loadtxt('./data/test.txt', dtype=str)
all_words = np.loadtxt('./data/allowed_words.txt', dtype=str)
possible_words = np.loadtxt('./data/possible_words.txt', dtype=str)

NUM_ALLOWED = len(all_words)
NUM_POSSIBLE = len(possible_words)

def main():
    if os.path.exists('./data/word_indices.json'):
        with open('./data/word_indices.json', 'r') as f:
            word_indices = json.load(f)
    else:
        print("Need to generate word-index mapping first. Run simulator.py")
        return

    # Get pattern matrix (check if already saved in file first)
    if os.path.exists('./data/pattern_matrix.npy'):
        pattern_matrix = np.load('./data/pattern_matrix.npy')
    else:
        print("Need to generate pattern matrix first. Run simulator.py")
        return

    # Get entropies (check if already saved in file first)
    if os.path.exists('./data/entropies.json'):
        with open('./data/entropies.json', 'r') as f:
            entropies = json.load(f)
    else:
        print("Need to generate entropies first. Run simulator.py")
        return
    
    answer = random.choice(possible_words)
    print(f"Answer is {answer}")

    # answer = "siren"

    possible_words_filtered = all_words.copy()
    guesses = set()
    for i in range(6):
        candidates = {w: e for w, e in entropies.items() if w not in guesses}
        guess = max(candidates, key=candidates.get)
        guesses.add(guess)
        pattern = word_eval(answer, guess)
        pattern_int = string_to_pattern_int(pattern)
        emoji_pattern = get_emoji_pattern(pattern_int)
        print(f"Guess {i+1}: {guess} -> {emoji_pattern}")

        if guess == answer:
            print(f"Solved! The word was {answer}.")
            break

        # Filter possible words based on the pattern
        possible_indices = []
        guess_index = word_indices[guess]
        for word in all_words:
            word_index = word_indices[word]
            if pattern_matrix[guess_index, word_index] == pattern_int:
                possible_indices.append(word_index)
        
        possible_words_filtered = all_words[possible_indices]
        print(f"{len(possible_words_filtered)} possible words remaining.")

        if len(possible_words_filtered) == 0:
            print("No possible words remaining. Something went wrong.")
            break

        # Update entropies for the next guess
        entropies = {}
        for word in possible_words_filtered:
            idx = word_indices[word]
            entropies[word] = get_entropy(idx, pattern_matrix, possible_indices)

    return

if __name__ == "__main__":
    main()