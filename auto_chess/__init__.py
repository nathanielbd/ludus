"""An auto-chess game

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
import itertools
from typing import Iterable, Optional, NamedTuple, Sequence, Tuple, TypedDict
import logging
from analysis import GamePayoffs


log = logging.getLogger(__name__)


class GameState(NamedTuple):
    player: 'Player'
    opponent: 'Player'
    attacker: Optional['Monster']
    defender: Optional['Monster']
    

    def invert(self) -> 'GameState':
        assert self.attacker is not None
        assert self.defender is not None
        return GameState(self.opponent, self.player, self.defender, self.attacker)


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
        return f"<monster {self._name} {self._dict}>"

    def current_atk(self, gamestate: GameState) -> int:
        return self._card.current_atk(self, gamestate)

    def is_alive(self) -> bool:
        return self._remaining_health > 0

    def print_at_game_state(self, game: GameState) -> str:
        return (f"<monster {self._name} ({self._remaining_health}) "
                f": {self._card}>")

    # convenience methods which defer to the Card:
    def atk(self, state: GameState) -> int:
        return self._card.current_atk(self, state)

    def heal(self, state: GameState, health: int) -> None:
        self._card.heal(self, state, health)

    def take_damage(self, game: GameState, damage: int) -> None:
        self._card.take_damage(self, game, damage)

    def on_death(self, game: GameState) -> None:
        self._card.on_death(self, game)

    def on_game_start(self, game: GameState) -> None:
        self._card.on_game_start(self, game)

    def before_combat(self, game: GameState) -> None:
        self._card.before_combat(self, game)


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

    def __str__(self) -> str:
        return f"<card {self.name} ({self.base_atk}/{self.health})>"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name \
            and self.base_atk == other.base_atk \
            and self.health == other.health

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def __hash__(self):
        return hash((self.name, self.base_atk, self.health))

    def _monster_name(self):
        return f"{self.name}-{_get_monster_id()}"

    # user-extensible methods:
    def on_game_start(self, monster: Monster, gamestate: GameState) -> None:
        """Called at the start of the game.

        This is where you initialize card-specific properties of the monster.
        """
        pass

    def before_combat(self, monster: Monster, gamestate: GameState) -> None:
        """Called before this monster punches an opposing monster

        (and gets punched back)
        """
        pass

    def heal(self, monster: Monster, gamestate: GameState, health: int) -> None:
        """Called when monster would restore health during a fight.

        If the health should actually be restored, defer to the
        superclass method rather than directly assigning
        monster._remaining_health.
        """
        if health <= 0:
            return
        log.info(
            "%s heals %d health",
            monster.print_at_game_state(gamestate), health,
        )
        new_hp = monster._remaining_health + health
        if new_hp > self.health:
            log.debug(
                "clamping healing %s for %d at %d",
                monster.print_at_game_state(gamestate), health, self.health,
            )
            new_hp = self.health
        monster._remaining_health = new_hp

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        """Called when monster would take damage during a fight.

        If the monster should actually take damage, defer to the
        superclass method rather than directly assigning
        monster._remaining_health.
        """
        if damage <= 0 or not monster.is_alive():
            return
        log.info("%s takes %d damage",
                 monster.print_at_game_state(gamestate), damage)
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
        # assign this to ensure is_alive returns false in the future
        monster._remaining_health = 0
        gamestate.player._remove_monster(monster)
        log.info("player %s's %s has died",
                 gamestate.player.name,
                 monster.print_at_game_state(gamestate))


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
            ", ".join(map(str, self.monsters))
        ]) + ">"

    def has_monsters(self) -> bool:
        return len(self.monsters) > 0

    def has_atk(self, gamestate: GameState) -> bool:
        def monster_has_attack(monster: Monster) -> bool:
            return monster.atk(gamestate) > 0
        return any(map(monster_has_attack, self.monsters))

    def _next_monster(self) -> Optional[Monster]:
        if self.has_monsters():
            monster = self.monsters.popleft()
            assert monster.is_alive()
            log.info(
                "player %s's next monster is %s",
                self.name, monster,
            )
            return monster
        else:
            log.info("%s has no monsters", self)
            return None

    def _enqueue_monster(self, monster):
        self.monsters.append(monster)

    def _remove_monster(self, monster):
        log.debug(
            "%s will remove %s",
            self, monster,
        )
        try:
            self.monsters.remove(monster)
            log.debug(
                "%s has removed %s",
                self, monster,
            )
        except ValueError:
            log.debug(
                "%s did not contain %s",
                self, monster,
            )
            pass

    def _on_game_start(self, gamestate):
        for monster in list(self.monsters):
            monster.on_game_start(gamestate)


P0_WIN = GamePayoffs.zero_sum_payoff(1)
P1_WIN = GamePayoffs.zero_sum_payoff(-1)
TIE = GamePayoffs.zero_sum_payoff(0)


class _Game:
    """A running game of auto chess."""
    def __init__(
            self,
            p0_deck: Iterable[Card],
            p1_deck: Iterable[Card],
            *,
            max_turns: int = 128,
    ):
        self.max_turns = max_turns
        self.players: tuple[Player, Player] = (Player(p0_deck, "zero"),
                                               Player(p1_deck, "one"))

    def p0(self) -> Player:
        return self.players[0]

    def p1(self) -> Player:
        return self.players[1]

    def maybe_end(self) -> Optional[GamePayoffs]:
        """If the game is over, returns p0's payoff. Otherwise, returns False.
        """
        if self.p0().has_monsters() and self.p1().has_monsters():
            (gs0, gs1) = self.gamestates()
            if not (self.p0().has_atk(gs0) or self.p1().has_atk(gs1)):
                return TIE
            else:
                return None
        elif (not self.p0().has_monsters()) and (not self.p0().has_monsters()):
            return TIE
        elif self.p0().has_monsters():
            return P0_WIN
        elif self.p1().has_monsters():
            return P1_WIN
        else:
            log.error("What the Heck")
            exit(1)

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
                          monsters[0],
                          monsters[1]),
                GameState(self.players[1],
                          self.players[0],
                          monsters[1],
                          monsters[0]))

    def fight_in_parallel(self, monsters: tuple[Monster, Monster]):
        gamestates = self.gamestates(monsters)

        log.info(
            "%s is fighting %s",
            monsters[0].print_at_game_state(gamestates[0]),
            monsters[1].print_at_game_state(gamestates[1]),
        )

        for (monster, gamestate) in zip(monsters, gamestates):
            monster.before_combat(gamestate)

        # the above step may have killed one or both monsters, so test
        # for that before battling.
        if all(monster.is_alive() for monster in monsters):
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

    def get_monsters(self) -> tuple[Monster, Monster]:
        m0 = self.p0()._next_monster()
        assert m0 is not None
        assert m0.is_alive()
        m1 = self.p1()._next_monster()
        assert m1 is not None
        assert m1.is_alive()
        return (m0, m1)

    def single_turn(self) -> Optional[GamePayoffs]:
        res = self.maybe_end()
        if res is not None:
            return res
        self.fight_in_parallel(self.get_monsters())
        self.print_players()
        return None

    def start_battle(self) -> None:
        for gamestate in self.gamestates():
            gamestate.player._on_game_start(gamestate)
            self.print_players()

    def print_players(self) -> None:
        for gamestate in self.gamestates():
            log.info(f"{gamestate.player}:")
            for monster in gamestate.player.monsters:
                log.info(f"  {monster.print_at_game_state(gamestate)}")

    def play(self) -> GamePayoffs:
        log.info("Starting game between %s and %s", self.p0(), self.p1())
        self.start_battle()
        for i in range(self.max_turns):
            res = self.single_turn()
            log.debug(f"that turn's result was {res}")
            if res is not None:
                return res
        log.info("Cutting off a game at %d turns", self.max_turns)
        return TIE


GAME_HASH_TABLE: dict[Tuple[Tuple[Card, Card, Card], Tuple[Card, Card, Card]], GamePayoffs] = {}

def decks_to_tuple(deck: Iterable[Card]):
    if len(deck) != 3:
        log.error(f"Invalid deck length {deck}")
        return None
    else:
        return tuple([deck[0], deck[1], deck[2]])

def play_auto_chess(
        p0_deck: Iterable[Card],
        p1_deck: Iterable[Card],
) -> GamePayoffs:
    """Entry point: run a game between two decks.

    p0_deck and p1_deck should each be a list (or possibly an
    iterable? I'm unsure... - pgoldman 2021-06-30) of Card objects.

    Return's p0's payoff against p1: 1 if p0 wins, -1 if p1 wins, 0 if
    tie.

    """
    deck0 = decks_to_tuple(p0_deck)
    deck1 = decks_to_tuple(p1_deck)

    if deck0 == None or deck1 == None:
        return _Game(p0_deck, p1_deck).play()

    cached = GAME_HASH_TABLE.get((deck0, deck1))
    if cached != None:
        log.debug(f"Using cached value {cached} for decks {(deck0, deck1)}")
        return cached

    result = _Game(p0_deck, p1_deck).play()
    GAME_HASH_TABLE[(deck0, deck1)] = result
    log.debug(f"Cached new value {result} for decks {(deck0, deck1)}")
    return result

def possible_decks(deck_size: int, cards: Sequence[Card]) -> list[Sequence[Card]]:
    return list(itertools.product(cards, repeat=deck_size))
