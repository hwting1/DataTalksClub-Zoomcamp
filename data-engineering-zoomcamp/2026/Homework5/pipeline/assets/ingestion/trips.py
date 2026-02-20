"""@bruin

# TODO: Set the asset name (recommended pattern: schema.asset_name).
# - Convention in this module: use an `ingestion.` schema for raw ingestion tables.
name: ingestion.trips

# TODO: Set the asset type.
# Docs: https://getbruin.com/docs/bruin/assets/python
type: python

# TODO: Pick a Python image version (Bruin runs Python in isolated environments).
# Example: python:3.11
image: python:3.11

# TODO: Set the connection.
connection: duckdb-default

# TODO: Choose materialization (optional, but recommended).
# Bruin feature: Python materialization lets you return a DataFrame (or list[dict]) and Bruin loads it into your destination.
# This is usually the easiest way to build ingestion assets in Bruin.
# Alternative (advanced): you can skip Bruin Python materialization and write a "plain" Python asset that manually writes
# into DuckDB (or another destination) using your own client library and SQL. In that case:
# - you typically omit the `materialization:` block
# - you do NOT need a `materialize()` function; you just run Python code
# Docs: https://getbruin.com/docs/bruin/assets/python#materialization
materialization:
  # TODO: choose `table` or `view` (ingestion generally should be a table)
  type: table
  # TODO: pick a strategy.
  # suggested strategy: append
  strategy: append

# TODO: Define output columns (names + types) for metadata, lineage, and quality checks.
# Tip: mark stable identifiers as `primary_key: true` if you plan to use `merge` later.
# Docs: https://getbruin.com/docs/bruin/assets/columns
columns:
  - name: tpep_pickup_datetime
    type: timestamp
    description: "When the meter was engaged"
  - name: tpep_dropoff_datetime
    type: timestamp
    description: "When the meter was disengaged"
@bruin"""

# TODO: Add imports needed for your ingestion (e.g., pandas, requests).
# - Put dependencies in the nearest `requirements.txt` (this template has one at the pipeline root).
# Docs: https://getbruin.com/docs/bruin/assets/python
import os
import json
import pandas as pd
from datetime import datetime, timezone
import io
import requests
from dateutil.relativedelta import relativedelta

# TODO: Only implement `materialize()` if you are using Bruin Python materialization.
# If you choose the manual-write approach (no `materialization:` block), remove this function and implement ingestion
# as a standard Python script instead.
def materialize():
    """
    TODO: Implement ingestion using Bruin runtime context.

    Required Bruin concepts to use here:
    - Built-in date window variables:
      - BRUIN_START_DATE / BRUIN_END_DATE (YYYY-MM-DD)
      - BRUIN_START_DATETIME / BRUIN_END_DATETIME (ISO datetime)
      Docs: https://getbruin.com/docs/bruin/assets/python#environment-variables
    - Pipeline variables:
      - Read JSON from BRUIN_VARS, e.g. `taxi_types`
      Docs: https://getbruin.com/docs/bruin/getting-started/pipeline-variables

    Design TODOs (keep logic minimal, focus on architecture):
    - Use start/end dates + `taxi_types` to generate a list of source endpoints for the run window.
    - Fetch data for each endpoint, parse into DataFrames, and concatenate.
    - Add a column like `extracted_at` for lineage/debugging (timestamp of extraction).
    - Prefer append-only in ingestion; handle duplicates in staging.
    """
    # --- Bruin runtime variables ---
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])

    # Generate list of (year, month) tuples between start_date and end_date (inclusive)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    months = []
    current = start.replace(day=1)
    while current <= end:
        months.append((current.year, current.month))
        current += relativedelta(months=1)

    # Fetch parquet files from NYC TLC and concatenate
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    frames = []
    extracted_at = datetime.now(tz=timezone.utc)

    for taxi_type in taxi_types:
        for year, month in months:
            url = f"{base_url}/{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            print(f"Fetching: {url}")
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            df = pd.read_parquet(io.BytesIO(response.content))
            df["taxi_type"] = taxi_type
            df["extracted_at"] = extracted_at
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    final_dataframe = pd.concat(frames, ignore_index=True)

    # Normalize column names to lowercase snake_case
    final_dataframe.columns = (
        final_dataframe.columns
        .str.strip()
        .str.lower()
        .str.replace(r'(?<=[a-z])(?=[A-Z])', '_', regex=True)
        .str.replace(r'[^a-z0-9_]', '_', regex=True)
        .str.replace(r'_+', '_', regex=True)
        .str.strip('_')
    )

    # Explicit renames for columns whose original names don't follow camelCase
    # e.g. PULocationID -> pulocationid (needs to be pu_location_id)
    rename_map = {
        "vendorid": "vendor_id",
        "ratecodeid": "ratecode_id",
        "pulocationid": "pu_location_id",
        "dolocationid": "do_location_id",
    }
    final_dataframe.rename(columns={k: v for k, v in rename_map.items() if k in final_dataframe.columns}, inplace=True)

    # Merge duplicate columns (e.g. airport_fee / Airport_fee both normalize to airport_fee)
    if final_dataframe.columns.duplicated().any():
        # Group duplicate columns by combining with fillna (keep whichever is not null)
        final_dataframe = final_dataframe.T.groupby(level=0).first().T

    # Strip timezone info from timestamp columns (DuckDB expects naive timestamps)
    for col in final_dataframe.select_dtypes(include=["datetimetz"]).columns:
        final_dataframe[col] = final_dataframe[col].dt.tz_localize(None)

    # Convert nullable float columns (caused by NaN in int columns) to pandas nullable Int64
    float_cols_that_should_be_int = [
        "vendor_id", "passenger_count", "ratecode_id", "payment_type",
        "pu_location_id", "do_location_id",
    ]
    for col in float_cols_that_should_be_int:
        if col in final_dataframe.columns:
            final_dataframe[col] = final_dataframe[col].astype("Int64")

    # Ensure monetary columns are float64
    money_cols = [
        "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
        "improvement_surcharge", "total_amount", "congestion_surcharge", "airport_fee",
    ]
    for col in money_cols:
        if col in final_dataframe.columns:
            final_dataframe[col] = final_dataframe[col].astype("float64")

    print(f"Final DataFrame shape: {final_dataframe.shape}")
    print(f"Dtypes:\n{final_dataframe.dtypes}")

    return final_dataframe