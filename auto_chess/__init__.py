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
- The Monster, which is a mutable in-game representation and behaves
  like a dict.
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

Generally, you should not subclass Monster, as they are intended only
as proxy objects for accessing Cards. You may, however, store
arbitrary mutable properties within a Monster, as if it were a
dict. You should not mutate the private properties defined in Monster
below, nor overwrite its card.

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
from typing import Iterable, Optional, NamedTuple
import logging


log = logging.getLogger(__name__)


class GameState(NamedTuple):
    player: 'Player'
    opponent: 'Player'
    defender: Optional['Monster'] = None

    def invert(self, attacker=None) -> 'GameState':
        return GameState(self.opponent, self.player, attacker)


class Monster:
    """A monster wihin an active game of auto-chess."""
    def __init__(self, card: 'Card'):
        self._card: 'Card' = card
        self._remaining_health: int = card.health
        self._name: str = card._monster_name()
        self._dict: dict = {}

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value) -> None:
        self._dict[key] = value

    def __str__(self) -> str:
        return f"{self._name} {self._dict}"

    def is_alive(self) -> bool:
        return self._remaining_health > 0

    def print_at_game_state(self, game: GameState) -> str:
        return f"<monster {self._name} ({self.atk(game)}/{self._remaining_health}) \
: {self._card}>"

    # convenience methods which defer to the Card:
    def atk(self, state: GameState) -> int:
        return self._card.current_atk(self, state)

    def take_damage(self, game: GameState, damage: int) -> None:
        self._card.take_damage(self, game, damage)

    def on_death(self, game: GameState) -> None:
        self._card.on_death(self, game)

    def on_battle_start(self, game: GameState) -> None:
        self._card.on_battle_start(self, game)


_next_monster_id: int = 0


def _get_monster_id() -> int:
    global _next_monster_id
    current = _next_monster_id
    _next_monster_id += 1
    return current


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
    def on_battle_start(self, monster: Monster, gamestate: GameState) -> None:
        """Called at the start of the battle."""
        pass

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        """Called when monster would take damage during a fight.

        If the monster should actually take damage, defer to the
        superclass method rather than directly assigning
        monster._remaining_health.
        """
        log.info(f"{monster.print_at_game_state(gamestate)} takes {damage} damage")
        monster._remaining_health -= damage
        if not monster.is_alive():
            monster.on_death(gamestate)

    def current_atk(self, monster: Monster, gamestate: GameState) -> int:
        """Compute and return monster's atk at a given game state.

        May call super().current_atk(monster, game) to defer to the
        number printed on the card.

        These methods may rely on being called before taking damage in
        a fight, and so may inspect their monster's remaining_health.

        These methods should not write any fields of the game, nor of
        the monster, as they may be called multiple times.
        """
        return self.base_atk

    def on_death(self, monster: Monster, gamestate: GameState) -> None:
        """Hook called when a monster would die.

        If this hook restore's the monster's health, it will not be
        treated as dead.

        If the monster should actually die, defer to the superclass
        method.

        """
        gamestate.player._remove_monster(monster)
        log.info(f"{gamestate.player}'s \
{monster.print_at_game_state(gamestate)} \
has died.")


def _instantiate_deck(deck: Iterable[Card]) -> collections.deque[Monster]:
    return collections.deque(map(Monster, deck))


class Player:
    def __init__(self, deck: Iterable[Card], name: Optional[str] = None):
        self.name: str = name or f"player-{_get_monster_id()}"
        self.monsters: collections.deque[Monster] = _instantiate_deck(deck)

    def __str__(self) -> str:
        return " ".join([
            "<player",
            self.name,
            "controls",
            ", ".join(map(str, self.monsters)),
            ">"
        ])

    def has_monsters(self) -> bool:
        return len(self.monsters) > 0

    def _next_monster(self) -> Optional[Monster]:
        if self.has_monsters():
            monster = self.monsters.popleft()
            assert monster.is_alive()
            log.info(f"{self}'s next monster is {monster}")
            return monster
        else:
            log.info(f"{self} has no monsters")
            return None

    def _enqueue_monster(self, monster):
        self.monsters.append(monster)

    def _remove_monster(self, monster):
        log.debug(f"{self} will remove {monster}")
        try:
            self.monsters.remove(monster)
            log.debug(f"{self} has removed {monster}")
        except ValueError:
            log.debug(f"{self} did not contain {monster}")
            pass

    def _on_battle_start(self, gamestate):
        for monster in self.monsters:
            monster.on_battle_start(gamestate)


