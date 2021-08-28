from auto_chess import Card
from typing import Callable, Dict, Iterable
from analysis import DeckResults
import logging
import math
import numpy as np

log = logging.getLogger(__name__)


# the result should be a float between 0 and 1, where 0 is bad and 1 is good.
Metric = Callable[[Iterable[DeckResults]], float]


def payoff_winrate(payoff: float) -> float:
    """from a payoff between -1 and 1, return a winrate between 0 and 1"""
    return (payoff / 2) + 0.5


def winrate_payoff(winrate: float) -> float:
    """from a winrate between 0 and 1, return a payoff between -1 and 1"""
    return (winrate * 2) - 1


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


def weighted_sum_cards(
        results: Iterable[DeckResults],
        *,
        key: Callable[[float], float] = lambda n: n,
) -> Dict[Card, float]:
    """Returns a mapping from cards to the average winrate of decks they appear in"""
    # sums maps cards to the total winrates of all the decks they appear in
    sums: dict[Card, float] = dict()
    counts: dict[Card, int] = dict()
    for result in results:
        for card in result.deck:
            try:
                counts[card] += 1
            except KeyError:
                counts[card] = 1
            try:
                prev = sums[card]
            except KeyError:
                prev = 0
            sums[card] = prev + key(payoff_winrate(result.avg_payoff))

    # weights normalizes sums to be in the range 0..=1
    weights = dict()
    for card, winsum in sums.items():
        weights[card] = winsum / counts[card]
    return weights


def per_card_winrate(
        results: Iterable[DeckResults],
        *,
        winrate_key: Callable[[float], float] = lambda n: n,
        variance_key: Callable[[float], float] = lambda n: n,
) -> float:
    per_card_payoffs = weighted_sum_cards(results, key=winrate_key).values()
    return sum(
        variance_key(abs(winrate_payoff(payoff)))
        for payoff in per_card_payoffs
    ) / len(per_card_payoffs)

def std_dev_metric(
        results: Iterable[DeckResults],
        *,
        winrate_key: Callable[[float], float] = lambda n: n,
        variance_key: Callable[[float], float] = lambda n: n,
) -> float:
    return np.std(list(weighted_sum_cards(results, key=winrate_key).values()))

def entropy_metric(
        results: Iterable[DeckResults],
        *,
        key: Callable[[float], float] = lambda n: n,
) -> float:
    # S = \sum{p_i ln(p_i)}
    cards = weighted_sum_cards(results)
    sum = 0.0
    for card in cards:
        sum += cards[card]

    entropy = 0.0
    for card in cards:
        p = cards[card] / sum
        entropy -= p * math.log(p)

    return entropy

