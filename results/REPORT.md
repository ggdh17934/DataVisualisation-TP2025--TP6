# TP6 — Northwind data mart

All seven instructor-supplied SQLite tables were loaded with dlt into the
Supabase PostgreSQL `staging` schema. Source and destination row counts match.
This source contains **16,282 orders** and **609,283 order-detail rows**;
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
Verified total revenue: **448,386,633.1695**; quantity: **15,538,602**;
average order value: **27,538.79**.
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
