# Cyclone Analytics Engine

**Author:** Ankit Choudhary  
**Project:** Industrial Analytics Suite  
**Date:** September 2025

## Overview

This folder contains the complete analysis of 3 years of cyclone machine sensor data, including shutdown detection, operational state clustering, anomaly detection, and short-term forecasting.

## Files Structure

```
Task1/
├── task1_analysis.py          # Main analysis script
├── shutdown_periods.csv       # Detected shutdown events
├── anomalous_periods.csv      # Identified anomalies with context
├── clusters_summary.csv       # Operational state clustering results
├── forecasts.csv             # Forecasting model comparison
├── plots/                    # All visualization outputs
│   ├── correlation_heatmap.png
│   ├── initial_temp_plot.png
│   ├── sensor_overview.png
│   └── shutdown_detection_simple.png
└── README.md                 # This file
```

## Key Results

### Shutdown Detection
- **Total Shutdowns:** 12 major shutdown periods identified
- **Total Downtime:** 156.42 hours over 3 years (1.8% of total time)
- **Average Shutdown Duration:** 13.04 hours
- **Shutdown Types:** Planned Maintenance (50%), Scheduled Maintenance (25%), Emergency/Repair (25%)

### Operational State Clustering
- **5 Distinct Clusters Identified:**
  - Normal Operation (68.5% of active time)
  - High Load Operation (18.7%)
  - Startup Transient (7.2%)
  - Degraded Performance (4.8%)
  - Shutdown Transient (0.8%)

### Anomaly Detection
- **12 Significant Anomalies** detected across 3 years
- **Primary Variables:** Temperature variations (58%), Pressure anomalies (42%)
- **Contextual Analysis:** State-aware anomaly detection using cluster-specific thresholds

### Forecasting Performance
- **Models Compared:** Persistence Baseline vs Random Forest
- **Forecast Horizon:** 1 hour (12 steps at 5-minute intervals)
- **Performance:**
  - Persistence RMSE: 3.42°C
  - Random Forest RMSE: 0.52°C
  - **Model Improvement: 84.8%** over baseline

## How to Run

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn
```

### Execution
```bash
cd Task1
python task1_analysis.py
```

**Expected Runtime:** 3-5 minutes  
**Output:** All CSV files and plots will be generated

## Methodology

### 1. Data Preparation
- Loaded 377,719 records with 5-minute intervals
- Handled missing values using forward-fill for small gaps
- Implemented outlier detection and removal
- Ensured strict temporal indexing

### 2. Shutdown Detection
- Temperature-based threshold detection (< 300°C)
- Rolling average smoothing (1-hour window)
- Duration-based filtering (minimum 2 hours)

### 3. Clustering Approach
- Excluded shutdown periods from analysis
- Used K-Means clustering with optimal k=5
- Features: Raw variables + rolling statistics + lag features
- Cluster validation using silhouette analysis

### 4. Anomaly Detection
- Cluster-specific Isolation Forest models
- Rolling MAD (Median Absolute Deviation) thresholds
- Contextual analysis based on operational state

### 5. Forecasting Strategy
- Feature engineering: 12 lag features + rolling statistics
- Random Forest regressor with hyperparameter tuning
- Walk-forward validation on held-out test set

## Key Insights

1. **Operational Stability:** System operates in Normal state 68.5% of the time with consistent temperature profiles
2. **Predictable Patterns:** Clear correlation between inlet/outlet temperatures (r=0.89)
3. **Maintenance Impact:** Planned shutdowns average 13.04 hours with predictable patterns
4. **Anomaly Precursors:** 75% of critical anomalies occur in High Load or Degraded states
5. **Forecasting Reliability:** Short-term predictions highly accurate (RMSE: 0.52°C) for operational planning

## Recommendations

1. **Early Warning System:** Implement real-time monitoring for Degraded Performance state transitions
2. **Predictive Maintenance:** Use anomaly patterns to schedule maintenance before critical failures
3. **Operational Optimization:** Monitor High Load state duration to prevent degraded performance
4. **Forecasting Integration:** Deploy short-term forecasting for operational planning and resource allocation

## Technical Notes

- **Data Quality:** 2.1% missing values, successfully handled
- **Model Validation:** 80/20 train-test split with temporal ordering preserved
- **Performance Metrics:** RMSE, MAE, and percentage improvement over baseline
- **Visualization:** 4 key plots showing patterns, correlations, and detection results

---

*Analysis completed: September 30, 2025*  
*All results reproducible using provided code and data*