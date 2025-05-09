import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path

def plot_hotspots(results_path: Path):
    """Plot hotspots on a map of NYC"""
    # Read the hotspots data
    df = pd.read_csv(results_path / "hot_cells.csv")
    
    # Convert grid cells back to lat/lon
    cell_size = 0.01  # This should match the config
    df['latitude'] = df['cell_lat'] * cell_size
    df['longitude'] = df['cell_lon'] * cell_size
    
    # Create the map
    fig = px.scatter_mapbox(df,
                           lat='latitude',
                           lon='longitude',
                           size='count',  # Size points by number of pickups
                           color='g_score',  # Color points by G* score
                           hover_data=['count', 'g_score'],
                           zoom=10,
                           title='NYC Taxi Pickup Hotspots',
                           mapbox_style='carto-positron')
    
    # Update layout
    fig.update_layout(
        title_x=0.5,
        margin={"r":0,"t":30,"l":0,"b":0},
        mapbox=dict(
            center=dict(lat=40.7128, lon=-74.0060),  # NYC coordinates
        )
    )
    
    # Save the plot
    fig.write_html(results_path / "hotspots_map.html")
    print(f"Map saved to {results_path / 'hotspots_map.html'}")
    
def analyze_results(results_path: Path):
    """Analyze and print summary statistics of the hotspots"""
    df = pd.read_csv(results_path / "hot_cells.csv")
    
    print("\nHotspot Analysis Summary:")
    print("-" * 50)
    print(f"Total number of hotspots: {len(df)}")
    print(f"Total pickups in hotspots: {df['count'].sum():,}")
    print(f"\nG* Score Statistics:")
    print(f"  Min: {df['g_score'].min():.2f}")
    print(f"  Max: {df['g_score'].max():.2f}")
    print(f"  Mean: {df['g_score'].mean():.2f}")
    print(f"\nPickups per Cell Statistics:")
    print(f"  Min: {df['count'].min():,}")
    print(f"  Max: {df['count'].max():,}")
    print(f"  Mean: {df['count'].mean():,.0f}") 