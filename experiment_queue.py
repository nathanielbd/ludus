import analysis.simulated_annealing as sa
import analysis.metrics as metrics
import logging
import pickle
import auto_chess as ac
from typing import Callable, Dict, Iterable
from analysis import DeckResults


log = logging.getLogger(__name__)


GROUP_SIZE = 4 # 256

def tt_sd(results: Iterable[DeckResults],
        *,
        key: Callable[[float], float] = lambda n: n,
) -> float:
    return metrics.top_ten_percent_metric(results, metric=metrics.std_dev_metric)

def tt_ent(results: Iterable[DeckResults],
        *,
        key: Callable[[float], float] = lambda n: n,
) -> float:
    return metrics.top_ten_percent_metric(results, metric=metrics.entropy_metric)


def optimize_rand_atkhp():
    return sa.genetic_optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        num_genes=12,
        build_cards_fn=sa.cards_with_atkhp
    )


def only_special_opt():
    return sa.genetic_optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        num_genes=10,
        build_cards_fn=sa.build_cards
    )


def round_robin_optimize():
    return sa.genetic_optimize(
        # metric=metrics.std_dev_metric,
        metric=tt_ent,
        group_size=64, # 2000,
        num_genes=10,
        build_cards_fn=sa.build_cards
    )


def optimize_five_atkhp():
    return sa.genetic_optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        num_genes=12,
        build_cards_fn=sa.cards_with_atkhp,
    )

def set_rotation(first = "optimize_five_atkhp", second = sa.other_cards_with_atkhp):
    with open(f"{first}.pickle", "rb") as picklein:
        first_set_res = pickle.load(picklein)
    first_set_vector = first_set_res
    first_set = sa.cards_with_atkhp(*first_set_vector)
    def set_two_cards(*stats):
        return first_set + second(*stats)
    return sa.genetic_optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        num_genes=14,
        build_cards_fn=set_two_cards
    )


def vanilla_cards(
        atk_0, hp_0,
        atk_1, hp_1,
        atk_2, hp_2,
        atk_3, hp_3,
):
    return [
        ac.Card(atk_0, hp_0, "zero"),
        ac.Card(atk_1, hp_1, "one"),
        ac.Card(atk_2, hp_2, "two"),
        ac.Card(atk_3, hp_3, "three")
    ]


def vanilla_cards_expt():
    return sa.genetic_optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        num_genes=8,
        build_cards_fn=vanilla_cards
    )


def rr_tt_ent():
    return sa.genetic_optimize(
        # metric=metrics.std_dev_metric,
        metric=tt_ent,
        group_size=64, # 2000,
        num_genes=10,
        build_cards_fn=sa.build_cards
    )

def rr_tt():
    return sa.genetic_optimize(
        # metric=metrics.std_dev_metric,
        metric=metric.entropy_metric,
        group_size=64, # 2000,
        num_genes=10,
        build_cards_fn=sa.build_cards
    )

EXPERIMENTS = (
    # (optimize_five_atkhp, "optimize_five_atkhp"),
    # (set_rotation, "set_rotation"),

    # leave this last!
    # (round_robin_optimize, "round_robin_optimize_tt_test"),
    (rr_tt_ent, "rr_tt_ent"),
    (rr_tt, "rr_tt")
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    log.setLevel(logging.INFO)
    sa.log.setLevel(logging.INFO)
    for (experiment, name) in EXPERIMENTS:
        log.info("running experiment %s\n\n", name)
        outfile = f"{name}.txt"
        picklefile = f"{name}.pickle"
        logging.basicConfig(filename=outfile)
        res = experiment()
        with open(picklefile, "wb") as pickleout:
            pickle.dump(res, pickleout)
        log.info("finished experiment %s", name)
