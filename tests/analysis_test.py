from analysis.simulated_annealing import optimize
from analysis.metrics import average_payoff_metric

def test_simulated_annealing():
    results = optimize(2)
    assert results.success
