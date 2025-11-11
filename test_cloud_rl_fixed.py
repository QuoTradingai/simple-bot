"""
Test cloud RL API with CORRECT endpoint and payload format
"""
import aiohttp
import asyncio
import hashlib

CLOUD_RL_API_URL = "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io"

# Get same user ID as production bot
broker_username = "alvarezjose4201@gmail.com"
USER_ID = hashlib.md5(broker_username.encode()).hexdigest()[:12]

async def test_rl_api():
    # Test with MES - LONG signal
    payload_mes = {
        "user_id": USER_ID,
        "symbol": "MES",
        "signal": "LONG",  # Correct field name!
        "entry_price": 5950.0,
        "vwap": 5948.5,
        "rsi": 35,
        "vix": 15
    }
    
    # Test with MNQ - SHORT signal  
    payload_mnq = {
        "user_id": USER_ID,
        "symbol": "MNQ",
        "signal": "SHORT",  # Correct field name!
        "entry_price": 20250.0,
        "vwap": 20252.5,
        "rsi": 65,
        "vix": 15
    }
    
    print(f"Testing Cloud RL API with User ID: {USER_ID}")
    print(f"URL: {CLOUD_RL_API_URL}/api/ml/should_take_signal\n")
    
    for symbol, payload in [("MES LONG", payload_mes), ("MNQ SHORT", payload_mnq)]:
        print(f"\n{'='*60}")
        print(f"Testing {symbol}")
        print(f"Payload: {payload}")
        print(f"{'='*60}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{CLOUD_RL_API_URL}/api/ml/should_take_signal",  # CORRECT endpoint!
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as response:
                    print(f"Response Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"\n✅ {symbol} Response:")
                        print(f"  Should Take: {data.get('take_trade', False)}")
                        print(f"  Confidence: {data.get('confidence', 0)*100:.1f}%")
                        print(f"  Reason: {data.get('reason', 'N/A')}")
                        print(f"  Sample Size (matched): {data.get('sample_size', 0)}")
                        print(f"  Win Rate: {data.get('win_rate', 0)*100:.1f}%")
                        print(f"  Avg P&L: ${data.get('avg_pnl', 0):.2f}")
                        print(f"  Risk Level: {data.get('risk_level', 'UNKNOWN')}")
                        
                        # Success if sample_size > 0!
                        if data.get('sample_size', 0) > 0:
                            print(f"\n🎉 SUCCESS! Found {data['sample_size']} matching experiences!")
                        else:
                            print(f"\n⚠️  No matching experiences found (need similar market conditions)")
                    else:
                        text = await response.text()
                        print(f"❌ Error: {text}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_rl_api())
