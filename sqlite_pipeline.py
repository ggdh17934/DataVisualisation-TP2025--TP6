"""Load all seven required Northwind tables into Supabase staging with dlt."""
import os
import sqlite3
from pathlib import Path
import requests
import dlt
from connection import configure_connection

ROOT = Path(__file__).resolve().parent
SOURCE_URL = "https://raw.githubusercontent.com/ahmed3991/DataVisualisation-TP2025/main/TP6/northwind.db"
TABLES = {"Customers": "customers", "Orders": "orders", "Employees": "employees",
          "Products": "products", "Categories": "categories", "Suppliers": "suppliers",
          "Order Details": "order_details"}
DECIMAL_COLUMNS = {"Products": ["UnitPrice"], "Orders": ["Freight"],
                   "Order Details": ["UnitPrice", "Discount"]}

def ensure_database():
    path = ROOT / "northwind.db"
    if not path.exists():
        response = requests.get(SOURCE_URL, timeout=120)
        response.raise_for_status()
        path.write_bytes(response.content)
    return path

def table_rows(source_table):
    with sqlite3.connect(ensure_database()) as connection:
        cursor = connection.execute(f'SELECT * FROM "{source_table}"')
        names = [column[0] for column in cursor.description]
        while rows := cursor.fetchmany(5000):
            yield [dict(zip(names, row)) for row in rows]

def load_sqlite_data():
    os.environ.setdefault("DLT_TELEMETRY", "false")
    url = configure_connection()
    pipeline = dlt.pipeline(pipeline_name="northwind_sqlite_copy", destination="postgres",
                           dataset_name="staging", pipelines_dir=str(ROOT / ".dlt-state"))
    for source, destination in TABLES.items():
        # SQLite NUMERIC values may arrive as either int or float. Declare the
        # intended decimal type so dlt keeps all prices in the same column.
        columns = {name: {"data_type": "decimal", "precision": 18, "scale": 6}
                   for name in DECIMAL_COLUMNS.get(source, [])}
        resource = dlt.resource(table_rows(source), name=destination,
                                write_disposition="replace", columns=columns)
        # Preserve binary images using standard inserts for these two tiny tables.
        # Other tables use CSV/COPY to avoid many small network INSERT calls.
        file_format = "insert_values" if source in {"Employees", "Categories"} else "csv"
        info = pipeline.run(resource, credentials=url, loader_file_format=file_format)
        info.raise_on_failed_jobs()
        print("Loaded:", source)
    return pipeline

if __name__ == "__main__":
    load_sqlite_data()
