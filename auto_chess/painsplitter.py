# Shares damage taken with allies, partitioning it between them

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class PainSplitter(Card):
    # dmg_percent should be in [0, 100] for how much of the damage
    # this card receives (rest split evenly between remaining allies)
    def __init__(self, *args, dmg_percent: int = 50, **kwargs):
        self.dmg_percent = dmg_percent
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<PainSplitter({self.dmg_percent}) {self.name} ({self.base_atk}/{self.health})>"

    def __eq__(self, other):
        return super().__eq__(self, other) and self.dmg_percent == other.dmg_percent

    def __hash__(self):
        return hash(super().__hash__(), self.dmg_percent)

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        if damage > 0 and monster.is_alive():
            friends = [m for m in gamestate.player.monsters
                       if m is not monster]
            if len(friends) == 0:
                # If no additional allies left, then this card
                # receives all the damage regardless
                log.info((f"{monster.print_at_game_state(gamestate)} shares"
                          f" {damage} damage with allies, but no allies left"))
                super().take_damage(monster, gamestate, damage)
            else:
                # Compute damage allocated to current card and allies,
                # then distribute
                log.info((f"{monster.print_at_game_state(gamestate)} shares"
                          " damage with allies, and takes "
                          f"{self.dmg_percent} percent of {damage} damage"))

                # Round for this monster such that the remaining
                # damage to distribute is even (handling either 1 or 2
                # remaining without reducing total damage taken)
                received_dmg = ((damage * self.dmg_percent) // 100) \
                    + ((damage - ((damage * self.dmg_percent) // 100)) % 2)
                super().take_damage(monster, gamestate, received_dmg)
                ally_dmg = (damage - received_dmg) // len(gamestate.player.monsters)
                for ally in friends:
                    if ally is not monster:
                        ally.take_damage(gamestate, ally_dmg)
