# Chapter 6 practice answers

**1.** Fraud gets through only if both checks miss it: 0.2 × 0.2 = 0.04, so 4 per cent (assuming the checks are independent, which similar checks often aren't).

**2.** We need 1 − 0.98ⁿ ≥ 0.95, so n ≥ log(0.05) / log(0.98).

```python
import numpy as np
print(np.ceil(np.log(0.05) / np.log(0.98)))
```

```output
149.0
```

**3.** Simulate 1,000 promotions of 5,000 spins each.

```python
rng = np.random.default_rng(3)
prizes = np.array([0, 5, 9.95, 25])
probs = np.array([0.50, 0.30, 0.15, 0.05])
totals = rng.choice(prizes, size=(1000, 5000),
                    p=probs).sum(axis=1)
print(f"mean ${totals.mean():,.0f}, sd ${totals.std():,.0f}")
print(f"5th to 95th percentile: "
      f"${np.percentile(totals, 5):,.0f} to "
      f"${np.percentile(totals, 95):,.0f}")
```

```output
mean $21,221, sd $408
5th to 95th percentile: $20,564 to $21,892
```

The total varies by only about ±3 per cent around $21,200, because it's a sum of many independent spins.
