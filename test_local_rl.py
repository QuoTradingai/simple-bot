"""
Test LOCAL RL engine to see what confidence ranges it gives
"""
import sys
sys.path.insert(0, 'src')

from signal_confidence import SignalConfidenceRL

# Initialize local RL brain
rl = SignalConfidenceRL(
    experience_file="data/signal_experience.json",
    backtest_mode=False,  # Live mode
    confidence_threshold=0.5
)

print(f"Loaded {len(rl.experiences)} experiences")
print(f"Winners: {len([e for e in rl.experiences if e.get('reward', 0) > 0])}")
print(f"Losers: {len([e for e in rl.experiences if e.get('reward', 0) <= 0])}")

# Test same conditions as cloud
tests = [
    ("Good - Low RSI", {'rsi': 25.0, 'vwap_distance': 0.95, 'atr': 2.5, 'volume_ratio': 1.2, 'hour': 10, 'day_of_week': 2, 'recent_pnl': 100.0, 'streak': 2, 'side': 'long', 'regime': 'NORMAL'}),
    ("Bad - High RSI", {'rsi': 70.0, 'vwap_distance': 1.05, 'atr': 1.0, 'volume_ratio': 0.8, 'hour': 15, 'day_of_week': 4, 'recent_pnl': -200.0, 'streak': -3, 'side': 'long', 'regime': 'VOLATILE'}),
    ("Neutral", {'rsi': 50.0, 'vwap_distance': 1.0, 'atr': 2.0, 'volume_ratio': 1.0, 'hour': 12, 'day_of_week': 2, 'recent_pnl': 0.0, 'streak': 0, 'side': 'long', 'regime': 'NORMAL'}),
    ("Strong Winner", {'rsi': 20.0, 'vwap_distance': 0.90, 'atr': 3.0, 'volume_ratio': 1.5, 'hour': 9, 'day_of_week': 1, 'recent_pnl': 500.0, 'streak': 5, 'side': 'long', 'regime': 'NORMAL'}),
]

print("\nLOCAL RL ENGINE RESULTS:")
print("="*80)

for name, state in tests:
    confidence, reason = rl.calculate_confidence(state)
    print(f"\n{name}:")
    print(f"  Confidence: {confidence:.1%}")
    print(f"  Reason: {reason}")
