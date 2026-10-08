# Code from The Data Science Interview Playbook, file 09_machine_learning
# Run from the repository root.

import sqlite3
import numpy as np
import pandas as pd

con = sqlite3.connect("data/corella.db")
orders = pd.read_sql(
    "SELECT * FROM orders WHERE status = 'delivered'", con,
    parse_dates=["ordered_at"])
customers = pd.read_sql("SELECT * FROM customers", con,
                        parse_dates=["signup_date"])
deliv = pd.read_sql("SELECT * FROM deliveries", con)

cutoff = pd.Timestamp("2026-04-01")
before = orders[orders["ordered_at"] < cutoff]
after = orders[(orders["ordered_at"] >= cutoff)
               & (orders["ordered_at"] < cutoff
                  + pd.Timedelta(days=90))]

recent = before[before["ordered_at"]
                >= cutoff - pd.Timedelta(days=90)]
population = recent["customer_id"].unique()
print(f"customers in population: {len(population)}")

b = before.merge(deliv, on="order_id", how="left")
feat = b.groupby("customer_id").agg(
    last_order=("ordered_at", "max"),
    first_order=("ordered_at", "min"),
    orders_total=("order_id", "count"),
    avg_basket=("basket_aud", "mean"),
    promo_share=("promo_code", lambda s: s.notna().mean()),
    avg_minutes=("delivery_minutes", "mean"),
    avg_rating=("rating", "mean"),
)
feat["recency_days"] = (cutoff - feat["last_order"]).dt.days
feat["tenure_days"] = (cutoff - feat["first_order"]).dt.days
feat["orders_90d"] = (before[before["ordered_at"] >= cutoff
                             - pd.Timedelta(days=90)]
                      .groupby("customer_id").size())
feat["orders_90d"] = feat["orders_90d"].fillna(0)
feat = feat.drop(columns=["last_order", "first_order"])

feat = feat.loc[population].join(
    customers.set_index("customer_id")[["plan", "channel"]])
feat["is_plus"] = (feat["plan"] == "plus").astype(int)
feat["paid_search"] = (feat["channel"]
                       == "paid_search").astype(int)
feat["churned"] = (~feat.index.isin(after["customer_id"])
                   ).astype(int)
print(feat["churned"].value_counts())
print(f"churn rate {feat['churned'].mean():.3f}")

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

features = ["recency_days", "tenure_days", "orders_total",
            "orders_90d", "avg_basket", "promo_share",
            "avg_minutes", "avg_rating", "is_plus",
            "paid_search"]
X, y = feat[features], feat["churned"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=1)

# avg_rating is missing for customers who never rated
fill = X_train.median()
logit = make_pipeline(StandardScaler(),
                      LogisticRegression(max_iter=1000))
logit.fit(X_train.fillna(fill), y_train)
p_logit = logit.predict_proba(X_test.fillna(fill))[:, 1]

gbm = HistGradientBoostingClassifier(random_state=1)
gbm.fit(X_train, y_train)
p_gbm = gbm.predict_proba(X_test)[:, 1]

p_recency = X_test["recency_days"]
for name, p in [("recency only", p_recency),
                ("logistic", p_logit),
                ("gradient boosting", p_gbm)]:
    print(f"{name:<18} AUC {roc_auc_score(y_test, p):.3f}")

from sklearn.metrics import confusion_matrix

order = np.argsort(-p_logit)
top = np.zeros_like(p_logit, dtype=int)
top[order[:50]] = 1
tn, fp, fn, tp = confusion_matrix(y_test, top).ravel()
print(f"contacted 50: {tp} churners, {fp} non-churners")
print(f"precision {tp / (tp + fp):.2f}, "
      f"recall {tp / (tp + fn):.2f}")
print(f"base rate in test set {y_test.mean():.2f}")

leaky = X.copy()
leaky["orders_all_time"] = (orders.groupby("customer_id")
                            .size().reindex(X.index))
Xl_train = leaky.loc[X_train.index]
Xl_test = leaky.loc[X_test.index]
m = HistGradientBoostingClassifier(random_state=1)
m.fit(Xl_train, y_train)
auc = roc_auc_score(y_test, m.predict_proba(Xl_test)[:, 1])
print(f"AUC with leaked feature {auc:.3f}")

from sklearn.tree import DecisionTreeClassifier

Xf_train, Xf_test = X_train.fillna(fill), X_test.fillna(fill)
for depth in [1, 3, 5, 10, None]:
    tree = DecisionTreeClassifier(max_depth=depth,
                                  random_state=1)
    tree.fit(Xf_train, y_train)
    tr = roc_auc_score(y_train,
                       tree.predict_proba(Xf_train)[:, 1])
    te = roc_auc_score(y_test,
                       tree.predict_proba(Xf_test)[:, 1])
    print(f"depth {str(depth):>4}: train {tr:.3f}, "
          f"test {te:.3f}")

coefs = pd.Series(logit[-1].coef_[0], index=features)
print(coefs.sort_values().round(2))
