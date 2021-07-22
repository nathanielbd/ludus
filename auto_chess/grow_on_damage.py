from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class GrowOnDamage(Card):
    def __init__(self, *args, atk_per_hit: int = 1, **kwargs):
        self.atk_per_hit = atk_per_hit
        super().__init__(*args, **kwargs)

    def on_game_start(self, monster: Monster, gamestate: GameState) -> None:
        monster["current_atk"] = self.base_atk
        super().on_game_start(monster, gamestate)

    def current_atk(self, monster: Monster, gamestate: GameState) -> int:
        return monster["current_atk"]

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        if damage > 0:
            monster["current_atk"] += self.atk_per_hit
        super().take_damage(monster, gamestate, damage)
