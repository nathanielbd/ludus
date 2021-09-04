import logging
import auto_chess as ac
import analysis
import analysis.sampling as sampling
import run_tournament as tourney
import analysis.metrics as metrics
import numpy as np
import matplotlib.pyplot as plt
import pickle

log = logging.getLogger(__name__)

GROUP_SIZE = 8

def run_group(cards):
    decks = ac.possible_decks(3, cards)
    return sampling.group_tournament(
                ac.play_auto_chess,
                decks,
                group_size=GROUP_SIZE,
            )

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.WARNING)

    values = []
    for i in range(0, 16):
        with open(f"group_size_1024/trial_{i}", "rb") as picklein:
            values += list(map(lambda x: x.avg_payoff, pickle.load(picklein)))

    
    fig = plt.figure()
    plt.hist(values, bins=75)
    plt.title("Plot 2D array")
    # plt.ylabel('Attack')
    # plt.xlabel('Health')
    # plt.colorbar()
    fig.savefig(f"hist.png")

    exit(0)

    base_cards = [tourney.BEAR, tourney.TANK, tourney.BRUISER, tourney.EXPLODE_ON_DEATH, tourney.RAMPAGE, tourney.FRIENDLY_VAMPIRE]

    best = 0.0
    best_atk = 0
    best_health = 0

    results = []
    for i in range(1, 10):
        row = []
        for j in range(1, 10):
            card = tourney.GROW_ON_DAMAGE
            card.base_atk = i
            card.health = j
            res = metrics.std_dev_metric(run_group(base_cards + [card]))
            row.append(res)
            print(res)
            if res > best:
                best = res
                best_atk = i
                best_health = j
            
        results.append(row)
    
    print(results)
    print(best)
    print(best_atk)
    print(best_health)

    fig = plt.figure(figsize=(10,10))
    plt.pcolormesh(np.array(results), cmap='plasma')
    plt.title("Plot 2D array")
    plt.ylabel('Attack')
    plt.xlabel('Health')
    plt.colorbar()
    fig.savefig(f"{GROUP_SIZE}.png")
