import auto_chess as ac
import analysis

from auto_chess.explode_on_death import ExplodeOnDeath
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


from typing import Sequence

import logging


log = logging.getLogger(__name__)


EXPLODE_ON_DEATH = ExplodeOnDeath(1, 1, "volatile")
GROW_ON_DAMAGE = GrowOnDamage(0, 5, "bezerker")
HEAL_ALLIES_ON_DEATH = HealOnDeath(1, 1, "suicidal cleric")
HEALTHDONOR = HealthDonor(1, 4, "good friend")
IGNORE_FIRST_DAMAGE = IgnoreFirstDamage(2, 1, "armor")
MORPH_ENEMIES = MorphOpponents(0, 3, "morph ball")
PAINSPLITTER = PainSplitter(2, 2, "bad friend")
RAMPAGE = RampAge(0, 5, "old fogey")
SURVIVALIST = Survivalist(3, 3, "coward")
THRESHOLD = ThreshOld(2, 2, "curmudgeon")
TIME_BOMB = TimeBomb(0, 10, "time bomb")


all_cards = (EXPLODE_ON_DEATH,
             GROW_ON_DAMAGE,
             HEAL_ALLIES_ON_DEATH,
             HEALTHDONOR,
             IGNORE_FIRST_DAMAGE,
             MORPH_ENEMIES,
             PAINSPLITTER,
             RAMPAGE,
             SURVIVALIST,
             THRESHOLD,
             TIME_BOMB)


def run_tourney() -> list[Sequence[ac.Card]]:
    decks = ac.possible_decks(3, all_cards)
    log.info(("running a round-robin tournament between "
              f"{len(decks)} decks composed of {len(all_cards)} cards"))
    return analysis.analytic_pareto(
        ac.play_auto_chess,
        decks,
        threshold=0.01,
        multiprocess=True,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.INFO)
    analysis.log.setLevel(logging.INFO)
    res = run_tourney()
    log.info(f"the winners of the tournament are: {res}")
