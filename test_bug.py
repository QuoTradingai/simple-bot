# Test to verify the bug
experiences = [
    {'side': 'LONG', 'rsi': 35, 'pnl': 50},
    {'side': 'SHORT', 'rsi': 65, 'pnl': -20},
    {'signal_type': 'LONG', 'rsi': 30, 'pnl': 100}
]

signal_type = 'LONG'

print("OLD CODE (BROKEN):")
for exp in experiences:
    if exp.get('signal_type', exp.get('signal')) != signal_type:
        print(f"  ❌ SKIP: {exp}")
        continue
    print(f"  ✅ MATCH: {exp}")

print("\nNEW CODE (FIXED):")
for exp in experiences:
    exp_signal = exp.get('signal_type') or exp.get('signal') or exp.get('side', '').upper()
    if exp_signal.upper() != signal_type.upper():
        print(f"  ❌ SKIP: {exp}")
        continue
    print(f"  ✅ MATCH: {exp}")
