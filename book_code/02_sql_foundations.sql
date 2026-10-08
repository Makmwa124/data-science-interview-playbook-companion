-- Code from The Data Science Interview Playbook, file 02_sql_foundations
-- Run against data/corella.db (SQLite)

SELECT name FROM sqlite_master
WHERE type = 'table'
ORDER BY name;

SELECT c.city,
       COUNT(*) AS delivered_orders
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.city
ORDER BY delivered_orders DESC;

SELECT COUNT(*) AS never_ordered
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

SELECT COUNT(*) AS never_ordered
FROM customers AS c
WHERE NOT EXISTS (
  SELECT 1 FROM orders AS o
  WHERE o.customer_id = c.customer_id
);

SELECT COUNT(*)                   AS all_rows,
       COUNT(promo_code)          AS with_code,
       COUNT(DISTINCT promo_code) AS distinct_codes
FROM orders;

SELECT ROUND(100.0 * COUNT(promo_code) / COUNT(*), 1)
         AS pct_with_promo
FROM orders;

SELECT customer_id,
       COUNT(*) AS delivered_orders
FROM orders
WHERE status = 'delivered'
GROUP BY customer_id
HAVING COUNT(*) > 100
ORDER BY delivered_orders DESC;

SELECT strftime('%Y-%m', ordered_at) AS month,
       COUNT(*)                       AS orders,
       ROUND(SUM(basket_aud - discount_aud
                 + delivery_fee_aud), 2) AS net_revenue
FROM orders
WHERE status = 'delivered'
  AND ordered_at >= '2025-01-01'
  AND ordered_at <  '2026-01-01'
GROUP BY month
ORDER BY month;

SELECT city,
       SUM(CASE WHEN plan = 'plus' THEN 1 ELSE 0 END)
         AS plus_customers,
       SUM(CASE WHEN plan = 'standard' THEN 1 ELSE 0 END)
         AS standard_customers,
       ROUND(100.0 * AVG(CASE WHEN plan = 'plus'
                              THEN 1.0 ELSE 0 END), 1)
         AS pct_plus
FROM customers
GROUP BY city
ORDER BY pct_plus DESC;

SELECT ROUND(SUM(o.basket_aud), 2) AS total_basket
FROM orders AS o
JOIN order_items AS i
  ON i.order_id = o.order_id
WHERE o.status = 'delivered';

SELECT ROUND(SUM(basket_aud), 2) AS total_basket
FROM orders
WHERE status = 'delivered';

SELECT COUNT(*)                       AS deliveries,
       COUNT(rating)                  AS rated,
       ROUND(AVG(rating), 2)          AS avg_rating,
       ROUND(AVG(COALESCE(rating, 0)), 2) AS wrong_avg
FROM deliveries;

SELECT MAX(basket_aud) AS second_highest
FROM orders
WHERE basket_aud < (SELECT MAX(basket_aud) FROM orders);

SELECT DISTINCT basket_aud
FROM orders
ORDER BY basket_aud DESC
LIMIT 1 OFFSET 1;
