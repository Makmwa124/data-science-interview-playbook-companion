-- Code from The Data Science Interview Playbook, file 10_product_cases
-- Run against data/corella.db (SQLite)

SELECT strftime('%Y-%m', ordered_at) AS month,
       COUNT(DISTINCT customer_id) AS customers,
       ROUND(1.0 * COUNT(*)
             / COUNT(DISTINCT customer_id), 3) AS per_cust,
       ROUND(AVG(basket_aud - discount_aud
                 + delivery_fee_aud), 2) AS aov,
       CAST(ROUND(SUM(basket_aud - discount_aud
                      + delivery_fee_aud)) AS INTEGER) AS rev
FROM orders
WHERE status = 'delivered'
  AND ordered_at >= '2025-06-01'
  AND ordered_at <  '2025-10-01'
GROUP BY month
ORDER BY month;

SELECT c.city,
       c.plan,
       SUM(o.ordered_at <  '2025-08-01') AS jul,
       SUM(o.ordered_at >= '2025-08-01') AS aug,
       SUM(o.ordered_at >= '2025-08-01')
         - SUM(o.ordered_at < '2025-08-01') AS change
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
  AND o.ordered_at >= '2025-07-01'
  AND o.ordered_at <  '2025-09-01'
GROUP BY c.city, c.plan
ORDER BY change
LIMIT 5;
