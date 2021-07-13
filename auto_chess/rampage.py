#Ramp+age, play on words!
#With each battle (aging), first gets stronger (ramps up), then gets weaker (ramps down) => based on middle-age threshold

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class RampAge(Card):
    def __init__(self, *args, middle_age: int = 4, **kwargs):
        self.middle_age = middle_age #Inflection point for stronger vs. weaker
        self.current_age = 0 #Begin at youngest age
        super().__init__(*args, **kwargs)

    def on_battle_start(self, monster: Monster, gamestate: GameState) -> None:
        log.info((f"{monster.print_at_game_state(gamestate)} "
                  f"ages one unit to {self.current_age} "))
        self.current_age += 1 #Gets one unit older in age
        super().on_battle_start(monster, gamestate)

    def current_atk(self, monster: Monster, gamestate: GameState) -> int:
        if self.current_age <= self.midde_age:
            log.info((f"{monster.print_at_game_state(gamestate)} "
                      f"is younger than {self.middle_age} units and gets stronger"))
            return self.base_atk + self.current_age
        else:
            log.info((f"{monster.print_at_game_state(gamestate)} "
                      f"is older than {self.middle_age} units and gets weaker"))
            return self.base_atk - (self.current_age - self.middle_age)
