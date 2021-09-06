from auto_chess import explode_on_death
import logging
import auto_chess as ac
import analysis
import analysis.sampling as sampling
import run_tournament as tourney
import analysis.metrics as metrics
import numpy as np
import matplotlib.pyplot as plt
import pickle
from typing import Callable
import sys
import copy
from multiprocessing import Pool

log = logging.getLogger(__name__)

GROUP_SIZE = 4

def run_group(cards):
    decks = ac.possible_decks(3, cards)
    return sampling.group_tournament(
                ac.play_auto_chess,
                decks,
                group_size=GROUP_SIZE,
            )

def histogram():
    values = []
    with open(f"round_robin/trial_0", "rb") as picklein:
        values = list(map(lambda x: x.avg_payoff, pickle.load(picklein)))

    fig = plt.figure()
    plt.hist(values, bins=50)
    plt.title("Round Robin Average Payoffs")
    fig.savefig(f"hist.png")

def set_atk(c, v):
    c.base_atk = v

def set_health(c, v):
    c.health = v

def f(cards):
    return metrics.std_dev_metric(run_group(cards))

def colormap(
    base_cards: list[ac.Card],
    var1_card: ac.Card,
    var1_key: Callable[[ac.Card, int], None] = set_atk,
    var1_range = range(1, 10),
    var2_card: ac.Card = None,
    var2_key: Callable[[ac.Card, int], None] = set_health,
    var2_range = range(1, 10),
):
    results = []
    for i in var1_range:
        row = []
        card1 = var1_card
        var1_key(card1, i)

        for j in var2_range:
            cards = base_cards + [card1]
            if var2_card is None:
                card2 = var1_card
                var2_key(card2, j)    
            else:
                card2 = copy.deepcopy(var2_card)
                var2_key(card2, j)
                cards.append(card2)
            print(cards)
            row.append(cards)

        with Pool(5) as p:
            results.append(list(p.map(f, row)))

    return results

def makeplot(data, name, title="Plot 2D array", xaxis=None, yaxis=None):
    if len(data) < 1:
        log.error("No Data")
        return
    
    # height = len(data)
    # width = len(data[0])
    
    fig = plt.figure()
    plt.pcolormesh(np.array(data), cmap='plasma')
    plt.title(title)
    plt.ylabel(xaxis)
    plt.xlabel(yaxis)
    plt.colorbar()
    fig.savefig(name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.WARNING)

    grow_on_damage = colormap([tourney.BEAR, tourney.TANK, tourney.BRUISER, tourney.EXPLODE_ON_DEATH, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE], var1_card=tourney.GROW_ON_DAMAGE)
    with open(f"{sys.argv[1]}/grow_on_damage.pickle", "wb") as pickleout:
        pickle.dump(grow_on_damage, pickleout)
    makeplot(grow_on_damage, f"{sys.argv[1]}/grow_on_damage.png")
    
    explode_on_death = colormap([tourney.BEAR, tourney.TANK, tourney.BRUISER, tourney.GROW_ON_DAMAGE, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE], var1_card=tourney.EXPLODE_ON_DEATH)
    with open(f"{sys.argv[1]}/explode_on_death.pickle", "wb") as pickleout:
        pickle.dump(explode_on_death, pickleout)
    makeplot(explode_on_death, f"{sys.argv[1]}/explode_on_death.png")

    bruiser_vs_grow = colormap([tourney.BEAR, tourney.TANK, tourney.BRUISER, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE, tourney.EXPLODE_ON_DEATH], var1_card=tourney.BRUISER, var1_key=set_atk, var2_card=tourney.GROW_ON_DAMAGE, var2_key=set_health)
    with open(f"{sys.argv[1]}/bruiser_vs_grow.pickle", "wb") as pickleout:
        pickle.dump(bruiser_vs_grow, pickleout)
    makeplot(bruiser_vs_grow, f"{sys.argv[1]}/bruiser_vs_grow.png")

