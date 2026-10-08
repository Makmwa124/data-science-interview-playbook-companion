# Code from The Data Science Interview Playbook, file 07_statistics
# Run from the repository root.

import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

con = sqlite3.connect("data/corella.db")
orders = pd.read_sql(
    "SELECT * FROM orders WHERE status = 'delivered'", con)
deliv = pd.read_sql("""
    SELECT de.*, dr.depot
    FROM deliveries AS de
    JOIN drivers AS dr ON dr.driver_id = de.driver_id""", con)
rng = np.random.default_rng(42)

b = orders["basket_aud"]
print(b.describe(percentiles=[.1, .5, .9]).round(2))
print(f"skewness {b.skew():.2f}")

syd = deliv.loc[deliv["depot"] == "Sydney", "delivery_minutes"]
n, mean, sd = len(syd), syd.mean(), syd.std()
se = sd / np.sqrt(n)
t = stats.t.ppf(0.975, df=n - 1)
print(f"n={n}, mean={mean:.2f}, sd={sd:.2f}, se={se:.3f}")
print(f"95% CI: {mean - t*se:.2f} to {mean + t*se:.2f}")

mel = deliv.loc[deliv["depot"] == "Melbourne",
                "delivery_minutes"]
res = stats.ttest_ind(syd, mel, equal_var=False)
diff = syd.mean() - mel.mean()
pooled_sd = np.sqrt((syd.var() + mel.var()) / 2)
print(f"difference {diff:.2f} min, t={res.statistic:.1f}, "
      f"p={res.pvalue:.2g}")
print(f"Cohen's d {diff / pooled_sd:.2f}")

deliv["slow"] = deliv["delivery_minutes"] > 45
table = pd.crosstab(deliv["depot"], deliv["slow"])
chi2, p, dof, expected = stats.chi2_contingency(table)
print(table)
print((100 * deliv.groupby("depot")["slow"].mean()).round(1))
print(f"chi2={chi2:.0f}, dof={dof}, p={p}")

basket = orders["basket_aud"].to_numpy()
boot = np.array([
    np.median(rng.choice(basket, size=basket.size))
    for _ in range(2000)
])
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"median {np.median(basket):.2f}, "
      f"95% CI {lo:.2f} to {hi:.2f}")

rated = deliv.dropna(subset=["rating"])
r, p = stats.pearsonr(rated["delivery_minutes"],
                      rated["rating"])
print(f"Pearson r = {r:.2f}, n = {len(rated)}")
print(rated.groupby(pd.cut(rated["delivery_minutes"],
                           [0, 30, 40, 50, 120]),
                    observed=True)["rating"]
           .agg(["mean", "count"]).round(2))

model = smf.ols("rating ~ delivery_minutes + C(depot)",
                data=rated).fit()
ci = model.conf_int()
out = pd.DataFrame({"coef": model.params,
                    "low": ci[0], "high": ci[1],
                    "p": model.pvalues})
out.index = out.index.str.replace(r"C\(depot\)\[T\.(.*)\]",
                                  r"depot: \1", regex=True)
print(out.round(4))
print(f"R-squared {model.rsquared:.3f}")

means = np.array([rng.choice(basket, size=50).mean()
                  for _ in range(5000)])
print(f"skew of baskets       {stats.skew(basket):.2f}")
print(f"skew of 50-order mean {stats.skew(means):.2f}")
print(f"sd of means {means.std():.2f} vs "
      f"sd/sqrt(50) {basket.std() / np.sqrt(50):.2f}")
