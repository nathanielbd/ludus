import analysis.simulated_annealing as sa
import analysis.metrics as metrics
import logging
import pickle
import auto_chess as ac


log = logging.getLogger(__name__)


GROUP_SIZE = 256


def optimize_five_atkhp(initval=5):
    return sa.optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        initval=[initval] * 12,
        build_cards_fn=sa.cards_with_atkhp,
    )


def round_robin_optimize():
    return sa.optimize(
        metric=metrics.std_dev_metric,
        group_size=2000,
        initval=[5] * 10,
        build_cards_fn=sa.build_cards,
    )

def set_rotation():
    with open("optimize_five_atkhp.pickle", "rb") as picklein:
        first_set_res = pickle.load(picklein)
    first_set_vector = first_set_res.x
    first_set = sa.cards_with_atkhp(*first_set_vector)
    def set_two_cards(stats):
        return first_set + sa.other_cards_with_atkhp(*stats)
    return sa.optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        initval=[5] * 14,
        build_cards_fn=set_two_cards,
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
    return sa.optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        initval=[1, 8, 3, 6, 5, 4, 7, 2],
        build_cards_fn=vanilla_cards,
)


EXPERIMENTS = (
    (vanilla_cards_expt, "vanilla_cards"),
    (optimize_five_atkhp, "optimize_five_atkhp"),
    (set_rotation, "set_rotation"),
    (lambda: optimize_five_atkhp(initval=1), "optimize_five_start_at_one"),

    # leave this last!
    (round_robin_optimize, "round_robin_optimize"),
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
