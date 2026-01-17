'''
Solver application for user to utilize during a Wordle game
'''

from ast import pattern
import numpy as np
import os
import random
from wordle import *
from simulator import *

# Each tile's aria-label uses the format:
# nth letter, [letter], [color]
# color = "correct" (green), "present in another position" (yellow), "absent" (gray)

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

    # Get expected scores (check if already saved in file first)
    if os.path.exists('./data/initial_expected_scores.json'):
        with open('./data/initial_expected_scores.json', 'r') as f:
            expected_scores = json.load(f)
    else:
        print("Need to generate entropies first. Run simulator.py")
        return
    
    freqs = get_freqs()

    response = ""
    allowed = {"1", "2", "3", "4"}

    while response not in allowed:
        print("1) Solver Assistant Mode")
        print("2) Test Bot Against Particular Word")
        print("3) Test Bot Against All Words")
        print("4) Print Results")
        response = input("Which would want: ")
    
    match response:
        case "1":
            # Test manually from user-given Wordle feedback
            cheating = ""
            allowed_chars = {"Y", "y", "N", "n"}
            while cheating not in allowed_chars:
                cheating = input("Do you want to cheat (Y/y - Yes, N/n - No): ")
            cheating = cheating.upper() == 'Y'

            play_game_assistant_mode(pattern_matrix, expected_scores, word_indices, freqs, cheating=cheating)

        case "2":
            # Test bot against user input word
            answer = ""
            while len(answer) != 5 or answer not in possible_words:
                answer = input("Enter the word to test the bot against: ").strip().upper()
                if len(answer) != 5:
                    print("Please enter a 5-letter word")
                elif answer.upper() not in possible_words:
                    print("Not a valid word")

            cheating = ""
            allowed_chars = {"Y", "y", "N", "n"}
            while cheating not in allowed_chars:
                cheating = input("Do you want to cheat (Y/y - Yes, N/n - No): ")
            cheating = cheating.upper() == 'Y'

            play_game_bot_with_freqs(answer, pattern_matrix, expected_scores, word_indices, freqs, cheating=cheating)

        case "3":
            # Test against all words
            cheating = ""
            allowed_chars = {"Y", "y", "N", "n"}
            while cheating not in allowed_chars:
                cheating = input("Do you want to cheat (Y/y - Yes, N/n - No): ")
            cheating = cheating.upper() == 'Y'

            simulate_all_games_bot(pattern_matrix, expected_scores, word_indices, freqs, cheating=cheating)

        case "4":
            # Print results
            filename = input("Enter filename that stores results: ")
            filename = filename.strip()

            if os.path.exists(f'./data/{filename}.json'):
                with open(f'./data/{filename}.json', 'r') as f:
                    results = json.load(f)
                    print(f"Attempt distribution over all possible words:\n")
                    keys = sorted([int(k) for k in results.keys()])
                    for k in keys:
                        print(f"{k} attempts: {len(results[str(k)])}")
                    
                    print("")
                    # for i in range(max(keys) - 3, max(keys) + 1):
                    #     worst_words = results[str(i)]
                    #     print(f"Worst words for {i} attempts: {worst_words}\n")
                    
                    total = sum(len(results[str(k)]) for k in keys)
                    average = sum(k * len(results[str(k)]) for k in keys) / total
                    print(f"Average number of attempts over all possible words: {average:.4f}")
                
            else:
                print("File not found.")
                

    # Test bot against a random or particular word
    # answer = random.choice(possible_words)
    # answer = "FLOAT"
    # play_game_bot(answer, pattern_matrix, entropies, word_indices)

    # Test manually against a random word or particular word
    # answer = random.choice(possible_words)
    # answer = "OOMPH"
    # play_game_piloted(answer, pattern_matrix, entropies, word_indices)

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

