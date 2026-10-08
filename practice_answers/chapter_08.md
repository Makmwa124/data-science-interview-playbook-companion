# Chapter 8 practice answers

```python
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

con = sqlite3.connect("data/corella.db")
test = pd.read_sql("SELECT * FROM checkout_test", con)
```

**1. Sample size for the observed lift.**

```python
rates = test.groupby("variant")["converted"].mean()
es = proportion_effectsize(rates["treatment"], rates["control"])
n = NormalIndPower().solve_power(es, alpha=0.05, power=0.8)
print(f"visitors per group: {np.ceil(n):,.0f}")
```

```output
visitors per group: 32,838
```

About 33,000 per group, roughly four times the test's actual size.

**2. Device balance.**

```python
t = pd.crosstab(test["device"], test["variant"])
chi2, p, dof, _ = stats.chi2_contingency(t)
print(t)
print(f"p = {p:.2f}")
```

```output
variant  control  treatment
device                     
android     2857       2715
ios         3637       3548
web         1583       1660
p = 0.08
```

With p = 0.08 there is no strong evidence of imbalance, and the differences between arms are small. I would still note it in the write-up.

**3. Weekly looks.**

```python
rng = np.random.default_rng(11)
def fpr(look_days, days=21, per_day=400, p=0.11, sims=2000):
    hits = 0
    looks = np.array(look_days) - 1
    for _ in range(sims):
        a = rng.random((days, per_day)) < p
        b = rng.random((days, per_day)) < p
        ca, cb = a.sum(1).cumsum(), b.sum(1).cumsum()
        n = per_day * np.arange(1, days + 1)
        pool = (ca + cb) / (2 * n)
        z = (cb - ca) / n / np.sqrt(pool * (1 - pool) * 2 / n)
        hits += (np.abs(z[looks]) > 1.96).any()
    return hits / sims

print(f"weekly looks: {fpr([7, 14, 21]):.3f}")
print(f"daily looks:  {fpr(range(1, 22)):.3f}")
```

```output
weekly looks: 0.105
daily looks:  0.265
```

Three looks inflate the false positive rate to roughly 10 per cent; daily looks far more.
