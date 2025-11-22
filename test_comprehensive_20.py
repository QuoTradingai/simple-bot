"""
Test cloud RL engine with 20 samples across diverse market conditions
"""
import requests

API_URL = "https://quotrading-flask-api.azurewebsites.net"
LICENSE_KEY = "TEST123"

def test_condition(name, rsi, vwap, atr, vol, hour, dow, pnl, streak, side, regime):
    """Test a market condition"""
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
            take = "[TAKE]" if result.get('take_trade') else "[SKIP]"
            reason = result.get('reason', '').split(' - ')[-1]
            print(f"{take:8s} {conf:5.1%} | {name:45s} | {reason}")
            return conf
        else:
            print(f"[ERROR] | {name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] | {name}: {e}")
        return None

print("\n" + "="*130)
print("TESTING CLOUD RL ENGINE WITH 20 SIMILAR EXPERIENCES")
print("="*130)
print(f"Decision  Conf  | Test Scenario                                | Details")
print("="*130)

print("\n--- LONG POSITIONS: RSI RANGE ---")
test_condition("Very Oversold: RSI 10", 10, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("Very Oversold: RSI 15", 15, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("Oversold: RSI 20", 20, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("Oversold: RSI 25", 25, 0.95, 2.5, 1.2, 10, 2, 100, 2, "long", "NORMAL")
test_condition("Low Normal: RSI 30", 30, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Low Normal: RSI 35", 35, 0.98, 2.0, 1.1, 11, 2, 50, 1, "long", "NORMAL")
test_condition("Neutral: RSI 40", 40, 0.98, 2.0, 1.0, 11, 2, 0, 0, "long", "NORMAL")
test_condition("Neutral: RSI 45", 45, 1.0, 2.0, 1.0, 12, 2, 0, 0, "long", "NORMAL")
test_condition("Neutral: RSI 50", 50, 1.0, 2.0, 1.0, 12, 2, 0, 0, "long", "NORMAL")
test_condition("High: RSI 55", 55, 1.02, 2.0, 1.0, 13, 3, -50, -1, "long", "NORMAL")
test_condition("High: RSI 60", 60, 1.05, 2.0, 1.0, 13, 3, -100, -2, "long", "NORMAL")
test_condition("Overbought: RSI 70", 70, 1.10, 2.0, 1.0, 14, 3, -100, -2, "long", "NORMAL")
test_condition("Overbought: RSI 75", 75, 1.10, 2.0, 1.0, 14, 3, -100, -2, "long", "NORMAL")
test_condition("Very Overbought: RSI 85", 85, 1.15, 2.5, 1.0, 15, 4, -150, -3, "long", "NORMAL")

print("\n--- SHORT POSITIONS: RSI RANGE ---")
test_condition("Oversold: RSI 25 SHORT", 25, 0.90, 2.5, 1.2, 10, 2, -100, -2, "short", "NORMAL")
test_condition("Low: RSI 35 SHORT", 35, 0.95, 2.0, 1.1, 11, 2, -50, -1, "short", "NORMAL")
test_condition("Neutral: RSI 50 SHORT", 50, 1.0, 2.0, 1.0, 12, 2, 0, 0, "short", "NORMAL")
test_condition("High: RSI 60 SHORT", 60, 1.05, 2.0, 1.1, 11, 2, 50, 1, "short", "NORMAL")
test_condition("Overbought: RSI 70 SHORT", 70, 1.10, 2.0, 1.1, 11, 2, 100, 2, "short", "NORMAL")
test_condition("Overbought: RSI 75 SHORT", 75, 1.10, 2.0, 1.1, 11, 2, 100, 2, "short", "NORMAL")
test_condition("Very Overbought: RSI 85 SHORT", 85, 1.15, 2.5, 1.2, 11, 2, 100, 2, "short", "NORMAL")

print("\n--- VOLATILITY CONDITIONS ---")
test_condition("Very Low Volatility: ATR 0.5", 35, 0.95, 0.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Low Volatility: ATR 1.0", 35, 0.95, 1.0, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Normal Volatility: ATR 2.5", 35, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Medium Volatility: ATR 5.0", 30, 0.90, 5.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("High Volatility: ATR 10.0", 25, 0.85, 10.0, 1.8, 9, 1, 100, 2, "long", "NORMAL")
test_condition("Very High Volatility: ATR 15.0", 20, 0.80, 15.0, 2.0, 9, 1, 100, 2, "long", "NORMAL")

print("\n--- VWAP DISTANCE (MEAN REVERSION) ---")
test_condition("Far Below VWAP: 0.85", 30, 0.85, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("Below VWAP: 0.90", 30, 0.90, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("Slightly Below: 0.95", 30, 0.95, 3.0, 1.5, 9, 1, 100, 2, "long", "NORMAL")
test_condition("At VWAP: 1.00", 50, 1.00, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Slightly Above: 1.05", 60, 1.05, 2.0, 1.0, 11, 2, 0, 0, "long", "NORMAL")
test_condition("Above VWAP: 1.10", 70, 1.10, 2.0, 1.0, 11, 2, -50, -1, "long", "NORMAL")
test_condition("Far Above VWAP: 1.15", 75, 1.15, 2.5, 1.0, 12, 2, -100, -2, "long", "NORMAL")

print("\n--- VOLUME CONDITIONS ---")
test_condition("Very Low Volume: 0.3x", 35, 0.95, 2.5, 0.3, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Low Volume: 0.6x", 35, 0.95, 2.5, 0.6, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Normal Volume: 1.0x", 35, 0.95, 2.5, 1.0, 10, 2, 50, 1, "long", "NORMAL")
test_condition("High Volume: 1.5x", 35, 0.95, 2.5, 1.5, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Very High Volume: 2.5x", 35, 0.95, 2.5, 2.5, 10, 2, 50, 1, "long", "NORMAL")

print("\n--- TIME OF DAY ---")
test_condition("Pre-Market: 8am", 30, 0.95, 2.5, 1.2, 8, 1, 50, 1, "long", "NORMAL")
test_condition("Market Open: 9:30am", 30, 0.95, 2.5, 1.2, 9, 1, 50, 1, "long", "NORMAL")
test_condition("Morning: 10am", 30, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("Late Morning: 11am", 30, 0.95, 2.5, 1.2, 11, 2, 50, 1, "long", "NORMAL")
test_condition("Lunch: 12pm", 30, 0.95, 2.5, 1.2, 12, 2, 50, 1, "long", "NORMAL")
test_condition("Afternoon: 1pm", 30, 0.95, 2.5, 1.2, 13, 3, 50, 1, "long", "NORMAL")
test_condition("Late Day: 2pm", 30, 0.95, 2.5, 1.2, 14, 3, 50, 1, "long", "NORMAL")
test_condition("Close: 3pm", 30, 0.95, 2.5, 1.2, 15, 4, 50, 1, "long", "NORMAL")

print("\n--- STREAK & RECENT PNL ---")
test_condition("Hot Streak: +3 wins, +$500", 30, 0.95, 2.5, 1.2, 10, 2, 500, 3, "long", "NORMAL")
test_condition("Winning: +2 wins, +$200", 30, 0.95, 2.5, 1.2, 10, 2, 200, 2, "long", "NORMAL")
test_condition("Fresh Start: 0 streak, $0", 30, 0.95, 2.5, 1.2, 10, 2, 0, 0, "long", "NORMAL")
test_condition("Cold Streak: -2 losses, -$200", 30, 0.95, 2.5, 1.2, 10, 2, -200, -2, "long", "NORMAL")
test_condition("Bleeding: -3 losses, -$500", 30, 0.95, 2.5, 1.2, 10, 2, -500, -3, "long", "NORMAL")

print("\n--- REGIME CONDITIONS ---")
test_condition("Normal Market", 30, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "NORMAL")
test_condition("High Volatility Regime", 30, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "HIGH_VOL")
test_condition("Trending Up", 30, 0.95, 2.5, 1.2, 10, 2, 50, 1, "long", "TRENDING")

print("\n--- EDGE CASES ---")
test_condition("Perfect Setup: Oversold + Below VWAP + High Vol", 20, 0.85, 8.0, 1.8, 9, 1, 100, 2, "long", "NORMAL")
test_condition("Terrible Setup: Overbought + Above VWAP + Low Vol", 75, 1.15, 1.0, 0.5, 14, 3, -100, -2, "long", "NORMAL")
test_condition("Mixed Signals: Oversold but Above VWAP", 25, 1.10, 2.5, 1.2, 10, 2, 0, 0, "long", "NORMAL")
test_condition("Counter-Trend Short: Oversold", 20, 0.85, 3.0, 1.5, 9, 1, -100, -2, "short", "NORMAL")

print("\n" + "="*130)
print("COMPREHENSIVE TESTING COMPLETE - 20 SIMILAR EXPERIENCES")
print("="*130)
