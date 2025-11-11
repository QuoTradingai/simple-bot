"""
Analyze what market conditions are triggering signals in the backtest
"""
import pandas as pd
import numpy as np
from datetime import datetime, time

# Load historical data
df = pd.read_csv('data/historical_data/ES_1min.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['time'] = df['timestamp'].dt.time
df['date'] = df['timestamp'].dt.date

# Filter to last 15 days (matching backtest)
last_date = df['timestamp'].max()
start_date = last_date - pd.Timedelta(days=15)
df = df[df['timestamp'] >= start_date].reset_index(drop=True)

print("=" * 80)
print("SIGNAL ANALYSIS - Last 15 Days")
print("=" * 80)
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Total bars: {len(df):,}")
print()

# Calculate VWAP for each day
def calculate_daily_vwap(df_day):
    """Calculate VWAP bands for a day"""
    df_day = df_day.copy()
    df_day['typical_price'] = (df_day['high'] + df_day['low'] + df_day['close']) / 3
    df_day['tpv'] = df_day['typical_price'] * df_day['volume']
    
    cumulative_tpv = df_day['tpv'].cumsum()
    cumulative_volume = df_day['volume'].cumsum()
    vwap = cumulative_tpv / cumulative_volume
    
    # Standard deviation
    df_day['vwap'] = vwap
    df_day['price_diff_sq'] = (df_day['typical_price'] - df_day['vwap']) ** 2
    df_day['weighted_diff_sq'] = df_day['price_diff_sq'] * df_day['volume']
    
    cumulative_weighted_diff_sq = df_day['weighted_diff_sq'].cumsum()
    variance = cumulative_weighted_diff_sq / cumulative_volume
    std_dev = np.sqrt(variance)
    
    df_day['vwap_upper_2'] = vwap + (2 * std_dev)
    df_day['vwap_lower_2'] = vwap - (2 * std_dev)
    
    return df_day

# Calculate RSI
def calculate_rsi(prices, period=10):
    """Calculate RSI"""
    deltas = prices.diff()
    gains = deltas.where(deltas > 0, 0.0)
    losses = -deltas.where(deltas < 0, 0.0)
    
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi

# Add indicators
df['rsi'] = calculate_rsi(df['close'], period=10)

# Process each day
signal_count = 0
long_signals = []
short_signals = []

for date in df['date'].unique():
    df_day = df[df['date'] == date].copy()
    
    if len(df_day) < 30:
        continue
    
    # Calculate VWAP
    df_day = calculate_daily_vwap(df_day)
    
    # Check for signals
    for idx in range(1, len(df_day)):
        current = df_day.iloc[idx]
        prev = df_day.iloc[idx - 1]
        
        # Skip after 4 PM (entry cutoff)
        if current['time'] >= time(16, 0):
            continue
        
        # Skip maintenance (5-6 PM)
        if current['time'] >= time(17, 0) and current['time'] < time(18, 0):
            continue
        
        # LONG signal: price bounces off lower VWAP band (2 std dev)
        if (prev['low'] <= df_day.iloc[idx - 1]['vwap_lower_2'] and 
            current['close'] > prev['close']):
            
            long_signals.append({
                'timestamp': current['timestamp'],
                'price': current['close'],
                'vwap': current['vwap'],
                'vwap_distance': ((current['close'] - current['vwap']) / current['vwap']) * 100,
                'rsi': current['rsi'],
                'volume': current['volume']
            })
            signal_count += 1
        
        # SHORT signal: price bounces off upper VWAP band (2 std dev)
        if (prev['high'] >= df_day.iloc[idx - 1]['vwap_upper_2'] and 
            current['close'] < prev['close']):
            
            short_signals.append({
                'timestamp': current['timestamp'],
                'price': current['close'],
                'vwap': current['vwap'],
                'vwap_distance': ((current['close'] - current['vwap']) / current['vwap']) * 100,
                'rsi': current['rsi'],
                'volume': current['volume']
            })
            signal_count += 1

print(f"📊 SIGNAL GENERATION:")
print(f"  Total Signals Detected: {signal_count}")
print(f"  LONG Signals: {len(long_signals)}")
print(f"  SHORT Signals: {len(short_signals)}")
print(f"  Signals Per Day: {signal_count / 15:.1f}")
print()

# Analyze LONG signals
if long_signals:
    long_df = pd.DataFrame(long_signals)
    print("🔵 LONG SIGNAL CONDITIONS:")
    print(f"  RSI Range: {long_df['rsi'].min():.1f} - {long_df['rsi'].max():.1f}")
    print(f"  RSI Average: {long_df['rsi'].mean():.1f}")
    print(f"  RSI Median: {long_df['rsi'].median():.1f}")
    print(f"  VWAP Distance: {long_df['vwap_distance'].min():.2f}% - {long_df['vwap_distance'].max():.2f}%")
    print(f"  Avg VWAP Distance: {long_df['vwap_distance'].mean():.2f}%")
    print()

# Analyze SHORT signals
if short_signals:
    short_df = pd.DataFrame(short_signals)
    print("🔴 SHORT SIGNAL CONDITIONS:")
    print(f"  RSI Range: {short_df['rsi'].min():.1f} - {short_df['rsi'].max():.1f}")
    print(f"  RSI Average: {short_df['rsi'].mean():.1f}")
    print(f"  RSI Median: {short_df['rsi'].median():.1f}")
    print(f"  VWAP Distance: {short_df['vwap_distance'].min():.2f}% - {short_df['vwap_distance'].max():.2f}%")
    print(f"  Avg VWAP Distance: {short_df['vwap_distance'].mean():.2f}%")
    print()

# Time distribution
print("⏰ SIGNAL TIME DISTRIBUTION:")
if long_signals:
    long_df['hour'] = pd.to_datetime(long_df['timestamp']).dt.hour
    print("\nLONG signals by hour:")
    hour_dist = long_df['hour'].value_counts().sort_index()
    for hour, count in hour_dist.items():
        print(f"  {hour:02d}:00 - {count:3d} signals ({count/len(long_signals)*100:.1f}%)")

if short_signals:
    short_df['hour'] = pd.to_datetime(short_df['timestamp']).dt.hour
    print("\nSHORT signals by hour:")
    hour_dist = short_df['hour'].value_counts().sort_index()
    for hour, count in hour_dist.items():
        print(f"  {hour:02d}:00 - {count:3d} signals ({count/len(short_signals)*100:.1f}%)")

print()
print("=" * 80)
print("KEY FINDINGS:")
print(f"• {signal_count} signals over 15 days = {signal_count/15:.1f} per day")
print(f"• Cloud RL filters these at 70% threshold to ~{signal_count * 0.26:.0f} trades")
print(f"• Most signals during: {long_df['hour'].mode()[0] if long_signals else 'N/A'}:00 (LONG)")
print("=" * 80)
