"""
Deformation Analyzer Module
Analyzes surface deformation from NISAR InSAR measurements
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path


class DeformationAnalyzer:
    """Analyze surface deformation patterns from InSAR data"""
    
    def __init__(self, config):
        """Initialize analyzer with configuration"""
        self.config = config
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Thresholds for risk assessment
        self.critical_rate = config.get('critical_rate_mm_year', 20)
        self.warning_rate = config.get('warning_rate_mm_year', 10)
    
    def analyze(self, df):
        """
        Perform comprehensive deformation analysis
        
        Args:
            df: pandas.DataFrame with InSAR measurements
        
        Returns:
            dict: Analysis results
        """
        results = {}
        
        # Filter high-quality measurements
        good_data = df[df['coherence'] > 0.7].copy()
        
        # Basic statistics
        results['total_points'] = len(df)
        results['high_quality_points'] = len(good_data)
        results['mean_displacement'] = float(good_data['displacement_mm'].mean())
        results['mean_velocity'] = float(good_data['velocity_mm_year'].mean())
        results['std_velocity'] = float(good_data['velocity_mm_year'].std())
        results['max_subsidence'] = float(good_data['velocity_mm_year'].min())
        results['max_uplift'] = float(good_data['velocity_mm_year'].max())
        
        # Deformation rate distribution
        results['velocity_percentiles'] = {
            '10th': float(good_data['velocity_mm_year'].quantile(0.10)),
            '25th': float(good_data['velocity_mm_year'].quantile(0.25)),
            '50th': float(good_data['velocity_mm_year'].quantile(0.50)),
            '75th': float(good_data['velocity_mm_year'].quantile(0.75)),
            '90th': float(good_data['velocity_mm_year'].quantile(0.90))
        }
        
        # Risk assessment
        results['risk_assessment'] = self._assess_risk(good_data)
        results['critical_points'] = int((good_data['velocity_mm_year'].abs() > self.critical_rate).sum())
        results['warning_points'] = int(((good_data['velocity_mm_year'].abs() > self.warning_rate) & 
                                        (good_data['velocity_mm_year'].abs() <= self.critical_rate)).sum())
        
        # Active deformation zones
        results['active_deformation_zones'] = self._identify_active_zones(good_data)
        
        # Deformation by type
        results['deformation_by_type'] = good_data.groupby('deformation_type')['velocity_mm_year'].agg([
            ('mean', 'mean'),
            ('count', 'count')
        ]).to_dict()
        
        # Spatial statistics
        results['spatial_extent'] = {
            'lon_range': [float(good_data['longitude'].min()), float(good_data['longitude'].max())],
            'lat_range': [float(good_data['latitude'].min()), float(good_data['latitude'].max())],
            'centroid': [float(good_data['longitude'].mean()), float(good_data['latitude'].mean())]
        }
        
        # Summary message
        results['summary'] = self._generate_summary(results)
        
        # Metadata
        results['analysis_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        results['observation_period_days'] = 180
        
        return results
    
    def _assess_risk(self, df):
        """Assess overall deformation risk level"""
        max_abs_rate = df['velocity_mm_year'].abs().max()
        
        if max_abs_rate > self.critical_rate:
            return 'HIGH - Critical deformation detected'
        elif max_abs_rate > self.warning_rate:
            return 'MODERATE - Significant deformation observed'
        else:
            return 'LOW - Normal deformation levels'
    
    def _identify_active_zones(self, df):
        """Identify zones with significant deformation"""
        zones = df.groupby('zone_name').agg({
            'velocity_mm_year': ['mean', 'min', 'max', 'count']
        }).round(2)
        
        active_zones = []
        for zone_name in zones.index:
            mean_vel = zones.loc[zone_name, ('velocity_mm_year', 'mean')]
            if abs(mean_vel) > self.warning_rate:
                active_zones.append({
                    'name': zone_name,
                    'mean_velocity': float(mean_vel),
                    'status': 'Active'
                })
        
        return active_zones
    
    def _generate_summary(self, results):
        """Generate human-readable summary"""
        risk = results['risk_assessment'].split(' - ')[0]
        mean_vel = results['mean_velocity']
        critical = results['critical_points']
        
        summary = f"Risk: {risk}, Mean velocity: {mean_vel:.1f} mm/year"
        if critical > 0:
            summary += f", {critical} critical points"
        
        return summary
    
    def save_results(self, results, filepath):
        """Save analysis results to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
