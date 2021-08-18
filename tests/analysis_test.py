from analysis.simulated_annealing import optimize


def test_simulated_annealing():
    results = optimize()
    assert results.success