def play_game_assistant_mode(pattern_matrix, initial_expected_scores, word_indices, freqs, cheating=False):
    guesses = set()
    score = 0
    win = False
    word_scores = initial_expected_scores.copy() # Expected scores
    remaining_words = all_words.copy()
    freq_probs = get_freq_probs(freqs) if not cheating else get_cheat_freq_probs()
    weights = get_weights(remaining_words, freq_probs) # Probs
    # entropies = get_entropies(all_words, remaining_words, weights) # Entropies
    possible_answers = set(possible_words)

    for i in range(6):
            score += 1
            # Need to aggregate expected score, entropy, and probability of being answer
            candidates = {w: s for w, s in word_scores.items() if w not in guesses}
            suggested_guesses = sorted(candidates, key=candidates.get)
            best_guess = suggested_guesses[0]

            if score > 1:
                pattern_probs = get_distributions(remaining_words, remaining_words, weights)
                idx = remaining_words.index(best_guess)

                # Switch to probe guessing if there is a dominant pattern
                if (max(pattern_probs[idx]) > 0.4 and 
                    ((cheating and len(possible_answers) > 2) or (not cheating and len(remaining_words) > 2))):
                    # Get entropies of all_words vs possible_words, next guess is max entropy over possible words
                    print(f"Using probe guessing for guess {score}")
                    entropies = get_entropies(all_words, remaining_words, weights)
                    candidates = {str(w): e for w, e in zip(all_words, entropies) if w not in guesses}
                    suggested_guesses = sorted(candidates, key=candidates.get, reverse=True)
            
            # Get user guess
            user_guess = get_user_guess(suggested_guesses)
            guesses.add(user_guess)

            # Get pattern user got from Wordle
            pattern = get_wordle_feedback()

            pattern_int = string_to_pattern_int(pattern)
            emoji_pattern = get_emoji_pattern(pattern_int)
            print(f"Guess {i+1}: {user_guess} -> {emoji_pattern}")

            if pattern_int == 242: # 242 means pattern is all 2's (green) so they guessed correctly
                print(f"Solved! The word was {user_guess}.")
                win = True
                break

            # Filter possible words based on the pattern
            new_remaining_words = []
            remaining_indices = set()
            guess_index = word_indices[user_guess]
            for word in all_words:
                word_index = word_indices[word]
                if (pattern_matrix[guess_index, word_index] == pattern_int and 
                    ((cheating and word in possible_answers) or (not cheating and word in remaining_words))):
                    new_remaining_words.append(str(word))
                    remaining_indices.add(word_index)
            remaining_words = new_remaining_words
            possible_answers = possible_answers.intersection(set(remaining_words))

            print(f"{len(candidates) - 1} possible candidates remaining.")
            print(f"{len(remaining_words)} possible solution words remaining.")
            if len(remaining_words) == 0:
                print("No possible words remaining. Something went wrong.")
                break

            # Update entropies for the next guess
            freq_probs = get_freq_probs(freqs) if not cheating else get_cheat_freq_probs()
            weights = get_weights(remaining_words, freq_probs)
            expected_scores = get_expected_scores(all_words, remaining_words, weights)
            word_scores = {str(all_words[i]): expected_scores[i] for i in range(len(all_words)) if i in remaining_indices}

    return score if win else -1

