# Module 3 Homework: Data Warehousing & BigQuery

In this homework we'll practice working with BigQuery and Google Cloud Storage.

When submitting your homework, you will also need to include
a link to your GitHub repository or other public code-hosting
site.

This repository should contain the code for solving the homework.

When your solution has SQL or shell commands and not code
(e.g. python files) file format, include them directly in
the README file of your repository.

## Data

For this homework we will be using the Yellow Taxi Trip Records for January 2024 - June 2024 (not the entire year of data).

Parquet Files are available from the New York City Taxi Data found here:

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Loading the data

You can use the following scripts to load the data into your GCS bucket:

- Python script: [load_yellow_taxi_data.py](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/03-data-warehouse/load_yellow_taxi_data.py)
- Jupyter notebook with DLT: [DLT_upload_to_GCP.ipynb](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/03-data-warehouse/DLT_upload_to_GCP.ipynb)

You will need to generate a Service Account with GCS Admin privileges or be authenticated with the Google SDK, and update the bucket name in the script.

If you are using orchestration tools such as Kestra, Mage, Airflow, or Prefect, do not load the data into BigQuery using the orchestrator.

Make sure that all 6 files show in your GCS bucket before beginning.

Note: You will need to use the PARQUET option when creating an external table.


## BigQuery Setup

Create an external table using the Yellow Taxi Trip Records. 

Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table). 
```SQL
CREATE SCHEMA IF NOT EXISTS `taxi_dataset`
OPTIONS(location='US');

CREATE OR REPLACE EXTERNAL TABLE `taxi_dataset.yellow_taxi_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dezoomcamp_hw3_hwting/yellow_tripdata_2024-*.parquet']
);

CREATE OR REPLACE TABLE taxi_dataset.yellow_taxi
AS
SELECT * FROM taxi_dataset.yellow_taxi_external;
```



## Question 1. Counting records

What is count of records for the 2024 Yellow Taxi Data?
```SQL
SELECT COUNT(*) AS cnt
FROM `taxi_dataset.yellow_taxi`;
```

## Question 2. Data read estimation

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
 
What is the **estimated amount** of data that will be read when this query is executed on the External Table and the Table?
```SQL
-- External Table 
SELECT COUNT(DISTINCT PULocationID) AS distinct_pu
FROM `taxi_dataset.yellow_taxi_external`;

-- Materialized Table
SELECT COUNT(DISTINCT PULocationID) AS distinct_pu
FROM `taxi_dataset.yellow_taxi`;
```

## Question 3. Understanding columnar storage

Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table.

Why are the estimated number of Bytes different?
```SQL
SELECT PULocationID
FROM `taxi_dataset.yellow_taxi`;

SELECT PULocationID, DOLocationID
FROM `taxi_dataset.yellow_taxi`;

```
Answer: BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (`PULocationID`, `DOLocationID`) requires

## Question 4. Counting zero fare trips

How many records have a fare_amount of 0?
```SQL
SELECT COUNT(*) AS zero_fare_cnt
FROM `taxi_dataset.yellow_taxi`
WHERE fare_amount = 0;
```

## Question 5. Partitioning and clustering

What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)
```SQL
CREATE OR REPLACE TABLE `taxi_dataset.yellow_taxi_part_clust`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT *
FROM `taxi_dataset.yellow_taxi`;
```
Answer: Partition by `tpep_dropoff_datetime` and Cluster on `VendorID`

## Question 6. Partition benefits

Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime
2024-03-01 and 2024-03-15 (inclusive)


Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values? 

 ```SQL
SELECT DISTINCT VendorID
FROM `taxi_dataset.yellow_taxi`
WHERE tpep_dropoff_datetime >= '2024-03-01'
  AND tpep_dropoff_datetime <  '2024-03-16';

SELECT DISTINCT VendorID
FROM `taxi_dataset.yellow_taxi_part_clust`
WHERE tpep_dropoff_datetime >= '2024-03-01'
  AND tpep_dropoff_datetime <  '2024-03-16';
 ```

## Question 7. External table storage

Where is the data stored in the External Table you created?

Answer: GCP Bucket

## Question 8. Clustering best practices

It is best practice in Big Query to always cluster your data:

Answer: False

## Question 9. Understanding table scans

No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?
```SQL
SELECT COUNT(*) AS cnt
FROM `taxi_dataset.yellow_taxi`;
```
Answer: 0MB, because it gets the row count from the table metadata without scanning the data.


## Submitting the solutions

Form for submitting: https://courses.datatalks.club/de-zoomcamp-2026/homework/hw3