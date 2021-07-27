from typing import NamedTuple, Callable, Iterable
from analysis import Deck


class DeckResults(NamedTuple):
    avg_winrate: float
    deck: Any


# the result should be a float between 0 and 1, where 0 is bad and 1 is good.
Metric = Callable[[Iterable[DeckResults]], float]


def average_win_rate_metric(results: Iterable[DeckResults]) -> float:
    count = 0
    total = 0
    for result in results:
        count += 1
        total += results.avg_winrate
    avg = total / count
    return abs(0.5 - avg) * 2.0  # how close is it to 0.5?
