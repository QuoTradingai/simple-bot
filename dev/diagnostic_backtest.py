#!/usr/bin/env python3
"""
Diagnostic backtest that logs EVERY step of signal checking.
This will show exactly where the 258 signals are being blocked.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from collections import deque
from datetime import datetime
import pytz

# Import key components
from src.capitulation_detector import CapitulationDetector

# Load data
print("Loading ES data...")
df = pd.read_csv('data/historical_data/ES_1min.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(f"Loaded {len(df)} bars from {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")

# Initialize detector
cap_detector = CapitulationDetector(tick_size=0.25, tick_value=12.50)

# Track statistics
total_bars = 0
warmup_blocked = 0
time_blocked = 0
condition_checks = 0
long_signals = 0
near_miss_8 = 0
near_miss_9 = 0

# Process bars
bars_deque = deque(maxlen=200)
eastern = pytz.timezone('US/Eastern')

print("\nProcessing bars...")
print("="*80)

for idx, row in df.iterrows():
    total_bars += 1
    
    # Convert to bar dict
    bar = {
        'timestamp': row['timestamp'],
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close'],
        'volume': row['volume']
    }
    
    bars_deque.append(bar)
    
    # Skip warmup period (114 bars)
    if len(bars_deque) < 114:
        if total_bars == 1 or total_bars % 20 == 0:
            print(f"[Warmup] Bar {total_bars}/114")
        warmup_blocked += 1
        continue
    
    # Skip if not enough bars for signal check
    if len(bars_deque) < 2:
        continue
    
    prev_bar = list(bars_deque)[-2]
    current_bar = list(bars_deque)[-1]
    
    # Check time-based blocks (4-6 PM ET)
    bar_time = current_bar['timestamp']
    if bar_time.tzinfo is None:
        bar_time = eastern.localize(bar_time)
    else:
        bar_time = bar_time.astimezone(eastern)
    
    hour = bar_time.hour
    if 16 <= hour < 18:  # 4-6 PM ET
        time_blocked += 1
        continue
    
    # Calculate required indicators
    # RSI
    recent_closes = [b['close'] for b in list(bars_deque)[-15:]]
    if len(recent_closes) >= 14:
        gains = []
        losses = []
        for i in range(1, len(recent_closes)):
            change = recent_closes[i] - recent_closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    else:
        rsi = None
    
    # VWAP (simple approximation)
    recent_bars = list(bars_deque)[-20:]
    total_pv = sum(b['close'] * b['volume'] for b in recent_bars)
    total_v = sum(b['volume'] for b in recent_bars)
    vwap = total_pv / total_v if total_v > 0 else current_bar['close']
    
    # Volume average
    recent_volumes = [b['volume'] for b in list(bars_deque)[-20:]]
    avg_volume_20 = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 1
    
    # Regime (simplified)
    regime = "NORMAL_TRENDING"
    
    # Check long signal conditions
    condition_checks += 1
    all_passed, details = cap_detector.check_all_long_conditions(
        bars=bars_deque,
        current_bar=current_bar,
        prev_bar=prev_bar,
        rsi=rsi,
        avg_volume_20=avg_volume_20,
        current_price=current_bar['close'],
        vwap=vwap,
        regime=regime
    )
    
    if all_passed:
        long_signals += 1
        print(f"\n{'='*80}")
        print(f"✅ LONG SIGNAL #{long_signals} at bar {total_bars}")
        print(f"   Time: {bar_time}")
        print(f"   Price: ${current_bar['close']:.2f}")
        print(f"   Flush: {details['flush_range_ticks']:.1f} ticks, vel={details['velocity']:.2f}")
        print(f"   RSI: {rsi:.1f if rsi else 'N/A'}")
        print(f"   Volume: {current_bar['volume']:.0f} (ratio={details['volume_ratio']:.2f}x)")
        print(f"{'='*80}\n")
    else:
        # Check near-misses
        failed = details.get('failed_conditions', [])
        passed_count = 9 - len(failed)
        
        if passed_count == 9:
            near_miss_9 += 1
            print(f"\n⚠️ 9/9 conditions passed but all_passed=False! Bar {total_bars}")
            print(f"   Failed conditions: {failed}")
            print(f"   Details: {details}")
        elif passed_count == 8:
            near_miss_8 += 1
            if near_miss_8 <= 10:  # Only log first 10
                print(f"\n🎯 NEAR MISS (8/9) at bar {total_bars}")
                print(f"   Failed: {', '.join(failed)}")
                print(f"   Flush: {details['flush_range_ticks']:.1f}t, vel={details['velocity']:.2f}")
                print(f"   RSI: {rsi:.1f if rsi else 'N/A'}, Vol ratio: {details['volume_ratio']:.2f}x")

# Print summary
print("\n" + "="*80)
print("DIAGNOSTIC BACKTEST SUMMARY")
print("="*80)
print(f"Total bars processed: {total_bars}")
print(f"Warmup blocked: {warmup_blocked} bars")
print(f"Time blocked (4-6 PM ET): {time_blocked} bars")
print(f"Condition checks performed: {condition_checks}")
print(f"")
print(f"RESULTS:")
print(f"  ✅ Long signals found: {long_signals}")
print(f"  🎯 Near-misses (8/9): {near_miss_8}")
print(f"  ⚠️  Anomalies (9/9 but failed): {near_miss_9}")
print("="*80)

if long_signals == 0:
    print("\n❌ NO SIGNALS FOUND - Something is wrong with condition checking!")
    print("Expected ~258 signals based on manual analysis.")
elif long_signals < 100:
    print(f"\n⚠️  Only {long_signals} signals found - Expected ~258")
    print("Some signals are still being blocked.")
else:
    print(f"\n✅ Found {long_signals} signals - this matches expected range!")
