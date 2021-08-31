import analysis.simulated_annealing as sa
import analysis.metrics as metrics
import logging
import pickle


GROUP_SIZE = 256


def optimize_five_atkhp(initval=5):
    return sa.optimize(
        metric=metrics.std_dev_metric,
        group_size=GROUP_SIZE,
        initval=[initval] * 12,
        build_cards_fn=sa.cards_with_atkhp,
    )


EXPERIMENTS = (
    (optimize_five_atkhp, "optimize_five_atkhp"),
    (lambda: optimize_five_atkhp(initval=1), "optimize_five_start_at_one"),
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sa.log.setLevel(logging.INFO)
    for (experiment, name) in EXPERIMENTS:
        outfile = f"{name}.txt"
        picklefile = f"{name}.pickle"
        logging.basicConfig(filename=outfile)
        res = experiment()
        with open(picklefile, "wb") as pickleout:
            pickle.dump(res, pickleout)
        log.info("finished experiment %s", name)
