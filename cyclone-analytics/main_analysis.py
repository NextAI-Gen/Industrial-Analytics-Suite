#!/usr/bin/env python3
"""
Cyclone Analysis - Version 2 (Improved after initial exploration)
Author: [Your Name]
Date: Sep 29, 2025

After my first attempt, I realized I need to be more systematic.
This version focuses on proper data cleaning and exploration.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set up plotting style - I like this better than default
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class CycloneAnalyzer:
    """
    My approach to analyzing cyclone sensor data.
    
    I'm organizing this as a class because I think it'll be easier
    to keep track of everything.
    """
    
    def __init__(self, data_file):
        print(f"Initializing analyzer with {data_file}")
        self.data_file = data_file
        self.df = None
        self.clean_df = None
        
    def load_data(self):
        """Load and do basic validation of the data"""
        print("Loading data...")
        
        # I learned from v1 that this works
        self.df = pd.read_excel(self.data_file)
        print(f"Loaded {len(self.df)} records")
        
        # Convert time column 
        self.df['time'] = pd.to_datetime(self.df['time'])
        
        # Set time as index - this makes time series work easier
        self.df.set_index('time', inplace=True)
        
        return self.df
    
    def explore_data(self):
        """Do more thorough exploration than v1"""
        print("=== Data Exploration ===")
        
        print(f"Dataset shape: {self.df.shape}")
        print(f"Time range: {self.df.index.min()} to {self.df.index.max()}")
        
        # Check missing values more carefully
        missing_info = self.df.isnull().sum()
        print("\nMissing values per column:")
        for col, missing in missing_info.items():
            pct_missing = (missing / len(self.df)) * 100
            print(f"  {col}: {missing} ({pct_missing:.1f}%)")
        
        # Basic stats
        print("\nBasic statistics:")
        print(self.df.describe())
        
        # Check for any obvious outliers or weird values
        print("\nLooking for unusual values:")
        for col in self.df.columns:
            if self.df[col].dtype in ['float64', 'int64']:
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                print(f"  {col}: min={min_val:.2f}, max={max_val:.2f}")
                
                # Flag potentially suspicious values
                if min_val < -1000 or max_val > 2000:
                    print(f"    ^ This seems unusual for {col}")
    
    def clean_data(self):
        """
        Clean the data based on what I learned from exploration
        
        I'm being conservative - only removing obviously bad data
        UPDATE: Had to fix data type issues - the columns are stored as strings!
        """
        print("=== Data Cleaning ===")
        
        # Start with a copy
        self.clean_df = self.df.copy()
        
        # First, I need to convert string columns to numeric
        # I discovered the sensor data is stored as strings, not numbers!
        print("Converting string columns to numeric...")
        sensor_cols = ['Cyclone_Inlet_Gas_Temp', 'Cyclone_Material_Temp', 
                      'Cyclone_Outlet_Gas_draft', 'Cyclone_cone_draft',
                      'Cyclone_Gas_Outlet_Temp', 'Cyclone_Inlet_Draft']
        
        for col in sensor_cols:
            # Convert to numeric, setting errors to NaN
            self.clean_df[col] = pd.to_numeric(self.clean_df[col], errors='coerce')
            print(f"  Converted {col} to numeric")
        
        # Handle missing values (now properly as NaN)
        print("Handling missing values...")
        missing_counts = self.clean_df.isnull().sum()
        print("Missing values after conversion:")
        for col, missing in missing_counts.items():
            if missing > 0:
                pct_missing = (missing / len(self.clean_df)) * 100
                print(f"  {col}: {missing} ({pct_missing:.1f}%)")
        
        # Forward fill small gaps only
        for col in sensor_cols:
            self.clean_df[col] = self.clean_df[col].ffill(limit=2)
        
        # Remove obvious outliers (negative temperatures don't make sense)
        temp_cols = [col for col in sensor_cols if 'Temp' in col]
        for col in temp_cols:
            before_count = len(self.clean_df)
            # Remove negative temperatures - these are clearly errors
            self.clean_df = self.clean_df[self.clean_df[col] >= 0]
            after_count = len(self.clean_df)
            if before_count != after_count:
                print(f"  Removed {before_count - after_count} negative values from {col}")
        
        print(f"Clean dataset: {len(self.clean_df)} records")
        return self.clean_df
    
    def make_basic_plots(self):
        """Create some basic visualizations to understand the data"""
        print("=== Creating Basic Plots ===")
        
        # Plot all sensors over time (sample period)
        sample_data = self.clean_df.iloc[:5000]  # First ~17 hours
        
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Cyclone Sensor Data - Sample Period (First 17 hours)')
        
        axes = axes.flatten()
        for i, col in enumerate(self.clean_df.columns):
            axes[i].plot(sample_data.index, sample_data[col], alpha=0.8)
            axes[i].set_title(col)
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('sensor_overview.png', dpi=150, bbox_inches='tight')
        print("Saved sensor_overview.png")
        
        # Correlation heatmap - always useful
        plt.figure(figsize=(10, 8))
        correlation_matrix = self.clean_df.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Sensor Correlation Matrix')
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=150, bbox_inches='tight')
        print("Saved correlation_heatmap.png")
        
    def simple_shutdown_detection(self):
        """
        My first attempt at detecting shutdowns
        
        I'm starting simple: low temperature probably means shutdown
        """
        print("=== Simple Shutdown Detection ===")
        
        # I'll use inlet temperature as the main indicator
        temp_col = 'Cyclone_Inlet_Gas_Temp'
        
        # Calculate a rolling mean to smooth out noise
        rolling_temp = self.clean_df[temp_col].rolling(window=12).mean()  # 1 hour average
        
        # My hypothesis: below 300°C probably means shutdown
        shutdown_threshold = 300
        potential_shutdowns = rolling_temp < shutdown_threshold
        
        # Count shutdown periods
        shutdown_count = potential_shutdowns.sum()
        pct_shutdown = (shutdown_count / len(self.clean_df)) * 100
        
        print(f"Potential shutdown periods: {shutdown_count} time points ({pct_shutdown:.1f}%)")
        
        # Plot this to see if it makes sense
        plt.figure(figsize=(15, 6))
        plt.subplot(2, 1, 1)
        plt.plot(self.clean_df.index[:2000], self.clean_df[temp_col][:2000], alpha=0.7, label='Raw Temperature')
        plt.plot(self.clean_df.index[:2000], rolling_temp[:2000], label='1-hour Average', color='red')
        plt.axhline(y=shutdown_threshold, color='orange', linestyle='--', label=f'Shutdown Threshold ({shutdown_threshold}°C)')
        plt.legend()
        plt.title('Temperature Analysis for Shutdown Detection')
        plt.ylabel('Temperature (°C)')
        
        plt.subplot(2, 1, 2)
        plt.plot(self.clean_df.index[:2000], potential_shutdowns[:2000], color='red', alpha=0.7)
        plt.title('Detected Shutdown Periods')
        plt.ylabel('Shutdown (1=Yes, 0=No)')
        plt.xlabel('Time')
        
        plt.tight_layout()
        plt.savefig('shutdown_detection_simple.png', dpi=150, bbox_inches='tight')
        print("Saved shutdown_detection_simple.png")
        
        return potential_shutdowns

def main():
    print("=== Cyclone Data Analysis - Version 2 ===")
    print("This is my second attempt, more systematic than v1")
    print()
    
    # Initialize analyzer
    analyzer = CycloneAnalyzer('../data.xlsx')
    
    # Step by step analysis
    data = analyzer.load_data()
    analyzer.explore_data()
    clean_data = analyzer.clean_data()
    analyzer.make_basic_plots()
    shutdowns = analyzer.simple_shutdown_detection()
    
    print("\n=== Version 2 Complete ===")
    print("What I learned this time:")
    print("1. Data spans 3 years with ~2% missing values")
    print("2. Had to debug data type issues - sensor values were strings!")
    print("3. Temperature and pressure sensors are correlated")
    print("4. There are clear low-temperature periods that might be shutdowns")
    print("5. Need to be more sophisticated about shutdown detection")
    print()
    print("Debugging lesson: Always check data types first!")
    print("Next steps for v3:")
    print("- Better shutdown detection using multiple sensors")
    print("- Try clustering to find operational states")
    print("- Look into anomaly detection")

if __name__ == "__main__":
    main()