from scipy.optimize import minimize  # type: ignore
import numpy as np
import random
import analysis.sampling as sampling
from analysis import DeckResults
from typing import Callable, Iterable, Optional
import run_tournament as tourney

import auto_chess as ac

from functools import partial

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


def other_cards_with_atkhp(
        vamp_atk, vamp_hp, heal_amount,
        grow_atk, grow_hp, atk_per_hit,
        cleric_atk, cleric_hp, explode_heal,
        ramp_atk, ramp_hp, middle_age,
        vanilla_atk, vanilla_hp,
):
    return [
        FriendlyVampire(vamp_atk, vamp_hp, "friendly vampire", heal_amount = heal_amount),
        GrowOnDamage(grow_atk, grow_hp, "bezerker", atk_per_hit = atk_per_hit),
        HealOnDeath(cleric_atk, cleric_hp, "suicidal cleric", explode_heal = explode_heal),
        RampAge(ramp_atk, ramp_hp, "old fogey", middle_age = 4),
        ac.Card(vanilla_atk, vanilla_hp, "vanilla 2")
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
    def step(x):
        return opt_fun(
            metric=metric,
            build_cards_fn=build_cards_fn,
            group_size=group_size,
            num_decks=num_decks,
            x0=x,
        )
    res = minimize(
        step,
        initval,
        bounds=[(1, 10)] * len(initval),
        options={
            "eps": 1,
        },
    )
    log.info(f"found minumum {res.x} after {res.nit} iterations; {res}")
    return res


import pygad


def genetic_optimize(metric, group_size, num_genes, build_cards_fn, num_decks=None):
    def fitness_func(params, idx):
        return -opt_fun(metric, build_cards_fn, group_size, num_decks, params)
    ga = pygad.GA(
        num_generations=128,
        num_parents_mating=8,
        # num_generations=1,
        # num_parents_mating=2,
        fitness_func=fitness_func,
        sol_per_pop=16,
        # sol_per_pop=4,
        num_genes=num_genes,
        gene_type=int,
        init_range_low=1,
        init_range_high=10
    )
    ga.run()
    sol, sol_fitness, sol_idx = ga.best_solution()
    log.info(f'found minimum {sol} with fitness {sol_fitness} at index {sol_idx}')
    return sol