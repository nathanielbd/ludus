from scipy.optimize import basinhopping
import numpy as np
import random
import analysis.sampling as sampling
from analysis import DeckResults
from typing import Callable, Iterable
import run_tournament as tourney

import auto_chess as ac

from functools import partial


import logging


log = logging.getLogger(__name__)


# try only perturbing the mechanic stats
# if no curse of dimensionality, try perturbing hp/atk too
def opt_fun(
    metric: Callable[[Iterable[DeckResults]], float],
    group_size: int,
    num_decks: None,
    x0: list[int]
) -> float:
    explode_damage, heal_amount, atk_per_hit, explode_heal, \
        heal_percent, armor_points, dmg_percent, middle_age, \
            target_age, detonation_time = x0
    # improve smoothness of function by decreasing the percent magnitudes
    heal_percent *= 10
    dmg_percent *= 10
    cards = tourney.ALL_CARDS

    decks = ac.possible_decks(3, cards)

    if num_decks:
        decks = random.sample(decks, k=num_decks)

    log.info(
            "running a group tournament between %d decks composed of %d cards",
            len(decks), len(cards),
        )
    results = sampling.group_tournament(
        ac.play_auto_chess,
        decks,
        group_size=group_size
    )
    score = metric(results)
    return -score


class StepIntegers:
    def __init__(self, stepsize=20):
        self.stepsize = stepsize

    def __call__(self, x):
        step_vec = np.random.rand(10)
        step_vec /= np.linalg.norm(step_vec)
        step_vec *= self.stepsize
        return (x + step_vec).astype(int)


step_integers = StepIntegers()


def show_minima(x, f, accepted):
    log.info(f"found minimum at {x} with value {f}; accepted: {accepted}")


def optimize(metric, opt_iters, group_size, num_decks):
    res = basinhopping(partial(opt_fun, metric, group_size, num_decks),
                        [1, 1, 1, 1, 5, 1, 5, 4, 4, 10],
                        # minimizer_kwargs={'method': 'L-BFGS-B', 'jac': True},
                        # minimizer_kwargs={'method': 'Nelder-Mead'},
                        niter=opt_iters,
                        disp=True,
                        seed=42,
                        take_step=step_integers,
                        callback=show_minima
                        )
    log.info(res.lowest_optimization_result)
    return res
