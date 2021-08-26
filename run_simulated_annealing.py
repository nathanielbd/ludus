import analysis.simulated_annealing as sa
import analysis.metrics as metrics
import logging

ACCEPTABLE_GROUP_SIZE = 256
ITERATIONS = 512  # i guess?

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sa.log.setLevel(logging.INFO)
    sa.optimize(
        metric=metrics.entropy_metric,
        opt_iters=ITERATIONS,
        group_size=ACCEPTABLE_GROUP_SIZE,
    )
