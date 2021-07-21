#Shares damage taken with allies, partitioning it between them

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class PainSplitter(Card):
    #dmg_percent should be in [0, 100] for how much of the damage this card receives (rest split evenly between remaining allies)
    def __init__(self, *args, dmg_percent: int = 50, **kwargs):
        self.dmg_percent = dmg_percent
        super().__init__(*args, **kwargs)

    def take_damage(self, monster: Monster, gamestate: GameState, damage: int) -> None:
        if damage > 0:
            #If no additional allies left, then this card receives all the damage regardless
            if len(gamestate.player) = 0:
                log.info((f"{monster.print_at_game_state(gamestate)} shares damage with allies, but no allies left "
                          f"takes {damage} damage"))
                super().take_damage(monster, gamestate, damage)
            #Compute damage allocated to current card and allies, then distribute
            #NOTE: Round for this monster such that the remaining damage to distribute is even (handling either 1 or 2 remaining without reducing total damage taken)
            else:
                log.info((f"{monster.print_at_game_state(gamestate)} shares damage with allies, "
                          f"takes {self.dmg_percent} percent of {damage} damage"))
                received_dmg = ((damage * self.dmg_percent) / 100) + ((damage - ((damage * self.dmg_percent) / 100)) % 2)
                super().take_damage(monster, gamestate, received_damage)
                ally_dmg = (damage - received_dmg) / len(gamestate.player)
                for ally in gamestate.player:
                    if ally is not self:
                    ally.take_damage(gamestate, ally_dmg)
