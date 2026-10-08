# Code from The Data Science Interview Playbook, file 05_python_pandas
# Run from the repository root.

import sqlite3
import numpy as np
import pandas as pd

con = sqlite3.connect("data/corella.db")
orders = pd.read_sql("SELECT * FROM orders", con,
                     parse_dates=["ordered_at"])
customers = pd.read_sql("SELECT * FROM customers", con,
                        parse_dates=["signup_date"])

print(orders.shape)
print(orders.dtypes)

print(orders["order_id"].is_unique)
print(orders["ordered_at"].min(), orders["ordered_at"].max())
print(orders.isna().sum()[lambda s: s > 0])
print(orders["status"].value_counts(normalize=True).round(3))

delivered = orders[orders["status"] == "delivered"]
df = delivered.merge(customers, on="customer_id",
                     how="left", validate="many_to_one")

table = df.pivot_table(index="city", columns="plan",
                       values="basket_aud", aggfunc="mean")
print(table.round(2))

spend = (df.assign(net=df["basket_aud"] - df["discount_aud"])
           .groupby(["city", "customer_id"], as_index=False)
           ["net"].sum())

top = (spend.sort_values("net", ascending=False)
            .groupby("city")
            .head(1)
            .sort_values("city"))
print(top.round(2).to_string(index=False))

weekly = (orders.set_index("ordered_at")
                .sort_index()
                .loc["2025-12-29":"2026-06-28"]
                .resample("W-SUN")["order_id"].count()
                .rename("orders")
                .to_frame())
weekly["avg_4w"] = weekly["orders"].rolling(4).mean().round(1)
print(weekly.head(6))
print(len(weekly), "weeks")

deliveries = pd.read_sql("SELECT * FROM deliveries", con)
deliveries["rated"] = deliveries["rating"].notna()
print(deliveries.groupby("rated")["delivery_minutes"]
                .describe()[["count", "mean", "50%"]]
                .round(1))

asof = pd.Timestamp("2026-06-30 23:59:59")
d = orders[orders["status"] == "delivered"]

rfm = d.groupby("customer_id").agg(
    last_order=("ordered_at", "max"),
    frequency=("order_id", "count"),
    monetary=("basket_aud", "sum"),
)
rfm["recency_days"] = (asof - rfm["last_order"]).dt.days
rfm = rfm.drop(columns="last_order")
print(rfm.describe().round(1))

bins = [0, 40, 80, np.inf]
labels = ["small", "medium", "large"]
orders["size"] = pd.cut(orders["basket_aud"], bins=bins,
                        labels=labels, right=False)
print(orders["size"].value_counts().sort_index())

def longest_increasing_run(counts):
    if not counts:
        return 0
    best = current = 1
    for prev, now in zip(counts, counts[1:]):
        current = current + 1 if now > prev else 1
        best = max(best, current)
    return best

print(longest_increasing_run([44, 44, 39, 43, 42, 36, 31]))
print(longest_increasing_run([30, 47, 50, 52, 41, 45]))
print(longest_increasing_run([]))

from collections import Counter

def top_codes(codes, k=3):
    return Counter(c for c in codes
                   if pd.notna(c)).most_common(k)

print(top_codes(orders["promo_code"].tolist()))
