from typing import NamedTuple, Callable, Iterable
from analysis import Deck


class DeckResults(NamedTuple):
    avg_winrate: float
    deck: Any


Metric = Callable[[Iterable[DeckResults]], float]


def frontier_size_metric(frontier: Iterable[DeckResults]) -> float:
    return sum(1 for _ in frontier)
