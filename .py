Python Scripts

Generate Fake Data

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
 
# ── Config ─────────────────────────────────────────────────────────────────
fake = Faker()
np.random.seed(42)
random.seed(42)
 
NUM_CUSTOMERS   = 1_000
NUM_PRODUCTS    = 100
NUM_ORDERS      = 5_000
NUM_ORDER_ITEMS = 12_000   # roughly 2-3 items per order on average
 
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
 
REGIONS        = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
LOYALTY_TIERS  = ["Standard", "Silver", "Gold", "Platinum"]
CATEGORIES     = ["Electronics", "Home & Garden", "Clothing", "Toys", "Sports", "Books", "Beauty"]
ORDER_STATUSES = ["completed", "completed", "completed", "returned", "cancelled"]  # weighted toward completed
 
 
# ── 1. customers.csv ────────────────────────────────────────────────────────
print("Generating customers...")
 
customer_ids = list(range(1, NUM_CUSTOMERS + 1))
 
customers = pd.DataFrame({
    "customer_id":  customer_ids,
    "first_name":   [fake.first_name() for _ in customer_ids],
    "last_name":    [fake.last_name()  for _ in customer_ids],
    "email":        [fake.email()      for _ in customer_ids],
    "region":       np.random.choice(REGIONS, size=NUM_CUSTOMERS),
    "loyalty_tier": np.random.choice(LOYALTY_TIERS, size=NUM_CUSTOMERS, p=[0.5, 0.25, 0.15, 0.10]),
    "join_date":    [
        fake.date_between(start_date="-3y", end_date="today")
        for _ in customer_ids
    ],
})
 
# Intentionally add some nulls to simulate messy data
null_indices = np.random.choice(customers.index, size=30, replace=False)
customers.loc[null_indices, "email"] = np.nan
 
customers.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
print(f"  Saved {len(customers)} customers.")
 
 
# ── 2. products.csv ─────────────────────────────────────────────────────────
print("Generating products...")
 
product_ids = list(range(1, NUM_PRODUCTS + 1))
 
unit_prices    = np.round(np.random.uniform(5, 300, size=NUM_PRODUCTS), 2)
supplier_costs = np.round(unit_prices * np.random.uniform(0.4, 0.7, size=NUM_PRODUCTS), 2)
 
products = pd.DataFrame({
    "product_id":     product_ids,
    "product_name":   [fake.catch_phrase() for _ in product_ids],
    "category":       np.random.choice(CATEGORIES, size=NUM_PRODUCTS),
    "unit_price":     unit_prices,
    "supplier_cost":  supplier_costs,
})
 
products.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)
print(f"  Saved {len(products)} products.")
 
 
# ── 3. orders.csv ───────────────────────────────────────────────────────────
print("Generating orders...")
 
order_ids = list(range(1, NUM_ORDERS + 1))
 
# Random dates over the last 12 months
start_date = datetime.now() - timedelta(days=365)
order_dates = [
    start_date + timedelta(days=random.randint(0, 365))
    for _ in order_ids
]
 
orders = pd.DataFrame({
    "order_id":    order_ids,
    "customer_id": np.random.choice(customer_ids, size=NUM_ORDERS),
    "order_date":  [d.strftime("%Y-%m-%d") for d in order_dates],
    "status":      [random.choice(ORDER_STATUSES) for _ in order_ids],
    "region":      np.random.choice(REGIONS, size=NUM_ORDERS),
})
 
# Intentionally add some nulls
null_indices = np.random.choice(orders.index, size=50, replace=False)
orders.loc[null_indices, "region"] = np.nan
 
orders.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)
print(f"  Saved {len(orders)} orders.")
 
 
# ── 4. order_items.csv ──────────────────────────────────────────────────────
print("Generating order items...")
 
# Assign order_ids randomly across NUM_ORDER_ITEMS rows
item_order_ids  = np.random.choice(order_ids, size=NUM_ORDER_ITEMS)
item_product_ids = np.random.choice(product_ids, size=NUM_ORDER_ITEMS)
 
# Look up unit_price from products table
price_lookup = products.set_index("product_id")["unit_price"].to_dict()
item_prices  = [price_lookup[pid] for pid in item_product_ids]
 
order_items = pd.DataFrame({
    "item_id":    range(1, NUM_ORDER_ITEMS + 1),
    "order_id":   item_order_ids,
    "product_id": item_product_ids,
    "quantity":   np.random.randint(1, 6, size=NUM_ORDER_ITEMS),
    "unit_price": item_prices,
})
 
# Add a few outlier quantities to simulate data issues
outlier_idx = np.random.choice(order_items.index, size=10, replace=False)
order_items.loc[outlier_idx, "quantity"] = np.random.randint(50, 200, size=10)
 
# Add duplicate rows to simulate messy data (will be cleaned in Python later)
dupes = order_items.sample(n=50, random_state=1)
order_items = pd.concat([order_items, dupes], ignore_index=True)
 
