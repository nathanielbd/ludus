import auto_chess


def test_one():
    tank = auto_chess.Card(1, 4, "tank")
    bruiser = auto_chess.Card(3, 1, "bruiser")
    deck_0 = [bruiser, bruiser]
    deck_1 = [bruiser, tank]
    assert auto_chess.play_auto_chess(deck_0, deck_1, False) == -1
    assert auto_chess.play_auto_chess(deck_1, deck_0, False) == 1
    assert auto_chess.play_auto_chess(deck_0, deck_0, False) == 0
    assert auto_chess.play_auto_chess(deck_1, deck_1, False) == 0
