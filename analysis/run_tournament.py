import auto_chess as ac
import analysis
import analysis.sampling as sampling

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


from typing import Iterable

import logging


log = logging.getLogger(__name__)


EXPLODE_ON_DEATH = ExplodeOnDeath(2, 1, "volatile")
FRIENDLY_VAMPIRE = FriendlyVampire(1, 3, "friendly vampire")
GROW_ON_DAMAGE = GrowOnDamage(0, 5, "bezerker")
HEAL_ALLIES_ON_DEATH = HealOnDeath(1, 2, "suicidal cleric")
HEALTHDONOR = HealthDonor(1, 4, "good friend")
IGNORE_FIRST_DAMAGE = IgnoreFirstDamage(2, 1, "armor")
MORPH_ENEMIES = MorphOpponents(0, 3, "morph ball")
PAINSPLITTER = PainSplitter(2, 2, "bad friend")
RAMPAGE = RampAge(0, 4, "old fogey")
SURVIVALIST = Survivalist(2, 2, "coward")
THRESHOLD = ThreshOld(2, 2, "curmudgeon")
TIME_BOMB = TimeBomb(1, 8, "time bomb")


ALL_CARDS = (EXPLODE_ON_DEATH,
             FRIENDLY_VAMPIRE,
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


def run_tourney() -> Iterable[analysis.DeckResults]:
    decks = ac.possible_decks(3, ALL_CARDS)
    log.info(
        "running a 2-stage group tournament between %d decks composed of %d cards",
        len(decks), len(ALL_CARDS),
    )
    # return analysis.round_robin(
    #     ac.play_auto_chess,
    #     decks,
    #     multiprocess=True,
    # )
    return sampling.group_tournament(
        ac.play_auto_chess,
        decks,
        stages_before_finals=2,
        group_size=512,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.INFO)
    analysis.log.setLevel(logging.INFO)
    sampling.log.setLevel(logging.INFO)
    res = run_tourney()
    log.info("tournament results are are:\n%s", list(res))
