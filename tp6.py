"""Run and verify the required Northwind dlt/dbt warehouse."""
# %% 1. Imports, private connection and source database
import json
import os
from pathlib import Path
import sqlite3

import pandas as pd
import psycopg2
from dbt.cli.main import dbtRunner
from connection import configure_connection
from sqlite_pipeline import TABLES, ensure_database, load_sqlite_data

ROOT = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
os.environ["DBT_SEND_ANONYMOUS_USAGE_STATS"] = "false"
url = configure_connection()
with sqlite3.connect(ensure_database()) as source:
    source_counts = {target: source.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                     for table, target in TABLES.items()}
print("Source row counts:", source_counts)

# %% 2. dlt: load the seven complete source tables into Supabase staging
load_sqlite_data()

# %% 3. dbt: connection check, dependencies, staging and marts with their tests
project = ROOT / "northwind_T"
runner = dbtRunner()
dbt_results = []
staging_models = [f"stg_{table}" for table in TABLES.values()]
mart_models = ["dim_customers", "dim_employees", "dim_products", "dim_suppliers",
               "dim_categories", "fct_orders", "fct_order_details"]
commands = [["deps"], ["debug"], ["run", "--select", *staging_models],
            ["test", "--select", *staging_models], ["run", "--select", *mart_models],
            ["test", "--select", *mart_models]]
for command in commands:
    result = runner.invoke(command + ["--project-dir", str(project), "--profiles-dir", str(project)])
    if not result.success:
        raise RuntimeError(f"dbt {' '.join(command)} failed; check the dbt log.") from result.exception
    if command[0] in {"run", "test"} and not result.result.results:
        raise RuntimeError("dbt selected no models or tests; check the selection.")
    dbt_results.append({"command": "dbt " + " ".join(command), "success": True})

# %% 4. Verify row counts, fact-table grain and reconciliation to SQLite
warehouse_counts = {}
with psycopg2.connect(url) as connection:
    with connection.cursor() as cursor:
        for table in TABLES.values():
            cursor.execute(f'SELECT COUNT(*) FROM staging.{table}')
            count = cursor.fetchone()[0]
            assert count == source_counts[table], f"Row-count mismatch: {table}"
            warehouse_counts[f"staging.{table}"] = count
        for table in ["dim_customers", "dim_employees", "dim_products", "dim_suppliers",
                      "dim_categories", "fct_orders", "fct_order_details"]:
            cursor.execute(f'SELECT COUNT(*) FROM northwind_warehouse.{table}')
            warehouse_counts[f"northwind_warehouse.{table}"] = cursor.fetchone()[0]
        cursor.execute("""SELECT SUM(extended_price), COUNT(DISTINCT order_id),
                          SUM(quantity), COUNT(*) FROM northwind_warehouse.fct_order_details""")
        revenue, orders, quantity, details = cursor.fetchone()
        cursor.execute("""SELECT order_detail_pk, order_id, product_id, quantity,
                          unit_price, discount, extended_price, order_date, shipping_delay_days
                          FROM northwind_warehouse.fct_order_details
                          ORDER BY order_id, product_id LIMIT 10""")
        preview = pd.DataFrame(cursor.fetchall(), columns=[c.name for c in cursor.description])
with sqlite3.connect(ensure_database()) as source:
    source_revenue, source_quantity, source_orders = source.execute(
        'SELECT SUM(UnitPrice * Quantity * (1 - Discount)), SUM(Quantity), COUNT(DISTINCT OrderID) FROM "Order Details"'
    ).fetchone()
assert abs(float(revenue) - source_revenue) < 0.01
assert int(quantity) == source_quantity and orders == source_orders
assert details == source_counts["order_details"]
summary = {"source_counts": source_counts, "warehouse_counts": warehouse_counts,
           "total_revenue": float(revenue), "total_orders": orders,
           "total_quantity": int(quantity), "detail_rows": details,
           "average_order_value": float(revenue) / orders, "dbt_commands": dbt_results}
(OUT / "verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
preview.to_csv(OUT / "fct_order_details_preview.csv", index=False)
print(pd.Series(warehouse_counts).to_string())
print(preview.to_string(index=False))
print("Revenue:", revenue, "Orders:", orders, "Quantity:", quantity)

# %% 5. Required warehouse explanation and documented starter corrections
report = f"""# TP6 — Northwind data mart

All seven instructor-supplied SQLite tables were loaded with dlt into the
Supabase PostgreSQL `staging` schema. Source and destination row counts match.
This source contains **{orders:,} orders** and **{details:,} order-detail rows**;
it is the larger database supplied by the teacher, not a tiny sample.
Suppliers are loaded too, because their staging and dimension models are required.

Seven staging models standardize columns, types and surrogate keys.
Five dimensions describe customers, employees, products, suppliers and categories.
`fct_orders` has one row per order; `fct_order_details` has one row per
order/product pair and keys referencing the dimensions, order dates and measures.
Date fields remain attributes, matching the detailed tasks; no extra date-dimension
or unrelated feature is introduced. Product dimensions include category names;
employee dimensions include full names; customers include first-order dates and
full addresses. Both fact tables include shipping delay, which TP7 needs.

Revenue = unit_price × quantity × (1 − discount).
Verified total revenue: **{float(revenue):,.4f}**; quantity: **{int(quantity):,}**;
average order value: **{float(revenue)/orders:,.2f}**.
SQL uses decimal arithmetic; the SQLite floating-point total agrees within one cent.
These are values in the source's monetary unit; the SQLite data do not establish
a currency, so the reports do not invent one.

All required dbt connection, run and test commands completed successfully.
Primary keys have unique/not-null tests, foreign keys have relationship tests,
and order status is checked against the allowed statuses. Dates lacking shipping
information stay NULL rather than being converted to a zero-day delivery.

Starter corrections: dlt actually normalizes identifiers to snake_case;
dbt references those names. `dbt_utils.generate_surrogate_key` replaces the
removed older `surrogate_key` macro. PostgreSQL timestamp subtraction with
EXTRACT computes shipping days; SQLite-only `julianday` cannot run here.
Prices, freight and discounts have explicit decimal hints during ingestion,
preventing SQLite's mixed integer/float values from splitting into variant columns.
The order fact explicitly includes its customer/employee surrogate keys, so
relationship tests check real columns. Models use views for staging and tables
for marts; rerunning replaces the coursework snapshot instead of duplicating it.
Tests use dbt's built-in assertions, with explicit SQL types, avoiding a second
dependency merely to assert the declared monetary column type.
Model names are selected explicitly because unqualified wildcard selections
do not match folder-qualified models consistently in the installed dbt version.

Credentials come from an ignored `.env` file or hidden input. None are saved
in the notebook or GitHub files. TP7 can now connect to northwind_warehouse.

Assignment: https://github.com/ahmed3991/DataVisualisation-TP2025/blob/main/TP6/TP6.md
"""
(OUT / "REPORT.md").write_text(report, encoding="utf-8")
print("Saved verification results and the TP6 explanation.")
