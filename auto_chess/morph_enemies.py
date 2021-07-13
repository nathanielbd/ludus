#Morph has a variable attack stat, copying the opponent's card's attack values
#  To maintain determinism, iterate over the opponent's cards in order

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class MorphOpponents(Card):
    def __init__(self, *args, **kwargs):
        self.next_to_morph = 0 #Always begin with defender as morphing target
        super().__init__(*args, **kwargs)

    def on_battle_start(self, monster: Monster, gamestate: GameState) -> None:
        log.info((f"{monster.print_at_game_state(gamestate)} "
                  f"sets its attack to match {self.next_to_morph}'s attack"))
        #Identify the morph target via the offset of next_to_morph from the defender
        modulus = len(gamestate.opponent.monsters)
        if gamestate.opponent.defender is not None:
            modulus = modulus + 1
        #0 offset is the defender, if one exists
        if ((self.next_to_morph % modulus) = 0) and gamestate.opponent.defender is not None:
            monster["current_atk"] = gamestate.defender.base_atk
        #non-0 offset is another opponent, if there was a defender
        elif gamestate.opponent.defender is not None:
            monster["current_atk"] = gamestate.opponent[(self.next_to_morph % modulus) - 1].base_atk
        #Without a defender, it is another opponent no matter what
        else:
            monster["current_atk"] = gamestate.opponent[(self.next_to_morph % modulus)].base_atk
        
        #Increment the index for the next morph target
        self.next_to_morph = self.next_to_morph + 1

    def current_atk(self, monster: Monster, gamestate: GameState) -> int:
        return monster["current_atk"]
