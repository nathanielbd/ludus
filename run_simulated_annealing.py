import analysis.simulated_annealing as sa
import analysis.metrics as metrics
import logging
import pickle

ACCEPTABLE_GROUP_SIZE = 256
ITERATIONS = 128

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sa.log.setLevel(logging.INFO)
    res = sa.optimize(
        metric=metrics.entropy_metric,
        opt_iters=ITERATIONS,
        group_size=ACCEPTABLE_GROUP_SIZE,
    )
    with open("simulated_annealing_result.pickle", "wb") as out:
        pickle.dump(res, out)
    log.info("optimizer settled on {res}")
