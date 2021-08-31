import logging
from typing import Iterable
from analysis import Deck, round_robin, PayoffFn, DeckResults
from random import shuffle


log = logging.getLogger(__name__)


def partition(elts: list[Deck], group_size: int) -> Iterable[list[Deck]]:
    for start in range(0, len(elts), group_size):
        yield elts[start:start + group_size]


def group_tournament(
        payoff_fn: PayoffFn,
        decks: list[Deck],
        *,
        group_size: int = 64,
) -> list[DeckResults]:
    def run_group(group: list[Deck]) -> Iterable[DeckResults]:
        return round_robin(
            payoff_fn,
            group,
            multiprocess=True,
        )

    my_decks: list[Deck] = decks.copy()
    shuffle(my_decks)
    groups = list(partition(my_decks, group_size))

    nested_results = map(run_group, groups)

    flat_results = [deck for group in nested_results for deck in group]

    return flat_results
