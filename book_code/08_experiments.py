# Code from The Data Science Interview Playbook, file 08_experiments
# Run from the repository root.

import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import (
    proportion_effectsize, proportions_ztest)

con = sqlite3.connect("data/corella.db")
test = pd.read_sql("SELECT * FROM checkout_test", con)
rng = np.random.default_rng(11)

effect = proportion_effectsize(0.12, 0.11)
n = NormalIndPower().solve_power(effect_size=effect,
                                 alpha=0.05, power=0.80)
print(f"visitors per group: {np.ceil(n):,.0f}")

summary = test.groupby("variant").agg(
    visitors=("visitor_id", "count"),
    conversions=("converted", "sum"),
    rate=("converted", "mean"))
print(summary.round(4))

conv = summary["conversions"].to_numpy()
nobs = summary["visitors"].to_numpy()
z, p = proportions_ztest(conv[::-1], nobs[::-1])

p_c, p_t = conv / nobs
diff = p_t - p_c
se = np.sqrt(p_c * (1 - p_c) / nobs[0]
             + p_t * (1 - p_t) / nobs[1])
lo, hi = diff - 1.96 * se, diff + 1.96 * se
print(f"lift {100*diff:.2f} pts, z={z:.2f}, p={p:.3f}")
print(f"95% CI {100*lo:.2f} to {100*hi:.2f} pts")
print(f"relative lift {100*diff/p_c:.1f}%")

counts = test["variant"].value_counts().sort_index()
chi2, p = stats.chisquare(counts)
print(counts.to_dict())
print(f"chi2={chi2:.2f}, p={p:.3f}")

c = test.loc[test["variant"] == "control", "order_value"]
t = test.loc[test["variant"] == "treatment", "order_value"]
res = stats.ttest_ind(t, c, equal_var=False)
print(f"control ${c.mean():.2f}, treatment ${t.mean():.2f}, "
      f"p={res.pvalue:.3f}")

boot = [rng.choice(t.to_numpy(), t.size).mean()
        - rng.choice(c.to_numpy(), c.size).mean()
        for _ in range(2000)]
print("bootstrap 95% CI for the difference: "
      f"{np.percentile(boot, 2.5):.2f} to "
      f"{np.percentile(boot, 97.5):.2f}")

seg = (test.groupby(["device", "variant"])["converted"]
           .agg(["mean", "count"]).unstack())
rows = []
for dev in ["android", "ios", "web"]:
    d = test[test["device"] == dev]
    g = d.groupby("variant")["converted"]
    z, p = proportions_ztest(g.sum()[::-1], g.count()[::-1])
    lift = g.mean()["treatment"] - g.mean()["control"]
    rows.append((dev, round(100 * lift, 2), round(p, 4)))
print(pd.DataFrame(rows, columns=["device", "lift_pts", "p"]))

def peeking_false_positive(days=21, per_day=400, p=0.11,
                           sims=2000):
    hits_peek = hits_end = 0
    for _ in range(sims):
        a = rng.random((days, per_day)) < p
        b = rng.random((days, per_day)) < p
        ca, cb = a.sum(1).cumsum(), b.sum(1).cumsum()
        n = per_day * np.arange(1, days + 1)
        pool = (ca + cb) / (2 * n)
        se = np.sqrt(pool * (1 - pool) * 2 / n)
        zs = (cb / n - ca / n) / se
        sig = np.abs(zs) > 1.96
        hits_peek += sig.any()
        hits_end += sig[-1]
    return hits_end / sims, hits_peek / sims

end, peek = peeking_false_positive()
print(f"false positives, one look at the end: {end:.3f}")
print(f"false positives, stop at first p<0.05: {peek:.3f}")
