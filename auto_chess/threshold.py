#Thresh+old, play on words!
#With each battle (aging), gets a token => upon death, will damage all enemies heavily (thresh) if goal age reached/surpased (threshold)

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class ThreshOld(Card):
    def __init__(self, *args, target_age: int = 4, **kwargs):
        self.target_age = target_age #Minimum desired age for defeath/death
        self.current_age = 0 #Begin at youngest age
        super().__init__(*args, **kwargs)

    def on_battle_start(self, monster: Monster, gamestate: GameState) -> None:
        log.info((f"{monster.print_at_game_state(gamestate)} "
                  f"ages one unit to {self.current_age} "))
        self.current_age += 1 #Gets one unit older in age
        super().on_battle_start(monster, gamestate)

    def on_death(self, monster: Monster, gamestate: GameState) -> int:
        if self.current_age >= self.target_age:
            log.info((f"{monster.print_at_game_state(gamestate)} "
                      f"died on or after target {self.target_age} units and deals that much damage to all enemies"))
            opponent_gamestate = gamestate.invert()
            for enemy in gamestate.opponent.monsters:
                enemy.take_damage(opponent_gamestate, self.target_age)
        else:
            log.info((f"{monster.print_at_game_state(gamestate)} "
                      f"died before target {self.target_age} units and heals gap in ages to all allies"))
            for ally in gamestate.player.monsters:
                if ally is not self:
                    ally.heal(gamestate, self.target_age - self.current_age)
