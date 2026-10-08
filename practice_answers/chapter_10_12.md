# Chapters 10 to 12 practice answers

**Chapter 10, question 2. August 2025 in Adelaide: delivery times and cancellations.**

```sql
SELECT strftime('%Y-%m', o.ordered_at) AS month,
       COUNT(*) AS orders,
       SUM(o.status = 'cancelled') AS cancelled,
       ROUND(AVG(de.delivery_minutes), 1) AS avg_minutes
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
LEFT JOIN deliveries AS de ON de.order_id = o.order_id
WHERE c.city = 'Adelaide'
  AND o.ordered_at >= '2025-06-01'
  AND o.ordered_at <  '2025-10-01'
GROUP BY month
ORDER BY month;
```

```output
month    orders  cancelled  avg_minutes
-------  ------  ---------  -----------
2025-06     561         30         34.2
2025-07     665         35         33.9
2025-08     595         27         34.3
2025-09     623         23         33.9
```

Neither delivery time nor cancellations moved in August, so a depot capacity problem looks unlikely.

**Chapter 10, question 3. Difference-in-differences set-up.**

```sql
SELECT c.plan,
       CASE WHEN o.ordered_at < '2026-01-01'
            THEN 'before' ELSE 'after' END AS period,
       ROUND(1.0 * COUNT(*) / 6, 1) AS orders_per_month
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
  AND o.ordered_at >= '2025-07-01'
  AND o.ordered_at <  '2026-07-01'
GROUP BY c.plan, period
ORDER BY c.plan, period DESC;
```

```output
plan      period  orders_per_month
--------  ------  ----------------
plus      before             834.2
plus      after              706.3
standard  before             927.2
standard  after              615.2
```

The difference-in-differences estimate is (Standard after − Standard before) − (Plus after − Plus before). In practice you'd model it monthly with a regression and check the pre-period trends are parallel.

**Chapter 11, question 2. Unit economics by city.**

```python
import sqlite3
import pandas as pd
con = sqlite3.connect("data/corella.db")
o = pd.read_sql("""SELECT o.*, c.city FROM orders o
    JOIN customers c USING (customer_id)
    WHERE o.status = 'delivered'
      AND o.ordered_at >= '2025-07-01'
      AND o.ordered_at <  '2026-07-01'""", con)
o["contribution"] = (o["basket_aud"] * 0.28 - o["discount_aud"]
                     + o["delivery_fee_aud"] - 6 - 11)
print(o.groupby("city")["contribution"].mean().round(2)
       .sort_values())
```

```output
city
Melbourne    2.91
Adelaide     3.11
Sydney       3.12
Perth        3.25
Brisbane     3.47
Name: contribution, dtype: float64
```

With the same cost assumptions everywhere, differences come from basket size and the mix of Plus and Standard customers. In reality, Sydney's longer delivery times would also mean a higher delivery cost per order.

**Chapter 11, question 3. Plus at $17.99.** Rerun the Question 11.3 query with `fees_saved > 17.99`. Before changing the price you'd want: how many members would cancel (price elasticity), how many order fewer times, and whether the change applies to existing members.

```sql
WITH monthly AS (
  SELECT o.customer_id, strftime('%Y-%m', o.ordered_at) AS month,
         SUM(CASE WHEN o.basket_aud < 80
                   AND COALESCE(o.promo_code, '') <> 'FREEDEL'
                  THEN 9.95 ELSE 0 END) AS fees_saved
  FROM orders AS o
  JOIN customers AS c ON c.customer_id = o.customer_id
  WHERE c.plan = 'plus' AND o.status = 'delivered'
    AND o.ordered_at >= '2026-01-01'
    AND o.ordered_at <  '2026-07-01'
  GROUP BY o.customer_id, month
)
SELECT ROUND(100.0 * AVG(fees_saved > 17.99), 1)
         AS pct_months_ahead
FROM monthly;
```

```output
pct_months_ahead
----------------
            56.3
```

**Chapter 12, question 1. A 60-day window.** Change `pd.Timedelta(days=30)` to `pd.Timedelta(days=60)` in the chapter's code (`book_code/12_take_home.py`). The return rate rises to about 85 per cent, and delivery time still shows no clear relationship once city and plan are controlled for.

**Chapters 10 and 11, open questions.** Questions 10.1 and 11.1 have no single right answer. Compare your answer with the structure in the matching chapter question: goal first, layered metrics with guardrails, stated assumptions, a sanity check and a recommendation.
