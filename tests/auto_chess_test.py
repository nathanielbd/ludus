from auto_chess import Card, play_auto_chess, P0_WIN, P1_WIN, TIE
from auto_chess.ignore_first_damage import IgnoreFirstDamage
from auto_chess.explode_on_death import ExplodeOnDeath
from auto_chess.heal_allies_on_death import HealOnDeath

import pytest


BEAR = Card(2, 2, "bear")
TANK = Card(1, 4, "tank")
BRUISER = Card(3, 1, "bruiser")


def test_one():
    deck_0 = [BRUISER, BRUISER]
    deck_1 = [BRUISER, TANK]
    assert play_auto_chess(deck_0, deck_1) == P1_WIN
    assert play_auto_chess(deck_1, deck_0) == P0_WIN
    assert play_auto_chess(deck_0, deck_0) == TIE
    assert play_auto_chess(deck_1, deck_1) == TIE


def test_armor_points():
    armor = IgnoreFirstDamage(3, 1, "armor", armor_points=1)
    deck_0 = [armor]
    deck_1 = [BEAR]
    assert play_auto_chess(deck_0, deck_1) == P0_WIN
    assert play_auto_chess(deck_1, deck_0) == P1_WIN
    assert play_auto_chess(deck_0, deck_0) == TIE


def test_explode_on_death():
    bomb = ExplodeOnDeath(1, 1, "bomb", explode_damage=1)
    assert play_auto_chess([bomb], [BEAR]) == TIE
    assert play_auto_chess([BEAR], [bomb]) == TIE


def test_heal_on_death():
    good_healer = HealOnDeath(1, 1, "good_healer", explode_heal=3)
    bad_healer = HealOnDeath(1, 1, "bad_healer", explode_heal=1)
    assert play_auto_chess([BRUISER, TANK],
                           [TANK, good_healer]) == P1_WIN
    assert play_auto_chess([BRUISER, TANK],
                           [TANK, bad_healer]) == P0_WIN
    assert play_auto_chess([TANK, good_healer],
                           [TANK, bad_healer]) == TIE


@pytest.mark.timeout(1)  # in seconds
def test_zero_atk_tie():
    zeroatk = Card(0, 1, "zeroatk")
    assert play_auto_chess([zeroatk], [zeroatk]) == TIE
