"""
Clean ES data: remove weekend bars, handle maintenance window
"""
import pandas as pd

print("Reading ES_1min.csv...")
df = pd.read_csv('data/historical_data/ES_1min.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

original_count = len(df)
print(f"Original bars: {original_count:,}")

# Remove weekend bars (Saturday=5, Sunday=6)
df['dayofweek'] = df['timestamp'].dt.dayofweek
weekend_bars = len(df[df['dayofweek'].isin([5, 6])])
df = df[~df['dayofweek'].isin([5, 6])].copy()
print(f"Removed {weekend_bars:,} weekend bars")

# ES futures trade Sunday 6pm ET to Friday 5pm ET
# Maintenance: Monday-Thursday 5:00-6:00 PM ET, Friday 5:00 PM - Sunday 6:00 PM ET
# Since data appears to be in local time, hour 17 = 5 PM
# Keep hour 17 but remove hour 22 (10 PM which seems to be a gap before restart at 23:00)

# The 61-minute gaps from 21:59->23:00 suggest maintenance is 22:00-23:00 in this timezone
print(f"\nRemoving maintenance hour (22:00-22:59)...")
maintenance_bars = len(df[df['timestamp'].dt.hour == 22])
df = df[df['timestamp'].dt.hour != 22].copy()
print(f"Removed {maintenance_bars:,} maintenance bars")

# Drop the helper column
df = df.drop(columns=['dayofweek'])

# Save cleaned data
df.to_csv('data/historical_data/ES_1min.csv', index=False)

print(f"\n✅ Cleaned ES_1min.csv:")
print(f"   Original: {original_count:,} bars")
print(f"   Cleaned:  {len(df):,} bars")
print(f"   Removed:  {original_count - len(df):,} bars")
print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

# Now rebuild the 15min bars from the cleaned 1min data
print(f"\nRebuilding ES_15min.csv from cleaned 1min data...")
df.set_index('timestamp', inplace=True)

df_15min = df.resample('15min').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()

df_15min.reset_index(inplace=True)
df_15min.to_csv('data/historical_data/ES_15min.csv', index=False)

print(f"\n✅ Rebuilt ES_15min.csv:")
print(f"   Total bars: {len(df_15min):,}")
print(f"   Date range: {df_15min['timestamp'].min()} to {df_15min['timestamp'].max()}")
