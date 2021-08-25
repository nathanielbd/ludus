from typing import Iterable, IO
from analysis import Deck, DeckResults
import pickle
import os
import run_tournament
import numpy as np


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


def deckresults_dict(results: Iterable[DeckResults]) -> dict[Deck, float]:
    return dict((res.deck, res.avg_payoff) for res in results)


def trial_avgs() -> Iterable[tuple[str, list[DeckResults]]]:
    return ((subdir, average_from_dir(subdir))
            for subdir in os.listdir(".")
            if subdir.startswith("group_size_") and os.path.isdir(subdir))


def rr_numbers() -> Iterable[DeckResults]:
    with open("round_robin/trial_0", "rb") as infile:
        return list(pickle.load(infile))


def output_metric(outfile: IO[str], name: str, value: float) -> None:
    outstr = f"{name}: {value}"
    print("  " + outstr)
    outfile.write(outstr)
    outfile.write("\n")


def compute_independent_metrics(outfile: IO[str], results: list[DeckResults]) -> None:
    for (metricname, func) in run_tournament.METRICS:
        output_metric(outfile, metricname, func(results))


def output_filename(trialdir: str) -> str:
    return trialdir + "_metrics.txt"


def errors(rr: dict[Deck, float], trial: dict[Deck, float]) -> dict[Deck, float]:
    res = {}
    for (deck, trial_payoff) in trial.items():
        res[deck] = abs(trial_payoff - rr[deck])
    return res


def compute_error_metrics(outfile: IO[str], errors: np.array) -> None:
    [min_error, low_quart, median, high_quart, max_error] = np.quantile(
        errors,
        [0.0, 0.25, 0.5, 0.75, 1.0],
    )
    mean = np.mean(errors)
    for (name, val) in [("min error", min_error),
                        ("low quartile", low_quart),
                        ("median", median),
                        ("high quartile", high_quart),
                        ("max error", max_error),
                        ("mean error", mean)]:
        output_metric(outfile, name, val)


def euclidean_distance(rr: dict[Deck, float], trial: dict[Deck, float]) -> float:
    return np.linalg.norm(
        list(trial_val - rr[deck] for (deck, trial_val) in trial.items())
    )


def compare_metrics() -> None:
    rr_seq = list(rr_numbers())
    with open("rr_metrics.txt", "w") as outfile:
        compute_independent_metrics(outfile, rr_seq)
    round_robin = deckresults_dict(rr_seq)
    for (trialdir, results) in trial_avgs():
        results = list(results)
        trial_dict = deckresults_dict(results)
        outfilename = output_filename(trialdir)
        print(f"computing metrics for {trialdir} to {outfilename}")
        trial_error = errors(round_robin, trial_dict)
        with open(output_filename(trialdir), "w") as outfile:
            compute_independent_metrics(outfile, results)
            compute_error_metrics(outfile, np.array(list(trial_error.values())))
            output_metric(
                outfile,
                "euclidean distance",
                euclidean_distance(round_robin, trial_dict)
            )


if __name__ == "__main__":
    compare_metrics()
