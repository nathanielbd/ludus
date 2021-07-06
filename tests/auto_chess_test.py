import auto_chess as ac
from auto_chess.ignore_first_damage import IgnoreFirstDamage
from auto_chess.explode_on_death import ExplodeOnDeath
from auto_chess.heal_allies_on_death import HealOnDeath

import pytest


BEAR = ac.Card(2, 2, "bear")
TANK = ac.Card(1, 4, "tank")
BRUISER = ac.Card(3, 1, "bruiser")


def test_one():
    deck_0 = [BRUISER, BRUISER]
    deck_1 = [BRUISER, TANK]
    assert ac.play_auto_chess(deck_0, deck_1) == ac.P1_WIN
    assert ac.play_auto_chess(deck_1, deck_0) == ac.P0_WIN
    assert ac.play_auto_chess(deck_0, deck_0) == ac.TIE
    assert ac.play_auto_chess(deck_1, deck_1) == ac.TIE


def test_armor_points():
    armor = IgnoreFirstDamage(3, 1, "armor", armor_points=1)
    deck_0 = [armor]
    deck_1 = [BEAR]
    assert ac.play_auto_chess(deck_0, deck_1) == ac.P0_WIN
    assert ac.play_auto_chess(deck_1, deck_0) == ac.P1_WIN
    assert ac.play_auto_chess(deck_0, deck_0) == ac.TIE


def test_explode_on_death():
    bomb = ExplodeOnDeath(1, 1, "bomb", explode_damage=1)
    assert ac.play_auto_chess([bomb], [BEAR]) == ac.TIE
    assert ac.play_auto_chess([BEAR], [bomb]) == ac.TIE


def test_heal_on_death():
    good_healer = HealOnDeath(1, 1, "good_healer", explode_heal=3)
    bad_healer = HealOnDeath(1, 1, "bad_healer", explode_heal=1)
    assert ac.play_auto_chess([BRUISER, TANK],
                              [TANK, good_healer]) == ac.P1_WIN
    assert ac.play_auto_chess([BRUISER, TANK],
                              [TANK, bad_healer]) == ac.P0_WIN
    assert ac.play_auto_chess([TANK, good_healer],
                              [TANK, bad_healer]) == ac.TIE


@pytest.mark.timeout(1)  # in seconds
def test_zero_atk_tie():
    zeroatk = ac.Card(0, 1, "zeroatk")
    assert ac.play_auto_chess([zeroatk], [zeroatk]) == ac.TIE


def phony_gamestate():
    return ac.GameState(
        ac.Player([]),
        ac.Player([]),
    )


def test_negative_atk():
    bear = ac.Monster(BEAR)
    for i in (0, -1):
        before_hp = bear._remaining_health
        bear.take_damage(phony_gamestate(), i)
        assert bear._remaining_health == before_hp


def test_negative_heal():
    bear = ac.Monster(BEAR)
    bear._remaining_health = 1
    for i in (0, -1):
        before_hp = bear._remaining_health
        bear.heal(phony_gamestate(), i)
        assert bear._remaining_health == before_hp
