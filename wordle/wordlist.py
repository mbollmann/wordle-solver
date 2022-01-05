from collections import Counter
import os
from . import WORDLE_LENGTH


class Wordlist(list):
    """A list of words with a fixed length that also provides
    quick access to letter frequencies."""

    def __init__(self, filename):
        super().__init__()
        self.letters = [None] * WORDLE_LENGTH
        self._load_wordlist(filename)
        self._calculate_letter_frequencies()

    def _load_wordlist(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        words = set()
        with open(filename, "r") as f:
            for line in f:
                word = line.strip()
                if len(word) == WORDLE_LENGTH:
                    words.add(word)
        self.extend(sorted(words))

    def _calculate_letter_frequencies(self):
        for pos in range(WORDLE_LENGTH):
            self.letters[pos] = Counter(word[pos] for word in self)
