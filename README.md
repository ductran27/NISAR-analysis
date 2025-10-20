# NASA-ISRO NISAR Surface Deformation Monitoring

Automated system for monitoring surface deformation and land changes using NASA-ISRO NISAR Synthetic Aperture Radar (SAR) data. Tracks ground movement, subsidence, and structural changes for disaster response and infrastructure monitoring.

## Overview

This project analyzes NISAR L-band SAR data to detect and monitor surface deformation patterns. The system processes interferometric SAR (InSAR) observations to identify ground movement, subsidence events, and potential hazard zones.

## Mission Background

NISAR (NASA-ISRO Synthetic Aperture Radar) is a joint Earth observation mission launching in 2024:
- Dual-frequency SAR (L-band and S-band)
- 12-day repeat cycle global coverage
- Applications: Earthquakes, volcanoes, landslides, subsidence, infrastructure monitoring

## Features

The system provides:
- Surface deformation rate analysis
- Temporal change detection
- Displacement time series
- Risk zone identification
- Visual change maps

## Data Processing

Processes:
- SAR amplitude analysis
- Coherence mapping
- Displacement calculation
- Time series generation
- Statistical change detection

## Automated Updates

GitHub Actions workflow runs daily to:
- Check for new NISAR data
- Process displacement measurements
- Generate deformation maps
- Update analysis results
- Commit findings automatically

## Output

Generated files:
- `data/` - SAR observations
- `results/` - Deformation analysis (JSON)
- `plots/` - Displacement maps and time series
- `maps/` - Geographic distribution of changes

## Applications

Monitoring for:
- Earthquake-induced ground motion
- Volcanic deformation
- Landslide susceptibility
- Ground subsidence (aquifer depletion, mining)
- Infrastructure stability

## Notes

Focuses on surface deformation monitoring for disaster preparedness and infrastructure management. Uses SAR remote sensing for all-weather, day-night observation capability.
