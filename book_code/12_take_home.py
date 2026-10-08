# Code from The Data Science Interview Playbook, file 12_take_home
# Run from the repository root.

import sqlite3
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

con = sqlite3.connect("data/corella.db")
o = pd.read_sql("""
    SELECT o.order_id, o.customer_id, o.ordered_at,
           o.basket_aud, c.city, c.plan, c.channel,
           d.delivery_minutes, d.rating
    FROM orders AS o
    JOIN customers AS c ON c.customer_id = o.customer_id
    LEFT JOIN deliveries AS d ON d.order_id = o.order_id
    WHERE o.status = 'delivered'""", con,
    parse_dates=["ordered_at"])

o = o.sort_values(["customer_id", "ordered_at", "order_id"])
o["order_n"] = o.groupby("customer_id").cumcount() + 1
o["next_at"] = o.groupby("customer_id")["ordered_at"].shift(-1)

first = o[o["order_n"] == 1].copy()
first = first[first["ordered_at"] < "2026-05-31"]
gap = first["next_at"] - first["ordered_at"]
first["returned"] = (gap <= pd.Timedelta(days=30)).astype(int)

print(f"customers: {len(first):,}")
print(f"missing delivery time: "
      f"{first['delivery_minutes'].isna().sum()}")
print(f"returned within 30 days: "
      f"{first['returned'].mean():.1%}")
print(first["delivery_minutes"].describe().round(1))

bands = pd.cut(first["delivery_minutes"],
               [0, 30, 40, 50, 120],
               labels=["30 or less", "31-40", "41-50",
                       "over 50"])
by_band = (first.groupby(bands, observed=True)["returned"]
                .agg(rate="mean", customers="count"))
by_band["rate"] = (100 * by_band["rate"]).round(1)
print(by_band)

by_city = first.groupby("city").agg(
    avg_minutes=("delivery_minutes", "mean"),
    return_rate=("returned", "mean"),
    customers=("returned", "size"))
by_city["return_rate"] = (100 * by_city["return_rate"]).round(1)
print(by_city.round(1).sort_values("avg_minutes"))

model = smf.logit(
    "returned ~ delivery_minutes + C(city) + C(plan)"
    " + C(channel) + basket_aud",
    data=first).fit(disp=0)

b = model.params["delivery_minutes"]
lo, hi = model.conf_int().loc["delivery_minutes"]
print(f"odds ratio per 10 extra minutes: {np.exp(10*b):.2f} "
      f"(95% CI {np.exp(10*lo):.2f} to {np.exp(10*hi):.2f})")
print(f"p-value {model.pvalues['delivery_minutes']:.2f}")
print(f"odds ratio, Standard vs Plus: "
      f"{np.exp(model.params['C(plan)[T.standard]']):.2f}")

fast = first.assign(delivery_minutes=30)
slow = first.assign(delivery_minutes=50)
p_fast = model.predict(fast).mean()
p_slow = model.predict(slow).mean()
print(f"predicted return rate if every first delivery "
      f"took 30 min: {p_fast:.1%}")
print(f"... if every first delivery took 50 min: "
      f"{p_slow:.1%}")

rated = first.dropna(subset=["rating"])
print(rated.groupby(bands, observed=True)["rating"]
           .agg(["mean", "count"]).round(2))

new_2025 = (first["ordered_at"].dt.year == 2025).sum()
extra = new_2025 * (p_fast - p_slow)
print(f"new customers in 2025: {new_2025:,}")
print(f"extra returning customers a year: {extra:.0f}")
print(f"break-even value per extra customer: "
      f"${400_000 / extra:,.0f}")
