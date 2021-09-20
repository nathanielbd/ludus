# Thresh+old, play on words!
#
# With each battle (aging), gets a token => upon death, will damage
# all enemies heavily (thresh) if goal age reached/surpased
# (threshold)

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class ThreshOld(Card):
    def __init__(self, *args, target_age: int = 4, **kwargs):
        # Minimum desired age for defeat/death
        self.target_age = target_age
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<ThreshOld({self.target_age}) {self.name} ({self.base_atk}/{self.health})>"

    def __eq__(self, other):
        return super().__eq__(other) and self.target_age == other.target_age

    def __hash__(self):
        return hash((super().__hash__(), self.target_age))

    def on_game_start(self, monster: Monster, gamestate: GameState) -> None:
        monster["current_age"] = 0
        super().on_game_start(monster, gamestate)

    def before_combat(self, monster: Monster, gamestate: GameState) -> None:
        log.info((f"{monster.print_at_game_state(gamestate)} "
                  f"ages one unit to {monster['current_age']} "))
        monster["current_age"] += 1
        super().on_game_start(monster, gamestate)

    def on_death(self, monster: Monster, gamestate: GameState) -> None:
        if monster["current_age"] >= self.target_age:
            log.info((f"{monster.print_at_game_state(gamestate)} "
                      f"died on or after target {self.target_age} units "
                      "and deals that much damage to all enemies"))
            opponent_gamestate = gamestate.invert()
            for enemy in list(gamestate.opponent.monsters):
                enemy.take_damage(opponent_gamestate, self.target_age)
        else:
            log.info((f"{monster.print_at_game_state(gamestate)} "
                      f"died before target {self.target_age} units "
                      "and heals its age to all allies"))
            for ally in list(gamestate.player.monsters):
                if ally is not monster:
                    ally.heal(gamestate, monster["current_age"])
        super().on_death(monster, gamestate)