order_items.to_csv(f"{OUTPUT_DIR}/order_items.csv", index=False)
print(f"  Saved {len(order_items)} order items (includes 50 intentional duplicates).")
 
 
# ── Summary ─────────────────────────────────────────────────────────────────
print("\nAll done! Files saved to the 'data/' folder:")
for fname in ["customers.csv", "products.csv", "orders.csv", "order_items.csv"]:
    path = f"{OUTPUT_DIR}/{fname}"
    df   = pd.read_csv(path)
    print(f"  {fname:20s}  {len(df):>6,} rows  x  {len(df.columns)} columns")

Connect SQL and Python 

import pandas as pd
from sqlalchemy import create_engine

# ── 1. Your connection details ───────────────────────────────────────────────
# Change these to match your MySQL setup.
# If you installed MySQL locally with default settings, only PASSWORD changes.

DB_HOST = "localhost"  # almost always localhost on a personal machine
DB_PORT = 3306  # MySQL default port — don't change unless you know it's different
DB_USER = "root"  # default MySQL username
DB_PASSWORD = "Your_password"  # ← put your MySQL password here
DB_NAME = "northshelf"  # the database we created

# ── 2. Create the connection (engine) ────────────────────────────────────────
# SQLAlchemy builds the connection that pandas uses under the hood.
# The format is: "mysql+mysqlconnector://user:password@host:port/database"

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("Connecting to MySQL...")

# ── 3. Read each table into a DataFrame ──────────────────────────────────────
# pd.read_sql() takes a SQL query (as a string) and the engine.
# You can write any SELECT query here — or just SELECT * to grab the whole table.

try:
    customers = pd.read_sql("SELECT * FROM customers", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    orders = pd.read_sql("SELECT * FROM orders", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)

    print("Connected! Tables loaded successfully.\n")

except Exception as e:
    print(f"Connection failed: {e}")
    print("\nCommon fixes:")
    print("  - Check your DB_PASSWORD is correct")
    print("  - Make sure MySQL server is running (check MySQL Workbench)")
    print("  - Make sure the northshelf database exists (run create_tables.sql first)")
    raise

# ── 4. Quick check: print shape and first few rows of each ───────────────────

print("── customers ──────────────────────────────")
print(f"Shape: {customers.shape}")  # (rows, columns)
print(customers.head(3))
print()

print("── products ───────────────────────────────")
print(f"Shape: {products.shape}")
print(products.head(3))
print()

print("── orders ─────────────────────────────────")
print(f"Shape: {orders.shape}")
print(orders.head(3))
print()

print("── order_items ────────────────────────────")
print(f"Shape: {order_items.shape}")
print(order_items.head(3))
print()

# ── 5. BONUS: Read a VIEW directly (same as reading a table) ─────────────────
# Once you've created the views in analysis_queries.sql,
# you can pull them straight into pandas like this:

# monthly_revenue = pd.read_sql("SELECT * FROM vw_monthly_revenue_by_category", engine)
# ltv_by_tier     = pd.read_sql("SELECT * FROM vw_ltv_by_loyalty_tier",         engine)
# region_perf     = pd.read_sql("SELECT * FROM vw_region_performance",           engine)

# print(monthly_revenue.head())


# ── 6. Check for nulls (quick data quality sense-check) ──────────────────────

print("── Null counts per table ──────────────────")
for name, df in [("customers", customers), ("orders", orders)]:
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]  # only show columns that actually have nulls
    print(f"\n{name}:")
    print(nulls if len(nulls) > 0 else "  No nulls found")

Cleaning 

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os

# ── Connection ───────────────────────────────────────────────────────────────
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "Blondebluetan_11"  # ← change this
DB_NAME = "northshelf"

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

OUTPUT_DIR = "data/data/cleaned"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Helper: print a simple before/after summary ──────────────────────────────
def report(label, df_before, df_after):
    rows_dropped = len(df_before) - len(df_after)
    print(f"  Rows before : {len(df_before):,}")
    print(f"  Rows after  : {len(df_after):,}")
    print(f"  Rows dropped: {rows_dropped:,}")
    print()


# ════════════════════════════════════════════════════════════════════════════
# LOAD RAW TABLES
# ════════════════════════════════════════════════════════════════════════════
print("Loading tables from MySQL...")
customers = pd.read_sql("SELECT * FROM customers", engine)
products = pd.read_sql("SELECT * FROM products", engine)
orders = pd.read_sql("SELECT * FROM orders", engine)
order_items = pd.read_sql("SELECT * FROM order_items", engine)
print("Done.\n")

# ════════════════════════════════════════════════════════════════════════════
# CLEAN: customers
# ════════════════════════════════════════════════════════════════════════════
print("── Cleaning customers ──────────────────────")
raw = customers.copy()

#1. Drop duplicate rows
customers = customers.drop_duplicates()

