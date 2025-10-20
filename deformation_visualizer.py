"""
Deformation Visualizer Module
Creates visualizations for NISAR deformation measurements
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class DeformationVisualizer:
    """Create visualizations for deformation data"""
    
    def __init__(self, config):
        """Initialize visualizer with configuration"""
        self.config = config
        self.plots_dir = Path('plots')
        self.plots_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def create_plots(self, df, results):
        """
        Create all visualizations
        
        Args:
            df: pandas.DataFrame with deformation data
            results: dict with analysis results
        
        Returns:
            list: Paths to created plot files
        """
        plots = []
        
        # Filter high-quality data
        good_data = df[df['coherence'] > 0.7].copy()
        
        # Deformation velocity map
        plots.append(self._plot_deformation_map(good_data, results))
        
        # Velocity distribution
        plots.append(self._plot_velocity_distribution(good_data, results))
        
        # Time series and risk zones
        plots.append(self._plot_risk_assessment(good_data, results))
        
        return plots
    
    def _plot_deformation_map(self, df, results):
        """Create deformation velocity map with geographic context"""
        fig = plt.figure(figsize=(18, 10))
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        
        # Set extent to US West Coast
        ax.set_extent([-125, -93, 25, 50], crs=ccrs.PlateCarree())
        
        # Add geographic features
        ax.add_feature(cfeature.LAND, facecolor='#F5F5DC', alpha=0.3)
        ax.add_feature(cfeature.OCEAN, facecolor='#E8F4F8')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='#333333')
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='#666666', linestyle='--', alpha=0.7)
        ax.add_feature(cfeature.STATES, linewidth=0.3, edgecolor='#888888', alpha=0.5)
        
        # Add gridlines
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        
        # Plot deformation - use diverging colormap (red=subsidence, blue=uplift)
        scatter = ax.scatter(df['longitude'], df['latitude'], 
                           c=df['velocity_mm_year'],  
                           s=60, cmap='RdBu',  # Red-Blue for subsidence-uplift
                           alpha=0.7, edgecolors='black', 
                           linewidth=0.5, zorder=5, transform=ccrs.PlateCarree(),
                           vmin=-25, vmax=10)  # Emphasize subsidence
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax, label='Velocity (mm/year)', 
                           fraction=0.025, pad=0.02, shrink=0.7)
        cbar.ax.tick_params(labelsize=10)
        cbar.ax.text(0.5, 0.02, 'Subsidence', transform=cbar.ax.transAxes, 
                    ha='center', fontsize=9, color='darkred')
        cbar.ax.text(0.5, 0.98, 'Uplift', transform=cbar.ax.transAxes, 
                    ha='center', va='top', fontsize=9, color='darkblue')
        
        # Title
        ax.set_title('NISAR Surface Deformation Monitoring\nInSAR Displacement Velocity Map', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add info box
        risk_level = results['risk_assessment'].split(' - ')[0]
        info_text = f"Risk Level: {risk_level}\n"
        info_text += f"Mean Velocity: {results['mean_velocity']:.1f} mm/year\n"
        info_text += f"Max Subsidence: {results['max_subsidence']:.1f} mm/year\n"
        info_text += f"Critical Points: {results['critical_points']}"
        
        ax.text(0.02, 0.02, info_text, transform=ax.transAxes, 
                fontsize=11, verticalalignment='bottom',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                         edgecolor='darkred', alpha=0.95, linewidth=2))
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'deformation_map_{timestamp}.png'
        plt.savefig(filepath, dpi=200, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filepath
    
    def _plot_velocity_distribution(self, df, results):
        """Create velocity distribution and statistics plots"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        ax1.hist(df['velocity_mm_year'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
        ax1.axvline(results['mean_velocity'], color='red', linestyle='--', linewidth=2, 
                   label=f"Mean: {results['mean_velocity']:.1f} mm/year")
        ax1.axvline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        ax1.set_xlabel('Velocity (mm/year)', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Deformation Velocity Distribution', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot by deformation type
        types = df['deformation_type'].unique()
        data_by_type = [df[df['deformation_type'] == t]['velocity_mm_year'] for t in types]
        ax2.boxplot(data_by_type, labels=types, vert=True)
        ax2.set_ylabel('Velocity (mm/year)', fontsize=11)
        ax2.set_title('Deformation by Type', fontsize=12, fontweight='bold')
        ax2.axhline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'velocity_distribution_{timestamp}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _plot_risk_assessment(self, df, results):
        """Create risk assessment visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Risk zones bar chart
        risk_data = {
            'Normal': len(df[df['velocity_mm_year'].abs() <= 10]),
            'Warning': results['warning_points'],
            'Critical': results['critical_points']
        }
        colors = ['green', 'orange', 'red']
        bars = ax1.bar(risk_data.keys(), risk_data.values(), color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Number of Points', fontsize=11)
        ax1.set_title('Risk Classification', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
        
        # Displacement vs Uncertainty scatter
        ax2.scatter(df['velocity_mm_year'], df['uncertainty_mm'], 
                   c=df['coherence'], cmap='viridis', s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax2.set_xlabel('Velocity (mm/year)', fontsize=11)
        ax2.set_ylabel('Uncertainty (mm)', fontsize=11)
        ax2.set_title('Measurement Quality', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axvline(0, color='gray', linestyle='--', alpha=0.5)
        
        # Add colorbar
        scatter = ax2.scatter(df['velocity_mm_year'], df['uncertainty_mm'], 
                             c=df['coherence'], cmap='viridis', s=50, alpha=0)
        cbar = plt.colorbar(scatter, ax=ax2, label='Coherence')
        cbar.ax.tick_params(labelsize=9)
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'risk_assessment_{timestamp}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
