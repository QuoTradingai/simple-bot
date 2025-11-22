"""
Test Cloud RL API with real migrated data
"""
import requests
import json

API_URL = "https://quotrading-flask-api.azurewebsites.net"
LICENSE_KEY = "TEST123"

def test_analyze_signal(test_name, signal_data):
    """Test analyze-signal endpoint"""
    print(f"\n{'='*80}")
    print(f"🧪 Test: {test_name}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/rl/analyze-signal",
            json=signal_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Response:")
            print(f"  Take Trade: {result.get('take_trade')}")
            print(f"  Confidence: {result.get('confidence'):.1%}")
            print(f"  Reason: {result.get('reason')}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

# Test 1: Good conditions (similar to winning trades)
print("\n" + "="*80)
print("TESTING CLOUD RL ENGINE WITH REAL MIGRATED DATA")
print("="*80)

test1 = test_analyze_signal("Good Conditions - Low RSI Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 25.0,  # Low RSI like winners
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

# Test 2: Bad conditions (similar to losing trades)
test2 = test_analyze_signal("Bad Conditions - High RSI Long", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 70.0,  # High RSI - overbought
        "vwap_distance": 1.05,
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

# Test 3: Neutral conditions
test3 = test_analyze_signal("Neutral Conditions - Mid RSI", {
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

# Test 4: Strong winning pattern
test4 = test_analyze_signal("Strong Winner Pattern - Very Low RSI", {
    "license_key": LICENSE_KEY,
    "symbol": "ES",
    "state": {
        "rsi": 20.0,  # Very low RSI
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

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if test1 and test2 and test3 and test4:
    confidences = [
        test1.get('confidence', 0),
        test2.get('confidence', 0),
        test3.get('confidence', 0),
        test4.get('confidence', 0)
    ]
    
    print(f"\nConfidence Levels:")
    print(f"  Good conditions: {test1.get('confidence', 0):.1%}")
    print(f"  Bad conditions: {test2.get('confidence', 0):.1%}")
    print(f"  Neutral conditions: {test3.get('confidence', 0):.1%}")
    print(f"  Strong winner: {test4.get('confidence', 0):.1%}")
    
    # Check if we have variation (not stuck at 65%)
    unique_confidences = len(set(confidences))
    
    if unique_confidences > 1:
        print(f"\n✅ SUCCESS: RL engine is analyzing real data!")
        print(f"   Found {unique_confidences} different confidence levels")
        print(f"   Not stuck at 65% anymore!")
    else:
        print(f"\n⚠️ WARNING: All confidences are the same: {confidences[0]:.1%}")
        print(f"   May still be stuck or all conditions similar")
else:
    print("\n❌ Some tests failed - check errors above")

print("\n" + "="*80)
