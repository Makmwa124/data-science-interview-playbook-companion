# Chapter 7 practice answers

```python
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

con = sqlite3.connect("data/corella.db")
o = pd.read_sql("""SELECT o.*, c.plan, c.city FROM orders o
    JOIN customers c USING (customer_id)
    WHERE o.status = 'delivered'""", con)
rng = np.random.default_rng(5)
```

**1. Plus vs Standard average basket.**

```python
p = o.loc[o["plan"] == "plus", "basket_aud"]
s = o.loc[o["plan"] == "standard", "basket_aud"]
diff = p.mean() - s.mean()
se = np.sqrt(p.var() / len(p) + s.var() / len(s))
print(f"difference ${diff:.2f}, "
      f"95% CI ${diff - 1.96*se:.2f} to ${diff + 1.96*se:.2f}")
```

```output
difference $15.06, 95% CI $14.39 to $15.73
```

Plus baskets are about $15 larger, nearly 30 per cent more than Standard: precise and commercially meaningful.

**2. Bootstrap the 90th percentile of Sydney's delivery times.**

```python
syd = pd.read_sql("""SELECT delivery_minutes FROM deliveries
    JOIN drivers USING (driver_id)
    WHERE depot = 'Sydney'""", con)["delivery_minutes"]
boot = [np.percentile(rng.choice(syd.to_numpy(), syd.size), 90)
        for _ in range(2000)]
print(f"p90 {np.percentile(syd, 90):.1f}, 95% CI "
      f"{np.percentile(boot, 2.5):.1f} to "
      f"{np.percentile(boot, 97.5):.1f}")
```

```output
p90 53.0, 95% CI 52.0 to 53.0
```

Delivery minutes are whole numbers, so the bootstrap distribution of the percentile is lumpy and the interval is very narrow.

**3. Plan in a basket regression.**

```python
m = smf.ols("basket_aud ~ C(plan) + C(city)", data=o).fit()
print(m.params.round(2))
```

```output
Intercept               66.22
C(plan)[T.standard]    -15.02
C(city)[T.Brisbane]     -0.17
C(city)[T.Melbourne]     0.40
C(city)[T.Perth]        -0.14
C(city)[T.Sydney]       -0.11
dtype: float64
```

`C(plan)[T.standard]` is the average difference in basket between Standard and Plus orders in the same city: about $15 lower. It's an association, not the effect of the plan itself.
