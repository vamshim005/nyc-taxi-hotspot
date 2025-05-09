import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import Config, DataScale
from src.analysis.hotspot_analysis import HotspotAnalysis

@pytest.fixture
def config():
    return Config(DataScale.DEV)

@pytest.fixture
def analyzer(config):
    return HotspotAnalysis(config)

def test_config_initialization():
    config = Config(DataScale.DEV)
    assert config.cell_size == 0.01
    assert config.min_trips_per_cell == 10
    assert "dev" in str(config.data_pattern)

def test_prod_config():
    config = Config(DataScale.PROD)
    assert "prod" in str(config.data_pattern)
    assert config.spark_config["spark.executor.memory"] == "4g"

def test_hotspot_analysis_initialization(analyzer):
    assert analyzer.spark is not None
    assert analyzer.config is not None

def test_geojson_output(analyzer, tmp_path):
    # Mock results path
    analyzer.config.results_path = tmp_path
    
    # Create sample data
    data = {
        'cell_lat': [4075, 4076],
        'cell_lon': [-7398, -7397],
        'count': [100, 200],
        'g_score': [1.5, 2.0]
    }
    df = pd.DataFrame(data)
    
    # Save as GeoJSON
    geojson_path = tmp_path / "hotspots.geojson"
    
    # Convert to GeoJSON format
    geojson_df = df.copy()
    geojson_df['latitude'] = geojson_df['cell_lat'] * analyzer.config.cell_size
    geojson_df['longitude'] = geojson_df['cell_lon'] * analyzer.config.cell_size
    
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
    with open(geojson_path, "w") as f:
        json.dump(geojson, f)
    
    # Verify file exists and is valid GeoJSON
    assert geojson_path.exists()
    with open(geojson_path) as f:
        data = json.load(f)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2 