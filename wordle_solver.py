#!/usr/bin/env python3

"""Usage: wordle_solver.py WORDLIST [options]

Arguments:
  WORDLIST                 Lexicon file with one word per line.

Options:
  -n, --num-trials NUM     Number of trials to run. [default: 10]
  -s, --seed NUM           Use a fixed seed for reproducibility.
  --debug                  Output debug-level info about what the script is doing.
  --help                   This helpful text.
"""

from docopt import docopt
import logging
import random
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import track

from wordle import Wordle, Wordlist, Clue
from wordle.solver import NaiveFrequencySolver

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)
log = logging.getLogger("rich")
console = Console()


def format_clue(clue):
    return ''.join(c.as_emoji() for c in clue)


def run_trial(solver, wordlist):
    wordle = Wordle.pick_randomly_from(wordlist)
    log.debug(f"Running game with target word: '{wordle.target}'")
    solver.reset()
    guess, clue = None, None
    while wordle.is_running:
        if guess is not None:
            solver.add_clue(guess, clue)
        guess = solver.make_guess()
        clue = wordle.guess(guess)
        log.debug(f"  {wordle.round}:  {guess}  {format_clue(clue)}")
    return wordle


def main(args):
    wordlist = Wordlist(args["WORDLIST"])
    log.info(f"Loaded wordlist with {len(wordlist)} entries of length 5.")

    solver = NaiveFrequencySolver(wordlist)
    log.info(f"Using {solver}")

    stats = {True: 0, False: 0}
    rounds = []
    for _ in track(range(int(args["--num-trials"]))):
        wordle = run_trial(solver, wordlist)
        stats[wordle.is_won] += 1
        if wordle.is_won:
            rounds.append(wordle.round)

    log.info(f"[green]      Won: {stats[True]:6d}[/]")
    log.info(f"[red]     Lost: {stats[False]:6d}[/]")
    win_rate = 100. * stats[True] / (stats[True] + stats[False])
    avg_rounds = sum(rounds) / len(rounds)
    log.info(f"[blue] Win Rate:  {win_rate:5.2f}%[/]")
    log.info(f"[blue]   Rounds:  {avg_rounds:5.2f}[/]")


if __name__ == "__main__":
    args = docopt(__doc__)
    if args["--debug"]:
        log.setLevel("DEBUG")
    if args["--seed"]:
        random.seed(int(args["--seed"]))

    r = main(args)
    exit(r)
