from auto_chess import Card, Monster, GameState
import logging


log = logging.getLogger(__name__)


class FriendlyVampire(Card):
    """When (before) it enters combat, it heals the ally to its left
(i.e. last in the player's order)
    """
    def __init__(self, *args, heal_amount: int = 1, **kwargs):
        self.heal_amount = heal_amount
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<FriendlyVampire({self.heal_amount}) {self.name} ({self.base_atk}/{self.health})>"
    
    def __eq__(self, other):
        return super().__eq__(self, other) and self.heal_amount == other.heal_amount

    def __hash__(self):
        return hash(super().__hash__(), self.heal_amount)

    def before_combat(self, monster: Monster, gamestate: GameState) -> None:
        heal_target = None
        for friend in reversed(gamestate.player.monsters):
            if friend is not monster:
                heal_target = friend
                break

        if heal_target is None:
            log.info("no friendly monster to heal.")
            return

        heal_target.heal(gamestate, self.heal_amount)
        super().before_combat(monster, gamestate)
