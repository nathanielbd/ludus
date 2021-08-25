from typing import Iterable
from analysis import Deck, DeckResults
import pickle
import os
import run_tournament


def average_from_dir(directory: str) -> list[DeckResults]:
    sums = {}
    trialct = 0
    for filename in os.listdir(directory):
        trialct += 1
        with open(directory + "/" + filename, "rb") as infile:
            testrun = pickle.load(infile)
        for deckresult in testrun:
            try:
                sums[deckresult.deck] += deckresult.avg_payoff
            except KeyError:
                sums[deckresult.deck] = deckresult.avg_payoff
    return [DeckResults(deck, sum / trialct) for (deck, sum) in sums.items()]


def trial_avgs() -> Iterable[tuple[str, list[DeckResults]]]:
    return ((subdir, average_from_dir(subdir))
            for subdir in os.listdir(".")
            if subdir.startswith("group_size_") and os.path.isdir(subdir))


def rr_numbers() -> Iterable[DeckResults]:
    with open("round_robin/trial_0") as infile:
        return list(pickle.load(infile))


def rr_dict() -> dict[Deck, float]:
    d = {}
    for deckresult in rr_numbers():
        d[deckresult.deck] = deckresult.avg_payoff
    return d


def compute_independent_metrics(filename, results) -> None:
    with open(filename, "w") as outfile:
        for (metricname, func) in run_tournament.METRICS:
                outfile.write(metricname)
                outfile.write(": ")
                outfile.write(str(func(results)))
                outfile.write("\n")


def compare_metrics() -> None:
    for (trialdir, results) in trial_avgs():
        compute_independent_metrics(trialdir + "_metrics.txt", list(results))


if __name__ == "__main__":
    compare_metrics()
