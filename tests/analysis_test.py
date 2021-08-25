from analysis.simulated_annealing import optimize
from analysis.metrics import average_payoff_metric


def test_simulated_annealing():
    results = optimize(average_payoff_metric, 5, 2, 2)
    print(results.lowest_optimization_result)
    assert results.lowest_optimization_result.success
