"""
Test to find intermediate confidence levels (between 0% and 100%)
"""
import requests

API_URL = "https://quotrading-flask-api.azurewebsites.net"
LICENSE_KEY = "TEST123"

def test_condition(name, rsi, vwap, atr, vol, hour, dow, pnl, streak, side, regime):
    """Quick test function"""
    try:
        response = requests.post(
            f"{API_URL}/api/rl/analyze-signal",
            json={
                "license_key": LICENSE_KEY,
                "symbol": "ES",
                "state": {
                    "rsi": rsi,
                    "vwap_distance": vwap,
                    "atr": atr,
                    "volume_ratio": vol,
                    "hour": hour,
                    "day_of_week": dow,
                    "recent_pnl": pnl,
                    "streak": streak,
                    "side": side,
                    "regime": regime
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            conf = result.get('confidence', 0)
            take = "✅" if result.get('take_trade') else "❌"
            reason = result.get('reason', '').split(' - ')[-1]  # Get just the stats part
            print(f"{take} {conf:5.1%} | {name:40s} | {reason[:80]}")
            return conf
        else:
            print(f"❌ Error | {name}")
            return None
    except Exception as e:
        print(f"❌ Error | {name}: {e}")
        return None

print("\n" + "="*120)
print("SEARCHING FOR INTERMEDIATE CONFIDENCE LEVELS")
print("="*120)
print(f"   Conf  | Test Name                                | Details")
print("="*120)

# Test various RSI levels with long positions
test_condition("RSI 10 Long", 10, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("RSI 15 Long", 15, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("RSI 20 Long", 20, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("RSI 25 Long", 25, 0.95, 2.5, 1.2, 10, 2, 100, 2, "long", "NORMAL")
test_condition("RSI 30 Long", 30, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("RSI 35 Long", 35, 0.98, 2.0, 1.1, 11, 2, 50, 1, "long", "NORMAL")
test_condition("RSI 40 Long", 40, 0.98, 2.0, 1.0, 11, 2, 0, 0, "long", "NORMAL")
test_condition("RSI 45 Long", 45, 1.0, 2.0, 1.0, 12, 2, 0, 0, "long", "NORMAL")

print()
# Test with different VWAP distances
test_condition("VWAP 0.85", 30, 0.85, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("VWAP 0.90", 30, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("VWAP 0.95", 30, 0.95, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("VWAP 1.00", 30, 1.00, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("VWAP 1.05", 30, 1.05, 2.0, 1.0, 11, 2, 0, 0, "long", "NORMAL")

print()
# Test with different ATR levels
test_condition("ATR 0.5", 35, 0.95, 0.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("ATR 1.0", 35, 0.95, 1.0, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("ATR 2.0", 35, 0.95, 2.0, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("ATR 3.0", 35, 0.95, 3.0, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("ATR 5.0", 35, 0.95, 5.0, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("ATR 10.0", 35, 0.95, 10.0, 1.5, 10, 2, 50, 1, "long", "NORMAL")

print()
# Test shorts at different RSI levels
test_condition("RSI 60 Short", 60, 1.05, 2.0, 1.1, 11, 2, 50, 1, "short", "NORMAL")
test_condition("RSI 65 Short", 65, 1.08, 2.0, 1.1, 11, 2, 50, 1, "short", "NORMAL")
test_condition("RSI 70 Short", 70, 1.10, 2.0, 1.1, 11, 2, 100, 2, "short", "NORMAL")
test_condition("RSI 75 Short", 75, 1.10, 2.0, 1.1, 11, 2, 100, 2, "short", "NORMAL")
test_condition("RSI 80 Short", 80, 1.15, 2.5, 1.2, 11, 2, 100, 2, "short", "NORMAL")

print()
# Test different times of day
test_condition("Hour 8 (Pre-market)", 30, 0.95, 2.5, 1.2, 8, 1, 50, 1, "long", "NORMAL")
test_condition("Hour 9 (Open)", 30, 0.95, 2.5, 1.2, 9, 1, 50, 1, "long", "NORMAL")
test_condition("Hour 10", 30, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Hour 11", 30, 0.95, 2.5, 1.2, 11, 2, 50, 1, "long", "NORMAL")
test_condition("Hour 12 (Lunch)", 30, 0.95, 2.5, 1.2, 12, 2, 50, 1, "long", "NORMAL")
test_condition("Hour 13", 30, 0.95, 2.5, 1.2, 13, 3, 50, 1, "long", "NORMAL")
test_condition("Hour 14", 30, 0.95, 2.5, 1.2, 14, 3, 50, 1, "long", "NORMAL")
test_condition("Hour 15 (Close)", 30, 0.95, 2.5, 1.2, 15, 4, 50, 1, "long", "NORMAL")

print()
# Test mixed conditions
test_condition("Mixed 1: RSI 32, VWAP 0.96", 32, 0.96, 2.3, 1.1, 10, 2, 25, 0, "long", "NORMAL")
test_condition("Mixed 2: RSI 38, VWAP 0.99", 38, 0.99, 2.1, 1.0, 11, 2, 0, 0, "long", "NORMAL")
test_condition("Mixed 3: RSI 42, VWAP 1.01", 42, 1.01, 1.9, 0.9, 12, 3, -25, 0, "long", "NORMAL")
test_condition("Mixed 4: RSI 28, ATR 4", 28, 0.94, 4.0, 1.3, 9, 1, 75, 1, "long", "NORMAL")
test_condition("Mixed 5: RSI 68, Short", 68, 1.08, 2.2, 1.1, 11, 2, 75, 1, "short", "NORMAL")

print()
# Test volume ratios
test_condition("Volume 0.5x", 35, 0.95, 2.5, 0.5, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Volume 0.8x", 35, 0.95, 2.5, 0.8, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Volume 1.0x", 35, 0.95, 2.5, 1.0, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Volume 1.2x", 35, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Volume 1.5x", 35, 0.95, 2.5, 1.5, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Volume 2.0x", 35, 0.95, 2.5, 2.0, 10, 2, 50, 1, "long", "NORMAL")

print("\n" + "="*120)
print("SEARCH COMPLETE")
print("="*120)
