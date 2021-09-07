# Ramp+age, play on words!
#
# With each battle (aging), first gets stronger (ramps up), then gets
# weaker (ramps down) => based on middle-age threshold

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class RampAge(Card):
    def __init__(self, *args, middle_age: int = 4, **kwargs):
        # Inflection point for stronger vs. weaker
        self.middle_age = middle_age
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<RampAge({self.middle_age}) {self.name} ({self.base_atk}/{self.health})>"

    def __eq__(self, other):
        return super().__eq__(self, other) and self.middle_age == other.middle_age

    def __hash__(self):
        return hash((super().__hash__(), self.middle_age))

    def on_game_start(self, monster: Monster, gamestate: GameState) -> None:
        monster["current_age"] = 0
        super().on_game_start(monster, gamestate)

    def before_combat(self, monster: Monster, gamestate: GameState) -> None:
        monster["current_age"] += 1
        log.info((f"{monster.print_at_game_state(gamestate)} "
                  f"ages one unit to {monster['current_age']} "))
        super().before_combat(monster, gamestate)

    def current_atk(self, monster: Monster, gamestate: GameState) -> int:
        try:
            if monster["current_age"] <= self.middle_age:
                return self.base_atk + monster["current_age"]
            else:
                return self.base_atk \
                    + self.middle_age \
                    - (monster["current_age"] - self.middle_age)
        except KeyError:
            return self.base_atk