P0_WIN = 1
P1_WIN = -1
TIE = 0


class _Game:
    """A running game of auto chess."""
    def __init__(
            self,
            p0_deck: Iterable[Card],
            p1_deck: Iterable[Card],
    ):
        self.players: tuple[Player, Player] \
            = (Player(p0_deck, "zero"), Player(p1_deck, "one"))

    def p0(self) -> Player:
        return self.players[0]

    def p1(self) -> Player:
        return self.players[1]

    def maybe_end(self) -> Optional[int]:
        """If the game is over, returns p0's payoff. Otherwise, returns False.
        """
        if self.p0().has_monsters() and self.p1().has_monsters():
            return None
        elif self.p0().has_monsters():
            return P0_WIN
        elif self.p1().has_monsters():
            return P1_WIN
        else:
            return TIE

    def gamestates(
            self,
            monsters: tuple[Optional[Monster], Optional[Monster]] = (None, None),
    ) -> tuple[GameState, GameState]:
        assert isinstance(monsters, tuple), f"{monsters} is a {type(monsters)}"
        if monsters[0] is not None:
            assert monsters[1] is not None
        else:
            assert monsters[1] is None

        return (GameState(self.players[0],
                          self.players[1],
                          monsters[1]),
                GameState(self.players[1],
                          self.players[0],
                          monsters[0]))

    def fight_in_parallel(self, monsters: tuple[Monster, Monster]):
        gamestates = self.gamestates(monsters)

        log.info(
                f"{monsters[0].print_at_game_state(gamestates[0])} \
is fighting \
{monsters[1].print_at_game_state(gamestates[1])}"
            )

        # read these in parallel before writing anything, in case
        # taking damage changes them
        atks = [
            monster.atk(gamestate)
            for (monster, gamestate)
            in zip(monsters, gamestates)
        ]

        for (monster, damage, gamestate) in zip(
                monsters,
                reversed(atks),
                gamestates,
        ):
            monster.take_damage(gamestate, damage)

        for (monster, gamestate) in zip(monsters, gamestates):
            if monster.is_alive():
                gamestate.player._enqueue_monster(monster)

        return self.maybe_end()

    def single_turn(self):
        res = self.maybe_end()
        if res is not None:
            return res
        monsters = tuple(player._next_monster() for player in self.players)
        (m0, m1) = monsters
        assert m0 is not None
        assert m0.is_alive()
        assert m1 is not None
        assert m1.is_alive()
        self.fight_in_parallel(monsters)
        self.print_players()

    def start_battle(self):
        for gamestate in self.gamestates():
            gamestate.player._on_battle_start(gamestate)
            self.print_players()

    def print_players(self):
        for gamestate in self.gamestates():
            log.info(f"{gamestate.player}:")
            for monster in gamestate.player.monsters:
                log.info(f"  {monster.print_at_game_state(gamestate)}")

    def play(self):
        self.start_battle()
        while True:
            res = self.single_turn()
            log.info(f"that turn's result was {res}")
            if res is not None:
                return res


def play_auto_chess(
        p0_deck: Iterable[Card],
        p1_deck: Iterable[Card],
):
    """Entry point: run a game between two decks.

    p0_deck and p1_deck should each be a list (or possibly an
    iterable? I'm unsure... - pgoldman 2021-06-30) of Card objects.

    Return's p0's payoff against p1: 1 if p0 wins, -1 if p1 wins, 0 if
    tie.

    """
    return _Game(p0_deck, p1_deck).play()
