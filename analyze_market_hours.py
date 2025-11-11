import pandas as pd

df = pd.read_csv('data/historical_data/ES_1min.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['time'] = df['timestamp'].dt.time
df['range'] = df['high'] - df['low']

# Different time periods
maintenance = df[(df['time'] >= pd.to_datetime('17:00').time()) & (df['time'] < pd.to_datetime('18:00').time())]
morning = df[(df['time'] >= pd.to_datetime('09:00').time()) & (df['time'] < pd.to_datetime('10:00').time())]
overnight = df[(df['time'] >= pd.to_datetime('00:00').time()) & (df['time'] < pd.to_datetime('06:00').time())]
regular = df[(df['time'] >= pd.to_datetime('09:30').time()) & (df['time'] < pd.to_datetime('16:00').time())]

print("ES FUTURES MARKET HOURS ANALYSIS")
print("=" * 60)

print("\n📊 REGULAR TRADING HOURS (9:30 AM - 4:00 PM ET):")
print(f"  Total bars: {len(regular):,}")
print(f"  Avg Volume: {regular['volume'].mean():.0f} contracts/min")
print(f"  Avg Range: {regular['range'].mean():.2f} points/min")
print(f"  Max Range: {regular['range'].max():.2f} points/min")

print("\n🌙 OVERNIGHT SESSION (12:00 AM - 6:00 AM ET):")
print(f"  Total bars: {len(overnight):,}")
print(f"  Avg Volume: {overnight['volume'].mean():.0f} contracts/min")
print(f"  Avg Range: {overnight['range'].mean():.2f} points/min")
print(f"  Max Range: {overnight['range'].max():.2f} points/min")

print("\n🔧 MAINTENANCE WINDOW (5:00 PM - 6:00 PM ET):")
print(f"  Total bars: {len(maintenance):,}")
print(f"  Avg Volume: {maintenance['volume'].mean():.0f} contracts/min")
print(f"  Avg Range: {maintenance['range'].mean():.2f} points/min")
print(f"  Max Range: {maintenance['range'].max():.2f} points/min")

print("\n🌅 MORNING PRE-MARKET (9:00 AM - 10:00 AM ET):")
print(f"  Total bars: {len(morning):,}")
print(f"  Avg Volume: {morning['volume'].mean():.0f} contracts/min")
print(f"  Avg Range: {morning['range'].mean():.2f} points/min")
print(f"  Max Range: {morning['range'].max():.2f} points/min")

print("\n" + "=" * 60)
print("KEY FINDINGS:")
print(f"Maintenance volume is {maintenance['volume'].mean() / regular['volume'].mean() * 100:.1f}% of regular hours")
print(f"Maintenance range is {maintenance['range'].mean() / regular['range'].mean() * 100:.1f}% of regular hours")
