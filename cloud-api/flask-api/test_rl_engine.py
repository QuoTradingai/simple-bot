"""
Test RL engine with real migrated data
"""
import requests
import json

API_URL = "https://quotrading-flask-api.azurewebsites.net"

def test_rl_engine():
    """Test RL engine with different market conditions"""
    
    print("🧪 Testing RL Engine with Real Data")
    print("="*70)
    
    # Test Case 1: Good conditions (similar to winners in DB)
    test1 = {
        "license_key": "TEST123",
        "symbol": "ES",
        "state": {
            "rsi": 25.5,  # Low RSI like winners
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
    }
    
    # Test Case 2: Bad conditions (similar to losers in DB)
    test2 = {
        "license_key": "TEST123",
        "symbol": "ES",
        "state": {
            "rsi": 50.0,  # Neutral RSI like losers
            "vwap_distance": 0.99,
            "atr": 1.5,
            "volume_ratio": 0.8,
            "hour": 15,
            "day_of_week": 4,
            "recent_pnl": -100.0,
            "streak": -3,
            "side": "long",
            "regime": "NORMAL"
        }
    }
    
    # Test Case 3: Volatile regime
    test3 = {
        "license_key": "TEST123",
        "symbol": "ES",
        "state": {
            "rsi": 70.0,
            "vwap_distance": 1.02,
            "atr": 5.0,
            "volume_ratio": 2.0,
            "hour": 9,
            "day_of_week": 1,
            "recent_pnl": -200.0,
            "streak": -5,
            "side": "short",
            "regime": "VOLATILE"
        }
    }
    
    tests = [
        ("Good Conditions (Low RSI, Positive Streak)", test1),
        ("Bad Conditions (Neutral RSI, Negative Streak)", test2),
        ("Volatile Regime (High RSI, Large Losses)", test3)
    ]
    
    for name, payload in tests:
        print(f"\n📊 Test: {name}")
        print("-" * 70)
        
        try:
            response = requests.post(
                f"{API_URL}/api/v1/analyze-signal",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"   Take Trade: {result.get('take_trade')}")
                print(f"   Confidence: {result.get('confidence'):.2%}")
                print(f"   Reason: {result.get('reason')}")
                
                # Check if confidence is different from 65%
                confidence = result.get('confidence', 0)
                if abs(confidence - 0.65) > 0.01:
                    print(f"   🎯 GOOD: Confidence varies from 65% baseline!")
                else:
                    print(f"   ⚠️  WARNING: Still at 65% - may indicate issue")
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ Test complete!")

if __name__ == "__main__":
    test_rl_engine()
