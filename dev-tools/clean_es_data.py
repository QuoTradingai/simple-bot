"""
Clean ES 1-minute data to match real market conditions:
1. Remove daily maintenance window (22:00-23:00 UTC / 17:00-18:00 EST)
2. Remove weekend bars (Saturday-Sunday)
3. Remove holiday periods (if volume = 0)
4. Ensure realistic volume levels
"""
import pandas as pd
from datetime import datetime, timedelta
import pytz

def clean_es_data(input_file, output_file):
    """Clean ES futures data to match real trading hours"""
    
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    original_count = len(df)
    print(f"Original bars: {original_count:,}")
    
    # Extract hour and day of week
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    
    # === FILTER 1: Remove daily maintenance window (22:00-22:59 UTC) ===
    # ES closes at 17:00 EST (22:00 UTC) and reopens at 18:00 EST (23:00 UTC)
    before_maintenance = len(df)
    df = df[df['hour'] != 22]
    maintenance_removed = before_maintenance - len(df)
    print(f"Removed {maintenance_removed:,} bars during maintenance window (22:00-23:00 UTC)")
    
    # === FILTER 2: Remove weekend bars ===
    # ES trades Sunday 18:00 EST to Friday 17:00 EST
    # In UTC: Sunday 23:00 to Saturday 22:00
    before_weekend = len(df)
    
    # Remove full Saturday (day_of_week = 5)
    df = df[df['day_of_week'] != 5]
    
    # Remove Sunday before 23:00 UTC (day_of_week = 6, hour < 23)
    df = df[~((df['day_of_week'] == 6) & (df['hour'] < 23))]
    
    weekend_removed = before_weekend - len(df)
    print(f"Removed {weekend_removed:,} weekend bars")
    
    # === FILTER 3: Remove bars with zero volume (holidays/outages) ===
    before_zero_vol = len(df)
    df = df[df['volume'] > 0]
    zero_vol_removed = before_zero_vol - len(df)
    print(f"Removed {zero_vol_removed:,} bars with zero volume")
    
    # === FILTER 4: Flag suspicious low-volume bars (likely synthetic) ===
    # During active hours, ES should have significant volume
    # Flag bars with volume = 1 during peak hours (13:30-20:00 UTC = 8:30am-3pm EST)
    peak_hours = df[(df['hour'] >= 13) & (df['hour'] <= 20)]
    low_vol_peak = len(peak_hours[peak_hours['volume'] == 1])
    if low_vol_peak > 0:
        print(f"⚠️  WARNING: {low_vol_peak:,} bars with volume=1 during peak hours (likely synthetic data)")
    
    # === QUALITY CHECK: Verify gaps exist ===
    df_sorted = df.sort_values('timestamp')
    df_sorted['time_diff'] = df_sorted['timestamp'].diff()
    
    # Count gaps (time diff > 1 minute)
    gaps = df_sorted[df_sorted['time_diff'] > pd.Timedelta(minutes=1)]
    print(f"\nFound {len(gaps):,} time gaps in data (expected for maintenance/weekends)")
    
    # Show sample gaps
    if len(gaps) > 0:
        print("\nSample gaps (first 5):")
        for idx, row in gaps.head(5).iterrows():
            prev_idx = df_sorted.index.get_loc(idx) - 1
            prev_time = df_sorted.iloc[prev_idx]['timestamp']
            print(f"  {prev_time} -> {row['timestamp']} (gap: {row['time_diff']})")
    
    # === SAVE CLEANED DATA ===
    # Remove helper columns
    df_clean = df.drop(columns=['hour', 'day_of_week'])
    
    df_clean.to_csv(output_file, index=False)
    
    final_count = len(df_clean)
    total_removed = original_count - final_count
    removal_pct = (total_removed / original_count) * 100
    
    print(f"\n{'='*80}")
    print(f"CLEANING COMPLETE")
    print(f"{'='*80}")
    print(f"Original bars:     {original_count:,}")
    print(f"Final bars:        {final_count:,}")
    print(f"Removed:           {total_removed:,} ({removal_pct:.1f}%)")
    print(f"Output file:       {output_file}")
    print(f"{'='*80}")
    
    # === FINAL STATS ===
    print("\nData coverage:")
    print(f"  Start: {df_clean['timestamp'].min()}")
    print(f"  End:   {df_clean['timestamp'].max()}")
    print(f"  Days:  {(df_clean['timestamp'].max() - df_clean['timestamp'].min()).days}")
    
    return df_clean


if __name__ == "__main__":
    # Process both data files
    
    print("="*80)
    print("CLEANING ES_1min.csv")
    print("="*80)
    clean_es_data(
        "data/historical_data/ES_1min.csv",
        "data/historical_data/ES_1min_cleaned.csv"
    )
    
    print("\n" + "="*80)
    print("CLEANING ES_1min_synthetic_90days.csv")
    print("="*80)
    clean_es_data(
        "data/historical_data/ES_1min_synthetic_90days.csv",
        "data/historical_data/ES_1min_synthetic_90days_cleaned.csv"
    )
    
    print("\n✅ Both files cleaned successfully!")
    print("Original files preserved, cleaned versions saved with '_cleaned' suffix")
