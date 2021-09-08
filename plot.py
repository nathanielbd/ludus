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
import experiment_queue as exp
import analysis.simulated_annealing as sa

log = logging.getLogger(__name__)

THREAD_COUNT = 12
GROUP_SIZE = 96
# Number of runs to average over
NUM_RUNS = 24

def run_group(cards, group_size=None):
    decks = ac.possible_decks(3, cards)
    if group_size != None:
        return list(sampling.group_tournament(
            ac.play_auto_chess,
            decks,
            group_size=group_size
        ))
    else:
        return list(sampling.round_robin(
                    ac.play_auto_chess,
                    decks,
                    multiprocess=True
                ))

def histogram(cards, path, picklefile=None, title="Round Robin Winrates", deck=True, group_size=None):
    results = run_group(cards, group_size=group_size)
    if picklefile:
        with open(picklefile, "wb") as pickleout:
            pickle.dump(results, pickleout)

    if deck: 
        values = list(map(lambda x: metrics.payoff_winrate(x.avg_payoff), results))

    # case if we want the card distribution
    if not deck:
        values = metrics.weighted_sum_cards(results)
        log.info(f'std: {metrics.std_dev_metric(results)}')
        log.info(f'entropy: {metrics.entropy_metric(results)}')
        log.info(f'per card payoff: {metrics.per_card_winrate(results, variance_key=lambda x: x**2)}')
    fig = plt.figure()
    plt.hist(values, bins=50)
    plt.title(title)
    plt.xlabel('Win rate')
    if deck:
        plt.ylabel('Decks')
    else:
        plt.ylabel('Cards')
    fig.savefig(path)

def set_atk(c, v):
    c.base_atk = v

def set_health(c, v):
    c.health = v

def set_rampage(c, v):
    c.middle_age = v

def noop(c, v):
    return

def single_run(cards):
    rv = metrics.std_dev_metric(run_group(cards))
    print(cards, rv)
    return rv

