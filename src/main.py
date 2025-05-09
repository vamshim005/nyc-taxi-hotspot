import argparse
from pathlib import Path
from src.config import Config, DataScale
from src.analysis.hotspot_analysis import HotspotAnalysis
from src.visualization.plot_hotspots import plot_hotspots, analyze_results

def main():
    parser = argparse.ArgumentParser(description='NYC Taxi Hotspot Analysis')
    parser.add_argument('--scale', choices=['dev', 'prod'], default='dev',
                      help='Analysis scale: dev (1 month) or prod (full year)')
    parser.add_argument('--zone-file', type=str, default='data/nyc_zones.csv',
                      help='Path to zone definition file')
    parser.add_argument('--no-plot', action='store_true',
                      help='Skip plotting the results')
    args = parser.parse_args()

    # Initialize configuration
    scale = DataScale.DEV if args.scale == 'dev' else DataScale.PROD
    config = Config(scale)
    
    # Initialize analysis
    analyzer = HotspotAnalysis(config)
    
    # Run hot cell analysis
    print("Running hot cell analysis...")
    hot_cells = analyzer.analyze_hot_cells()
    print(f"Found {len(hot_cells)} significant hot cells")
    
    # Run hot zone analysis
    print("\nRunning hot zone analysis...")
    hot_zones = analyzer.analyze_hot_zones(args.zone_file)
    print(f"Analyzed {len(hot_zones)} zones")
    
    # Analyze results
    analyze_results(config.results_path)
    
    # Plot results
    if not args.no_plot:
        print("\nGenerating visualization...")
        plot_hotspots(config.results_path)
    
    print("\nAnalysis complete! Results saved in the results/ directory")

if __name__ == "__main__":
    main() 