#2. Fix data format
customers["join_date"] = pd.to_datetime(customers["join_date"], errors = "coerce")
# coerce turns unparsable into NaT instead of crashing

#3. Handle nulls
#email is replaced with placeholders
#loyalty_tier / region is filled unknown

customers["email"] = customers["email"].fillna("unknown@email.com")
customers["loyalty_tier"] = customers["loyalty_tier"].fillna("Unknown")
customers["region"] = customers["region"].fillna("Unknown")

report("customers", raw, customers)
#quick check
print("  remaining nulls:")
print(customers.isnull().sum(), "\n")

# ════════════════════════════════════════════════════════════════════════════
# CLEAN: products
# ════════════════════════════════════════════════════════════════════════════
print("── Cleaning products ───────────────────────")
raw = products.copy()
#1. Drop duplicates

products = products.drop_duplicates()
#2. Handle Nulls
#   If price or cost is missing, we can't calculate revenue -- drop those rows

products = products.dropna(subset=["unit_price", "supplier_cost"])
#3. Cap price outliers at 99th percentile
#   (protects against a $999,999 typo skewing all our revenue numbers)

price_cap = products["unit_price"].quantile(0.99)
print(f" unit_price 99th percentile cap: ${price_cap:,.2f}")

products["unit_price"] = products["unit_price"].clip(upper=price_cap)
# .clip(upper=X) replaces anything above X with X — simple and clean

report("products", raw, products)

# ════════════════════════════════════════════════════════════════════════════
# CLEAN: orders
# ════════════════════════════════════════════════════════════════════════════
print("── Cleaning orders ─────────────────────────")
raw = orders.copy()

# 1. Drop duplicate rows
orders = orders.drop_duplicates()

# 2. Fix date format — this is the most important one for Power BI
orders["order_date"] = pd.to_datetime(orders["order_date"], errors = "coerce")

# 3. Drop rows where order_date is missing (can't place on a timeline without a date)
before = len(orders)
orders = orders.dropna(subset=["order_date"])

print(f" Dropped{before - len(orders):,} rows with missing order_date")

# 4. Handle null region — fill with "Unknown" (we still want the order's revenue)
orders["region"] = orders["region"].fillna("Unknown")

# 5. Sanity check: remove any orders with unrecognized status values
valid_statuses = ["completed", "returned", "cancelled"]
orders = orders[orders["status"].isin(valid_statuses)]

report("orders", raw, orders)

# ════════════════════════════════════════════════════════════════════════════
# CLEAN: order_items
# ════════════════════════════════════════════════════════════════════════════
print("── Cleaning order_items ────────────────────")
raw = order_items.copy()

# 1. Drop duplicate rows (we intentionally added 50 in the generator)
order_items = order_items.drop_duplicates()
print(f" Duplicates removed: {len(raw) - len(order_items):,}")

# 2. Drop rows with missing quantity or unit_price (can't calculate revenue)
order_items = order_items.dropna(subset=["quantity", "unit_price"])

# 3. Drop rows where quantity <= 0 (nonsense data)
order_items = order_items[order_items["quantity"] > 0]

# 4. Cap quantity outliers at 99th percentile
#    (the generator added some 50-200 unit orders to simulate data issues)
qty_cap = order_items["quantity"].quantile(0.99)
print(f" quantity 99th percentile cap  :{qty_cap:.0f} units")
order_items["quantity"] = order_items["quantity"].clip(upper=qty_cap)

# 5. Cap unit_price outliers at 99th percentile
price_cap = order_items["unit_price"].quantile(0.99)
print(f"  unit_price 99th percentile cap  : ${price_cap:.2f} units")
order_items["unit_price"] = order_items["unit_price"].clip(upper=price_cap)

# 6. Add a revenue column (quantity x price) — used in Power BI
order_items["revenue"] = order_items["quantity"] * order_items["unit_price"]

report("order_items", raw, order_items)

# ════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════════════════════

print("── Exporting cleaned CSVs ──────────────────")

customers.to_csv(f"{OUTPUT_DIR}/customers_clean.csv", index=False)
products.to_csv(f"{OUTPUT_DIR}/products_clean.csv", index=False)
orders.to_csv(f"{OUTPUT_DIR}/orders_clean.csv", index=False)
order_items.to_csv(f"{OUTPUT_DIR}/order_items_clean.csv", index=False)

print(f"  Saved to {OUTPUT_DIR}/")
print()

# ════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════════════════════
print("── Final summary ───────────────────────────")
for name, df in [
    ("customers_clean", customers),
    ("products_clean", products),
    ("orders_clean", orders),
    ("order_items_clean", order_items),
]:
    total_nulls = df.isnull().sum().sum()
    print(f"  {name:25s}  {len(df):>6,} rows  |  {total_nulls} nulls remaining")

print("\nCleaning complete! CSVs are ready to import into Power BI.")

