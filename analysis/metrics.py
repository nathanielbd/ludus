from typing import NamedTuple, Callable, Iterable
from analysis import Deck


class DeckResults(NamedTuple):
    avg_winrate: float
    deck: Any


Metric = Callable[[Iterable[DeckResults]], float]


def average_win_rate_metric(results: Iterable[DeckResults]) -> float:
    count = 0
    total = 0
    for result in results:
        count += 1
        total += results.avg_winrate
    avg = total / count
    return abs(0.5 - avg) * 2.0  # how close is it to 0.5?