def play_game_bot_with_freqs(answer, pattern_matrix, initial_expected_scores, word_indices, freqs, cheating=False):
    print(f"Answer is {answer}")
    guess = ""
    score = 1
    guesses = set()
    word_scores = initial_expected_scores.copy()
    remaining_words = list(all_words.copy())
    freq_probs = get_freq_probs(freqs) if not cheating else get_cheat_freq_probs()
    weights = get_weights(remaining_words, freq_probs)
    possible_answers = set(possible_words)
    
    while guess.lower() != answer.lower():
            candidates = {w: s for w, s in word_scores.items() if w not in guesses}
            guess = min(candidates, key=candidates.get)
            
            if score > 1:
                pattern_probs = get_distributions(remaining_words, remaining_words, weights)
                idx = remaining_words.index(guess)

                # Switch to probe guessing if there is a dominant pattern
                if (max(pattern_probs[idx]) > 0.4 and 
                    ((cheating and len(possible_answers) > 2) or (not cheating and len(remaining_words) > 2))):
                    # Get entropies of all_words vs possible_words, next guess is max entropy over possible words
                    print(f"Using probe guessing for guess {score}")
                    entropies = get_entropies(all_words, remaining_words, weights)
                    candidates = {str(w): e for w, e in zip(all_words, entropies) if w not in guesses}
                    guess = max(candidates, key=candidates.get)
            
            guesses.add(guess)
            pattern = word_eval(answer, guess)
            pattern_int = string_to_pattern_int(pattern)
            emoji_pattern = get_emoji_pattern(pattern_int)
            print(f"Guess {score}: {guess} -> {emoji_pattern}")

            if guess.lower() == answer.lower():
                print(f"Solved! The word was {answer}.")
                break

            # Filter possible words based on the pattern
            new_remaining_words = []
            remaining_indices = set()
            guess_index = word_indices[guess]
            for word in all_words:
                word_index = word_indices[word]
                if (pattern_matrix[guess_index, word_index] == pattern_int and 
                    ((cheating and word in possible_answers) or (not cheating and word in remaining_words))):
                    new_remaining_words.append(str(word))
                    remaining_indices.add(word_index)
            remaining_words = new_remaining_words
            possible_answers = possible_answers.intersection(set(remaining_words))

            # print(f"{len(candidates) - 1} possible candidates remaining.")
            print(f"{len(remaining_words)} possible solution words remaining.")

            if len(remaining_words) == 0:
                print("No possible words remaining. Something went wrong.")
                break

            # Update entropies for the next guess
            freq_probs = get_freq_probs(freqs) if not cheating else get_cheat_freq_probs()
            weights = get_weights(remaining_words, freq_probs)
            expected_scores = get_expected_scores(all_words, remaining_words, weights)
            word_scores = {str(all_words[i]): expected_scores[i] for i in range(len(all_words)) if i in remaining_indices}

            score += 1

    return score

def simulate_all_games_bot(pattern_matrix, initial_expected_scores, word_indices, freqs, cheating=False):
    filename = input("Enter filename to store results: ")
    filename = filename.strip()
    attempt_count = {}
    for answer in possible_words:
        score = play_game_bot_with_freqs(answer, pattern_matrix, initial_expected_scores, word_indices, freqs, cheating=cheating)
        if score not in attempt_count:
            attempt_count[score] = {str(answer)}
        else:
            attempt_count[score].add(str(answer))

    print(f"Attempt distribution over all possible words:\n")
    keys = sorted(attempt_count.keys())
    for k in keys:
        print(f"{k} attempts: {len(attempt_count[k])}")
    
    max_attempts = max(attempt_count.keys())
    worst_words = attempt_count[max_attempts]
    print(f"Worst words were {worst_words} with {max_attempts} attempts.")

    with open(f'./data/{filename}.json', 'w') as f:
        results = {k: list(v) for k, v in attempt_count.items()}
        json.dump(results, f)

def get_user_guess(suggested_guesses):
    user_guess = ""
    while len(user_guess) != 5 or user_guess.upper() not in all_words:
        print(f"Top 10 suggested guesses: {suggested_guesses[:10]}")
        user_guess = input(f"\nEnter a guess: ").strip()
        if len(user_guess) != 5:
            print("Please enter a 5-letter word")
        elif user_guess.upper() not in all_words:
            print("Not a valid word")
    return user_guess.upper() 

def get_wordle_feedback():
    pattern = ""
    allowed_chars = {"G", "g", "Y", "y", "X", "x"}
    diff = {}
    while len(pattern) != 5 or diff:
        pattern = input("Provide the color pattern given by Wordle (G/g - green, Y/y - yellow, X/x - gray): ").strip()
        diff = set(pattern) - allowed_chars
        if len(pattern) != 5:
            print("Please enter a pattern of length 5")
        elif diff:
            print("Please input a valid pattern given from Wordle feedback (G/g - green, Y/y - yellow, X/x - gray)")
    
    # Convert pattern to ternary string
    pattern = pattern.upper()
    pattern = list(pattern)
    for j in range(len(pattern)):
        c = pattern[j]
        if c == 'G':
            pattern[j] = EXACT
        elif c == 'Y':
            pattern[j] = MISPLACED
        else:
            pattern[j] = MISS
    
    return pattern

if __name__ == "__main__":
    main()