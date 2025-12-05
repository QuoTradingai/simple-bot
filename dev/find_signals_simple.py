#!/usr/bin/env python3
"""
Simple diagnostic to count how many times all 9 conditions are met.
Uses minimal dependencies to avoid import errors.
"""

import csv
from datetime import datetime
from collections import deque

# Configuration from capitulation_detector.py
MIN_FLUSH_TICKS = 8
MIN_VELOCITY = 1.5
FLUSH_LOOKBACK_BARS = 7
NEAR_EXTREME_TICKS = 12
VOLUME_SPIKE_THRESHOLD = 1.2
RSI_OVERSOLD_EXTREME = 45
TICK_SIZE = 0.25

# Load data
print("Loading ES data...")
bars = []
with open('data/historical_data/ES_1min.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        bars.append({
            'timestamp': datetime.fromisoformat(row['timestamp']),
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': float(row['volume'])
        })

print(f"Loaded {len(bars)} bars")

# Process bars
signals_found = 0
near_miss_8 = 0
near_miss_9 = 0

bars_deque = deque(maxlen=200)

for idx in range(len(bars)):
    bars_deque.append(bars[idx])
    
    # Skip warmup
    if len(bars_deque) < 114:
        continue
    
    if len(bars_deque) < 2:
        continue
    
    current_bar = bars[-1] if idx == len(bars) - 1 else bars[idx]
    prev_bar = bars[idx - 1] if idx > 0 else current_bar
    
    # Calculate RSI
    if len(bars_deque) >= 15:
        recent_closes = [b['close'] for b in list(bars_deque)[-15:]]
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
        avg_loss = sum(losses) / len(losses) if losses else 1
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    else:
        rsi = None
    
    # Calculate VWAP
    recent_bars = list(bars_deque)[-20:]
    total_pv = sum(b['close'] * b['volume'] for b in recent_bars)
    total_v = sum(b['volume'] for b in recent_bars)
    vwap = total_pv / total_v if total_v > 0 else current_bar['close']
    
    # Volume average
    recent_volumes = [b['volume'] for b in list(bars_deque)[-20:]]
    avg_volume_20 = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 1
    
    # Check 9 conditions for LONG
    recent_bars_for_flush = list(bars_deque)[-FLUSH_LOOKBACK_BARS:]
    highest_high = max(b['high'] for b in recent_bars_for_flush)
    lowest_low = min(b['low'] for b in recent_bars_for_flush)
    flush_range = highest_high - lowest_low
    flush_range_ticks = flush_range / TICK_SIZE
    
    bar_count = len(recent_bars_for_flush)
    velocity = flush_range_ticks / bar_count if bar_count > 0 else 0
    
    distance_from_low = (current_bar['close'] - lowest_low) / TICK_SIZE
    current_volume = current_bar['volume']
    
    # Conditions
    conditions = {}
    conditions['1_flush_happened'] = flush_range_ticks >= MIN_FLUSH_TICKS
    conditions['2_flush_fast'] = velocity >= MIN_VELOCITY
    conditions['3_near_bottom'] = distance_from_low <= NEAR_EXTREME_TICKS
    conditions['4_rsi_oversold'] = rsi is not None and rsi < RSI_OVERSOLD_EXTREME
    conditions['5_volume_spike'] = current_volume >= (avg_volume_20 * VOLUME_SPIKE_THRESHOLD)
    conditions['6_stopped_new_lows'] = current_bar['low'] >= prev_bar['low']
    conditions['7_reversal_candle'] = current_bar['close'] > current_bar['open']
    conditions['8_below_vwap'] = current_bar['close'] < vwap
    conditions['9_regime_allows'] = True  # Simplified - always allow
    
    # Count passed
    passed_count = sum(1 for v in conditions.values() if v)
    
    if passed_count == 9:
        signals_found += 1
        if signals_found <= 5:
            print(f"\n✅ Signal #{signals_found} at bar {idx}")
            print(f"   Time: {current_bar['timestamp']}")
            print(f"   Price: ${current_bar['close']:.2f}")
            print(f"   Flush: {flush_range_ticks:.1f}t, vel={velocity:.2f}")
            rsi_str = f"{rsi:.1f}" if rsi is not None else "N/A"
            print(f"   RSI: {rsi_str}")
            print(f"   Volume: {current_volume:.0f} ({current_volume/avg_volume_20:.2f}x)")
    elif passed_count == 8:
        near_miss_8 += 1
        failed = [k for k, v in conditions.items() if not v]
        if near_miss_8 <= 5:
            print(f"\n🎯 Near-miss (8/9) at bar {idx}. Failed: {', '.join(failed)}")

print("\n" + "="*80)
print(f"RESULTS:")
print(f"  ✅ Signals found: {signals_found}")
print(f"  🎯 Near-misses (8/9): {near_miss_8}")
print("="*80)

if signals_found > 0:
    print(f"\n✅ SUCCESS! Found {signals_found} signals in the data.")
    print("The conditions ARE being met. Bug is in backtest execution flow.")
else:
    print("\n❌ No signals found. Need to debug condition logic.")
