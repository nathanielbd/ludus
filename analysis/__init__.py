import numpy as np
import pathos.multiprocessing as mproc  # type: ignore
import itertools
from typing import Callable, Sequence, TypeVar, Iterable, NamedTuple, Any


Deck = TypeVar("Deck")


# each Job stores the indices with which it corresponds in the payoff
# matrix so that we can evaluate them out of order and then insert
# them into the matrix as appropriate.

# if mypy sucked less, this would be defined as:
# class Job(NamedTuple, Generic[Deck]):
#     i: int
#     deck_i: Deck
#     j: int
#     deck_j: Deck
# but for some stupid reason, mypy doesn't support generic named tuple
# types, so instead we get the following.
class Job(NamedTuple):
    i: int
    deck_i: Any
    j: int
    deck_j: Any


class FinishedJob(NamedTuple):
    job: Job
    payoff: float


PayoffFn = Callable[[Deck, Deck], float]
RunnerFn = Callable[[PayoffFn, Iterable[Job]], Iterable[FinishedJob]]


def _jobs_iterator(decks, zero_sum) -> Iterable[Job]:
    """Iterate over the Jobs required to compute a payoff matrix for the decks."""
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
    """Run the jobs in the calling process by applying payoff_fn to the two decks"""
    for job in jobs:
        payoff = payoff_fn(job.deck_i, job.deck_j)
        yield FinishedJob(job, payoff)


def _run_multiprocess(
        payoff_fn: PayoffFn,
        jobs: Iterable[Job],
) -> Iterable[FinishedJob]:
    """Run the jobs in parallel in multiple processes"""
    def run_job(job):
        payoff = payoff_fn(job.deck_i, job.deck_j)
        return FinishedJob(job, payoff)

    with mproc.ProcessPool() as pool:
        return pool.uimap(run_job, jobs)


def _collect_finished_jobs(
        matrix: np.ndarray,
        jobs: Iterable[FinishedJob],
        zero_sum: bool,
) -> np.ndarray:
    """Insert the results of all the finished jobs into a payoff matrix"""
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
    """Compute and return the Pareto optimal frontier among the decks.

    payoff_fn should be a function from two decks, d0 and d1, which
    returns a real-number payoff for d0.

    FIXME: have payoff_fn return a tuple of payoffs?

    If the game defined by payoff_fn is zero sum, i.e. payoff_fn(d0,
    d1) == - payoff_fn(d1, d0) forall d0, d1 in decks, providing
    zero_sum=true will avoid needlessly recomputing those inverted
    matchups.

    If threshold is provided, it should be a non-negative real
    number. Any deck whose total payoff is within threshold of the
    optimum will be treated as optimal.

    If multiprocess is provided and True, payoff_fn will be evaluated
    in parallel using multiple processes. If multiprocess is False or
    unspecified, payoff_fn will be evaluated sequentially within the
    calling process.

    """
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
