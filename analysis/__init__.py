import numpy as np
import pathos.multiprocessing as mproc  # type: ignore
import itertools
import collections
from typing import Callable, Sequence, TypeVar, Iterable


Deck = TypeVar("Deck")


Job = collections.namedtuple(
    "Job",
    ["i", "deck0", "j", "deck1"],
)
FinishedJob = collections.namedtuple(
    "FinishedJob",
    ["job", "payoff"],
)
PayoffFn = Callable[[Deck, Deck], float]
RunnerFn = Callable[[PayoffFn, Iterable[Job]], Iterable[FinishedJob]]


def _jobs_iterator(decks, zero_sum) -> Iterable[Job]:
    for ((i, d0), (j, d1)) in itertools.product(
            enumerate(decks),
            enumerate(decks),
    ):
        if j <= i or not zero_sum:
            yield Job(i, d0, j, d1)


def _run_sequentially(
        payoff_fn: PayoffFn,
        jobs: Iterable[Job],
) -> Iterable[FinishedJob]:
    for job in jobs:
        payoff = payoff_fn(job.deck0, job.deck1)
        yield FinishedJob(job, payoff)


def _run_multiprocess(
        payoff_fn: PayoffFn,
        jobs: Iterable[Job],
) -> Iterable[FinishedJob]:
    def run_job(job):
        payoff = payoff_fn(job.deck0, job.deck1)
        return FinishedJob(job, payoff)

    with mproc.ProcessPool() as pool:
        return pool.uimap(run_job, jobs)


def _collect_finished_jobs(
        matrix: np.ndarray,
        jobs: Iterable[FinishedJob],
        zero_sum: bool,
) -> np.ndarray:
    for (job, payoff) in jobs:
        i = job.i
        j = job.j
        matrix[i, j] = payoff
        if zero_sum and j > i:
            matrix[j, i] = - payoff
    return matrix


def _runner_fn(multiprocess: bool) -> RunnerFn:
    if multiprocess:
        return _run_multiprocess
    else:
        return _run_sequentially


def analytic_pareto(
        payoff_fn: PayoffFn,
        decks: Sequence[Deck],
        *,
        zero_sum: bool = False,
        threshold: float = 0,
        multiprocess: bool = False,
) -> list[Deck]:
    n_decks = len(decks)
    payoffs = np.empty((n_decks, n_decks))

    payoffs = _collect_finished_jobs(
        payoffs,
        _runner_fn(multiprocess)(
            payoff_fn,
            _jobs_iterator(decks, zero_sum),
        ),
        zero_sum,
    )

    payoff_sums = np.sum(payoffs, 1)

    best = np.amax(payoff_sums)

    return [
        deck for (deck, payoff)
        in zip(decks, payoff_sums)
        if abs(best - payoff) <= threshold
    ]
