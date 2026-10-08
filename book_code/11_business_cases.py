# Code from The Data Science Interview Playbook, file 11_business_cases
# Run from the repository root.

import sqlite3
import pandas as pd

con = sqlite3.connect("data/corella.db")
o = pd.read_sql("""
    SELECT o.*, c.plan
    FROM orders AS o
    JOIN customers AS c ON c.customer_id = o.customer_id
    WHERE o.status = 'delivered'
      AND o.ordered_at >= '2025-07-01'
      AND o.ordered_at <  '2026-07-01'""", con)

margin, pick, drive = 0.28, 6.00, 11.00
o["contribution"] = (o["basket_aud"] * margin
                     - o["discount_aud"]
                     + o["delivery_fee_aud"]
                     - pick - drive)

print(f"orders in the last 12 months: {len(o):,}")
print(o.groupby("plan")[["basket_aud", "delivery_fee_aud",
                         "contribution"]].mean().round(2))
print(f"loss-making orders: "
      f"{(o['contribution'] < 0).mean():.1%}")
