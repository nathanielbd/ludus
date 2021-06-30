"""An auto-chess game

FIXME: detect case where zero-attack monsters will cause an infinite
       battle and return a tie

FIXME: do something sensible for negative-attack monsters - clamp to zero?

FIXME: some way for monster hooks to get a handle on the monster
       they're fighting.

You are intended to create cards with interesting abilities by
subclassing Card, and defining methods on its various hooks. Each of
these hooks will take at least three arguments:
- The Card as self. This must be immutable, as it is shared between
  many monsters and many games.
- The Monster, which is a mutable in-game representation.
- The Game, a mutable representation of the game state.
The game's Game.active_player and Game.opponent methods will return
Player objects denoting the monster's controller and opponent,
respectively.

Generally, you should not subclass Monster, as they are intended only
as proxy objects for accessing Cards. You may, however, store
arbitrary mutable properties within a Monster. You should not mutate
the private properties defined in Monster below, nor overwrite its
card.

If you want do define a new hook on Card, you must:

- define a method on Card which takes as arguments: self, monster,
  game, followed by any others.
- define a method on _Monster which takes as arguments: self, game,
  followed by any others, and invokes the associated method on
  Monster._card.
- Find the appropriate spot in Game to invoke that method. At that
  spot:
  1. get a handle on the monster and its controlling player
  2. construct a local function of no arguments which invokes the
     appropriate method on the monster.
  3. pass that function to Game._call_with_active_player.
  This will arrange for the game's Game.active_player and
  Game.opponent methods to return appropriate values.

"""

import collections

class Monster:
    """A monster wihin an active game of auto-chess."""
    def __init__(self, card):
        self._card = card
        self._remaining_health = card.health
        self._name = card._monster_name()

    def is_alive(self):
        return self._remaining_health > 0

    def print_at_game_state(self, game):
        return f"<monster {self._name} ({self.atk(game)}/{self._remaining_health}) : {self._card}>"

    # convenience methods which defer to the Card:
    def atk(self, game):
        return self._card.current_atk(self, game)

    def take_damage(self, game, damage):
        self._card.take_damage(self, game, damage)

    def on_death(self, game):
        self._card.on_death(self, game)

_next_monster_id = 0
def _get_monster_id():
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
    def __init__(self, atk, health, name):
        self.base_atk = atk
        self.health = health
        self.name = name
    def __str__(self):
        return f"<card {self.name} ({self.base_atk}/{self.health})>"
    def _monster_name(self):
        return f"{self.name}-{_get_monster_id()}"

    # user-extensible methods:
    def take_damage(self, monster, game, damage):
        """Called when monster would take damage during a fight.

        If the monster should actually take damage, defer to the
        superclass method rather than directly assigning
        monster._remaining_health.
        """
        monster._remaining_health -= damage
    def current_atk(self, monster, game):
        """Compute and return monster's atk at a given game state.

        May call super().current_atk(monster, game) to defer to the
        number printed on the card.

        These methods may rely on being called before taking damage in
        a fight, and so may inspect their monster's remaining_health.

        These methods should not write any fields of the game, nor of
        the monster, as they may be called multiple times.
        """
        return self.base_atk
    def on_death(self, monster, game):
        """Hook called when a monster dies.

        Note that, by this point, the monster is already dead - this
        hook cannot revive it.
        """
        pass

def _instantiate_deck(deck):
    return collections.deque(map(Monster, deck))

class Player:
    def __init__(self, deck):
        self.monsters = _instantiate_deck(deck)
    def has_monsters(self):
        return len(self.monsters) > 0
    def _next_monster(self):
        while self.has_monsters():
            monster = self.monsters.popleft()
            if monster.is_alive():
                return monster
        return False
    def _enqueue_monster(self, monster):
        self.monsters.append(monster)

P0_WIN = 1
P1_WIN = -1
TIE = 0

class Game:
    """A running game of auto chess.

    Most hook methods on Card will take a Game object as an argument,
    so that effects may alter the game state.
    """
    def __init__(self, p0_deck, p1_deck, print_output=True):
        self._players = [Player(p0_deck), Player(p1_deck)]
        self.print_output = print_output
        self._active_player = None

    def _p0(self):
        return self._players[0]

    def _p1(self):
        return self._players[1]

    def active_player(self):
        """Return the Player which controlsthe active monster"""
        assert isinstance(self._active_player, Player)
        return self._active_player

    def opponent(self):
        """Return the Player which is the opponent of the active monster's controller."""
        active = self.active_player()
        if active is self._players[0]:
            return self._players[1]
        elif active is self._players[1]:
            return self._players[0]
        else:
            raise Exception(f"Game.active_player() {active} is not in Game._players! {self._players}")

    def _maybe_end(self):
        """If the game is over, returns p0's payoff. Otherwise, returns False."""
        if self._p0().has_monsters() and self._p1().has_monsters():
            return False
        elif self._p0().has_monsters():
            return P0_WIN
        elif self._p1().has_monsters():
            return P1_WIN
        else:
            return TIE

    def _call_with_active_player(self, player, fn):
        """Every call to a Monster or Card hook must be enclosed in a
        _call_with_active_player which binds that monster's controller.
        """
        self._active_player = player
        fn()
        self._active_player = None

    def _fight_in_parallel(self, monsters):
        if self.print_output:
            print(f"{monsters[0].print_at_game_state(self)} is fighting {monsters[1].print_at_game_state(self)}")
        # read these in parallel before writing anything, in case taking damage changes them
        atks = [m.atk(self) for m in monsters]

        for (active_player, monster, damage) in zip(self._players, monsters, reversed(atks)):
            def monster_damaged():
                monster.take_damage(self, damage)
            self._call_with_active_player(active_player, monster_damaged)

        for (active_player, monster) in zip(self._players, monsters):
            if monster.is_alive():
                active_player._enqueue_monster(monster)
            else:
                def monster_dies():
                    if self.print_output:
                        print(f"{active_player}'s {monster.print_at_game_state(self)} has died.")
                    monster.on_death(self)
                self._call_with_active_player(active_player, monster_dies)

        return self._maybe_end()

    def _single_turn(self):
        monsters = [player._next_monster() for player in self._players]
        [m0, m1] = monsters
        if m0 and m1:
            return self._fight_in_parallel(monsters)
        elif m0:
            return P0_WIN
        elif m1:
            return P1_WIN
        else:
            return TIE

    def _play(self):
        while True:
            res = self._single_turn()
            if self.print_output:
                print(f"that turn's result was {res}")
            # this nasty line brought to you by 0 being falsey and == to False
            if res is not False:
                return res

def play_auto_chess(p0_deck, p1_deck, print_output=True):
    """Entry point: run a game between two decks.

    p0_deck and p1_deck should each be a list (or possibly an
    iterable? I'm unsure... - pgoldman 2021-06-30) of Card objects.

    Return's p0's payoff against p1: 1 if p0 wins, -1 if p1 wins, 0 if
    tie.

    Unless print_output is supplied and false-ey, will print game
    status to standard output.

    """
    return Game(p0_deck, p1_deck, print_output)._play()
