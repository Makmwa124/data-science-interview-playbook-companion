-- Code from The Data Science Interview Playbook, file 04_sql_patterns
-- Run against data/corella.db (SQLite)

WITH firsts AS (
  SELECT customer_id,
         MIN(ordered_at) AS first_at
  FROM orders
  WHERE status = 'delivered'
  GROUP BY customer_id
),
activity AS (
  SELECT DISTINCT
         o.customer_id,
         strftime('%Y-%m', f.first_at) AS cohort,
         (CAST(strftime('%Y', o.ordered_at) AS INTEGER)
          - CAST(strftime('%Y', f.first_at) AS INTEGER)) * 12
         + CAST(strftime('%m', o.ordered_at) AS INTEGER)
         - CAST(strftime('%m', f.first_at) AS INTEGER)
           AS month_n
  FROM orders AS o
  JOIN firsts AS f ON f.customer_id = o.customer_id
  WHERE o.status = 'delivered'
)
SELECT cohort,
       COUNT(DISTINCT CASE WHEN month_n = 0
                           THEN customer_id END) AS size,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 1
                           THEN customer_id END)
             / COUNT(DISTINCT CASE WHEN month_n = 0
                           THEN customer_id END), 1) AS m1,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 3
                           THEN customer_id END)
             / COUNT(DISTINCT CASE WHEN month_n = 0
                           THEN customer_id END), 1) AS m3,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 6
                           THEN customer_id END)
             / COUNT(DISTINCT CASE WHEN month_n = 0
                           THEN customer_id END), 1) AS m6,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_n = 12
                           THEN customer_id END)
             / COUNT(DISTINCT CASE WHEN month_n = 0
                           THEN customer_id END), 1) AS m12
FROM activity
WHERE cohort BETWEEN '2025-01' AND '2025-06'
GROUP BY cohort
ORDER BY cohort;

WITH sessions AS (
  SELECT customer_id,
         date(event_time) AS day,
         MAX(event_type = 'view_product')   AS viewed,
         MAX(event_type = 'add_to_cart')    AS carted,
         MAX(event_type = 'begin_checkout') AS checkout,
         MAX(event_type = 'purchase')       AS purchased
  FROM app_events
  GROUP BY customer_id, date(event_time)
),
steps AS (
  SELECT 1 AS step, 'view_product' AS event,
         SUM(viewed) AS sessions FROM sessions
  UNION ALL
  SELECT 2, 'add_to_cart', SUM(carted) FROM sessions
  UNION ALL
  SELECT 3, 'begin_checkout', SUM(checkout) FROM sessions
  UNION ALL
  SELECT 4, 'purchase', SUM(purchased) FROM sessions
)
SELECT step, event, sessions,
       ROUND(100.0 * sessions
             / LAG(sessions) OVER (ORDER BY step), 1)
         AS pct_of_prev,
       ROUND(100.0 * sessions
             / FIRST_VALUE(sessions) OVER (ORDER BY step), 1)
         AS pct_of_first
FROM steps
ORDER BY step;

SELECT COUNT(*) AS duplicated_groups,
       SUM(n - 1) AS extra_rows
FROM (
  SELECT customer_id, event_time, event_type,
         COUNT(*) AS n
  FROM app_events
  GROUP BY customer_id, event_time, event_type
  HAVING COUNT(*) > 1
);

WITH ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id, event_time, event_type
           ORDER BY event_id) AS rn
  FROM app_events
)
SELECT COUNT(*) AS rows_after_dedup
FROM ranked
WHERE rn = 1;

WITH days AS (
  SELECT DISTINCT customer_id,
         date(event_time) AS day
  FROM app_events
  WHERE event_type = 'app_open'
),
grouped AS (
  SELECT customer_id,
         day,
         julianday(day) - ROW_NUMBER() OVER (
           PARTITION BY customer_id ORDER BY day) AS grp
  FROM days
),
streaks AS (
  SELECT customer_id,
         MIN(day) AS start_day,
         COUNT(*) AS streak_days
  FROM grouped
  GROUP BY customer_id, grp
)
SELECT customer_id, start_day, streak_days
FROM streaks
ORDER BY streak_days DESC, customer_id
LIMIT 5;

SELECT d.driver_name,
       d.hired_on,
       m.driver_name AS manager,
       m.hired_on    AS manager_hired
FROM drivers AS d
JOIN drivers AS m
  ON m.driver_id = d.manager_id
WHERE d.hired_on < m.hired_on
ORDER BY d.depot, d.hired_on;

WITH monthly AS (
  SELECT DISTINCT customer_id,
         strftime('%Y-%m', ordered_at) AS month
  FROM orders
  WHERE status = 'delivered'
),
firsts AS (
  SELECT customer_id, MIN(month) AS first_month
  FROM monthly
  GROUP BY customer_id
),
june AS (
  SELECT customer_id FROM monthly WHERE month = '2026-06'
),
may AS (
  SELECT customer_id FROM monthly WHERE month = '2026-05'
)
SELECT 'new' AS segment, COUNT(*) AS customers
FROM june JOIN firsts USING (customer_id)
WHERE first_month = '2026-06'
UNION ALL
SELECT 'retained', COUNT(*)
FROM june JOIN may USING (customer_id)
UNION ALL
SELECT 'returning', COUNT(*)
FROM june JOIN firsts USING (customer_id)
WHERE first_month < '2026-06'
  AND customer_id NOT IN (SELECT customer_id FROM may)
UNION ALL
SELECT 'churned', COUNT(*)
FROM may
WHERE customer_id NOT IN (SELECT customer_id FROM june);

WITH d AS (
  SELECT dr.depot,
         de.delivery_minutes AS mins,
         ROW_NUMBER() OVER (PARTITION BY dr.depot
                            ORDER BY de.delivery_minutes) AS rn,
         COUNT(*) OVER (PARTITION BY dr.depot) AS n
  FROM deliveries AS de
  JOIN drivers AS dr ON dr.driver_id = de.driver_id
)
SELECT depot,
       AVG(mins) AS median_minutes,
       MAX(n) AS deliveries
FROM d
WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
GROUP BY depot
ORDER BY median_minutes;

SELECT a.product_id AS product_a,
       b.product_id AS product_b,
       COUNT(*)     AS orders_together
FROM order_items AS a
JOIN order_items AS b
  ON  b.order_id   = a.order_id
  AND b.product_id > a.product_id
GROUP BY a.product_id, b.product_id
ORDER BY orders_together DESC
LIMIT 5;

WITH n AS (SELECT COUNT(DISTINCT order_id) AS total
           FROM order_items),
p AS (SELECT product_id,
             COUNT(*) * 1.0 / (SELECT total FROM n) AS share
      FROM order_items GROUP BY product_id),
pairs AS (
  SELECT a.product_id AS pa, b.product_id AS pb,
         COUNT(*) * 1.0 / (SELECT total FROM n) AS share
  FROM order_items AS a
  JOIN order_items AS b
    ON b.order_id = a.order_id
   AND b.product_id > a.product_id
  GROUP BY pa, pb
)
SELECT pa, pb,
       ROUND(pairs.share / (p1.share * p2.share), 2) AS lift
FROM pairs
JOIN p AS p1 ON p1.product_id = pa
JOIN p AS p2 ON p2.product_id = pb
ORDER BY lift DESC
LIMIT 5;
