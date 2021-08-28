from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class HealOnDeath(Card):
    def __init__(self, *args, explode_heal: int = 1, **kwargs):
        self.explode_heal = explode_heal
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<HealOnDeath({self.explode_heal}) {self.name} ({self.base_atk}/{self.health})>"

    def on_death(self, monster: Monster, gamestate: GameState) -> None:
        log.info((f"{monster.print_at_game_state(gamestate)} "
                  f"heals its allies for {self.explode_heal} health"))
        for ally in list(gamestate.player.monsters):
            if ally is not monster:
                ally.heal(gamestate, self.explode_heal)
        super().on_death(monster, gamestate)
