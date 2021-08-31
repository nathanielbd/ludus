from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class ExplodeOnDeath(Card):
    def __init__(self, *args, explode_damage: int = 1, **kwargs):
        self.explode_damage = explode_damage
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<ExplodeOnDeath({self.explode_damage}) {self.name} ({self.base_atk}/{self.health})>"

    def on_death(self, monster: Monster, gamestate: GameState) -> None:
        log.info((f"{monster.print_at_game_state(gamestate)} explodes "
                  f"for {self.explode_damage} damage"))
        opponent_gamestate = gamestate.invert()
        for enemy in list(gamestate.opponent.monsters):
            log.debug(f"{enemy.print_at_game_state(opponent_gamestate)} taking {self.explode_damage} explosion damage")
            enemy.take_damage(opponent_gamestate, self.explode_damage)
        if gamestate.defender and gamestate.defender.is_alive():
            log.debug(f"Defender {gamestate.defender.print_at_game_state(opponent_gamestate)} taking {self.explode_damage} explosion damage")
            gamestate.defender.take_damage(opponent_gamestate, self.explode_damage)
        super().on_death(monster, gamestate)
