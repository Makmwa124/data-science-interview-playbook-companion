# Chapter 4 practice answers

**1. Cohorts by signup month.** Only the cohort definition changes: use `signup_date`, and every customer (including those who never ordered) belongs to a cohort.

```sql
WITH activity AS (
  SELECT DISTINCT c.customer_id,
         strftime('%Y-%m', c.signup_date) AS cohort,
         (CAST(strftime('%Y', o.ordered_at) AS INTEGER)
          - CAST(strftime('%Y', c.signup_date) AS INTEGER)) * 12
         + CAST(strftime('%m', o.ordered_at) AS INTEGER)
         - CAST(strftime('%m', c.signup_date) AS INTEGER)
           AS month_n
  FROM customers AS c
  LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
   AND o.status = 'delivered'
),
sizes AS (
  SELECT strftime('%Y-%m', signup_date) AS cohort,
         COUNT(*) AS size
  FROM customers GROUP BY cohort
)
SELECT a.cohort, s.size,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 1
             THEN customer_id END) / s.size, 1) AS m1,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 3
             THEN customer_id END) / s.size, 1) AS m3
FROM activity AS a
JOIN sizes AS s ON s.cohort = a.cohort
WHERE a.cohort BETWEEN '2025-01' AND '2025-06'
GROUP BY a.cohort, s.size
ORDER BY a.cohort;
```

```output
cohort   size    m1    m3
-------  ----  ----  ----
2025-01   144  54.2  43.8
2025-02   133  59.4  42.1
2025-03   143  53.1  46.2
2025-04   144  56.3  48.6
2025-05   157  62.4  47.1
2025-06   170  60.0  40.6
```

Rates are lower than in Question 4.1 because the denominator now includes customers who never ordered.

**2. Added to cart but never purchased in June.**

```sql
SELECT COUNT(*) AS customers
FROM (
  SELECT customer_id
  FROM app_events
  GROUP BY customer_id
  HAVING SUM(event_type = 'add_to_cart') > 0
     AND SUM(event_type = 'purchase') = 0
);
```

```output
customers
---------
       57
```

**3. Longest gap between consecutive delivered orders** (top five customers).

```sql
WITH g AS (
  SELECT customer_id,
         julianday(ordered_at) - julianday(LAG(ordered_at)
           OVER (PARTITION BY customer_id
                 ORDER BY ordered_at)) AS gap
  FROM orders
  WHERE status = 'delivered'
)
SELECT customer_id,
       CAST(MAX(gap) AS INTEGER) AS longest_gap_days
FROM g
GROUP BY customer_id
ORDER BY longest_gap_days DESC
LIMIT 5;
```

```output
customer_id  longest_gap_days
-----------  ----------------
      10362               309
      10642               250
      10152               249
      10975               235
      10701               213
```

**4. 90th percentile delivery time by depot** (nearest-rank method).

```sql
WITH d AS (
  SELECT dr.depot, de.delivery_minutes AS mins,
         ROW_NUMBER() OVER (PARTITION BY dr.depot
                            ORDER BY de.delivery_minutes) AS rn,
         COUNT(*) OVER (PARTITION BY dr.depot) AS n
  FROM deliveries AS de
  JOIN drivers AS dr ON dr.driver_id = de.driver_id
)
SELECT depot, mins AS p90_minutes
FROM d
WHERE rn = CAST(0.9 * n + 0.9999 AS INTEGER)
ORDER BY p90_minutes;
```

```output
depot      p90_minutes
---------  -----------
Adelaide            43
Perth               45
Brisbane            47
Melbourne           50
Sydney              53
```
