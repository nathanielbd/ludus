import pathos.multiprocessing as mproc  # type: ignore
import logging
from typing import Sequence, Iterable
from analysis import Deck, analytic_pareto, PayoffFn
from random import shuffle


log = logging.getLogger(__name__)


def partition(elts: Sequence[Deck], group_size: int) -> Iterable[Sequence[Deck]]:
    for start in range(0, len(elts), group_size):
        yield elts[start:start + group_size]


def approximate_pareto_group_tournament(
        payoff_fn: PayoffFn,
        decks: Sequence[Deck],
        *,
        threshold: float = 0,
        group_size: int = 64,
        stages_before_finals: int = 1,
) -> Sequence[Deck]:
    shuffle(decks)
    def run_group_stage(group: list[Deck]) -> list[Deck]:
        return analytic_pareto(
            payoff_fn,
            group,
            threshold=threshold,
            multiprocess=False,
        )

    remaining_decks = decks

    with mproc.ProcessPool() as pool:
        for stage in range(stages_before_finals):
            shuffle(remaining_decks)
            groups = list(partition(remaining_decks, group_size))

            log.info(
                "group stage %d with %d groups of %d decks each (%d total decks)",
                stage, len(groups), group_size, len(decks),
            )

            group_winners = pool.uimap(run_group_stage, groups)

            remaining_decks = [deck for group in group_winners for deck in group]

            log.info(
                "after group stage %d, there are %d decks (%f percent of the field)",
                stage, len(remaining_decks), len(remaining_decks) / len(decks),
            )

            if len(remaining_decks) <= group_size:
                log.info(
                    "fewer decks remaining than one group; cutting directly to finals"
                )
                break

    log.info(
        "after the group stages, %d decks remain (%f percent of the field)",
        len(remaining_decks), len(remaining_decks) / len(decks),
    )
    log.debug("the finalists after the group stages are: %s", remaining_decks)

    return analytic_pareto(
        payoff_fn,
        remaining_decks,
        threshold=threshold,
        multiprocess=True,
    )
