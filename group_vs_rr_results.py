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
) -> None:
    outname = f"{subdir}/{trialname}_metrics.txt"
    errvec = np.array(list(
        errors(round_robin, deckresults_dict(results)).values()
    ))
    [min_error, low_quart, median, high_quart, max_error] = np.quantile(
        errvec,
        [0.0, 0.25, 0.5, 0.75, 1.0],
    )
    mean = np.mean(errvec)
    print(f"computing metrics for {subdir}/{trialname}")
    with open(outname, "w") as outfile:
        for (name, val) in [("min error", min_error),
                            ("low quartile", low_quart),
                            ("median", median),
                            ("high quartile", high_quart),
                            ("max error", max_error),
                            ("mean error", mean)]:
            output_metric(outfile, name, val)


def rr_numbers() -> Iterable[DeckResults]:
    with open("round_robin/trial_0", "rb") as infile:
        return list(pickle.load(infile))


def compare_metrics() -> None:
    round_robin = deckresults_dict(list(rr_numbers()))

    for (trialdir, trialname, results) in trial_iterator():
        results = list(results)
        compute_error_metrics(trialdir, trialname, results, round_robin)


if __name__ == "__main__":
    compare_metrics()
