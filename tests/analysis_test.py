from analysis.simulated_annealing import optimize
from analysis.metrics import average_payoff_metric

def test_simulated_annealing():
    results = optimize(average_payoff_metric, 1, 1)
    assert results.success
