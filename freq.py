"""
Generates word_freq.json for the relative frequencies of each allowed word
"""

import numpy as np
import json
import numbers
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl

all_words = np.loadtxt('./data/allowed_words.txt', dtype=str)

all_words = set(word.upper() for word in all_words)

kernel_path = r"C:\Program Files\Wolfram Research\Wolfram\14.3\WolframKernel.exe"
with WolframLanguageSession(kernel=kernel_path) as session:

    freqs = {}

    for word in sorted(all_words):
        word = word.lower()
        freq = session.evaluate(wl.WordFrequencyData(word))
        if isinstance(freq, numbers.Number):
            freqs[word] = freq
        else:
            freqs[word] = 0.0
        print(f"Frequency of {word}: {freqs[word]}")
        
    with open('./data/word_freq_updated.json', 'w') as f:
        json.dump(freqs, f)