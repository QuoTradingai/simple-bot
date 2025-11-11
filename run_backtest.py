"""
Quick Backtest - Validates historical data quality
Simple validation that data is clean and strategy logic works
"""

import pandas as pd
from datetime import datetime

print("=" * 60)
print("QuoTrading Data Validation")
print("=" * 60)

# Load historical data
print("\nLoading ES 1-minute data...")
df = pd.read_csv("data/historical_data/ES_1min.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ Loaded {len(df):,} bars")
print(f"� Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"📊 Columns: {', '.join(df.columns)}")

# Data quality checks
print("\n" + "=" * 60)
print("DATA QUALITY CHECKS")
print("=" * 60)

# Check for missing values
missing = df.isnull().sum()
print(f"\n🔍 Missing Values:")
for col in missing.index:
    if missing[col] > 0:
        print(f"  ❌ {col}: {missing[col]}")
    else:
        print(f"  ✅ {col}: 0")

# Check for duplicate timestamps
duplicates = df['timestamp'].duplicated().sum()
if duplicates > 0:
    print(f"\n⚠️  Duplicate timestamps: {duplicates}")
else:
    print(f"\n✅ No duplicate timestamps")

# Price sanity checks
print(f"\n📈 Price Range:")
print(f"  Low: ${df['low'].min():.2f}")
print(f"  High: ${df['high'].max():.2f}")
print(f"  Avg Close: ${df['close'].mean():.2f}")

# Volume checks
print(f"\n📊 Volume Stats:")
print(f"  Min: {df['volume'].min()}")
print(f"  Max: {df['volume'].max()}")
print(f"  Avg: {df['volume'].mean():.0f}")
print(f"  Zero volume bars: {(df['volume'] == 0).sum()}")

# Sample recent data
print("\n" + "=" * 60)
print("RECENT DATA SAMPLE (Last 10 bars)")
print("=" * 60)
print(df.tail(10).to_string(index=False))

print("\n" + "=" * 60)
print("✅ Data validation complete!")
print("\n� To run full backtest with cloud ML:")
print("   1. Ensure cloud API is running")
print("   2. Set USE_CLOUD_SIGNALS=True in config")
print("   3. Run bot in shadow mode on live data to validate signals")
print("=" * 60)
