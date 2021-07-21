#Swaps remaining health and attack whenever the attack stat is greater, effectively weakening in exchange for more health

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class PainSplitter(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        super().take_damage(monster, gamestate, damage)
        self.swap_health_atk(monster, gamestate)

    def heal(self, state: GameState, health: int) -> None:
        super().heal(monster, gamestate, damage)
        self.swap_health_atk(monster, gamestate)

    def swap_health_atk(self, monster: Monster, gamestate: GameState) -> None:
        log.info((f"{monster.print_at_game_state(gamestate)} checks whether to swap health and attack, "
                  f"attack {self.base_atk} vs. health {self.health} (health should be greater of two)"))
        if self.attack > self.health:
            temp = self.attack
            self.attack = self.health
            self.health = temp
