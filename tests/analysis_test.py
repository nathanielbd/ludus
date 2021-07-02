import analysis


ROCK = 0
PAPER = 1
SCISSORS = 2
ROCK_PAPER_SCISSORS = [ROCK, PAPER, SCISSORS]
ROCK_PAPER_SCISSORS_PAYOFFS = [[0, -1, 1],
                               [1, 0, -1],
                               [-1, 1, 0]]


def play_rock_paper_scissors(p0, p1):
    return ROCK_PAPER_SCISSORS_PAYOFFS[p0][p1]


def test_analytic_pareto_rock_paper_scissors():
    frontier = analysis.analytic_pareto(
        play_rock_paper_scissors,
        ROCK_PAPER_SCISSORS,
    )
    assert frontier == ROCK_PAPER_SCISSORS


def test_analytic_pareto_symmetry():
    frontier_asymmetric = analysis.analytic_pareto(
        play_rock_paper_scissors,
        ROCK_PAPER_SCISSORS,
        zero_sum=False,
    )
    assert frontier_asymmetric == ROCK_PAPER_SCISSORS
    frontier_symmetric = analysis.analytic_pareto(
        play_rock_paper_scissors,
        ROCK_PAPER_SCISSORS,
        zero_sum=True,
    )
    assert frontier_symmetric == ROCK_PAPER_SCISSORS


def test_skewed_frontier():
    just_rock = analysis.analytic_pareto(
        play_rock_paper_scissors,
        [ROCK, SCISSORS],
    )
    assert just_rock == [ROCK]


def test_multiprocessing():
    parallel_frontier_zero_sum = analysis.analytic_pareto(
        play_rock_paper_scissors,
        ROCK_PAPER_SCISSORS,
        zero_sum=True,
        multiprocess=True,
    )
    parallel_frontier = analysis.analytic_pareto(
        play_rock_paper_scissors,
        ROCK_PAPER_SCISSORS,
        multiprocess=True,
    )
    sequential_frontier = analysis.analytic_pareto(
        play_rock_paper_scissors,
        ROCK_PAPER_SCISSORS,
    )
    assert parallel_frontier == sequential_frontier
    assert parallel_frontier_zero_sum == sequential_frontier
