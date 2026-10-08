-- Code from The Data Science Interview Playbook, file 11_business_cases
-- Run against data/corella.db (SQLite)

WITH monthly AS (
  SELECT o.customer_id,
         strftime('%Y-%m', o.ordered_at) AS month,
         COUNT(*) AS orders,
         SUM(CASE WHEN o.basket_aud < 80
                   AND COALESCE(o.promo_code, '') <> 'FREEDEL'
                  THEN 9.95 ELSE 0 END) AS fees_saved
  FROM orders AS o
  JOIN customers AS c ON c.customer_id = o.customer_id
  WHERE c.plan = 'plus'
    AND o.status = 'delivered'
    AND o.ordered_at >= '2026-01-01'
    AND o.ordered_at <  '2026-07-01'
  GROUP BY o.customer_id, month
)
SELECT COUNT(*)                          AS member_months,
       ROUND(AVG(orders), 2)             AS avg_orders,
       ROUND(AVG(fees_saved), 2)         AS avg_saved,
       ROUND(100.0 * AVG(fees_saved > 14.99), 1)
         AS pct_months_ahead
FROM monthly;
