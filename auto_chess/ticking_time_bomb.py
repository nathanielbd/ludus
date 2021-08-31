# With each interaction (damage or heal), gets a token => if in a
# battle with enough tokens, simply self destructs to kill both it and
# the defender
#
# NOTE: If killed before detonation, then nothing happens (defused)

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class TimeBomb(Card):
    def __init__(self, *args, detonation_time: int = 10, **kwargs):
        # Minimum desired tokens to detonate
        self.detonation_time = detonation_time
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<TimeBomb({self.detonation_time}) {self.name} ({self.base_atk}/{self.health})>"

    def before_combat(self, monster: Monster, gamestate: GameState) -> None:
        """If enough time has elapsed, explode!"""
        if monster["current_time"] > self.detonation_time:
            log.info((f"{monster.print_at_game_state(gamestate)} detonates "
                      f"to kill itself and {gamestate.defender} "))
            self.on_death(monster, gamestate)
            if gamestate.defender is not None:
                gamestate.defender.on_death(gamestate.invert())

    def decrease_countdown(self, monster: Monster, gamestate: GameState) -> None:
        monster["current_time"] += 1

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        if damage > 0:
            self.decrease_countdown(monster, gamestate)
        super().take_damage(monster, gamestate, damage)

    def heal(self, monster: Monster, gamestate: GameState, health: int) -> None:
        if health > 0:
            self.decrease_countdown(monster, gamestate)
        super().heal(monster, gamestate, health)

    def on_game_start(self, monster: Monster, gamestate: GameState) -> None:
        monster["current_time"] = 0  # Begin at no counters
        super().on_game_start(monster, gamestate)
