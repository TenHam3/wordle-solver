'''
Simulator for Wordle's game mechanics to be used in simulation (solver.py)
'''

from collections import Counter
import numpy as np

# Examples for edge case yellows:

# SISSY is the word
# PSYCH is guess - XYYXX
# STASH is guess - GXXGX
# SPILL is guess - GXYXX

# ISSUE is the word
# SISSY is guess - YYGXX
# MASKS is guess - XXGXY
# ISLES is guess - GGXYY

# SPEED is guess (not the word)
# ABIDE is word - SPEED's evaluations would be XXYXY
# ERASE is word - SPEED's evaluations would be YXYYX
# STEAL is word - SPEED's evaluations would be GXGXX
# CREPE is word - SPEED's evaluations would be XYGYX

# G - green, Y - yellow, X - gray
# 0 - gray, 1 - yellow, 2 - green
MISS = np.uint8(0)
MISPLACED = np.uint8(1)
EXACT = np.uint8(2)

def string_to_pattern_int(pattern_string):
    # Converts ternary pattern string (base 3) to decimal (base 10) int
    return int(pattern_string, 3)


def pattern_int_to_string(pattern):
    string = []
    while pattern > 0:
        pattern, remainder = divmod(pattern, 3)
        string.append(remainder)
    return string.reverse()

def get_emoji_pattern(pattern):
    d = {MISS: "⬛", MISPLACED: "🟨", EXACT: "🟩"}
    return "".join(d[x] for x in pattern_int_to_string(pattern))

def word_eval(word, guess):
    # Count occurrences of each letter in the target word
    counts = Counter(word)
    res = ['X'] * 5

    # First pass for greens, possible yellows, and grays
    for i in range(len(guess)):
        curr = guess[i]
        if counts[curr] > 0:
            if word[i] == curr:
                # Green, correct position
                res[i] = 'G'
                counts[curr] -= 1
            else:
                # May be yellow, mark as M for now
                res[i] = 'M'
        # else:
            # Gray, not in word, so keep X

    # Second pass for yellows
    for i in range(len(guess)):
        if res[i] == 'M':
            curr = guess[i]
            if counts[curr] > 0:
                res[i] = 'Y'
                counts[curr] -= 1
            else:
                res[i] = 'X'
    
    return res

def simulate_game(word, guesses):
    evaluations = []
    # Evaluate each guess against the target word
    for guess in guesses:
        evaluations.append(word_eval(word, guess))
    
    # Return evaluations and number of guesses taken
    if guesses[-1] == word:
        return evaluations, len(guesses)
    else:
        return evaluations, len(guesses) + 1  # +1 for failure