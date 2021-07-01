"""An auto-chess game

FIXME: detect case where zero-attack monsters will cause an infinite
       battle and return a tie

FIXME: do something sensible for negative-attack monsters - clamp to
       zero?

You are intended to create cards with interesting abilities by
subclassing Card, and defining methods on its various hooks. Each of
these hooks will take at least three arguments:
- The Card as self. This must be immutable, as it is shared between
  many monsters and many games.
- The Monster, which is a mutable in-game representation.
- The GameState, a namedtuple which includes handles on various
  mutable aspects of the game state.
  - GameState.player is a Player object for the controller of the
    monster whose method is being invoked. Depending on the context,
    that monster may or may not appear in that Player's monsters
    deque.
  - GameState.opponent is a Player object for the other player.
  - GameState.defender is the other Monster involved in battle, or
    None in contexts where no Monster vs Monster combat is
    happening. If GameState.defender is not None, that monster will
    not appear in the Gamestate.opponent.monsters deque.
  - GameState.print_output is a boolean, which if True means verbose
    output should be printed to stdout about the progress of the game.

Generally, you should not subclass Monster, as they are intended only
as proxy objects for accessing Cards. You may, however, store
arbitrary mutable properties within a Monster. You should not mutate
the private properties defined in Monster below, nor overwrite its
card.

If you want do define a new hook on Card, you must:

- define a method on Card which takes as arguments: self, monster,
  gamestate, followed by any others.
- define a method on Monster which takes as arguments: self,
  gamestate, followed by any others, and invokes the associated method
  on Monster._card.
- Find the appropriate spot in Game to invoke that method. At that
  spot:
  1. construct a GameState object with handles on each Player in
     player and opponent. If during combat, also put a handle on the
     other monster in defender.
  2. invoke the method on Monster, with the GameState and any other
     arguments.

"""

import collections
from typing import Iterable, Optional, Any, Callable

class Monster:
    """A monster wihin an active game of auto-chess."""
    def __init__(self, card):
        self._card = card
        self._remaining_health: int = card.health
        self._name = card._monster_name()

    def is_alive(self) -> int:
        return self._remaining_health > 0

    def print_at_game_state(self, game) -> str:
        return f"<monster {self._name} ({self.atk(game)}/{self._remaining_health}) : {self._card}>"

    # convenience methods which defer to the Card:
    def atk(self, state) -> int:
        return self._card.current_atk(self, state)

    def take_damage(self, game, damage: int):
        self._card.take_damage(self, game, damage)

    def on_death(self, game):
        self._card.on_death(self, game)

_next_monster_id: int = 0
def _get_monster_id() -> int:
    global _next_monster_id
    current = _next_monster_id
    _next_monster_id += 1
    return current

GameState = collections.namedtuple(
    "GameState",
    ["print_output", "player", "opponent", "defender"],
    defaults = [None], # note that defaults apply to the rightmost
                       # fields, so this default is for defender (as
                       # there will be times when no defender is
                       # active)
)

class Card:
    """A game piece which represents a monster to be used in a game of auto-chess.

    These objects must be immutable. You should never ever assign to
    their fields outside of the constructor under any circumstances.

    Note that the order in which methods will be invoked between
    competing monsters is unpredictable: e.g. when monsters m0 and m1
    fight and both die, their cards' on_death methods may be called
    either m0 -> m1 or m1 -> m0.
    """
    def __init__(self, atk: int, health: int, name: str):
        self.base_atk = atk
        self.health = health
        self.name = name
    def __str__(self):
        return f"<card {self.name} ({self.base_atk}/{self.health})>"
    def _monster_name(self):
        return f"{self.name}-{_get_monster_id()}"

    # user-extensible methods:
    def take_damage(self, monster, gamestate, damage):
        """Called when monster would take damage during a fight.

        If the monster should actually take damage, defer to the
        superclass method rather than directly assigning
        monster._remaining_health.
        """
        monster._remaining_health -= damage
        if not monster.is_alive():
            monster.on_death(gamestate)

    def current_atk(self, monster, gamestate) -> int:
        """Compute and return monster's atk at a given game state.

        May call super().current_atk(monster, game) to defer to the
        number printed on the card.

        These methods may rely on being called before taking damage in
        a fight, and so may inspect their monster's remaining_health.

        These methods should not write any fields of the game, nor of
        the monster, as they may be called multiple times.
        """
        return self.base_atk

    def on_death(self, monster, gamestate):
        """Hook called when a monster would die.

        If this hook restore's the monster's health, it will not be treated as dead.

        If the monster should actually die, defer to the superclass method.
        """
        gamestate.player._remove_monster(monster)
        if gamestate.print_output:
            print(f"{gamestate.player}'s {monster.print_at_game_state(self)} has died.")

