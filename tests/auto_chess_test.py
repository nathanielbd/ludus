import auto_chess
from auto_chess.ignore_first_damage import IgnoreFirstDamage


def test_one():
    tank = auto_chess.Card(1, 4, "tank")
    bruiser = auto_chess.Card(3, 1, "bruiser")
    deck_0 = [bruiser, bruiser]
    deck_1 = [bruiser, tank]
    assert auto_chess.play_auto_chess(deck_0, deck_1) == -1
    assert auto_chess.play_auto_chess(deck_1, deck_0) == 1
    assert auto_chess.play_auto_chess(deck_0, deck_0) == 0
    assert auto_chess.play_auto_chess(deck_1, deck_1) == 0


def test_armor_points():
    armor = IgnoreFirstDamage(3, 1, "armor", armor_points=1)
    bear = auto_chess.Card(2, 2, "bear")
    deck_0 = [armor]
    deck_1 = [bear]
    assert auto_chess.play_auto_chess(deck_0, deck_1) == 1
    assert auto_chess.play_auto_chess(deck_1, deck_0) == -1
    assert auto_chess.play_auto_chess(deck_0, deck_0) == 0
