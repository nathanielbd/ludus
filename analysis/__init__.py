import numpy as np
import pathos.multiprocessing as mproc  # type: ignore
import itertools
from typing import Callable, Sequence, TypeVar, Iterable, NamedTuple, Any
import logging


Deck = TypeVar("Deck")


log = logging.getLogger(__name__)


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


class GamePayoffs(NamedTuple):
    p0_payoff: float
    p1_payoff: float

    @classmethod
    def zero_sum_payoff(cls, p0_payoff: float) -> 'GamePayoffs':
        return cls(p0_payoff, - p0_payoff)


class FinishedJob(NamedTuple):
    job: Job
    payoffs: GamePayoffs


PayoffFn = Callable[[Deck, Deck], GamePayoffs]
RunnerFn = Callable[[PayoffFn, Iterable[Job]], Iterable[FinishedJob]]


def zero_sum_payoff_fn(fn: Callable[[Deck, Deck], float]) -> PayoffFn:
    def payoff_inner(deck_0, deck_1):
        return GamePayoffs.zero_sum_payoff(fn(deck_0, deck_1))
    return payoff_inner


def _jobs_iterator(decks) -> Iterable[Job]:
    """Iterate over the Jobs required to compute a payoff matrix for the decks."""
    for ((i, d0), (j, d1)) in itertools.product(
            enumerate(decks),
            enumerate(decks),
    ):
        if j <= i:
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
) -> np.ndarray:
    """Insert the results of all the finished jobs into a payoff matrix"""
    for (job, payoffs) in jobs:
        i = job.i
        j = job.j

        if i == j:
            assert payoffs.p0_payoff == payoffs.p1_payoff, \
                f"""mismatched payoffs {payoffs.p0_payoff}, {payoffs.p1_payoff}
    in mirror match at ({i}, {j})
    between {job.deck_i} and {job.deck_j}"""

        matrix[i, j] = payoffs.p0_payoff
        matrix[j, i] = payoffs.p1_payoff

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
        threshold: float = 0,
        multiprocess: bool = False,
) -> list[Deck]:
    """Compute and return the Pareto optimal frontier among the decks.

    payoff_fn should be a function from two decks, d0 and d1, which
    returns a GamePayoffs object containing payoffs for d0 and
    d1. Zero-sum games (i.e. those where d0_payoff = - d1_payoff) may
    use zero_sum_payoff_fn to transform a payoff function for d0 into
    a payoff function for both players, or may use
    GamePayoffs.zero_sum_payoff in their payoff functions to return a
    value.

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

    # n_decks choose 2 + n_decks
    total_jobs = (n_decks * (n_decks - 1)) // 2 + n_decks

    payoffs = _collect_finished_jobs(
        total_jobs,
        payoffs,
        _runner_fn(multiprocess)(
            payoff_fn,
            _jobs_iterator(decks),
        ),
    )

    payoff_avgs = np.mean(payoffs, axis=1, dtype=np.float64)

    best = np.amax(payoff_avgs)

    return [
        deck for (deck, payoff)
        in zip(decks, payoff_avgs)
        if abs(best - payoff) <= threshold
    ]
