# Chapter 2 practice answers

**1. Orders and average discount by promo code.**

```sql
SELECT promo_code,
       COUNT(*) AS orders,
       ROUND(AVG(discount_aud), 2) AS avg_discount
FROM orders
WHERE promo_code IS NOT NULL
GROUP BY promo_code
ORDER BY orders DESC;
```

```output
promo_code  orders  avg_discount
----------  ------  ------------
WELCOME10     1420          5.54
SPRING15       747          8.96
FREEDEL        696           0.0
WINTER10       689          5.92
```

FREEDEL shows a zero discount because its value is the waived delivery fee, not a basket discount.

**2. Category with the highest quantity sold on delivered orders.**

```sql
SELECT p.category,
       SUM(i.quantity) AS units
FROM order_items AS i
JOIN orders AS o ON o.order_id = i.order_id
JOIN products AS p ON p.product_id = i.product_id
WHERE o.status = 'delivered'
GROUP BY p.category
ORDER BY units DESC;
```

```output
category        units
--------------  -----
Fruit & Veg     86557
Pantry          58818
Dairy           54714
Meat & Seafood  26593
Bakery          23862
Drinks          15595
Household        8077
```

**3. Drivers per depot, excluding managers.**

```sql
SELECT depot, COUNT(*) AS drivers
FROM drivers
WHERE manager_id IS NOT NULL
GROUP BY depot
ORDER BY drivers DESC;
```

```output
depot      drivers
---------  -------
Adelaide         6
Sydney           5
Melbourne        5
Brisbane         4
Perth            3
```

**4. Percentage of 2025 orders that attracted a delivery fee.**

```sql
SELECT ROUND(100.0 * AVG(delivery_fee_aud > 0), 1)
         AS pct_with_fee
FROM orders
WHERE ordered_at >= '2025-01-01'
  AND ordered_at <  '2026-01-01';
```

```output
pct_with_fee
------------
        43.6
```
