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
possible_words = np.loadtxt('./data/solutions.txt', dtype=str)

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
    
    # Test bot against a random or particular word
    # answer = random.choice(possible_words)
    # answer = "FLOAT"
    # play_game_bot(answer, pattern_matrix, entropies, word_indices)

    # Test manually against a random word or particular word
    # answer = random.choice(possible_words)
    # answer = "OOMPH"
    # play_game_piloted(answer, pattern_matrix, entropies, word_indices)

    # Test manually from user-given Wordle feedback
    play_game_piloted_no_ans(pattern_matrix, entropies, word_indices)

    # Test against all words
    # attempt_count = {}
    # max_attempts = 0
    # worst_words = set()
    # for answer in possible_words:
    #     score = play_game(answer, pattern_matrix, entropies, word_indices)
    #     attempt_count[score] = attempt_count.get(score, 0) + 1
        
    #     if score > max_attempts: 
    #         worst_words = set()
    #         worst_words.add(str(answer))
    #     elif score == max_attempts:
    #         worst_words.add(str(answer))
        
    #     max_attempts = max(max_attempts, score)

    # print(f"Attempt distribution over all possible words:\n")
    # keys = sorted(attempt_count.keys())
    # for k in keys:
    #     print(f"{k} attempts: {attempt_count[k]}")
    
    # print(f"Worst words were {worst_words} with {max_attempts} attempts.")

def play_game_bot(answer, pattern_matrix, entropies, word_indices):
    print(f"Answer is {answer}")
    guess = ""
    i = 0
    guesses = set()
    entropies_copy = entropies.copy() 
    while guess.lower() != answer.lower():
            candidates = {w: e for w, e in entropies_copy.items() if w not in guesses}
            guess = max(candidates, key=candidates.get)
            guesses.add(guess)
            pattern = word_eval(answer, guess)
            pattern_int = string_to_pattern_int(pattern)
            emoji_pattern = get_emoji_pattern(pattern_int)
            print(f"Guess {i+1}: {guess} -> {emoji_pattern}")

            if guess.lower() == answer.lower():
                print(f"Solved! The word was {answer}.")
                break

            # Filter possible words based on the pattern
            possible_indices = []
            guess_index = word_indices[guess]
            for word in all_words:
                word_index = word_indices[word]
                if pattern_matrix[guess_index, word_index] == pattern_int and word in candidates:
                    possible_indices.append(word_index)
            
            possible_words_filtered = all_words[possible_indices]
            print(f"{len(candidates) - 1} possible candidates remaining.")
            print(f"{len(possible_words_filtered)} possible solution words remaining.")

            if len(possible_words_filtered) == 0:
                print("No possible words remaining. Something went wrong.")
                break

            # Update entropies for the next guess
            entropies_copy = {}
            for word in possible_words_filtered:
                idx = word_indices[word]
                entropies_copy[word] = get_entropy(idx, pattern_matrix, possible_indices)
            i += 1

    return i + 1

def play_game_piloted(answer, pattern_matrix, entropies, word_indices):
    print(f"Answer is {answer}")
    guesses = set()
    entropies_copy = entropies.copy() 
    score = 0
    for i in range(6):
            score += 1
            candidates = {w: e for w, e in entropies_copy.items() if w not in guesses}
            suggested_guess = max(candidates, key=candidates.get)
            user_guess = ""
            while len(user_guess) != 5 or user_guess.upper() not in all_words:
                user_guess = input(f"Enter a guess (suggested best guess is {suggested_guess}): ")
                if len(user_guess) != 5:
                    print("Please enter a 5-letter word")
                elif user_guess.upper() not in all_words:
                    print("Not a valid word")
            
            guesses.add(user_guess)
            pattern = word_eval(answer, user_guess)
            pattern_int = string_to_pattern_int(pattern)
            emoji_pattern = get_emoji_pattern(pattern_int)
            print(f"Guess {i+1}: {user_guess} -> {emoji_pattern}")

            if user_guess.lower() == answer.lower():
                print(f"Solved! The word was {answer}.")
                break

            # Filter possible words based on the pattern
            possible_indices = []
            guess_index = word_indices[user_guess.upper()]
            for word in all_words:
                word_index = word_indices[word]
                if pattern_matrix[guess_index, word_index] == pattern_int and word in candidates:
                    possible_indices.append(word_index)
            
            possible_words_filtered = all_words[possible_indices]
            print(f"{len(candidates) - 1} possible candidates remaining.")
            print(f"{len(possible_words_filtered)} possible solution words remaining.")

            if len(possible_words_filtered) == 0:
                print("No possible words remaining. Something went wrong.")
                break

            # Update entropies for the next guess
            entropies_copy = {}
            for word in possible_words_filtered:
                idx = word_indices[word]
                entropies_copy[word] = get_entropy(idx, pattern_matrix, possible_indices)

    return score

def play_game_piloted_no_ans(pattern_matrix, entropies, word_indices):
    guesses = set()
    entropies_copy = entropies.copy() 
    score = 0
    for i in range(6):
            score += 1
            candidates = {w: e for w, e in entropies_copy.items() if w not in guesses}
            suggested_guess = max(candidates, key=candidates.get)
            user_guess = ""
            while len(user_guess) != 5 or user_guess.upper() not in all_words:
                user_guess = input(f"Enter a guess (suggested best guess is {suggested_guess}): ")
                if len(user_guess) != 5:
                    print("Please enter a 5-letter word")
                elif user_guess.upper() not in all_words:
                    print("Not a valid word")
            
            guesses.add(user_guess)

            pattern = ""
            allowed_chars = {"G", "g", "Y", "y", "X", "x"}
            diff = {}
            while len(pattern) != 5 or diff:
                pattern = input("Provide the color pattern given by Wordle (G/g - green, Y/y - yellow, X/x - gray): ")
                diff = set(pattern) - allowed_chars
                if len(pattern) != 5:
                    print("Please enter a pattern of length 5")
                elif diff:
                    print("Please input a valid pattern given from Wordle feedback (G/g - green, Y/y - yellow, X/x - gray)")

            pattern = list(pattern)
            for j in range(len(pattern)):
                c = pattern[j]
                if c.upper() == 'G':
                    pattern[j] = EXACT
                elif c.upper() == 'Y':
                    pattern[j] = MISPLACED
                else:
                    pattern[j] = MISS

            pattern_int = string_to_pattern_int(pattern)
            emoji_pattern = get_emoji_pattern(pattern_int)
            print(f"Guess {i+1}: {user_guess} -> {emoji_pattern}")

            if pattern_int == 242: # 242 means pattern is all 2's (green) so they guessed correctly
                print(f"Solved! The word was {user_guess.upper()}.")
                break

            # Filter possible words based on the pattern
            possible_indices = []
            guess_index = word_indices[user_guess.upper()]
            for word in all_words:
                word_index = word_indices[word]
                if pattern_matrix[guess_index, word_index] == pattern_int and word in candidates:
                    possible_indices.append(word_index)
            
            possible_words_filtered = all_words[possible_indices]
            print(f"{len(candidates) - 1} possible candidates remaining.")
            print(f"{len(possible_words_filtered)} possible solution words remaining.")

            if len(possible_words_filtered) == 0:
                print("No possible words remaining. Something went wrong.")
                break

            # Update entropies for the next guess
            entropies_copy = {}
            for word in possible_words_filtered:
                idx = word_indices[word]
                entropies_copy[word] = get_entropy(idx, pattern_matrix, possible_indices)
    
    return score

if __name__ == "__main__":
    main()