# Shares healing amount with allies, partitioning it between them

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class HealthDonor(Card):
    # heal_percent should be in [0, 100] for how much of the recovery
    # this card receives (rest split evenly between remaining allies)
    def __init__(self, *args, heal_percent: int = 50, **kwargs):
        self.heal_percent = heal_percent
        super().__init__(*args, **kwargs)

    def heal(self, monster: Monster, gamestate: GameState, health: int) -> None:
        if health > 0:
            if len(gamestate.player.monsters) == 0:
                # If no additional allies left, then this card
                # receives all the health regardless
                log.info((f"{monster.print_at_game_state(gamestate)}"
                          " shares health with allies, but no allies left"))
                super().heal(monster, gamestate, health)
            else:
                # Compute health allocated to current card and allies,
                # then distribute
                log.info((f"{monster.print_at_game_state(gamestate)}"
                          " shares health with allies, "
                          f"recovers {self.heal_percent} percent of {health} health"))
                # Round for this monster such that the remaining
                # health to distribute is even (handling either 1 or 2
                # remaining without reducing total damage taken)
                received_health = ((health * self.heal_percent) // 100) \
                    + ((health - ((health * self.heal_percent) // 100)) % 2)
                super().heal(monster, gamestate, received_health)
                ally_health = (health - received_health) \
                    // len(gamestate.player.monsters)
                for ally in list(gamestate.player.monsters):
                    if ally is not self:
                        ally.heal(gamestate, ally_health)
