-- Code from The Data Science Interview Playbook, file 03_window_functions
-- Run against data/corella.db (SQLite)

WITH spend AS (
  SELECT c.city,
         o.customer_id,
         ROUND(SUM(o.basket_aud - o.discount_aud), 2) AS spend
  FROM orders AS o
  JOIN customers AS c ON c.customer_id = o.customer_id
  WHERE o.status = 'delivered'
  GROUP BY c.city, o.customer_id
),
ranked AS (
  SELECT *,
         DENSE_RANK() OVER (PARTITION BY city
                            ORDER BY spend DESC) AS rnk
  FROM spend
)
SELECT city, customer_id, spend, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY city, rnk;

WITH monthly AS (
  SELECT strftime('%Y-%m', ordered_at) AS month,
         SUM(basket_aud - discount_aud
             + delivery_fee_aud) AS revenue
  FROM orders
  WHERE status = 'delivered'
    AND ordered_at >= '2025-01-01'
    AND ordered_at <  '2026-01-01'
  GROUP BY month
)
SELECT month,
       CAST(ROUND(revenue) AS INTEGER) AS revenue,
       CAST(ROUND(SUM(revenue) OVER (ORDER BY month))
            AS INTEGER) AS cumulative
FROM monthly
ORDER BY month;

WITH monthly AS (
  SELECT strftime('%Y-%m', ordered_at) AS month,
         SUM(basket_aud - discount_aud
             + delivery_fee_aud) AS revenue
  FROM orders
  WHERE status = 'delivered'
    AND ordered_at >= '2025-01-01'
    AND ordered_at <  '2026-01-01'
  GROUP BY month
)
SELECT month,
       CAST(ROUND(revenue) AS INTEGER) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER w)
             / LAG(revenue) OVER w, 1) AS pct_change
FROM monthly
WINDOW w AS (ORDER BY month)
ORDER BY month;

WITH gaps AS (
  SELECT customer_id,
         julianday(ordered_at)
           - julianday(LAG(ordered_at) OVER (
               PARTITION BY customer_id
               ORDER BY ordered_at)) AS days_since_prev
  FROM orders
  WHERE status = 'delivered'
)
SELECT c.plan,
       COUNT(g.days_since_prev)          AS gaps,
       ROUND(AVG(g.days_since_prev), 1)  AS avg_days
FROM gaps AS g
JOIN customers AS c ON c.customer_id = g.customer_id
GROUP BY c.plan;

WITH numbered AS (
  SELECT customer_id,
         promo_code,
         ROW_NUMBER() OVER (PARTITION BY customer_id
                            ORDER BY ordered_at,
                                     order_id) AS n
  FROM orders
)
SELECT COUNT(*) AS customers,
       SUM(promo_code IS NOT NULL) AS used_promo,
       ROUND(100.0 * AVG(promo_code IS NOT NULL), 1)
         AS pct_used_promo
FROM numbered
WHERE n = 1;

WITH daily AS (
  SELECT date(ordered_at) AS day,
         COUNT(*) AS orders
  FROM orders
  WHERE ordered_at >= '2026-06-01'
    AND ordered_at <  '2026-07-01'
  GROUP BY day
)
SELECT day,
       orders,
       ROUND(AVG(orders) OVER (
         ORDER BY day
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1)
         AS avg_7d
FROM daily
ORDER BY day
LIMIT 10;

WITH city_cat AS (
  SELECT c.city,
         p.category,
         SUM(i.quantity * i.unit_price) AS sales
  FROM order_items AS i
  JOIN orders    AS o ON o.order_id    = i.order_id
  JOIN customers AS c ON c.customer_id = o.customer_id
  JOIN products  AS p ON p.product_id  = i.product_id
  WHERE o.status = 'delivered'
  GROUP BY c.city, p.category
)
SELECT city,
       category,
       ROUND(100.0 * sales
             / SUM(sales) OVER (PARTITION BY city), 1) AS pct
FROM city_cat
WHERE city = 'Adelaide'
ORDER BY pct DESC;

WITH spend AS (
  SELECT customer_id,
         SUM(basket_aud - discount_aud) AS spend
  FROM orders
  WHERE status = 'delivered'
  GROUP BY customer_id
),
deciles AS (
  SELECT spend,
         NTILE(10) OVER (ORDER BY spend DESC) AS decile
  FROM spend
)
SELECT decile,
       COUNT(*) AS customers,
       CAST(ROUND(SUM(spend)) AS INTEGER) AS spend,
       ROUND(100.0 * SUM(spend)
             / (SELECT SUM(spend) FROM spend), 1) AS pct
FROM deciles
GROUP BY decile
ORDER BY decile;
