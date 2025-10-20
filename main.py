#!/usr/bin/env python3
"""
NASA-ISRO NISAR Surface Deformation Monitoring System
Processes SAR data to detect ground movement and subsidence
"""

import os
import sys
from datetime import datetime
import yaml
from pathlib import Path

from sar_processor import NISARProcessor
from deformation_analyzer import DeformationAnalyzer
from deformation_visualizer import DeformationVisualizer


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main execution function"""
    print(f"=== NISAR Deformation Monitoring System ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        config = load_config()
        print(f"Configuration loaded")
        
        # Initialize modules
        processor = NISARProcessor(config['data_sources'])
        analyzer = DeformationAnalyzer(config['analysis'])
        visualizer = DeformationVisualizer(config['visualization'])
        print(f"Modules initialized")
        
        # Process SAR data
        print(f"\nProcessing NISAR SAR data...")
        data = processor.process_latest_data()
        if data is None or len(data) == 0:
            print("No new deformation data available. Waiting for next acquisition.")
            return
        print(f"Data processed: {len(data)} measurement points")
        
        # Analyze deformation
        print(f"\nAnalyzing surface deformation...")
        results = analyzer.analyze(data)
        print(f"Analysis complete")
        print(f"  - Mean displacement: {results['mean_displacement']:.2f} mm/year")
        print(f"  - Active zones: {results['active_deformation_zones']}")
        print(f"  - Risk level: {results['risk_assessment']}")
        
        # Generate visualizations
        print(f"\nGenerating visualizations...")
        plots = visualizer.create_plots(data, results)
        print(f"Visualizations created: {len(plots)} plots")
        
        # Save results
        print(f"\nSaving results...")
        result_file = Path('results') / f"deformation_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        result_file.parent.mkdir(exist_ok=True)
        analyzer.save_results(results, result_file)
        print(f"Results saved to {result_file}")
        
        print(f"\n=== Analysis Complete ===")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
