# DataVisualisation-TP2025 — TP6

Complete solution of the [teacher's TP6](https://github.com/ahmed3991/DataVisualisation-TP2025/blob/main/TP6/TP6.md): Northwind SQLite → dlt → Supabase PostgreSQL → dbt staging and marts, with the required tests.

- `TP6.ipynb`: notebook, real outputs and the explanation.
- `tp6.py`: equivalent entry point; `sqlite_pipeline.py`: the required ingestion script.
- `northwind_T/`: seven staging models, five dimensions, two fact tables and dbt tests.
- `northwind.db`: the exact database supplied by the instructor.
- `EXPLICATION_AR.md`: Arabic explanation of every stage.
- `results/`: verification, fact preview and written report.

## Run

Copy `.env.example` to `.env` and fill in your Supabase **session pooler** host, user, port, database and existing database password. The connection uses SSL. The private `.env` is ignored by Git and is not included in the notebook.

```sh
python -m pip install -r requirements.txt
python tp6.py
```

Alternatively open `TP6.ipynb` and run all cells. In Colab, download/upload the notebook from this private repository; companion files are recreated and Northwind is downloaded from the teacher's public source if needed. Supply your database details when prompted; password input is hidden. A full load is larger than the usual Northwind sample and can take several minutes.

The script runs `dbt deps`, `dbt debug`, staging models/tests and marts models/tests. It compares every source table count with Supabase and reconciles the revenue, quantity and distinct-order totals. Staging views and final tables are created under `northwind_warehouse`.

Rerunning replaces the seven coursework source tables and rebuilds these warehouse models, so use a database/project dedicated to this coursework. Binary pictures are preserved using normal dlt loading for two tiny tables; CSV/COPY makes the remaining tables load efficiently.

Starter fixes are documented in the report: normalized snake_case identifiers, `generate_surrogate_key`, PostgreSQL shipping-date arithmetic, and the surrogate keys needed by relationship tests. No additional dashboard or bonus task is added to TP6.

Verified on the real Supabase project: 14 models and all 76 dbt tests pass. All 609,283 order-detail rows and 16,282 orders match the instructor's source; revenue and quantity reconcile. The notebook was executed successfully from beginning to end.
