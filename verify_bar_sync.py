"""
Verify that 15min bars correctly aggregate from 1min bars
"""
import pandas as pd

# Read both files
print("Reading data files...")
df_1min = pd.read_csv('data/historical_data/ES_1min.csv')
df_15min = pd.read_csv('data/historical_data/ES_15min.csv')

df_1min['timestamp'] = pd.to_datetime(df_1min['timestamp'])
df_15min['timestamp'] = pd.to_datetime(df_15min['timestamp'])

# Check a few random 15min bars to verify they match the 1min aggregation
import random
random.seed(42)

# Get last 100 15min bars for testing
test_bars = df_15min.tail(100).sample(5).sort_values('timestamp')

print("\n" + "="*100)
print("VERIFICATION: Checking if 15min bars correctly aggregate 1min bars")
print("="*100)

all_match = True

for idx, bar_15min in test_bars.iterrows():
    timestamp = bar_15min['timestamp']
    
    # Get the 15 1min bars that should make up this 15min bar
    end_time = timestamp + pd.Timedelta(minutes=15)
    bars_1min = df_1min[(df_1min['timestamp'] >= timestamp) & (df_1min['timestamp'] < end_time)]
    
    if len(bars_1min) == 0:
        print(f"\n⚠️  {timestamp}: NO 1min bars found!")
        all_match = False
        continue
    
    # Calculate what the 15min bar SHOULD be from 1min bars
    expected_open = bars_1min.iloc[0]['open']
    expected_high = bars_1min['high'].max()
    expected_low = bars_1min['low'].min()
    expected_close = bars_1min.iloc[-1]['close']
    expected_volume = bars_1min['volume'].sum()
    
    # Compare
    actual_open = bar_15min['open']
    actual_high = bar_15min['high']
    actual_low = bar_15min['low']
    actual_close = bar_15min['close']
    actual_volume = bar_15min['volume']
    
    match = (
        expected_open == actual_open and
        expected_high == actual_high and
        expected_low == actual_low and
        expected_close == actual_close and
        expected_volume == actual_volume
    )
    
    if match:
        print(f"\n✅ {timestamp}: MATCH ({len(bars_1min)} bars)")
    else:
        print(f"\n❌ {timestamp}: MISMATCH ({len(bars_1min)} bars)")
        all_match = False
        
    print(f"   15min bar: O={actual_open} H={actual_high} L={actual_low} C={actual_close} V={actual_volume}")
    print(f"   Expected:  O={expected_open} H={expected_high} L={expected_low} C={expected_close} V={expected_volume}")
    
    if not match:
        if expected_open != actual_open:
            print(f"      Open diff: {actual_open} vs {expected_open}")
        if expected_high != actual_high:
            print(f"      High diff: {actual_high} vs {expected_high}")
        if expected_low != actual_low:
            print(f"      Low diff: {actual_low} vs {expected_low}")
        if expected_close != actual_close:
            print(f"      Close diff: {actual_close} vs {expected_close}")
        if expected_volume != actual_volume:
            print(f"      Volume diff: {actual_volume} vs {expected_volume}")

print("\n" + "="*100)
if all_match:
    print("✅ ALL CHECKS PASSED - 15min bars correctly aggregate 1min bars")
else:
    print("❌ SYNC ISSUES FOUND - 15min bars do NOT match 1min aggregation")
print("="*100)
