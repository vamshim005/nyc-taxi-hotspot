from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, expr, sum, avg, stddev, sqrt, count, lit
from pyspark.sql.types import DoubleType, StructType, StructField, StringType
import numpy as np
from scipy import stats
import pandas as pd
from src.config import Config, DataScale

class HotspotAnalysis:
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize Spark with appropriate configurations
        self.spark = SparkSession.builder \
            .appName("HotspotAnalysis") \
            .config("spark.sql.parquet.compression.codec", "snappy") \
            .config("spark.sql.shuffle.partitions", config.spark_config["spark.sql.shuffle.partitions"]) \
            .config("spark.executor.memory", config.spark_config["spark.executor.memory"]) \
            .config("spark.driver.memory", config.spark_config["spark.driver.memory"]) \
            .getOrCreate()
        
    def _create_grid_cell(self, lat, lon):
        """Create grid cell coordinates based on lat/lon"""
        cell_lat = int(lat / self.config.cell_size)
        cell_lon = int(lon / self.config.cell_size)
        return cell_lat, cell_lon
    
    def _calculate_getis_ord(self, values, weights):
        """Calculate Getis-Ord G* statistic"""
        n = len(values)
        if n < 2:
            return 0.0
            
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return 0.0
            
        weighted_sum = np.sum(values * weights)
        sum_weights = np.sum(weights)
        
        # Calculate G* statistic
        g_star = (weighted_sum - mean * sum_weights) / (std * np.sqrt((n * sum_weights - sum_weights**2) / (n - 1)))
        return float(g_star)
    
    def analyze_hot_cells(self):
        """Perform hot cell analysis on taxi trip data using Spark window functions"""
        # Read Parquet data
        df = self.spark.read.parquet(str(self.config.raw_data_path / self.config.data_pattern))
        
        # Create grid cells
        df = df.withColumn("cell_lat", expr(f"CAST(Start_Lat / {self.config.cell_size} AS INT)")) \
             .withColumn("cell_lon", expr(f"CAST(Start_Lon / {self.config.cell_size} AS INT)"))
        
        # Group by cell and count
        cell_counts = df.groupBy("cell_lat", "cell_lon").count() \
            .filter(col("count") >= self.config.min_trips_per_cell)
        
        # Define window for neighboring cells (1 cell radius)
        neighbors_window = Window.partitionBy() \
            .orderBy("cell_lat", "cell_lon") \
            .rangeBetween(-1, 1)
        
        # Calculate Getis-Ord G* statistic components
        stats_df = cell_counts \
            .withColumn("n", count("count").over(neighbors_window)) \
            .withColumn("weighted_sum", sum("count").over(neighbors_window)) \
            .withColumn("mean", avg("count").over(Window.partitionBy())) \
            .withColumn("std", stddev("count").over(Window.partitionBy())) \
            .withColumn("sum_weights", lit(9.0))  # 3x3 grid, all weights = 1
        
        # Calculate G* statistic
        g_star_df = stats_df.withColumn(
            "g_score",
            (col("weighted_sum") - col("mean") * col("sum_weights")) / 
            (col("std") * sqrt(
                (col("n") * col("sum_weights") - col("sum_weights") * col("sum_weights")) / 
                (col("n") - lit(1.0))
            ))
        )
        
        # Get top 50 hotspots
        top_hotspots = g_star_df.orderBy(col("g_score").desc()).limit(50)
        
        # Convert to pandas for saving (small dataset now)
        pdf = top_hotspots.toPandas()
        
        # Save results
        output_path = self.config.results_path / "hot_cells.csv"
        pdf.to_csv(output_path, index=False)
        
        # Also save as GeoJSON for visualization
        geojson_df = pdf.copy()
        geojson_df['latitude'] = geojson_df['cell_lat'] * self.config.cell_size
        geojson_df['longitude'] = geojson_df['cell_lon'] * self.config.cell_size
        
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row['longitude'], row['latitude']]
                    },
                    "properties": {
                        "count": int(row['count']),
                        "g_score": float(row['g_score'])
                    }
                }
                for _, row in geojson_df.iterrows()
            ]
        }
        
        import json
        with open(self.config.results_path / "hotspots.geojson", "w") as f:
            json.dump(geojson, f)
        
        return pdf
    
    def analyze_hot_zones(self, zone_path):
        """Perform hot zone analysis using predefined zones"""
        # Read Parquet data
        df = self.spark.read.parquet(str(self.config.raw_data_path / self.config.data_pattern))
        zones = self.spark.read.csv(zone_path, header=True, inferSchema=True)
        
        # Join data with zones
        joined_df = df.crossJoin(zones).filter(
            (col("Start_Lat") >= col("min_lat")) &
            (col("Start_Lat") <= col("max_lat")) &
            (col("Start_Lon") >= col("min_lon")) &
            (col("Start_Lon") <= col("max_lon"))
        )
        
        # Group by zone and count
        zone_counts = joined_df.groupBy("zone_id", "zone_name", "area").count()
        
        # Convert to pandas for analysis
        pdf = zone_counts.toPandas()
        
        # Calculate zone statistics
        pdf['density'] = pdf['count'] / pdf['area']
        pdf['z_score'] = stats.zscore(pdf['density'])
        
        # Sort by density
        pdf = pdf.sort_values('density', ascending=False)
        
        # Save results
        output_path = self.config.results_path / "hot_zones.csv"
        pdf.to_csv(output_path, index=False)
        
        # Print top zones
        print("\nTop 5 Hot Zones:")
        print("-" * 50)
        for _, row in pdf.head().iterrows():
            print(f"{row['zone_name']}:")
            print(f"  Pickups: {row['count']:,}")
            print(f"  Density: {row['density']:,.1f} pickups/sq km")
            print(f"  Z-score: {row['z_score']:.2f}")
            print()
        
        return pdf 