def mean_of_multiple_runs(cards):
    runs = []
    for i in range(0, NUM_RUNS):
        runs.append(single_run(cards))
    print(cards, runs, np.mean(runs))
    return np.mean(runs)

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
        card1 = copy.deepcopy(var1_card)
        var1_key(card1, i)

        for j in var2_range:
            cards = copy.deepcopy(base_cards)
            if var2_card is None:
                var2_key(card1, j)
                cards.append(card1)
            else:
                card2 = copy.deepcopy(var2_card)
                var2_key(card2, j)
                cards.append(card1)
                cards.append(card2)
            row.append(copy.deepcopy(cards))
        
        with Pool(THREAD_COUNT) as p:
            results.append(list(p.map(single_run, row)))

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
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.colorbar()
    fig.savefig(name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.WARNING)

    histogram(sa.build_cards(1, 3, 4, 3, 3, 1, 7, 8, 5, 7), f"{sys.argv[1]}/special_only_1_3_4_3_3_1_7_8_5_7.png", picklefile=f"{sys.argv[1]}/special_only_1_3_4_3_3_1_7_8_5_7.pickle", deck=True, group_size=None)
    histogram(sa.build_cards(4, 5, 8, 8, 4, 8, 3, 3, 3, 5), f"{sys.argv[1]}/special_only_4_5_8_8_4_8_3_3_3_5.png", picklefile=f"{sys.argv[1]}/special_only_4_5_8_8_4_8_3_3_3_5.pickle", deck=True, group_size=None)

    histogram(sa.build_cards(1, 3, 4, 3, 3, 1, 7, 8, 5, 7), f"{sys.argv[1]}/special_only_1_3_4_3_3_1_7_8_5_7_cards.png", picklefile=f"{sys.argv[1]}/special_only_1_3_4_3_3_1_7_8_5_7_cards.pickle", deck=False, group_size=None)
    histogram(sa.build_cards(4, 5, 8, 8, 4, 8, 3, 3, 3, 5), f"{sys.argv[1]}/special_only_4_5_8_8_4_8_3_3_3_5_cards.png", picklefile=f"{sys.argv[1]}/special_only_4_5_8_8_4_8_3_3_3_5_cards.pickle", deck=False, group_size=None)

    exit(0)

    bruiser = colormap([tourney.BEAR, tourney.TANK, tourney.EXPLODE_ON_DEATH, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE, tourney.GROW_ON_DAMAGE], var1_card=tourney.BRUISER)
    with open(f"{sys.argv[1]}/bruiser.pickle", "wb") as pickleout:
        pickle.dump(bruiser, pickleout)
    makeplot(bruiser, f"{sys.argv[1]}/bruiser.png", title="Bruiser", xaxis="Health", yaxis="Attack")

    rampage = colormap([tourney.BEAR, tourney.TANK, tourney.BRUISER, tourney.EXPLODE_ON_DEATH, tourney.FRIENDLY_VAMPIRE, tourney.GROW_ON_DAMAGE], var1_card=tourney.RAMPAGE, var1_key=set_rampage, var2_range=range(1, 2), var2_key=noop)
    with open(f"{sys.argv[1]}/rampage.pickle", "wb") as pickleout:
        pickle.dump(rampage, pickleout)
    makeplot(rampage, f"{sys.argv[1]}/rampage.png", title="Rampage", xaxis="Age")

    grow_on_damage = colormap([tourney.BEAR, tourney.TANK, tourney.BRUISER, tourney.EXPLODE_ON_DEATH, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE], var1_card=tourney.GROW_ON_DAMAGE)
    with open(f"{sys.argv[1]}/grow_on_damage.pickle", "wb") as pickleout:
        pickle.dump(grow_on_damage, pickleout)
    makeplot(grow_on_damage, f"{sys.argv[1]}/grow_on_damage.png", title="Grow on Damage", xaxis="Health", yaxis="Attack")
    
    explode_on_death = colormap([tourney.BEAR, tourney.TANK, tourney.BRUISER, tourney.GROW_ON_DAMAGE, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE], var1_card=tourney.EXPLODE_ON_DEATH)
    with open(f"{sys.argv[1]}/explode_on_death.pickle", "wb") as pickleout:
        pickle.dump(explode_on_death, pickleout)
    makeplot(explode_on_death, f"{sys.argv[1]}/explode_on_death.png", title="Explode on Death", xaxis="Health", yaxis="Attack")

    bruiser_vs_grow = colormap([tourney.BEAR, tourney.TANK, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE, tourney.EXPLODE_ON_DEATH], var1_card=tourney.BRUISER, var1_key=set_atk, var2_card=tourney.GROW_ON_DAMAGE, var2_key=set_health)
    with open(f"{sys.argv[1]}/bruiser_vs_grow.pickle", "wb") as pickleout:
        pickle.dump(bruiser_vs_grow, pickleout)
    makeplot(bruiser_vs_grow, f"{sys.argv[1]}/bruiser_vs_grow.png", title="Bruiser Attack vs Grow on Damage Health", xaxis="Health", yaxis="Attack")

    bear_vs_grow = colormap([tourney.TANK, tourney.BRUISER, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE, tourney.EXPLODE_ON_DEATH], var1_card=tourney.BEAR, var1_key=set_atk, var2_card=tourney.GROW_ON_DAMAGE, var2_key=set_health)
    with open(f"{sys.argv[1]}/bear_vs_grow.pickle", "wb") as pickleout:
        pickle.dump(bear_vs_grow, pickleout)
    makeplot(bear_vs_grow, f"{sys.argv[1]}/bear_vs_grow.png", title="Bear Attack vs Grow on Damage Health", xaxis="Health", yaxis="Attack")

    bruiser_vs_explode = colormap([tourney.BEAR, tourney.TANK, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE, tourney.GROW_ON_DAMAGE], var1_card=tourney.BRUISER, var1_key=set_atk, var2_card=tourney.EXPLODE_ON_DEATH, var2_key=set_health)
    with open(f"{sys.argv[1]}/bruiser_vs_explode.pickle", "wb") as pickleout:
        pickle.dump(bruiser_vs_explode, pickleout)
    makeplot(bruiser_vs_explode, f"{sys.argv[1]}/bruiser_vs_explode.png", title="Bruiser Attack vs Explode on Death Health", xaxis="Health", yaxis="Attack")

