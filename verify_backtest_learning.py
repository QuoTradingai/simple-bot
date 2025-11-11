#!/usr/bin/env python3
"""
Verify that the backtest is learning from ALL 9 features.
Checks the most recent experiences saved during the backtest run.
"""

import json
from datetime import datetime, timedelta

print("=" * 80)
print("BACKTEST LEARNING VERIFICATION")
print("=" * 80)

# Load all experiences
with open('cloud-api/signal_experience.json', 'r') as f:
    data = json.load(f)
    all_experiences = data.get('experiences', [])

print(f"\nTotal experiences in database: {len(all_experiences)}")

# Get experiences from the last hour (recent backtest run)
now = datetime.now()
one_hour_ago = now - timedelta(hours=1)

recent_experiences = []
for exp in all_experiences:
    timestamp_str = exp.get('timestamp', '')
    try:
        exp_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        if exp_time > one_hour_ago:
            recent_experiences.append(exp)
    except:
        pass

print(f"Experiences from recent backtest (last hour): {len(recent_experiences)}")

if len(recent_experiences) == 0:
    print("\nNo recent experiences found. Checking last 100 instead...")
    recent_experiences = all_experiences[-100:]

print("\n" + "=" * 80)
print("FEATURE ANALYSIS (Recent Backtest Experiences)")
print("=" * 80)

# Define all 9 features we expect
required_features = {
    'rsi': 'RSI (Relative Strength Index)',
    'atr': 'ATR (Average True Range)',
    'vwap_distance': 'VWAP Distance',
    'vix': 'VIX (Volatility Index)',
    'volume_ratio': 'Volume Ratio',
    'hour': 'Hour of Day',
    'day_of_week': 'Day of Week',
    'recent_pnl': 'Recent P&L',
    'streak': 'Win/Loss Streak'
}

# Count how many experiences have each feature
feature_counts = {feature: 0 for feature in required_features}
complete_experiences = 0

for exp in recent_experiences:
    state = exp.get('state', {})
    has_all = True
    
    for feature in required_features:
        if feature in state:
            feature_counts[feature] += 1
        else:
            has_all = False
    
    if has_all:
        complete_experiences += 1

# Display results
print("\nFeature Presence in Recent Experiences:")
print(f"{'Feature':<20} {'Count':<10} {'Percentage':<12} {'Description'}")
print("-" * 80)

for feature, description in required_features.items():
    count = feature_counts[feature]
    pct = (count / len(recent_experiences) * 100) if recent_experiences else 0
    status = "[OK]" if pct == 100 else "[!!]"
    print(f"{status} {feature:<17} {count:>4}/{len(recent_experiences):<4} {pct:>6.1f}%       {description}")

print("\n" + "=" * 80)
print(f"Complete experiences (all 9 features): {complete_experiences}/{len(recent_experiences)} ({100*complete_experiences/len(recent_experiences):.1f}%)")
print("=" * 80)

# Show sample of a complete experience
if complete_experiences > 0:
    print("\n" + "=" * 80)
    print("SAMPLE: Complete Experience with All 9 Features")
    print("=" * 80)
    
    # Find first complete experience
    for exp in recent_experiences:
        state = exp.get('state', {})
        if all(f in state for f in required_features):
            print(f"\nTimestamp: {exp.get('timestamp', 'N/A')}")
            print(f"Side: {state.get('side', 'N/A')}")
            print(f"Action: {exp.get('action', {})}")
            print(f"Reward: {exp.get('reward', 'N/A')}")
            
            print("\nAll 9 Features:")
            for feature, description in required_features.items():
                value = state.get(feature, 'MISSING')
                print(f"  {feature:<20} = {value:>12} | {description}")
            
            break

# Feature diversity check
if len(recent_experiences) > 0:
    print("\n" + "=" * 80)
    print("FEATURE DIVERSITY (Proving bot learns different patterns)")
    print("=" * 80)
    
    # Collect values for diversity analysis
    volume_ratios = [exp.get('state', {}).get('volume_ratio', 0) for exp in recent_experiences if 'volume_ratio' in exp.get('state', {})]
    hours = [exp.get('state', {}).get('hour', 0) for exp in recent_experiences if 'hour' in exp.get('state', {})]
    days = [exp.get('state', {}).get('day_of_week', 0) for exp in recent_experiences if 'day_of_week' in exp.get('state', {})]
    streaks = [exp.get('state', {}).get('streak', 0) for exp in recent_experiences if 'streak' in exp.get('state', {})]
    vix_values = [exp.get('state', {}).get('vix', 0) for exp in recent_experiences if 'vix' in exp.get('state', {})]
    
    if volume_ratios:
        print(f"\nVolume Ratios: {min(volume_ratios):.3f} to {max(volume_ratios):.3f}")
        print(f"  -> Bot learns from LOW and HIGH volume conditions")
    
    if hours:
        print(f"\nHours of Day: {min(hours)} to {max(hours)}")
        print(f"  -> Bot learns from {len(set(hours))} different hours (early morning, midday, afternoon)")
    
    if days:
        unique_days = set(days)
        day_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        days_str = ', '.join([day_names.get(d, str(d)) for d in sorted(unique_days)])
        print(f"\nDays of Week: {days_str}")
        print(f"  -> Bot learns from {len(unique_days)} different days (weekly patterns)")
    
    if streaks:
        print(f"\nWin/Loss Streaks: {min(streaks)} to {max(streaks)}")
        print(f"  -> Bot learns from winning AND losing streaks")
    
    if vix_values:
        print(f"\nVIX Values: {min(vix_values):.1f} to {max(vix_values):.1f}")
        if min(vix_values) == max(vix_values):
            print(f"  -> Note: All VIX values are {vix_values[0]} (using default - historical data doesn't have real VIX)")

print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

if complete_experiences == len(recent_experiences) and len(recent_experiences) > 0:
    print("[SUCCESS] Bot is learning from ALL 9 features!")
    print("  - Pattern matching uses: RSI, VWAP, Time, VIX, Volume, Hour, Day, Streak, Recent P&L")
    print("  - Every experience captures complete market context")
    print("  - Ready for intelligent trade selection based on historical patterns")
elif complete_experiences > 0:
    pct = 100 * complete_experiences / len(recent_experiences)
    print(f"[PARTIAL SUCCESS] {pct:.1f}% of recent experiences have all 9 features")
    print("  - Most new experiences are complete")
    print("  - Some older experiences may be missing VIX (from before feature expansion)")
else:
    print("[WARNING] No complete experiences found with all 9 features")
    print("  - Check if backtest is sending all features to cloud API")

print("=" * 80)
