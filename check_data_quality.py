"""
Check data quality: gaps, weekend bars, maintenance hours
"""
import pandas as pd
from datetime import time

print("Reading ES_1min.csv...")
df = pd.read_csv('data/historical_data/ES_1min.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date
df['time'] = df['timestamp'].dt.time
df['dayofweek'] = df['timestamp'].dt.dayofweek  # 0=Mon, 6=Sun
df['hour'] = df['timestamp'].dt.hour

print("\n" + "="*100)
print("DATA QUALITY CHECKS")
print("="*100)

# 1. Check for weekend bars (Saturday=5, Sunday=6)
print("\n1. WEEKEND BARS CHECK:")
weekend_bars = df[df['dayofweek'].isin([5, 6])]
if len(weekend_bars) > 0:
    print(f"   ❌ Found {len(weekend_bars)} weekend bars:")
    print(weekend_bars[['timestamp', 'dayofweek']].head(10))
else:
    print("   ✅ No weekend bars found")

# 2. Check for maintenance hours (ES maintenance: 5:00 PM - 6:00 PM ET = 17:00 - 18:00)
print("\n2. MAINTENANCE HOURS CHECK (5:00-6:00 PM ET):")
# Convert to UTC (ET is UTC-5 in summer, UTC-4 in winter, but data should already be in local time)
maintenance_bars = df[(df['hour'] == 17) | ((df['hour'] == 18) & (df['timestamp'].dt.minute == 0))]
if len(maintenance_bars) > 0:
    print(f"   ⚠️  Found {len(maintenance_bars)} bars during maintenance window:")
    print(f"   (Note: Check if these are actual maintenance or just after-hours trading)")
    print(maintenance_bars[['timestamp']].head(10))
else:
    print("   ✅ No bars during typical maintenance window")

# 3. Check for gaps (missing 1-minute bars during trading hours)
print("\n3. GAP ANALYSIS:")

# Sort by timestamp
df_sorted = df.sort_values('timestamp').reset_index(drop=True)

# Calculate time differences
df_sorted['time_diff'] = df_sorted['timestamp'].diff()

# Find gaps > 1 minute (but not weekend gaps or daily close gaps)
gaps = df_sorted[df_sorted['time_diff'] > pd.Timedelta(minutes=1)]

# Filter out expected gaps (weekends, daily close 17:00-18:00)
unexpected_gaps = []
for idx, row in gaps.iterrows():
    prev_timestamp = df_sorted.loc[idx-1, 'timestamp']
    curr_timestamp = row['timestamp']
    
    # Skip if gap crosses weekend
    if prev_timestamp.dayofweek == 4 and curr_timestamp.dayofweek == 6:  # Fri -> Sun
        continue
    if prev_timestamp.dayofweek == 5:  # Saturday
        continue
        
    # Skip if gap is during maintenance (around 17:00-18:00)
    if prev_timestamp.hour == 16 and curr_timestamp.hour == 18:
        continue
    if prev_timestamp.hour == 17:
        continue
        
    unexpected_gaps.append({
        'prev_time': prev_timestamp,
        'curr_time': curr_timestamp,
        'gap_minutes': row['time_diff'].total_seconds() / 60
    })

if len(unexpected_gaps) > 0:
    print(f"   ❌ Found {len(unexpected_gaps)} unexpected gaps:")
    for gap in unexpected_gaps[:10]:
        print(f"      Gap: {gap['prev_time']} -> {gap['curr_time']} ({gap['gap_minutes']:.0f} min)")
else:
    print("   ✅ No unexpected gaps found (only normal weekend/maintenance gaps)")

# 4. Check trading hours distribution
print("\n4. TRADING HOURS DISTRIBUTION:")
print("   Hour | Bars")
print("   -----|------")
for hour in range(24):
    count = len(df[df['hour'] == hour])
    if count > 0:
        bar = "█" * (count // 1000)
        print(f"   {hour:02d}:00| {count:6d} {bar}")

# 5. Daily bar count check
print("\n5. DAILY BAR COUNT:")
daily_counts = df.groupby('date').size()
print(f"   Min bars per day: {daily_counts.min()}")
print(f"   Max bars per day: {daily_counts.max()}")
print(f"   Avg bars per day: {daily_counts.mean():.0f}")

days_with_issues = daily_counts[daily_counts < 1000]  # ES trades ~23 hours, should have ~1380 bars
if len(days_with_issues) > 0:
    print(f"\n   ⚠️  {len(days_with_issues)} days with < 1000 bars (possible partial days):")
    for date, count in days_with_issues.head(10).items():
        print(f"      {date}: {count} bars")

print("\n" + "="*100)
print("SUMMARY")
print("="*100)
print(f"Total bars: {len(df):,}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Total days: {len(df['date'].unique())}")
print("="*100)
