"""
Quick test of cloud RL API connectivity
"""
import aiohttp
import asyncio
import hashlib

CLOUD_RL_API_URL = "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io"

# Get same user ID as production bot
broker_username = "alvarezjose4201@gmail.com"
USER_ID = hashlib.md5(broker_username.encode()).hexdigest()[:12]

async def test_rl_api():
    # Test with MES
    payload_mes = {
        "user_id": USER_ID,
        "symbol": "MES",
        "side": "long",
        "rsi": 35,
        "vwap_distance": -0.5,
        "volume_ratio": 1.2,
        "streak": 0,
        "time_of_day_score": 0.7,
        "volatility": 1.0,
        "exploration_rate": 5
    }
    
    # Test with MNQ
    payload_mnq = {
        "user_id": USER_ID,
        "symbol": "MNQ",
        "side": "long",
        "rsi": 35,
        "vwap_distance": -0.5,
        "volume_ratio": 1.2,
        "streak": 0,
        "time_of_day_score": 0.7,
        "volatility": 1.0,
        "exploration_rate": 5
    }
    
    print(f"Testing Cloud RL API with User ID: {USER_ID}")
    print(f"URL: {CLOUD_RL_API_URL}/api/ml/get_confidence\n")
    
    for symbol, payload in [("MES", payload_mes), ("MNQ", payload_mnq)]:
        print(f"\n{'='*60}")
        print(f"Testing {symbol}")
        print(f"{'='*60}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{CLOUD_RL_API_URL}/api/ml/get_confidence",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as response:
                    print(f"Response Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"\n✅ {symbol} Response:")
                        print(f"  Should Take: {data.get('should_take', False)}")
                        print(f"  Confidence: {data.get('ml_confidence', 0):.1%}")
                        print(f"  Reason: {data.get('reason', 'N/A')}")
                        print(f"  Total Experiences: {data.get('total_experience_count', 0)}")
                        print(f"  Sample Size (matched): {data.get('sample_size', 0)}")
                        print(f"  Win Rate: {data.get('win_rate', 0):.1%}")
                    else:
                        text = await response.text()
                        print(f"❌ Error: {text}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_rl_api())
