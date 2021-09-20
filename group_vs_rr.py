import auto_chess as ac
import analysis
import analysis.sampling as sampling
import run_tournament as tourney
import pickle
import math
import os
import logging


log = logging.getLogger(__name__)


def compare_sampling(cards: list[ac.Card], deck_size=3) -> None:
    decks = ac.possible_decks(deck_size, cards)

    def output_trial_data(subdir, trial_number, data):
        os.makedirs(subdir, exist_ok=True)
        with open(subdir + "/trial_" + str(trial_number), "wb") as outfile:
            pickle.dump(list(data), outfile)

    for grp_frac in [2, 3, 4, 6, 12]:
        # some of the more interesting factor
        group_size = 1788 / grp_frac
        assert group_size % 1 == 0

        group_size = int(group_size)

        subdir = "group_v_rr_res/group_size_" + str(group_size)

        for trial in range(0, 16):
            data = sampling.group_tournament(
                ac.play_auto_chess,
                decks,
                group_size=group_size,
            )
            output_trial_data(subdir, trial, data)

            log.info("finished trial %d for group size %d", trial, group_size)

    real_results = analysis.round_robin(
        ac.play_auto_chess,
        decks,
        multiprocess=True,
    )

    output_trial_data("group_v_rr_res/round_robin", 0, real_results)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    compare_sampling(tourney.ALL_CARDS)
