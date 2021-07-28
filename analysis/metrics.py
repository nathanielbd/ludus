from typing import Callable, Iterable
from analysis import DeckResults
import logging
import math


log = logging.getLogger(__name__)


# the result should be a float between 0 and 1, where 0 is bad and 1 is good.
Metric = Callable[[Iterable[DeckResults]], float]


def payoff_winrate(payoff: float) -> float:
    """from a payoff between -1 and 1, return a winrate between 0 and 1"""
    return (payoff / 2) + 0.5


def average_payoff_metric(results: Iterable[DeckResults]) -> float:
    """Good if most decks have close to zero average payoff, bad if their
average payoff is high or low.
    """
    count: int = 0
    total: float = 0
    for result in results:
        count += 1
        # sqrt is larger than its input for the numbers we care about,
        # so this will punish small values disproportionately
        total += abs(result.avg_payoff)
    avg = total / count

    log.debug("total payoff deviance is %f, count is %d", total, count)

    return 1.0 - avg  # how close is it to 0.0?


def sqrt_average_payoff_metric(results: Iterable[DeckResults]) -> float:
    """Good if most decks have close to zero average payoff, bad if their
average payoff is high or low.

    Punishes small deviances more than avg_payoff_metric
    """
    count: int = 0
    total: float = 0
    for result in results:
        count += 1
        # sqrt is larger than its input for the numbers we care about,
        # so this will punish small values disproportionately
        total += math.sqrt(abs(result.avg_payoff))
    avg = total / count

    log.debug("total sqrt payoff is %f, count is %d", total, count)

    return 1.0 - avg  # how close is it to 0.0?
