import auto_chess as ac
import analysis
import analysis.sampling as sampling
import analysis.metrics as metrics

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

from typing import Iterable, List
import math
import logging

log = logging.getLogger(__name__)

BEAR = ac.Card(2, 2, "bear")
TANK = ac.Card(1, 4, "tank")
BRUISER = ac.Card(3, 1, "bruiser")
EXPLODE_ON_DEATH = ExplodeOnDeath(2, 1, "volatile", explode_damage = 1)
FRIENDLY_VAMPIRE = FriendlyVampire(1, 3, "friendly vampire", heal_amount = 1)
GROW_ON_DAMAGE = GrowOnDamage(0, 5, "bezerker", atk_per_hit = 1)
HEAL_ALLIES_ON_DEATH = HealOnDeath(1, 2, "suicidal cleric", explode_heal = 1)
HEALTHDONOR = HealthDonor(1, 4, "good friend", heal_percent = 1)
IGNORE_FIRST_DAMAGE = IgnoreFirstDamage(2, 1, "armor", armor_points = 1)
MORPH_ENEMIES = MorphOpponents(0, 3, "morph ball")
PAINSPLITTER = PainSplitter(2, 2, "bad friend", dmg_percent = 50)
RAMPAGE = RampAge(0, 4, "old fogey", middle_age = 4)
SURVIVALIST = Survivalist(2, 2, "coward")
THRESHOLD = ThreshOld(2, 2, "curmudgeon", target_age = 4)
TIME_BOMB = TimeBomb(1, 8, "time bomb", detonation_time = 10)

SIMPLE_CARDS = [BEAR,
                TANK,
                BRUISER]

ALL_CARDS = [BEAR,
             TANK,
             BRUISER,
             EXPLODE_ON_DEATH,
             FRIENDLY_VAMPIRE,
             GROW_ON_DAMAGE,
             HEAL_ALLIES_ON_DEATH,
            #  HEALTHDONOR,
             IGNORE_FIRST_DAMAGE,
             MORPH_ENEMIES,
             PAINSPLITTER,
             RAMPAGE,
             SURVIVALIST,
             THRESHOLD,
             TIME_BOMB]


METRICS: tuple[tuple[str, metrics.Metric], ...] = (
    ("average payoff deviance", metrics.average_payoff_metric),
    ("square-root payoff deviance",
     lambda i: metrics.average_payoff_metric(i, key=math.sqrt)),
    ("squared payoff deviance",
     lambda i: metrics.average_payoff_metric(i, key=lambda n: n**2)),
    ("per-card winrate", metrics.per_card_winrate),
    ("squared per-card winrate",
     lambda i: metrics.per_card_winrate(i, variance_key=lambda n: n**2)),
    ("entropy metric", metrics.entropy_metric),
)


def run_tourney(cards: List[ac.Card], deck_size=3, stages_before_finals=1024) -> \
        Iterable[analysis.DeckResults]:
    decks = ac.possible_decks(deck_size, cards)
    log.info(
        "running a group tournament between %d decks composed of %d cards",
        len(decks), len(cards),
    )
    # return analysis.round_robin(
    #     ac.play_auto_chess,
    #     decks,
    #     multiprocess=True,
    # )
    return sampling.group_tournament(
        ac.play_auto_chess,
        list(decks),
        group_size = 64,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.INFO)
    analysis.log.setLevel(logging.INFO)
    sampling.log.setLevel(logging.INFO)
    res = list(run_tourney(ALL_CARDS))
    for (name, metric) in METRICS:
        log.info("metric %s = %f", name, metric(res))

    log.debug("results are are:\n%s", res)
