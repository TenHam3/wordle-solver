"""
Generates allowed words list based on the predicted updated solution set obtained by the scraper
"""

import numpy as np

all_words = np.loadtxt('./data/allowed_words.txt', dtype=str)
possible_words = np.loadtxt('./data/solutions.txt', dtype=str)

all_words = set(word.upper() for word in all_words)
print(f"Before adding words: {len(all_words)}")

for word in possible_words:
    all_words.add(word.upper())

print(f"Total allowed words: {len(all_words)}")

with open('./data/allowed_words.txt', 'w') as f:
    for word in sorted(all_words):
        f.write(word + '\n')