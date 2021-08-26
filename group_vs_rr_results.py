from typing import Iterable, IO
from analysis import Deck, DeckResults
import pickle
import os
import run_tournament
import numpy as np


def deckresults_dict(results: Iterable[DeckResults]) -> dict[Deck, float]:
    return dict((res.deck, res.avg_payoff) for res in results)


def read_trial(path: str) -> list[DeckResults]:
    with open(path, "rb") as infile:
        return list(pickle.load(infile))


def trial_iterator() -> Iterable[tuple[str, str, list[DeckResults]]]:
    for subdir in os.listdir("."):
        if subdir.startswith("group_size_") and os.path.isdir(subdir):
            for trialname in os.listdir(subdir):
                fullpath = f"{subdir}/{trialname}"
                if trialname.startswith("trial_") and os.path.isfile(fullpath):
                    yield (subdir, trialname, read_trial(fullpath))


def output_metric(outfile: IO[str], name: str, value: float) -> None:
    outstr = f"{name}: {value}"
    print("  " + outstr)
    outfile.write(outstr)
    outfile.write("\n")


def errors(rr: dict[Deck, float], trial: dict[Deck, float]) -> dict[Deck, float]:
    res = {}
    for (deck, trial_payoff) in trial.items():
        res[deck] = abs(trial_payoff - rr[deck])
    return res


def compute_error_metrics(
        subdir: str,
        trialname: str,
        results: list[DeckResults],
        round_robin: dict[Deck, float],
) -> tuple[float, ...]:
    errvec = np.array(list(
        errors(round_robin, deckresults_dict(results)).values()
    ))
    [min_error, low_quart, median, high_quart, max_error] = np.quantile(
        errvec,
        [0.0, 0.25, 0.5, 0.75, 1.0],
    )
    mean = np.mean(errvec)
    return (min_error, low_quart, median, high_quart, max_error, mean)


def rr_numbers() -> Iterable[DeckResults]:
    with open("round_robin/trial_0", "rb") as infile:
        return list(pickle.load(infile))


def compare_metrics() -> None:
    round_robin = deckresults_dict(list(rr_numbers()))

    outfiles = {}
    for (trialdir, trialname, results) in trial_iterator():
        try:
            out = outfiles[trialdir]
        except KeyError:
            out = open(f"{trialdir}_results.txt", "w")
            out.write("# min error, low quartile, median, high quartile, max error, mean error\n")
        results = list(results)
        for metric in compute_error_metrics(trialdir, trialname, results, round_robin):
            out.write(f"{metric}, ")
        out.write("\n")


if __name__ == "__main__":
    compare_metrics()
