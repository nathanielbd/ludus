"""An auto-chess game

FIXME: detect case where zero-attack monsters will cause an infinite
       battle and return a tie

FIXME: do something sensible for negative-attack monsters - clamp to zero?

You are intended to create cards with interesting abilities by
subclassing Card, and defining methods on its various hooks.

"""
import collections

class _Monster:
    """A monster wihin an active game of auto-chess."""
    def __init__(self, card):
        self.card = card
        self.remaining_health = self.card.health
        self.name = card._monster_name()
    def is_alive(self):
        return self.remaining_health > 0
    def atk(self, game):
        return self.card.current_atk(self, game)
    def take_damage(self, dmg, game):
        self.card.take_damage(self, dmg, game)
    def on_death(self, game):
        self.card.on_death(self, game)
    def print_at_game_state(self, game):
        return f"<monster {self.name} {self.atk(game)} / {self.remaining_health} : {self.card}>"

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
        return f"<card {self.name} {self.base_atk} / {self.health}>"
    def _monster_name(self):
        return f"{self.name}-{_get_monster_id()}"
    def _instantiate(self):
        return _Monster(self)
    # user-extensible methods:
    def take_damage(self, monster, dmg, game):
        """Called when monster would take damage during a fight.

        If the monster should actually take damage, defer to the
        superclass method rather than directly assigning
        monster.remaining_health.
        """
        monster.remaining_health -= dmg
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
        pass

def _instantiate_deck(deck):
    return collections.deque(map(_Monster, deck))

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
    def __init__(self, p0_deck, p1_deck, print_output=True):
        self.p0 = Player(p0_deck)
        self.p1 = Player(p1_deck)
        self.print_output = print_output
    def _maybe_end(self):
        """If the game is over, returns p0's payoff. Otherwise, returns False."""
        if self.p0.has_monsters() and self.p1.has_monsters():
            return False
        elif self.p0.has_monsters():
            return P0_WIN
        elif self.p1.has_monsters():
            return P1_WIN
        else:
            return TIE
    def _fight_in_parallel(self, m0, m1):
        if self.print_output:
            print(f"{m0.print_at_game_state(self)} is fighting {m1.print_at_game_state(self)}")
        # read these in parallel before writing anything, in case taking damage changes them
        m0_atk = m0.atk(self)
        m1_atk = m1.atk(self)
        m0.take_damage(m1_atk, self)
        m1.take_damage(m0_atk, self)
        if m0.is_alive():
            self.p0._enqueue_monster(m0)
        else:
            if self.print_output:
                print(f"p0's {m0.print_at_game_state(self)} has died.")
            m0.on_death(self)
        if m1.is_alive():
            self.p1._enqueue_monster(m1)
        else:
            if self.print_output:
                print(f"p1's {m1.print_at_game_state(self)} has died")
            m1.on_death(self)
        return self._maybe_end()
    def _single_turn(self):
        m0 = self.p0._next_monster()
        m1 = self.p1._next_monster()
        if m0 and m1:
            return self._fight_in_parallel(m0, m1)
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
    """Return's p0's payoff against p1: 1 if p0 wins, -1 if p1 wins, 0 if tie."""
    return Game(p0_deck, p1_deck, print_output)._play()
