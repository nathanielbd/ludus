import pathos.multiprocessing as mproc  # type: ignore
import logging
from typing import Sequence, Iterable
from analysis import Deck, round_robin, PayoffFn, DeckResults
from random import shuffle


log = logging.getLogger(__name__)


def partition(elts: Sequence[Deck], group_size: int) -> Iterable[Sequence[Deck]]:
    for start in range(0, len(elts), group_size):
        yield elts[start:start + group_size]


def group_tournament(
        payoff_fn: PayoffFn,
        decks: Sequence[Deck],
        *,
        group_size: int = 64,
        group_winners: int = 8,  # the number of decks that will "survive" each group
        stages_before_finals: int = 1,
) -> Iterable[DeckResults]:
    def run_group_stage(group: list[Deck]) -> Iterable[Deck]:
        results = list(round_robin(
            payoff_fn,
            group,
            multiprocess=False,
        ))

        # these have to be functions because python can't map accessors...
        def payoff(res: DeckResults) -> float:
            return res.avg_payoff

        def deck(res: DeckResults) -> Deck:
            return res.deck

        results.sort(reverse=True, key=payoff)
        return list(map(deck, results[:8]))

    remaining_decks: list = list(decks)

    with mproc.ProcessPool() as pool:
        for stage in range(stages_before_finals):
            shuffle(remaining_decks)
            groups = list(partition(remaining_decks, group_size))

            log.info(
                "group stage %d with %d groups of %d decks each (%d total decks)",
                stage, len(groups), group_size, len(decks),
            )

            winners = pool.uimap(run_group_stage, groups)

            remaining_decks = [deck for group in winners for deck in group]

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

    return round_robin(
        payoff_fn,
        remaining_decks,
        multiprocess=True,
    )