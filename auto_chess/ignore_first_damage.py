from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class IgnoreFirstDamage(Card):
    def __init__(
            self,
            *args,
            armor_points: int = 1,
            **kwargs
    ):
        self.armor_points = armor_points
        super().__init__(*args, **kwargs)

    def on_game_start(self, monster: Monster, gamestate: GameState) -> None:
        monster["armor_points"] = self.armor_points

    def __str__(self) -> str:
        return f"<IgnoreFirstdamage({self.armor_points}) {self.name} ({self.base_atk}/{self.health})>"

    def __eq__(self, other):
        return super().__eq__(self, other) and self.armor_points == other.armor_points

    def __hash__(self):
        return hash((super().__hash__(), self.armor_points))

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        if monster["armor_points"] > 0:
            log.info(f"{monster.print_at_game_state(gamestate)} loses an armor point")
            monster["armor_points"] -= 1
        else:
            super().take_damage(monster, gamestate, damage)
