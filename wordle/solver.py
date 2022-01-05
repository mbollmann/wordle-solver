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

    def fits_constraints(self, word, invert_greens=False):
        if self.is_empty:  # no clues yet
            return True
        for pos, letter in enumerate(word):
            if (
                self.found_letters[pos] is not None
                and not invert_greens
                and self.found_letters[pos] != letter
            ):
                return False
            if letter in self.must_contain and pos in self.must_contain[letter]:
                # letter must be in there, but is in wrong position ("yellow" clue)
                return False
            if letter in self.must_not_contain:
                return False
        if not all(letter in word for letter in self.must_contain):
            return False
        if invert_greens and any(
            letter in word for letter in self.found_letters if letter is not None
        ):
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
            candidates[word] = sum(
                self._words.letters[pos][letter] for pos, letter in enumerate(word)
            )
        return candidates.most_common(1)[0][0]

    def make_guess(self):
        if self._constraints.is_empty:
            return self._initial_guess

        candidates = Counter()
        for word in self._words:
            if not self._constraints.fits_constraints(word):
                continue  # obey all constraints
            candidates[word] = sum(
                self._words.letters[pos][letter] for pos, letter in enumerate(word)
            )
        return candidates.most_common(1)[0][0]


class FlexFrequencySolver(NaiveFrequencySolver):
    """..."""

    def make_guess(self):
        if self._constraints.is_empty:
            return self._initial_guess

        # How many letters we still need to find (in the worst case,
        # i.e. assuming no duplicate letters). Considers:
        # - how many positions we definitely know
        # - how many other, different letters we have already found (in the wrong position)
        letters_to_find = (
            WORDLE_LENGTH
            - sum(x is not None for x in self._constraints.found_letters)
            - len(
                set(self._constraints.must_contain.keys())
                - set(self._constraints.found_letters)
            )
        )

        invert_greens = letters_to_find > 2

        candidates = Counter()
        while not candidates:
            for word in self._words:
                if not self._constraints.fits_constraints(
                    word, invert_greens=invert_greens
                ):
                    continue  # obey all constraints
                candidates[word] = sum(
                    self._words.letters[pos][letter] for pos, letter in enumerate(word)
                )
            # In case running with invert_greens=True didn't give any
            # candidates, this will repeat the loop without this condition
            invert_greens = False

        return candidates.most_common(1)[0][0]
