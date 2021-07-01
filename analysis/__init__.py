import numpy as np
from typing import Callable, Any, Iterable

def analytic_pareto(
        payoff_fn: Callable[[Any, Any], float],
        decks: Iterable[Any],
        zero_sum: bool = False,
        threshold: float = 0,
) -> list[Any]:
    n_decks = len(decks)
    payoffs = np.empty((n_decks, n_decks))
    for (i, deck_0) in enumerate(decks):
        for (j, deck_1) in enumerate(decks):
            if zero_sum and i < j:
                payoffs[i, j] = - payoffs[j, i]
            else:
                payoffs[i, j] = payoff_fn(deck_0, deck_1)

    payoff_sums = np.sum(payoffs, 1)

    best = np.amax(payoff_sums)

    return [deck for (deck, payoff) in zip(decks, payoff_sums) if abs(best - payoff) <= threshold]
