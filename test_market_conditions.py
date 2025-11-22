"""
Test Cloud RL API with diverse market conditions
"""
import requests
import json

API_URL = "https://quotrading-flask-api.azurewebsites.net"
LICENSE_KEY = "TEST123"

def test_analyze_signal(test_name, signal_data):
    """Test analyze-signal endpoint"""
    print(f"\n{'='*80}")
    print(f"🧪 {test_name}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/rl/analyze-signal",
            json=signal_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            take = "✅ TAKE" if result.get('take_trade') else "❌ SKIP"
            print(f"{take} | Confidence: {result.get('confidence'):.1%} | {result.get('reason')}")
            return result
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

print("\n" + "="*80)
print("COMPREHENSIVE MARKET CONDITION TESTING")
print("="*80)

# Test 1: Oversold (RSI < 30) - Should have high win rate based on data
test_analyze_signal("Oversold RSI 25 - Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 25.0,
        "vwap_distance": 0.95,
        "atr": 2.5,
        "volume_ratio": 1.2,
        "hour": 10,
        "day_of_week": 2,
        "recent_pnl": 100.0,
        "streak": 2,
        "side": "long",
        "regime": "NORMAL"
    }
})

# Test 2: Very oversold (RSI < 20) - Should be even better
test_analyze_signal("Very Oversold RSI 15 - Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 15.0,
        "vwap_distance": 0.90,
        "atr": 3.0,
        "volume_ratio": 1.5,
        "hour": 9,
        "day_of_week": 1,
        "recent_pnl": 500.0,
        "streak": 5,
        "side": "long",
        "regime": "NORMAL"
    }
})

# Test 3: Neutral RSI 50
test_analyze_signal("Neutral RSI 50 - Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 50.0,
        "vwap_distance": 1.0,
        "atr": 2.0,
        "volume_ratio": 1.0,
        "hour": 12,
        "day_of_week": 2,
        "recent_pnl": 0.0,
        "streak": 0,
        "side": "long",
        "regime": "NORMAL"
    }
})

# Test 4: High RSI 60
test_analyze_signal("High RSI 60 - Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 60.0,
        "vwap_distance": 1.05,
        "atr": 1.5,
        "volume_ratio": 0.9,
        "hour": 14,
        "day_of_week": 3,
        "recent_pnl": -50.0,
        "streak": -1,
        "side": "long",
        "regime": "NORMAL"
    }
})

# Test 5: Overbought (RSI > 70) - Should have lower win rate
test_analyze_signal("Overbought RSI 75 - Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 75.0,
        "vwap_distance": 1.10,
        "atr": 1.0,
        "volume_ratio": 0.8,
        "hour": 15,
        "day_of_week": 4,
        "recent_pnl": -200.0,
        "streak": -3,
        "side": "long",
        "regime": "VOLATILE"
    }
})

# Test 6: Very overbought (RSI > 80)
test_analyze_signal("Very Overbought RSI 85 - Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 85.0,
        "vwap_distance": 1.15,
        "atr": 0.8,
        "volume_ratio": 0.7,
        "hour": 15,
        "day_of_week": 4,
        "recent_pnl": -300.0,
        "streak": -4,
        "side": "long",
        "regime": "VOLATILE"
    }
})

# Test 7: Short side - Oversold (should be bad for shorts)
test_analyze_signal("Oversold RSI 25 - SHORT (Bad)", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 25.0,
        "vwap_distance": 0.95,
        "atr": 2.5,
        "volume_ratio": 1.2,
        "hour": 10,
        "day_of_week": 2,
        "recent_pnl": 0.0,
        "streak": 0,
        "side": "short",
        "regime": "NORMAL"
    }
})

# Test 8: Short side - Overbought (should be good for shorts)
test_analyze_signal("Overbought RSI 75 - SHORT (Good)", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 75.0,
        "vwap_distance": 1.10,
        "atr": 2.0,
        "volume_ratio": 1.1,
        "hour": 11,
        "day_of_week": 2,
        "recent_pnl": 100.0,
        "streak": 2,
        "side": "short",
        "regime": "NORMAL"
    }
})

# Test 9: High volatility (ATR)
test_analyze_signal("High Volatility - ATR 15", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 40.0,
        "vwap_distance": 0.98,
        "atr": 15.0,
        "volume_ratio": 2.0,
        "hour": 10,
        "day_of_week": 1,
        "recent_pnl": 0.0,
        "streak": 0,
        "side": "long",
        "regime": "VOLATILE"
    }
})

# Test 10: Low volatility (ATR)
test_analyze_signal("Low Volatility - ATR 1", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 40.0,
        "vwap_distance": 0.98,
        "atr": 1.0,
        "volume_ratio": 0.8,
        "hour": 14,
        "day_of_week": 3,
        "recent_pnl": 0.0,
        "streak": 0,
        "side": "long",
        "regime": "NORMAL"
    }
})

# Test 11: Perfect setup - All indicators aligned
test_analyze_signal("Perfect Setup - All Aligned", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 20.0,
        "vwap_distance": 0.92,
        "atr": 3.5,
        "volume_ratio": 1.8,
        "hour": 9,
        "day_of_week": 1,
        "recent_pnl": 1000.0,
        "streak": 8,
        "side": "long",
        "regime": "NORMAL"
    }
})

# Test 12: Worst setup - All indicators bad
test_analyze_signal("Worst Setup - All Bad", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 85.0,
        "vwap_distance": 1.20,
        "atr": 0.5,
        "volume_ratio": 0.5,
        "hour": 15,
        "day_of_week": 4,
        "recent_pnl": -500.0,
        "streak": -5,
        "side": "long",
        "regime": "VOLATILE"
    }
})

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)
