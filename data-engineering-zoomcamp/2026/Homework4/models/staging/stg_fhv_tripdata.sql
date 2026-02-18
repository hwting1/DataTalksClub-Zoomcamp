WITH source AS (
    SELECT *
    FROM {{ source('raw','fhv_tripdata') }}
),

renamed AS (
    SELECT
        dispatching_base_num,

        CAST(PUlocationID AS INT64) AS pickup_location_id,
        CAST(DOlocationID AS INT64) AS dropoff_location_id,

        pickup_datetime,
        dropoff_datetime

    FROM source
    WHERE dispatching_base_num IS NOT NULL
)

SELECT * FROM renamed
