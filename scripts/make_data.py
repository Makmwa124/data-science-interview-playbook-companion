"""Build the Corella Market practice data for The Data Science Interview Playbook.

Corella Market is a fictional online grocery delivery business. Every customer,
driver and order here is made up. Run this script from the repository root:

    python scripts/make_data.py

It writes data/corella.db (SQLite) and the same tables as CSV files in data/.
The random seed is fixed, so you get exactly the data used in the book.
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
DATA = Path("data")
DATA.mkdir(exist_ok=True)
END = pd.Timestamp("2026-06-30")

# ---------------------------------------------------------------- products
products = [
    ("Fruit & Veg", ["Bananas 1kg", "Royal Gala Apples 1kg", "Baby Spinach 120g",
                     "Brown Onions 1kg", "Carrots 1kg", "Avocado", "Cherry Tomatoes 250g",
                     "Washed Potatoes 2kg"], (2.5, 7.0)),
    ("Dairy", ["Full Cream Milk 2L", "Greek Yoghurt 1kg", "Tasty Cheese 500g",
               "Salted Butter 250g", "Free Range Eggs 12pk", "Oat Milk 1L"], (3.0, 9.5)),
    ("Bakery", ["Sourdough Loaf", "Wholemeal Bread", "Croissants 4pk",
                "Wraps 8pk"], (3.5, 7.5)),
    ("Pantry", ["Basmati Rice 2kg", "Penne 500g", "Olive Oil 750ml", "Rolled Oats 1kg",
                "Peanut Butter 375g", "Tinned Tomatoes 400g", "Coffee Beans 500g",
                "Honey 500g"], (1.5, 18.0)),
    ("Meat & Seafood", ["Chicken Thighs 1kg", "Beef Mince 500g", "Salmon Fillets 2pk",
                        "Lamb Chops 600g", "Pork Sausages 500g"], (8.0, 22.0)),
    ("Drinks", ["Sparkling Water 10pk", "Orange Juice 2L", "Kombucha 4pk",
                "Cold Brew 1L"], (4.0, 14.0)),
    ("Household", ["Dishwashing Liquid", "Paper Towel 4pk", "Laundry Powder 2kg"],
     (4.5, 16.0)),
]
rows = []
pid = 101
for cat, names, (lo, hi) in products:
    for n in names:
        rows.append((pid, n, cat, round(float(rng.uniform(lo, hi)) * 2) / 2 - 0.01))
        pid += 1
products = pd.DataFrame(rows, columns=["product_id", "product_name", "category", "price"])
products["price"] = products["price"].round(2)

# ---------------------------------------------------------------- customers
months = pd.period_range("2024-01", "2025-12", freq="M")
cust_rows = []
cid = 10001
cities = ["Adelaide", "Melbourne", "Sydney", "Brisbane", "Perth"]
city_p = [0.34, 0.24, 0.20, 0.13, 0.09]
channels = ["organic", "paid_search", "referral", "social"]
chan_p = [0.38, 0.30, 0.17, 0.15]
for i, m in enumerate(months):
    n = int(rng.poisson(80 + 4 * i))
    for _ in range(n):
        day = int(rng.integers(1, m.days_in_month + 1))
        ch = rng.choice(channels, p=chan_p)
        plus_p = {"organic": 0.22, "paid_search": 0.15, "referral": 0.32, "social": 0.18}[ch]
        cust_rows.append((cid, pd.Timestamp(m.year, m.month, day),
                          rng.choice(cities, p=city_p), ch,
                          "plus" if rng.random() < plus_p else "standard"))
        cid += 1
customers = pd.DataFrame(cust_rows, columns=["customer_id", "signup_date", "city",
                                             "channel", "plan"])

# ---------------------------------------------------------------- orders
promo_codes = ["SPRING15", "FREEDEL", "WINTER10"]
cat_weights = {"Fruit & Veg": 3.0, "Dairy": 2.5, "Bakery": 1.6, "Pantry": 2.0,
               "Meat & Seafood": 1.4, "Drinks": 1.0, "Household": 0.7}
pw = products["category"].map(cat_weights).to_numpy()
pw = pw / pw.sum()

order_rows, item_rows = [], []
oid = 500001
for c in customers.itertuples(index=False):
    plus = c.plan == "plus"
    if rng.random() > (0.90 if plus else 0.82):
        continue  # signed up, never ordered
    rate = (2.6 if plus else 1.2) * rng.lognormal(0, 0.35)  # orders per 30 days
    hazard = (0.05 if plus else 0.12) * (1.35 if c.channel == "paid_search" else 1.0)
    life_days = rng.exponential(30 / hazard)
    t = c.signup_date + pd.Timedelta(days=float(rng.exponential(3)))
    churn_at = c.signup_date + pd.Timedelta(days=life_days)
    first = True
    while t <= END and t <= churn_at:
        n_items = int(np.clip(rng.poisson(5.5 if plus else 4.2), 1, 12))
        picks = rng.choice(len(products), size=n_items, replace=False, p=pw)
        total = 0.0
        for p in picks:
            q = int(rng.choice([1, 1, 1, 2, 2, 3]))
            price = float(products.price.iloc[p])
            item_rows.append((oid, int(products.product_id.iloc[p]), q, price))
            total += q * price
        if first and rng.random() < 0.55:
            promo = "WELCOME10"
        elif rng.random() < 0.06:
            promo = str(rng.choice(promo_codes))
        else:
            promo = None
        discount = round(total * 0.10, 2) if promo in ("WELCOME10", "WINTER10") else (
            round(total * 0.15, 2) if promo == "SPRING15" else 0.0)
        fee = 0.0 if (plus or total >= 80 or promo == "FREEDEL") else 9.95
        r = rng.random()
        status = "delivered" if r < 0.935 else ("cancelled" if r < 0.985 else "refunded")
        hour = int(rng.choice(range(7, 22), p=np.array(
            [2, 3, 4, 5, 6, 6, 5, 5, 6, 7, 9, 10, 9, 7, 5], float) / 89))
        ts = t.normalize() + pd.Timedelta(hours=hour, minutes=int(rng.integers(0, 60)))
        order_rows.append((oid, c.customer_id, ts, status, round(total, 2), discount,
                           fee, promo))
        oid += 1
        first = False
        gap = rng.exponential(30 / rate)
        if t.month == 12:
            gap *= 0.8  # busier in December
        t = t + pd.Timedelta(days=float(max(gap, 1.0)))

orders = pd.DataFrame(order_rows, columns=["order_id", "customer_id", "ordered_at",
                                           "status", "basket_aud", "discount_aud",
                                           "delivery_fee_aud", "promo_code"])
order_items = pd.DataFrame(item_rows, columns=["order_id", "product_id", "quantity",
                                               "unit_price"])

# ---------------------------------------------------------------- drivers
first_names = ["Aisha", "Ben", "Chloe", "Daniel", "Emma", "Farid", "Grace", "Hamish",
               "Isla", "Jack", "Kiri", "Liam", "Mei", "Noah", "Olivia", "Priya",
               "Quinn", "Ravi", "Sofia", "Tom", "Uma", "Vikram", "Willow", "Xavier",
               "Yasmin", "Zac", "Amara", "Brodie", "Caitlin", "Dev"]
last_names = ["Nguyen", "Smith", "Patel", "Wilson", "Chen", "Brown", "Taylor", "Singh",
              "Murphy", "Kelly", "Ali", "Martin", "Walker", "Young", "King"]
drv = []
did = 1
for city in cities:
    mgr = did
    n = {"Adelaide": 7, "Melbourne": 6, "Sydney": 6, "Brisbane": 5, "Perth": 4}[city]
    for k in range(n):
        name = f"{first_names[(did * 7) % 30]} {last_names[(did * 4) % 15]}"
        hired = pd.Timestamp("2023-06-01") + pd.Timedelta(days=int(rng.integers(0, 900)))
        drv.append((did, name, city, None if k == 0 else mgr, hired.date().isoformat()))
        did += 1
drivers = pd.DataFrame(drv, columns=["driver_id", "driver_name", "depot", "manager_id",
                                     "hired_on"])
drivers["manager_id"] = drivers["manager_id"].astype("Int64")

# ---------------------------------------------------------------- deliveries
deliv = orders.loc[orders.status != "cancelled", ["order_id", "customer_id"]].merge(
    customers[["customer_id", "city"]], on="customer_id")
pool = {c: drivers.loc[(drivers.depot == c) & drivers.manager_id.notna(), "driver_id"]
        .to_numpy() for c in cities}
deliv["driver_id"] = [int(rng.choice(pool[c])) for c in deliv.city]
base = {"Adelaide": 34, "Melbourne": 41, "Sydney": 44, "Brisbane": 38, "Perth": 36}
deliv["delivery_minutes"] = [int(round(base[c] + rng.gamma(2.0, 4.0) - 8 +
                                       rng.normal(0, 4))) for c in deliv.city]
deliv["delivery_minutes"] = deliv["delivery_minutes"].clip(lower=12)
deliv["rating"] = np.where(rng.random(len(deliv)) < 0.38,
                           np.nan,
                           np.clip(np.round(5.4 - deliv.delivery_minutes / 30 +
                                            rng.normal(0, 0.7, len(deliv))), 1, 5))
deliveries = deliv[["order_id", "driver_id", "delivery_minutes", "rating"]]

# ---------------------------------------------------------------- app events (June 2026)
ev = []
eid = 1
active = orders.loc[orders.ordered_at >= "2026-05-01", "customer_id"].unique()
for c in active:
    for d in pd.date_range("2026-06-01", "2026-06-30"):
        if rng.random() > 0.28:
            continue
        t0 = d + pd.Timedelta(minutes=int(rng.integers(7 * 60, 22 * 60)))
        steps = ["app_open", "view_product"]
        if rng.random() < 0.55:
            steps.append("add_to_cart")
            if rng.random() < 0.62:
                steps.append("begin_checkout")
                if rng.random() < 0.78:
                    steps.append("purchase")
        for j, s in enumerate(steps):
            ev.append((eid, int(c), t0 + pd.Timedelta(minutes=2 * j), s))
            eid += 1
            if rng.random() < 0.015:  # the app sometimes double-fires an event
                ev.append((eid, int(c), t0 + pd.Timedelta(minutes=2 * j), s))
                eid += 1
app_events = pd.DataFrame(ev, columns=["event_id", "customer_id", "event_time",
                                       "event_type"])

# ---------------------------------------------------------------- experiment
n = 16000
variant = rng.choice(["control", "treatment"], size=n)
device = rng.choice(["ios", "android", "web"], size=n, p=[0.45, 0.35, 0.20])
p = np.where(variant == "control", 0.112, 0.121) * np.where(device == "web", 0.85, 1.0)
converted = (rng.random(n) < p).astype(int)
value = np.where(converted == 1, np.round(rng.gamma(4.0, 17.0, n), 2), 0.0)
checkout_test = pd.DataFrame({
    "visitor_id": np.arange(1, n + 1),
    "assigned_on": (pd.Timestamp("2026-05-04") +
                    pd.to_timedelta(rng.integers(0, 21, n), unit="D")).date.astype(str),
    "variant": variant, "device": device, "converted": converted, "order_value": value})

# ---------------------------------------------------------------- write
customers["signup_date"] = customers["signup_date"].dt.date.astype(str)
orders["ordered_at"] = orders["ordered_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
app_events["event_time"] = app_events["event_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

tables = {"customers": customers, "orders": orders, "order_items": order_items,
          "products": products, "drivers": drivers, "deliveries": deliveries,
          "app_events": app_events, "checkout_test": checkout_test}
db = DATA / "corella.db"
if db.exists():
    db.unlink()
con = sqlite3.connect(db)
for name, df in tables.items():
    df.to_sql(name, con, index=False)
    df.to_csv(DATA / f"{name}.csv", index=False)
con.commit()
con.close()
for name, df in tables.items():
    print(f"{name:<14}{len(df):>8,} rows")
