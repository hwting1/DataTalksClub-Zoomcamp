# Module 4 Homework: Analytics Engineering with dbt

In this homework, we'll use the dbt project in `04-analytics-engineering/taxi_rides_ny/` to transform NYC taxi data and answer questions by querying the models.

## Setup

1. Set up your dbt project following the [setup guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering/setup)
2. Load the Green and Yellow taxi data for 2019-2020 into your warehouse
```SQL
CREATE SCHEMA IF NOT EXISTS `nytaxi`
OPTIONS(location='US');

CREATE SCHEMA IF NOT EXISTS `nytaxi_prod`
OPTIONS(location='US');

CREATE OR REPLACE EXTERNAL TABLE `nytaxi.external_green_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = [
    'gs://dtc-data-lake-hwting/green/green_tripdata_2019-*.parquet',
    'gs://dtc-data-lake-hwting/green/green_tripdata_2020-*.parquet'
  ]
);

CREATE OR REPLACE TABLE `nytaxi.green_tripdata` AS
SELECT *
FROM `nytaxi.external_green_tripdata`;

CREATE OR REPLACE EXTERNAL TABLE `nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = [
    'gs://dtc-data-lake-hwting/yellow/yellow_tripdata_2019-*.parquet',
    'gs://dtc-data-lake-hwting/yellow/yellow_tripdata_2020-*.parquet'
  ]
);

CREATE OR REPLACE TABLE `nytaxi.yellow_tripdata` AS
SELECT *
FROM `nytaxi.external_yellow_tripdata`;
```

3. Run `dbt build --target prod` to create all models and run tests

> **Note:** By default, dbt uses the `dev` target. You must use `--target prod` to build the models in the production dataset, which is required for the homework queries below.

After a successful build, you should have models like `fct_trips`, `dim_zones`, and `fct_monthly_zone_revenue` in your warehouse.

---

### Question 1. dbt Lineage and Execution

Given a dbt project with the following structure:

```
models/
├── staging/
│   ├── stg_green_tripdata.sql
│   └── stg_yellow_tripdata.sql
└── intermediate/
    └── int_trips_unioned.sql (depends on stg_green_tripdata & stg_yellow_tripdata)
```

If you run `dbt run --select int_trips_unioned`, what models will be built?

Answer: `int_trips_unioned` only

---

### Question 2. dbt Tests

You've configured a generic test like this in your `schema.yml`:

```yaml
columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
```

Your model `fct_trips` has been running successfully for months. A new value `6` now appears in the source data.

What happens when you run `dbt test --select fct_trips`?

Answer: dbt will fail the test, returning a non-zero exit code

---

### Question 3. Counting Records in `fct_monthly_zone_revenue`

After running your dbt project, query the `fct_monthly_zone_revenue` model.

What is the count of records in the `fct_monthly_zone_revenue` model?

```SQL
SELECT COUNT(*) 
FROM nytaxi_prod.fct_monthly_zone_revenue;
```

---

### Question 4. Best Performing Zone for Green Taxis (2020)

Using the `fct_monthly_zone_revenue` table, find the pickup zone with the **highest total revenue** (`revenue_monthly_total_amount`) for **Green** taxi trips in 2020.

Which zone had the highest revenue?

```SQL
SELECT
    pickup_zone,
    SUM(revenue_monthly_total_amount) AS total_revenue
FROM `nytaxi_prod.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND revenue_month >= DATE '2020-01-01'
  AND revenue_month <  DATE '2021-01-01'
GROUP BY pickup_zone
ORDER BY total_revenue DESC
LIMIT 5;
```

---

### Question 5. Green Taxi Trip Counts (October 2019)

Using the `fct_monthly_zone_revenue` table, what is the **total number of trips** (`total_monthly_trips`) for Green taxis in October 2019?

```SQL
SELECT
    SUM(total_monthly_trips) AS total_trips
FROM `nytaxi_prod.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND revenue_month = DATE '2019-10-01';
```

---

### Question 6. Build a Staging Model for FHV Data

Create a staging model for the **For-Hire Vehicle (FHV)** trip data for 2019.

1. Load the [FHV trip data for 2019](https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhv) into your data warehouse
2. Create a staging model `stg_fhv_tripdata` with these requirements:
   - Filter out records where `dispatching_base_num IS NULL`
   - Rename fields to match your project's naming conventions (e.g., `PUlocationID` → `pickup_location_id`)

What is the count of records in `stg_fhv_tripdata`?

```SQL
CREATE OR REPLACE EXTERNAL TABLE `nytaxi.external_fhv_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = [
    'gs://dtc-data-lake-hwting/fhv/fhv_tripdata_2019-*.parquet'
  ]
);

CREATE OR REPLACE TABLE `nytaxi.fhv_tripdata` AS
SELECT *
FROM `nytaxi.external_fhv_tripdata`;
```

```bash
dbt run --select stg_fhv_tripdata --target prod
```

```SQL
SELECT COUNT(*)
FROM nytaxi_prod.stg_fhv_tripdata;
```

---

## Submitting the solutions

- Form for submitting: <https://courses.datatalks.club/de-zoomcamp-2026/homework/hw4>