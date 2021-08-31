from scipy.optimize import minimize  # type: ignore
import numpy as np
import random
import analysis.sampling as sampling
from analysis import DeckResults
from typing import Callable, Iterable, Optional
import run_tournament as tourney

import auto_chess as ac

from functools import partial


import logging


log = logging.getLogger(__name__)


def build_cards(
        explode_damage: int,
        heal_amount: int,
        atk_per_hit: int,
        explode_heal: int,
        heal_percent: int,
        armor_points: int,
        dmg_percent: int,
        middle_age: int,
        target_age: int,
        detonation_time: int,
) -> list[ac.Card]:
    from auto_chess.explode_on_death import ExplodeOnDeath
    from auto_chess.friendly_vampire import FriendlyVampire
    from auto_chess.grow_on_damage import GrowOnDamage
    from auto_chess.heal_allies_on_death import HealOnDeath
    from auto_chess.healthdonor import HealthDonor
    from auto_chess.ignore_first_damage import IgnoreFirstDamage
    from auto_chess.morph_enemies import MorphOpponents
    from auto_chess.painsplitter import PainSplitter
    from auto_chess.rampage import RampAge
    from auto_chess.survivalist import Survivalist
    from auto_chess.threshold import ThreshOld
    from auto_chess.ticking_time_bomb import TimeBomb

    # improve smoothness of function by decreasing the percent magnitudes
    heal_percent *= 10
    dmg_percent *= 10
    
    return [
        ExplodeOnDeath(2, 1, "volatile", explode_damage = explode_damage),
        FriendlyVampire(1, 3, "friendly vampire", heal_amount = heal_amount),
        GrowOnDamage(0, 5, "bezerker", atk_per_hit = atk_per_hit),
        HealOnDeath(1, 2, "suicidal cleric", explode_heal = explode_heal),
        HealthDonor(1, 4, "good friend", heal_percent = heal_percent),
        IgnoreFirstDamage(2, 1, "armor", armor_points = armor_points),
        MorphOpponents(0, 3, "morph ball"),
        PainSplitter(2, 2, "bad friend", dmg_percent = dmg_percent),
        RampAge(0, 4, "old fogey", middle_age = 4),
        Survivalist(2, 2, "coward"),
        ThreshOld(2, 2, "curmudgeon", target_age = target_age),
        TimeBomb(1, 8, "time bomb", detonation_time = detonation_time)
    ]

def cards_with_atkhp(
        surv_atk, surv_hp,
        morph_atk, morph_hp,
        armor_atk, armor_hp, armor_points,
        bomb_atk, bomb_hp, explode_damage,
        vanilla_atk, vanilla_hp,
) -> list[ac.Card]:
    return [
        Survivalist(surv_atk, surv_hp, "coward"),
        MorphOpponents(morph_atk, morph_hp, "morph ball"),
        IgnoreFirstDamage(armor_atk, armor_hp, "armor", armor_points = armor_points),
        ExplodeOnDeath(bomb_atk, bomb_hp, "volatile", explode_damage = explode_damage),
        ac.Card(vanilla_atk, vanilla_hp, "vanilla")
    ]

# try only perturbing the mechanic stats
# if no curse of dimensionality, try perturbing hp/atk too
def opt_fun(
        metric: Callable[[Iterable[DeckResults]], float],
        build_cards_fn: Callable,
        group_size: int,
        num_decks: Optional[int],
        x0: list[int],
) -> float:
    log.info("chosen params for this run are %s", x0)
    cards = build_cards_fn(*x0)

    decks = ac.possible_decks(3, cards)

    if num_decks:
        decks = random.sample(decks, k=num_decks)

    log.info(
            "running a group tournament of group_size %d between %d decks composed of %d cards",
            group_size, len(decks), len(cards),
        )
    results = sampling.group_tournament(
        ac.play_auto_chess,
        decks,
        group_size=group_size
    )
    score = metric(results)
    log.info(f"metric evaluated to {score}")
    return score



class StepIntegers:
    def __init__(self, stepsize=20):
        self.stepsize = stepsize

    def __call__(self, x):
        step_vec = np.random.rand(10)
        step_vec /= np.linalg.norm(step_vec)
        step_vec *= self.stepsize
        return (x + step_vec).astype(int)


step_integers = StepIntegers()


def show_minima(x):
    log.info(f"found minimum at {x}")


def optimize(metric, group_size, initval, build_cards_fn, num_decks=None):
    res = minimize(
        partial(opt_fun, build_cards_fn, metric, group_size, num_decks),
        initval,
        bounds=[(1, 10)] * 10,
        options={
            "eps": 1,
        },
    )
    log.info(f"found minumum {res.x} after {res.nit} iterations; {res}")
    return res
