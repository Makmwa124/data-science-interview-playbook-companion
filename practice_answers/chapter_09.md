# Chapter 9 practice answers

The chapter's code is in `book_code/09_machine_learning.py`. Wrap it in a function of the cut-off date to answer these quickly.

```python
import sqlite3
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

con = sqlite3.connect("data/corella.db")
orders = pd.read_sql(
    "SELECT * FROM orders WHERE status = 'delivered'", con,
    parse_dates=["ordered_at"])
cust = pd.read_sql("SELECT * FROM customers", con)
D = pd.Timedelta

def build(cutoff):
    cutoff = pd.Timestamp(cutoff)
    b = orders[orders["ordered_at"] < cutoff]
    a = orders[(orders["ordered_at"] >= cutoff)
               & (orders["ordered_at"] < cutoff + D(days=90))]
    pop = b.loc[b["ordered_at"] >= cutoff - D(days=90),
                "customer_id"].unique()
    f = b.groupby("customer_id").agg(
        last=("ordered_at", "max"), first=("ordered_at", "min"),
        orders_total=("order_id", "count"),
        avg_basket=("basket_aud", "mean"))
    f["recency_days"] = (cutoff - f["last"]).dt.days
    f["tenure_days"] = (cutoff - f["first"]).dt.days
    for name, lo, hi in [("orders_90d", 90, 0),
                         ("orders_prev90", 180, 90)]:
        w = b[(b["ordered_at"] >= cutoff - D(days=lo))
              & (b["ordered_at"] < cutoff - D(days=hi))]
        f[name] = w.groupby("customer_id").size()
    f = f.fillna({"orders_90d": 0, "orders_prev90": 0})
    f["trend"] = f["orders_90d"] - f["orders_prev90"]
    f = f.loc[pop].join(cust.set_index("customer_id")["plan"])
    f["is_plus"] = (f["plan"] == "plus").astype(int)
    f["churned"] = (~f.index.isin(a["customer_id"])).astype(int)
    return f

def auc(f, cols):
    Xtr, Xte, ytr, yte = train_test_split(
        f[cols], f["churned"], test_size=0.3,
        stratify=f["churned"], random_state=1)
    m = make_pipeline(StandardScaler(),
                      LogisticRegression(max_iter=1000))
    m.fit(Xtr, ytr)
    return roc_auc_score(yte, m.predict_proba(Xte)[:, 1]), m, Xte, yte

base = ["recency_days", "tenure_days", "orders_total",
        "orders_90d", "avg_basket", "is_plus"]
```

**1. A different cut-off.**

```python
for c in ["2026-01-01", "2026-04-01"]:
    f = build(c)
    print(c, f"n={len(f)}, churn={f['churned'].mean():.2f}, "
          f"AUC={auc(f, base)[0]:.3f}")
```

```output
2026-01-01 n=1256, churn=0.29, AUC=0.808
2026-04-01 n=932, churn=0.30, AUC=0.831
```

**2. Adding the trend feature.**

```python
f = build("2026-04-01")
print(f"without trend {auc(f, base)[0]:.3f}, "
      f"with trend {auc(f, base + ['trend'])[0]:.3f}")
```

```output
without trend 0.831, with trend 0.831
```

The trend adds little: recency already captures most of what it measures.

**3. Precision and recall by number contacted.**

```python
_, m, Xte, yte = auc(f, base)
score = m.predict_proba(Xte)[:, 1]
order = np.argsort(-score)
y = yte.to_numpy()[order]
for k in [25, 50, 100, 150, 200]:
    k = min(k, len(y))
    print(f"top {k:>3}: precision {y[:k].mean():.2f}, "
          f"recall {y[:k].sum() / y.sum():.2f}")
```

```output
top  25: precision 0.80, recall 0.24
top  50: precision 0.72, recall 0.43
top 100: precision 0.62, recall 0.75
top 150: precision 0.47, recall 0.86
top 200: precision 0.40, recall 0.95
```

The test set has 280 customers. Plot `precision` and `recall` against `k` with matplotlib to see the trade-off.
