import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import os

def load_data():
    """Load analysis results"""
    try:
        hot_cells = pd.read_csv('results/hot_cells.csv')
        hot_zones = pd.read_csv('results/hot_zones.csv')
        return hot_cells, hot_zones
    except FileNotFoundError:
        st.warning("No analysis results found. Please run the analysis first.")
        return None, None

def create_heatmap(hot_cells):
    """Create a heatmap of hot cells"""
    fig = px.density_heatmap(
        hot_cells,
        x='cell_lon',
        y='cell_lat',
        z='g_score',
        color_continuous_scale='Viridis',
        title='NYC Taxi Hotspots Heatmap'
    )
    
    fig.update_layout(
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        mapbox_style="carto-positron"
    )
    
    return fig

def create_zone_map(hot_zones):
    """Create a map with hot zones"""
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)
    
    for _, row in hot_zones.iterrows():
        folium.Rectangle(
            bounds=[[row['min_lat'], row['min_lon']], 
                   [row['max_lat'], row['max_lon']]],
            color='red' if row['z_score'] > 1.96 else 'blue',
            fill=True,
            popup=f"Zone {row['zone_id']}: Z-score = {row['z_score']:.2f}"
        ).add_to(m)
    
    return m

def main():
    st.title("NYC Taxi Hotspot Analysis")
    
    # Sidebar
    st.sidebar.title("Analysis Options")
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["Hot Cells", "Hot Zones"]
    )
    
    # Load data
    hot_cells, hot_zones = load_data()
    
    if analysis_type == "Hot Cells" and hot_cells is not None:
        st.header("Hot Cell Analysis")
        
        # Display heatmap
        st.plotly_chart(create_heatmap(hot_cells))
        
        # Display statistics
        st.subheader("Top Hotspots")
        st.dataframe(hot_cells.nlargest(10, 'g_score'))
        
        # Display distribution
        st.subheader("G-score Distribution")
        fig = px.histogram(hot_cells, x='g_score', title='Distribution of G-scores')
        st.plotly_chart(fig)
        
    elif analysis_type == "Hot Zones" and hot_zones is not None:
        st.header("Hot Zone Analysis")
        
        # Display zone map
        st.subheader("Hot Zones Map")
        folium_static(create_zone_map(hot_zones))
        
        # Display statistics
        st.subheader("Zone Statistics")
        st.dataframe(hot_zones.sort_values('z_score', ascending=False))
        
        # Display distribution
        st.subheader("Z-score Distribution")
        fig = px.histogram(hot_zones, x='z_score', title='Distribution of Z-scores')
        st.plotly_chart(fig)

if __name__ == "__main__":
    main() 