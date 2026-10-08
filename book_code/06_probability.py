# Code from The Data Science Interview Playbook, file 06_probability
# Run from the repository root.

import numpy as np
rng = np.random.default_rng(7)

exact = 1 - 0.9**4
late = rng.random((1_000_000, 4)) < 0.10
simulated = late.any(axis=1).mean()
print(f"exact {exact:.4f}, simulated {simulated:.4f}")

p_fraud, sens, fpr = 0.005, 0.90, 0.02
exact = sens * p_fraud / (sens * p_fraud + fpr * (1 - p_fraud))

n = 2_000_000
fraud = rng.random(n) < p_fraud
flag = np.where(fraud, rng.random(n) < sens,
                rng.random(n) < fpr)
print(f"exact {exact:.4f}, simulated {fraud[flag].mean():.4f}")

prizes = np.array([0, 5, 9.95, 25])
probs = np.array([0.50, 0.30, 0.15, 0.05])
exact = (prizes * probs).sum()
spins = rng.choice(prizes, size=1_000_000, p=probs)
print(f"exact {exact:.4f}, simulated {spins.mean():.4f}")

d, k = 10_000, 120
exact = 1 - np.prod((d - np.arange(k)) / d)
codes = rng.integers(0, d, size=(100_000, k))
codes.sort(axis=1)
dup = (np.diff(codes, axis=1) == 0).any(axis=1)
print(f"exact {exact:.4f}, simulated {dup.mean():.4f}")

from scipy import stats

p = 0.06
print(f"mean {stats.geom.mean(p):.2f}")
print(f"P(more than 20) exact {0.94**20:.4f}, "
      f"scipy {stats.geom.sf(20, p):.4f}")
draws = rng.geometric(p, size=1_000_000)
print(f"simulated mean {draws.mean():.2f}, "
      f"P(>20) {(draws > 20).mean():.4f}")

exact = 1 - stats.binom.cdf(1, n=10, p=0.1)
sims = rng.binomial(10, 0.1, size=1_000_000)
print(f"exact {exact:.4f}, simulated {(sims >= 2).mean():.4f}")

lam = 3
print(f"P(0 in an hour) {stats.poisson.pmf(0, lam):.4f}")
gaps = rng.exponential(1 / lam, size=1_000_000) * 60
print(f"mean gap {gaps.mean():.1f} minutes")
print(f"P(gap > 60 min) {(gaps > 60).mean():.4f}")

def rolls_until_double_six(rng):
    n, prev_six = 0, False
    while True:
        n += 1
        six = rng.integers(1, 7) == 6
        if six and prev_six:
            return n
        prev_six = six

trials = [rolls_until_double_six(rng) for _ in range(100_000)]
print(f"simulated mean {np.mean(trials):.1f}")
