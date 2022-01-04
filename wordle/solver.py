from collections import Counter
from . import WORDLE_LENGTH
from .game import Clue

import logging
log = logging.getLogger("rich")


class Constraints:
    def __init__(self):
        self.found_letters = [None] * WORDLE_LENGTH
        self.must_contain = {}
        self.must_not_contain = set()
        self.is_empty = True

    def add_constraint(self, guess, clues):
        for pos, (letter, clue) in enumerate(zip(guess, clues)):
            if clue == Clue.GREEN:
                self.found_letters[pos] = letter
            elif clue == Clue.YELLOW:
                try:
                    self.must_contain[letter].add(pos)
                except KeyError:
                    self.must_contain[letter] = set([pos])
            else:
                self.must_not_contain.add(letter)
        self.is_empty = False

    def fits_constraints(self, word):
        if self.is_empty:  # no clues yet
            return True
        for pos, letter in enumerate(word):
            if self.found_letters[pos] is not None and self.found_letters[pos] != letter:
                return False
            if letter in self.must_contain and pos in self.must_contain[letter]:
                # letter must be in there, but is in wrong position ("yellow" clue)
                return False
            if letter in self.must_not_contain:
                return False
        if not all(letter in word for letter in self.must_contain):
            return False
        return True


class Solver:
    def __init__(self, wordlist):
        self._words = wordlist
        self._constraints = None

    def reset(self):
        self._constraints = Constraints()

    def add_clue(self, guess, clue):
        self._constraints.add_constraint(guess, clue)

    def make_guess(self):
        raise NotImplementedError()


class NaiveFrequencySolver(Solver):
    """Tries to solve a Wordle by picking the most frequent letter in each position.

    From all valid words that obey all the discovered clues, this solver will
    pick the one that maximizes the observed letter frequencies at each
    position.
    """

    def __init__(self, wordlist):
        super().__init__(wordlist)
        self._initial_guess = self._find_best_initial_guess()

    def _find_best_initial_guess(self):
        candidates = Counter()
        for word in self._words:
            # No duplicate letters for the initial guess
            if len(word) != len(set(word)):
                continue
            candidates[word] = sum(self._words.letters[pos][letter] for pos, letter in enumerate(word))
        return candidates.most_common(1)[0][0]

    def make_guess(self):
        if self._constraints.is_empty:
            return self._initial_guess

        candidates = Counter()
        for word in self._words:
            if not self._constraints.fits_constraints(word):
                continue  # obey all constraints
            candidates[word] = sum(self._words.letters[pos][letter] for pos, letter in enumerate(word))
        return candidates.most_common(1)[0][0]
