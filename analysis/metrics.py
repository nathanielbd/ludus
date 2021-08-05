from auto_chess import Card
from typing import Callable, Dict, Iterable
from analysis import DeckResults
import logging
import math


log = logging.getLogger(__name__)


# the result should be a float between 0 and 1, where 0 is bad and 1 is good.
Metric = Callable[[Iterable[DeckResults]], float]


def payoff_winrate(payoff: float) -> float:
    """from a payoff between -1 and 1, return a winrate between 0 and 1"""
    return (payoff / 2) + 0.5


def average_payoff_metric(
        results: Iterable[DeckResults],
        *,
        key: Callable[[float], float] = lambda n: n,
) -> float:
    """Good if most decks have close to zero average payoff, bad if their
average payoff is high or low.

    If provided, key should be a function from a float between 0 and 1
    to a float in the same range. Juicy examples might be math.sqrt
    (to punish small deviations disproportionately) or lambda n: n**2
    (to punish large deviations disproportionately)

    """
    count: int = 0
    total: float = 0
    for result in results:
        count += 1
        keyed = key(abs(result.avg_payoff))
        total += keyed
    avg = total / count

    log.debug(
        "total payoff deviance through key %s is %f, count is %d",
        key, total, count,
    )

    return 1.0 - avg  # how close is it to 0.0?


def sum_cards(results: Iterable[DeckResults]) -> Dict[Card, int]:
    cards: Dict[Card, int] = dict()
    for result in results:
        for card in result.deck:
            if card in cards:
                cards[card] += 1
            else:
                cards[card] = 1
    return cards


def same_cards_metric(
        results: Iterable[DeckResults],
        *,
        key: Callable[[float], float] = lambda n: n,
) -> float:
    cards = sum_cards(results)

    sum = 0
    for card in cards:
        sum += cards[card]
    return sum / len(cards)


def entropy_metric(
        results: Iterable[DeckResults],
        *,
        key: Callable[[float], float] = lambda n: n,
) -> float:
    # S = \sum{p_i ln(p_i)}
    cards = sum_cards(results)
    sum = 0
    for card in cards:
        sum += cards[card]

    entropy = 0.0
    for card in cards:
        p = cards[card] / sum
        entropy -= p * math.log(p)

    return entropy
