"""
Convert 1-minute bars to 15-minute bars to sync the timeframes
"""
import pandas as pd
from datetime import datetime

# Read the 1-minute data
print("Reading ES_1min.csv...")
df_1min = pd.read_csv('data/historical_data/ES_1min.csv')
df_1min['timestamp'] = pd.to_datetime(df_1min['timestamp'])

# Read existing 15-minute data to get the last timestamp
print("Reading ES_15min.csv...")
df_15min_existing = pd.read_csv('data/historical_data/ES_15min.csv')
df_15min_existing['timestamp'] = pd.to_datetime(df_15min_existing['timestamp'])
last_15min_timestamp = df_15min_existing['timestamp'].max()

print(f"Last 15min timestamp: {last_15min_timestamp}")
print(f"1min data range: {df_1min['timestamp'].min()} to {df_1min['timestamp'].max()}")

# Filter 1min data to only include data AFTER the last 15min timestamp
df_1min_new = df_1min[df_1min['timestamp'] > last_15min_timestamp].copy()
print(f"New 1min bars to convert: {len(df_1min_new)}")

if len(df_1min_new) == 0:
    print("No new data to convert - files are already in sync!")
else:
    # Set timestamp as index for resampling
    df_1min_new.set_index('timestamp', inplace=True)
    
    # Resample to 15-minute bars
    print("Converting to 15-minute bars...")
    df_15min_new = df_1min_new.resample('15min').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Reset index to get timestamp back as a column
    df_15min_new.reset_index(inplace=True)
    
    print(f"Created {len(df_15min_new)} new 15-minute bars")
    print(f"New 15min range: {df_15min_new['timestamp'].min()} to {df_15min_new['timestamp'].max()}")
    
    # Combine with existing 15min data
    df_15min_combined = pd.concat([df_15min_existing, df_15min_new], ignore_index=True)
    df_15min_combined.sort_values('timestamp', inplace=True)
    
    # Save the updated 15min file
    df_15min_combined.to_csv('data/historical_data/ES_15min.csv', index=False)
    
    print(f"\n✅ Updated ES_15min.csv:")
    print(f"   Total bars: {len(df_15min_combined)}")
    print(f"   Date range: {df_15min_combined['timestamp'].min()} to {df_15min_combined['timestamp'].max()}")
    print(f"   Added: {len(df_15min_new)} new bars")
