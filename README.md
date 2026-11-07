# The Data Science Interview Playbook: companion files

Free practice files for the book **The Data Science Interview Playbook: SQL, Statistics, Case Questions and Take-Home Tasks, with Worked Model Answers** by Mathew Kariuki.

Every example in the book uses Corella Market, a fictional online grocery delivery business with depots in five Australian cities. This repository holds its practice database, the same tables as CSV files, every SQL query and Python example from the book, model answers to the practice questions, and printable worksheets, so you can work through every question yourself.

## Download

Click the green **Code** button above, then **Download ZIP**. Unzip it somewhere sensible, such as your Documents folder.

## What's here

| Path | What it is |
| --- | --- |
| `data/corella.db` | The practice database (SQLite): customers, orders, order items, products, drivers, deliveries, app events and an A/B test |
| `data/*.csv` | The same eight tables as CSV files |
| `book_code/` | Every SQL query (`.sql`) and Python example (`.py`) from the book, by chapter |
| `practice_answers/` | Model answers, with real outputs, to the practice questions in Chapters 2 to 12 |
| `worksheets/` | Case-question framework, take-home checklist and behavioural story bank (Markdown and PDF) |
| `scripts/make_data.py` | The script that generates the data (fixed seed, so you get exactly the book's data) |
| `requirements.txt` | The Python packages used in the book |

## Quick start

1. For the SQL chapters, open `data/corella.db` in a free SQLite client such as DB Browser for SQLite, and try:

   ```sql
   SELECT city, COUNT(*) AS customers
   FROM customers
   GROUP BY city
   ORDER BY customers DESC;
   ```

2. For the Python chapters, install Python, then run:

   ```
   pip install -r requirements.txt
   ```

3. In VS Code, choose **File > Open Folder** and open this folder. Run any file in `book_code/`, or create a notebook here and start with:

   ```python
   import sqlite3
   import pandas as pd
   con = sqlite3.connect("data/corella.db")
   orders = pd.read_sql("SELECT * FROM orders", con)
   orders.head()
   ```

Paths such as `data/corella.db` assume this folder is your working directory.

Tested with Python 3.13, pandas 3.0, NumPy 2.5, SciPy 1.18, statsmodels 0.15 and scikit-learn 1.9. The SQL is written for SQLite 3.28 or later (Python's built-in `sqlite3` module is fine); the book notes the PostgreSQL, Snowflake, BigQuery and SQL Server equivalents where they differ.

## Get the book

- **Paperback:** [Amazon.com](https://www.amazon.com/dp/B0HPZC3TK4) · [Amazon.com.au](https://www.amazon.com.au/dp/B0HPZC3TK4)
- **Kindle:** [Amazon.com](https://www.amazon.com/dp/B0HPZ8MH1B) · [Amazon.com.au](https://www.amazon.com.au/dp/B0HPZ8MH1B)

## About

Corella Market and every person and business in its data are fictional. The data and code are free to use for learning. The book itself is © 2026 Mathew Kariuki.

Spotted a problem with an example or the data? Please open an issue.
