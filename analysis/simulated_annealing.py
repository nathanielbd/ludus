# import analysis.run_tournament as run_tournament
from scipy.optimize import basinhopping
import analysis.sampling as sampling
from analysis import DeckResults
from typing import Callable, Iterable

import auto_chess as ac
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

from functools import partial

# choose metric
# from analysis.metrics import average_payoff_metric

import logging


log = logging.getLogger(__name__)


# try only perturbing the mechanic stats
# if no curse of dimensionality, try perturbing hp/atk too
def opt_fun(
    metric: Callable[[Iterable[DeckResults]], float],
    n_iters: int,
    # explode_damage: int = 1,
    # heal_amount: int = 1,
    # atk_per_hit: int = 1,
    # explode_heal: int = 1,
    # heal_percent: int = 50,
    # armor_points: int = 1,
    # dmg_percent: int = 50,
    # middle_age: int = 4,
    # target_age: int = 4,
    # detonation_time: int = 10,
    # n_iters: int = 1024
    x0: list[int, int, int, int, int, int, int, int, int, int]
) -> float:
    explode_damage, heal_amount, atk_per_hit, explode_heal, \
        heal_percent, armor_points, dmg_percent, middle_age, \
            target_age, detonation_time = x0
    explode_on_death = ExplodeOnDeath(2, 1, "bomb", explode_damage=explode_damage)
    friendly_vampire = FriendlyVampire(1, 3, "friendly vampire", heal_amount=heal_amount)
    grow_on_damage = GrowOnDamage(0, 5, "berserker", atk_per_hit=atk_per_hit)
    heal_on_death = HealOnDeath(1, 2, "suicidal cleric", explode_heal=explode_heal)
    health_donor = HealthDonor(1, 4, "angel", heal_percent=heal_percent)
    ignore_first_damage = IgnoreFirstDamage(2, 1, "shield warrior", armor_points=armor_points)
    morph_opponents = MorphOpponents(0, 3, "morpher")
    painsplitter = PainSplitter(2, 2, 'painsplitter', dmg_percent=dmg_percent)
    rampage = RampAge(0, 4, 'rampage', middle_age=middle_age)
    survivalist = Survivalist(2, 2, 'survivalist')
    threshold = ThreshOld(2, 2, 'threshold', target_age=target_age)
    time_bomb = TimeBomb(1, 8, 'time bomb', detonation_time=detonation_time)

    cards = (explode_on_death,
             friendly_vampire,
             grow_on_damage,
             heal_on_death,
             health_donor,
             ignore_first_damage,
             morph_opponents,
             painsplitter,
             rampage,
             survivalist,
             threshold,
             time_bomb)

    decks = ac.possible_decks(3, cards)
    log.info(
            "running a group tournament between %d decks composed of %d cards",
            len(decks), len(cards),
        )
    results = sampling.group_tournament(
        ac.play_auto_chess,
        decks,
        stages_before_finals=2
    )
    # score = average_payoff_metric(results)
    score = metric
    return -score


# really ugly system right now
# figure out how to do currying so that extra parameters 
# can be added before injection into simulated annealing


def optimize(metric, n_iters):
    return basinhopping(partial(opt_fun, metric, n_iters),
                        [1, 1, 1, 1, 50, 1, 50, 4, 4, 10]
    )
