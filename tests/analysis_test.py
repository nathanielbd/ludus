# from analysis.simulated_annealing import optimize
from analysis.simulated_annealing import genetic_optimize
from analysis.simulated_annealing import build_cards
# from analysis.metrics import average_payoff_metric
from analysis.metrics import std_dev_metric


# def test_simulated_annealing():
#     results = optimize(average_payoff_metric, 10, 4, 4)
#     print(results.lowest_optimization_result)
#     assert results.lowest_optimization_result.success

def test_genetic_alg():
    sol = genetic_optimize(std_dev_metric, 4, 10, build_cards)
    assert sol.all()