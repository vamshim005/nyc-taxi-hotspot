# NYC Taxi Hotspot Analysis

[![CI](https://github.com/vamshim005/nyc-taxi-hotspot/actions/workflows/ci.yml/badge.svg)](https://github.com/vamshim005/nyc-taxi-hotspot/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/vamshim005/nyc-taxi-hotspot/branch/main/graph/badge.svg)](https://codecov.io/gh/vamshim005/nyc-taxi-hotspot)
[![Docker Image](https://img.shields.io/docker/pulls/vamshim005/nyc-taxi-hotspot.svg)](https://hub.docker.com/r/vamshim005/nyc-taxi-hotspot)

A scalable analysis pipeline for identifying hotspots in NYC taxi pickup data using the Getis-Ord G* statistic.

## Features :

- **Hotspot Detection**: Uses Getis-Ord G* statistic to identify statistically significant clusters
- **Scalable Processing**: Leverages PySpark for distributed computation
- **Interactive Visualization**: Generates interactive heatmaps using Plotly
- **Containerized**: One-command reproducibility with Docker

## Quick Start

```bash
# Install dependencies
make install

# Download sample data
make download-data

# Run analysis
make run
```

## Data

The project uses NYC Taxi Trip data. Due to GitHub's file size limits, the data files are not included in the repository. You can download them using:

```bash
# Development dataset (1 month)
make download-data

# Full dataset (1 year)
wget -O data/yellow_tripdata_2009-*.parquet \
    https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2009-{01..12}.parquet
```

## Performance

The analysis pipeline is optimized for large-scale data processing:

| Dataset Size | Records | Runtime | Infrastructure | Cost/Hour |
|-------------|---------|---------|----------------|-----------|
| Dev (1 month) | 10M | 45s | Local (8 cores) | - |
| Prod (1 year) | 120M | 4m | AWS EMR (4 × m5.xlarge) | $0.77 |

Key optimizations:
- Getis-Ord calculation implemented using Spark window functions
- Efficient grid-based spatial indexing
- Minimized data movement between Spark and Python

## Architecture

```
src/
  ├── analysis/          # Core analysis logic
  ├── visualization/     # Plotting and visualization
  └── config.py         # Configuration management

tests/                  # Unit tests
data/                  # Input data directory
results/               # Analysis outputs
```

## Development

```bash
# Run tests
make test

# Build Docker image
make build

# Clean up
make clean
```

## Results

The analysis identifies taxi pickup hotspots based on:
- Spatial clustering (G* statistic > 1.96, p < 0.05)
- Minimum trip threshold (10 pickups/cell)
- Adaptive grid size (0.01° ≈ 1.1km)

Example hotspots include:
- Manhattan Downtown (G* = 19.65)
- JFK Airport (G* = 14.18)
- LaGuardia Airport (G* = 12.93)

## Example Hotspot Heatmap

[View Interactive NYC Taxi Hotspot Heatmap](results/hotspots_map.html)

## License

MIT 