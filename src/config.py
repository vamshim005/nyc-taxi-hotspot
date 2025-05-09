from enum import Enum
from pathlib import Path

class DataScale(Enum):
    DEV = "dev"  # Single month for development
    PROD = "prod"  # Full year for production

class Config:
    def __init__(self, scale: DataScale = DataScale.DEV):
        self.scale = scale
        self.base_path = Path("data")
        
        # Data paths
        self.raw_data_path = self.base_path
        self.processed_data_path = self.base_path
        self.results_path = Path("results")
        
        # Create necessary directories
        self.results_path.mkdir(exist_ok=True)
        
        # Data patterns
        if scale == DataScale.DEV:
            self.data_pattern = "yellow_tripdata_2009-01.parquet"
        else:
            self.data_pattern = "yellow_tripdata_2009-*.parquet"
        
        # Spark configurations
        self.spark_config = {
            "spark.sql.parquet.compression.codec": "snappy",
            "spark.sql.shuffle.partitions": "200" if scale == DataScale.PROD else "20",
            "spark.executor.memory": "4g" if scale == DataScale.PROD else "2g",
            "spark.driver.memory": "4g" if scale == DataScale.PROD else "2g"
        }
        
        # Analysis parameters
        self.cell_size = 0.01  # degrees
        self.time_step = 1  # days
        self.min_trips_per_cell = 10  # minimum trips for statistical significance 