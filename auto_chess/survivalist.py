# Swaps remaining health and attack whenever the attack stat is
# greater, effectively weakening in exchange for more health

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class Survivalist(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_game_start(self, monster: Monster, game: GameState) -> None:
        monster["atk"] = self.base_atk
        super().on_game_start(monster, game)

    def current_atk(self, monster: Monster, game: GameState) -> int:
        return monster["atk"]

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        super().take_damage(monster, gamestate, damage)
        self.swap_health_atk(monster, gamestate)

    def heal(self, monster: Monster, state: GameState, health: int) -> None:
        super().heal(monster, state, health)
        self.swap_health_atk(monster, state)

    def swap_health_atk(self, monster: Monster, gamestate: GameState) -> None:
        if monster.atk(gamestate) > monster._remaining_health:
            log.info((f"{monster.print_at_game_state(gamestate)}"
                      " swaps its attack for its health"))
            temp = monster["atk"]
            monster["atk"] = monster._remaining_health
            monster["atk"] = temp
