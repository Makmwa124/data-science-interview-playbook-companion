# Chapter 5 practice answers

```python
import sqlite3
import numpy as np
import pandas as pd

con = sqlite3.connect("data/corella.db")
orders = pd.read_sql("SELECT * FROM orders", con,
                     parse_dates=["ordered_at"])
customers = pd.read_sql("SELECT * FROM customers", con)
```

**1. Promo share per customer, averaged by channel.**

```python
d = orders[orders["status"] == "delivered"]
share = (d.assign(promo=d["promo_code"].notna())
          .groupby("customer_id")["promo"].mean()
          .rename("promo_share").reset_index()
          .merge(customers, on="customer_id"))
print(share.groupby("channel")["promo_share"].mean().round(3))
```

```output
channel
organic        0.164
paid_search    0.188
referral       0.169
social         0.184
Name: promo_share, dtype: float64
```

**2. Driver median delivery time and rank within depot.**

```python
deliv = pd.read_sql("""SELECT de.*, dr.depot, dr.driver_name
    FROM deliveries de JOIN drivers dr USING (driver_id)""", con)
med = (deliv.groupby(["depot", "driver_name"])
            ["delivery_minutes"].median().reset_index())
med["rank"] = (med.groupby("depot")["delivery_minutes"]
                  .rank(method="dense").astype(int))
print(med.sort_values(["depot", "rank"]).head(6)
         .to_string(index=False))
```

```output
   depot   driver_name  delivery_minutes  rank
Adelaide Caitlin Smith              33.0     1
Adelaide   Farid Brown              33.0     1
Adelaide     Mei Kelly              33.0     1
Adelaide Olivia Murphy              33.0     1
Adelaide     Tom Young              33.0     1
Adelaide Vikram Walker              34.0     2
```

**3. Distinct days from a list of timestamps.**

```python
from datetime import datetime

def distinct_days(stamps):
    return len({s.date() for s in stamps})

print(distinct_days([datetime(2026, 6, 1, 9),
                     datetime(2026, 6, 1, 18),
                     datetime(2026, 6, 2, 7)]))
```

```output
2
```

**4. The Question 4.1 cohort table in pandas.**

```python
first = d.groupby("customer_id")["ordered_at"].min()
x = d[["customer_id", "ordered_at"]].copy()
x["cohort"] = x["customer_id"].map(first).dt.to_period("M")
x["month_n"] = (x["ordered_at"].dt.to_period("M")
                - x["cohort"]).apply(lambda p: p.n)
active = (x.drop_duplicates(["customer_id", "month_n"])
           .groupby(["cohort", "month_n"]).size()
           .unstack())
ret = active[[1, 3, 6, 12]].div(active[0], axis=0) * 100
print(ret.loc["2025-01":"2025-06"].round(1))
```

```output
month_n    1     3     6     12
cohort                         
2025-01  61.7  51.3  35.7  22.6
2025-02  64.0  47.4  31.6  19.3
2025-03  61.6  53.6  37.6  24.8
2025-04  65.0  55.3  39.8  20.3
2025-05  70.5  59.0  44.3  18.0
2025-06  68.6  50.0  39.3  25.7
```

The figures match the SQL version in Question 4.1.
