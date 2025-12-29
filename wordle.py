'''
Simulator for Wordle's game mechanics to be used in simulation (solver.py)
'''

from collections import Counter

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

