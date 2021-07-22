# Morph has a variable attack stat, copying the opponent's card's
# attack values
#
# To maintain determinism, iterate over the opponent's cards in order

from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class MorphOpponents(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_game_start(self, monster: Monster, gamestate: GameState) -> None:
        monster["next_to_morph"] = 0   # Always begin with defender as morphing target

    def copy_atk(self, monster: Monster, state: GameState, copy_from: Monster) -> None:
        opponent_state = state.invert()
        log.info((f"{monster.print_at_game_state(state)} sets its attack to "
                  f"match {copy_from.print_at_game_state(opponent_state)}'s attack"))
        monster["current_atk"] = copy_from.current_atk(opponent_state)

    def before_combat(self, monster: Monster, gamestate: GameState) -> None:
        candidates = [defender for defender in [gamestate.defender] if defender]
        candidates.extend(gamestate.opponent.monsters)
        next_to_morph = candidates[monster["next_to_morph"] % len(candidates)]
        self.copy_atk(monster, gamestate, next_to_morph)
        monster["next_to_morph"] += 1

    def current_atk(self, monster: Monster, gamestate: GameState) -> int:
        return monster["current_atk"]
