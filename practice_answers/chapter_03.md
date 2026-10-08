# Chapter 3 practice answers

**1. Running count of each customer's orders** (first few rows shown).

```sql
SELECT customer_id, order_id, ordered_at,
       COUNT(*) OVER (PARTITION BY customer_id
                      ORDER BY ordered_at, order_id
                      ROWS BETWEEN UNBOUNDED PRECEDING
                               AND CURRENT ROW) AS order_n
FROM orders
ORDER BY customer_id, ordered_at
LIMIT 6;
```

```output
customer_id  order_id  ordered_at           order_n
-----------  --------  -------------------  -------
      10001    500001  2024-01-13 13:57:00        1
      10001    500002  2024-01-16 13:12:00        2
      10001    500003  2024-01-18 13:46:00        3
      10001    500004  2024-03-29 21:54:00        4
      10001    500005  2024-04-13 12:54:00        5
      10001    500006  2024-04-18 20:57:00        6
```

**2. Each driver's fastest delivery, keeping ties** (count of tied rows per driver shown).

```sql
WITH r AS (
  SELECT driver_id, order_id, delivery_minutes,
         RANK() OVER (PARTITION BY driver_id
                      ORDER BY delivery_minutes) AS rnk
  FROM deliveries
)
SELECT driver_id,
       MIN(delivery_minutes) AS fastest,
       COUNT(*) AS deliveries_at_fastest
FROM r
WHERE rnk = 1
GROUP BY driver_id
ORDER BY driver_id
LIMIT 8;
```

```output
driver_id  fastest  deliveries_at_fastest
---------  -------  ---------------------
        2       17                      2
        3       15                      1
        4       17                      1
        5       13                      1
        6       17                      1
        7       17                      3
        9       23                      1
       10       20                      1
```

**3. New customers per month in 2025, with a cumulative total.**

```sql
WITH m AS (
  SELECT strftime('%Y-%m', signup_date) AS month,
         COUNT(*) AS new_customers
  FROM customers
  WHERE signup_date >= '2025-01-01'
    AND signup_date <  '2026-01-01'
  GROUP BY month
)
SELECT month, new_customers,
       SUM(new_customers) OVER (ORDER BY month) AS cumulative
FROM m
ORDER BY month;
```

```output
month    new_customers  cumulative
-------  -------------  ----------
2025-01            144         144
2025-02            133         277
2025-03            143         420
2025-04            144         564
2025-05            157         721
2025-06            170         891
2025-07            164        1055
2025-08            162        1217
2025-09            161        1378
2025-10            143        1521
2025-11            175        1696
2025-12            168        1864
```

**4. Each product's best month by units in 2025** (first eight products).

```sql
WITH monthly AS (
  SELECT i.product_id,
         strftime('%Y-%m', o.ordered_at) AS month,
         SUM(i.quantity) AS units
  FROM order_items AS i
  JOIN orders AS o ON o.order_id = i.order_id
  WHERE o.status = 'delivered'
    AND o.ordered_at >= '2025-01-01'
    AND o.ordered_at <  '2026-01-01'
  GROUP BY i.product_id, month
),
ranked AS (
  SELECT *, RANK() OVER (PARTITION BY product_id
                         ORDER BY units DESC) AS rnk
  FROM monthly
)
SELECT product_id, month, units
FROM ranked
WHERE rnk = 1
ORDER BY product_id
LIMIT 8;
```

```output
product_id  month    units
----------  -------  -----
       101  2025-12    622
       102  2025-12    652
       103  2025-12    660
       104  2025-12    619
       105  2025-12    650
       106  2025-12    605
       107  2025-12    629
       108  2025-12    677
```

Most products peak in December, matching the seasonal pattern in revenue.
