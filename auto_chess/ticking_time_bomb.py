#With each interaction (damage or heal), gets a token => if in a battle with enough tokens, simply self destructs to kill both it and the defender
#NOTE: If killed before detonation, then nothing happens (defused)

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class TimeBomb(Card):
    def __init__(self, *args, detonation_time: int = 10, **kwargs):
        self.detonation_time = detonation_time #Minimum desired tokens to detonate
        self.current_time = 0 #Begin at no counters
        super().__init__(*args, **kwargs)

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        if damage > 0:
            self.current_time += 1 #Interaction via damage, increase countdown
        super().take_damage(monster, gamestate, damage)

    def heal(self, monster: Monster, gamestate: GameState, health: int) -> None:
        if health >= 0:
            self.current_time += 1 #Interaction via healing, increase countdown
        super().heal(monster, gamestate, health)

    def on_battle_start(self, monster: Monster, gamestate: GameState) -> None:
        if current_time > detonation_time:
            log.info((f"{monster.print_at_game_state(gamestate)} detonates "
                      f"to kill itself and {gamestate.defender} "))
            self.take_damage(monster, gamestate, self.health + 1000) #Overkill to guarantee death
            gamestate.defender.take_damage(gamestate.invert(), gamestate.defender.health + 1000) #Overkill to guarantee death
        else:
            super().on_battle_start(monster, gamestate)
