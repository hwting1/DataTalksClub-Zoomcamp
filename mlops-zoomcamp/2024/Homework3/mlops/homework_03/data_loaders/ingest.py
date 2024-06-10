import os
import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader


@data_loader
def ingest_files(**kwargs) -> pd.DataFrame:

    file_path = os.path.join(os.path.dirname(__file__), '..', 'yellow_tripdata_2023-03.parquet')
    df = pd.read_parquet(file_path)
    
    return df