def _instantiate_deck(deck: Iterable[Card]) -> collections.deque[Monster]:
    return collections.deque(map(Monster, deck))

class Player:
    def __init__(self, deck: Iterable[Card]):
        self.monsters: collections.deque[Monster] = _instantiate_deck(deck)

    def has_monsters(self) -> bool:
        return len(self.monsters) > 0

    def _next_monster(self) -> Optional[Monster]:
        if self.has_monsters():
            monster = self.monsters.popleft()
            assert monster.is_alive()
            return monster
        else:
            return None

    def _enqueue_monster(self, monster):
        self.monsters.append(monster)

    def _remove_monster(self, monster):
        if monster in self.monsters:
            self.monsters.remove(monster)

P0_WIN = 1
P1_WIN = -1
TIE = 0

class Game:
    """A running game of auto chess.

    Most hook methods on Card will take a Game object as an argument,
    so that effects may alter the game state.
    """
    def __init__(
            self,
            p0_deck: Iterable[Card],
            p1_deck: Iterable[Card],
            print_output: bool = True,
    ):
        self._players: tuple[Player, Player] = (Player(p0_deck), Player(p1_deck))
        self.print_output = print_output

    def _p0(self) -> Player:
        return self._players[0]

    def _p1(self) -> Player:
        return self._players[1]

    def _maybe_end(self) -> Optional[int]:
        """If the game is over, returns p0's payoff. Otherwise, returns False."""
        if self._p0().has_monsters() and self._p1().has_monsters():
            return None
        elif self._p0().has_monsters():
            return P0_WIN
        elif self._p1().has_monsters():
            return P1_WIN
        else:
            return TIE

    def _gamestates(self, monsters: Optional[list[Monster]] = None) -> list[GameState]:
        if monsters is None:
            monsters = [None, None]
        assert len(monsters) == 2
        return list(map(
            GameState,
            [self.print_output, self.print_output], # GameState.print_output
            self._players, # GameState.player
            reversed(self._players), # GameState.opponent
            reversed(monsters), # GameState.defender
        ))

    def _fight_in_parallel(self, monsters: list[Monster]):
        if self.print_output:
            print(
                f"{monsters[0].print_at_game_state(self)} is fighting {monsters[1].print_at_game_state(self)}"
            )

        gamestates = self._gamestates(monsters)

        # read these in parallel before writing anything, in case taking damage changes them
        atks = [monster.atk(gamestate) for (monster, gamestate) in zip(monsters, gamestates)]

        for (monster, damage, gamestate) in zip(
                monsters,
                reversed(atks),
                gamestates,
        ):
            monster.take_damage(gamestate, damage)

        for (monster, gamestate) in zip(monsters, gamestates):
            if monster.is_alive():
                gamestate.player._enqueue_monster(monster)

        return self._maybe_end()

    def _single_turn(self):
        res = self._maybe_end()
        if res is not None:
            return res
        monsters = [player._next_monster() for player in self._players]
        [m0, m1] = monsters
        assert m0 and m0.is_alive() and m1 and m1.is_alive()
        self._fight_in_parallel(monsters)

    def _play(self):
        while True:
            res = self._single_turn()
            if self.print_output:
                print(f"that turn's result was {res}")
            # this nasty line brought to you by 0 being falsey and == to False
            if res is not None:
                return res

def play_auto_chess(
        p0_deck: Iterable[Card],
        p1_deck: Iterable[Card],
        print_output: bool = True,
):
    """Entry point: run a game between two decks.

    p0_deck and p1_deck should each be a list (or possibly an
    iterable? I'm unsure... - pgoldman 2021-06-30) of Card objects.

    Return's p0's payoff against p1: 1 if p0 wins, -1 if p1 wins, 0 if
    tie.

    Unless print_output is supplied and false-ey, will print game
    status to standard output.

    """
    return Game(p0_deck, p1_deck, print_output)._play()
