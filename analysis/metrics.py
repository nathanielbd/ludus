from typing import Callable, Iterable
from analysis import DeckResults
import logging


log = logging.getLogger(__name__)


# the result should be a float between 0 and 1, where 0 is bad and 1 is good.
Metric = Callable[[Iterable[DeckResults]], float]


def payoff_winrate(payoff: float) -> float:
    """from a payoff between -1 and 1, return a winrate between 0 and 1"""
    return (payoff / 2) + 0.5


def average_win_rate_metric(results: Iterable[DeckResults]) -> float:
    """Note: in a zero-sum game, this metric will always be 1.0..."""
    count: int = 0
    total: float = 0
    for result in results:
        count += 1
        total += payoff_winrate(result.avg_payoff)
    avg = total / count

    log.debug("total winrate is %f, count is %d", total, count)

    return 1.0 - (abs(0.5 - avg) * 2.0)  # how close is it to 0.5?
