from enum import Enum
import random
from . import WORDLE_LENGTH, MAX_ROUNDS


class Clue(Enum):
    GREY = 1
    YELLOW = 2
    GREEN = 3

    def as_emoji(self):
        if self == Clue.GREY:
            return "⬜"
        elif self == Clue.YELLOW:
            return "🟨"
        return "🟩"

    def as_string(self):
        return str(self._value_)


class GameStatus(Enum):
    RUNNING = 0
    LOST = 1
    WON = 2


class Wordle:
    def __init__(self, target):
        assert len(target) == WORDLE_LENGTH, f"Word must have length {WORDLE_LENGTH}, got {target}"
        self._target = target
        self._round = 0
        self._history = []
        self._status = GameStatus.RUNNING

    @classmethod
    def pick_randomly_from(cls, wordlist):
        word = random.choice(wordlist)
        return cls(word)

    def guess(self, word):
        assert len(word) == len(self._target), f"Guess has the wrong length"

        clues = []
        for x, y in zip(word, self._target):
            if x == y:
                clues.append(Clue.GREEN)
            elif x in self._target:
                clues.append(Clue.YELLOW)
            else:
                clues.append(Clue.GREY)
        self._round += 1

        if all(clue == Clue.GREEN for clue in clues):
            self._status = GameStatus.WON
        elif self._round == MAX_ROUNDS:
            self._status = GameStatus.LOST

        self._history.append((word, clues))
        return clues

    @property
    def is_running(self):
        return self._status == GameStatus.RUNNING

    @property
    def is_won(self):
        return self._status == GameStatus.WON

    @property
    def target(self):
        return self._target

    @property
    def round(self):
        return self._round
