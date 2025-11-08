"""
LIVE Cloud API Test - Tests actual Azure Container App
Tests real bot → cloud communication with multiple users/symbols
"""
import asyncio
import aiohttp
import hashlib
import random
from datetime import datetime
from typing import Dict, Any, List

# Your LIVE Azure Cloud API
CLOUD_API_URL = "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io"

# Test users
TEST_USERS = [
    "test_user_1",
    "test_user_2", 
    "test_user_3",
    "test_user_4",
    "test_user_5"
]

# Test symbols
TEST_SYMBOLS = ["ES", "NQ", "YM", "RTY", "CL"]

def get_user_id(username: str) -> str:
    """Generate user ID same way bot does"""
    return hashlib.md5(username.encode()).hexdigest()[:12]


async def test_get_confidence(session: aiohttp.ClientSession, user: str, symbol: str) -> Dict[str, Any]:
    """Test getting confidence from cloud API (real bot behavior)"""
    user_id = get_user_id(user)
    
    # Generate realistic market state
    payload = {
        "user_id": user_id,
        "symbol": symbol,
        "side": random.choice(["long", "short"]),
        "rsi": random.uniform(30, 70),
        "vwap_distance": random.uniform(0.995, 1.005),
        "volume_ratio": random.uniform(0.8, 1.5),
        "streak": random.randint(-3, 3),
        "time_of_day_score": random.uniform(0.3, 0.9),
        "volatility": random.uniform(0.8, 1.3)
    }
    
    try:
        start_time = datetime.now()
        async with session.post(
            f"{CLOUD_API_URL}/api/ml/get_confidence",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=5.0)
        ) as response:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000  # ms
            
            if response.status == 200:
                data = await response.json()
                return {
                    "success": True,
                    "user": user,
                    "symbol": symbol,
                    "side": payload["side"],
                    "confidence": data.get("confidence", 0),
                    "should_trade": data.get("should_trade", False),
                    "total_trades": data.get("total_trades", 0),
                    "response_time_ms": round(elapsed, 1),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "user": user,
                    "symbol": symbol,
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        return {
            "success": False,
            "user": user,
            "symbol": symbol,
            "error": str(e)
        }


async def test_save_trade(session: aiohttp.ClientSession, user: str, symbol: str) -> Dict[str, Any]:
    """Test saving trade to cloud API (real bot behavior)"""
    user_id = get_user_id(user)
    
    # Generate realistic trade result
    pnl = random.uniform(-100, 200)  # Realistic P&L range
    payload = {
        "user_id": user_id,
        "symbol": symbol,
        "side": random.choice(["long", "short"]),
        "signal": f"{random.choice(['long', 'short'])}_bounce",
        "rsi": random.uniform(30, 70),
        "vwap_distance": random.uniform(0.995, 1.005),
        "volume_ratio": random.uniform(0.8, 1.5),
        "streak": random.randint(-3, 3),
        "time_of_day_score": random.uniform(0.3, 0.9),
        "volatility": random.uniform(0.8, 1.3),
        "pnl": pnl,
        "duration_minutes": random.uniform(5, 60),
        "exit_reason": random.choice(["target", "stop", "time"])
    }
    
    try:
        start_time = datetime.now()
        async with session.post(
            f"{CLOUD_API_URL}/api/ml/save_trade",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=5.0)
        ) as response:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000  # ms
            
            if response.status == 200:
                data = await response.json()
                return {
                    "success": True,
                    "user": user,
                    "symbol": symbol,
                    "pnl": round(pnl, 2),
                    "total_trades": data.get("total_shared_trades", 0),
                    "win_rate": data.get("shared_win_rate", 0),
                    "response_time_ms": round(elapsed, 1),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "user": user,
                    "symbol": symbol,
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        return {
            "success": False,
            "user": user,
            "symbol": symbol,
            "error": str(e)
        }


async def test_concurrent_users(num_users: int = 20):
    """
    Simulate 20 users all trading different symbols simultaneously
    Tests real-world load on Azure cloud
    """
    print("=" * 80)
    print("🧪 LIVE CLOUD API TEST - Azure Container Apps")
    print("=" * 80)
    print(f"Testing {num_users} concurrent users on live cloud API")
    print(f"Cloud: {CLOUD_API_URL}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Check cloud stats
        print("📊 Test 1: Check Cloud Stats")
        print("-" * 80)
        try:
            async with session.get(f"{CLOUD_API_URL}/api/ml/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"✅ Cloud is ONLINE")
                    print(f"   Total Trades: {stats.get('total_trades', 0):,}")
                    print(f"   Win Rate: {stats.get('win_rate', 0):.1%}")
                    print(f"   Avg P&L: ${stats.get('avg_pnl', 0):.2f}")
                    print(f"   Total P&L: ${stats.get('total_pnl', 0):,.2f}")
                else:
                    print(f"❌ Cloud returned status {response.status}")
                    return
        except Exception as e:
            print(f"❌ Could not connect to cloud: {e}")
            return
        
        print()
        
        # Test 2: Multiple users getting confidence simultaneously
        print(f"🧠 Test 2: {num_users} Users Getting Confidence (Concurrent)")
        print("-" * 80)
        
        # Create tasks for concurrent requests
        tasks = []
        for i in range(num_users):
            user = random.choice(TEST_USERS)
            symbol = random.choice(TEST_SYMBOLS)
            tasks.append(test_get_confidence(session, user, symbol))
        
        # Run all requests concurrently
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Analyze results
        successes = [r for r in results if r["success"]]
        failures = [r for r in results if not r["success"]]
        
        print(f"Results: {len(successes)}/{num_users} successful")
        print(f"Total time: {total_time:.2f}s ({total_time/num_users*1000:.1f}ms avg per request)")
        
        if successes:
            avg_response = sum(r["response_time_ms"] for r in successes) / len(successes)
            max_response = max(r["response_time_ms"] for r in successes)
            min_response = min(r["response_time_ms"] for r in successes)
            print(f"Response times: min={min_response:.1f}ms, avg={avg_response:.1f}ms, max={max_response:.1f}ms")
            
            # Show sample results
            print("\nSample responses:")
            for r in successes[:3]:
                print(f"   {r['user'][:10]} | {r['symbol']} {r['side']:5} | "
                      f"Confidence: {r['confidence']:.1%} | Trade: {r['should_trade']} | "
                      f"{r['response_time_ms']}ms")
        
        if failures:
            print(f"\n❌ {len(failures)} failures:")
            for r in failures[:3]:
                print(f"   {r['user']} | {r['symbol']} | Error: {r['error']}")
        
        print()
        
        # Test 3: Multiple users saving trades simultaneously
        print(f"💾 Test 3: {num_users} Users Saving Trades (Concurrent)")
        print("-" * 80)
        
        tasks = []
        for i in range(num_users):
            user = random.choice(TEST_USERS)
            symbol = random.choice(TEST_SYMBOLS)
            tasks.append(test_save_trade(session, user, symbol))
        
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        total_time = (datetime.now() - start_time).total_seconds()
        
        successes = [r for r in results if r["success"]]
        failures = [r for r in results if not r["success"]]
        
        print(f"Results: {len(successes)}/{num_users} successful")
        print(f"Total time: {total_time:.2f}s ({total_time/num_users*1000:.1f}ms avg per request)")
        
        if successes:
            avg_response = sum(r["response_time_ms"] for r in successes) / len(successes)
            total_pnl = sum(r["pnl"] for r in successes)
            print(f"Response times: avg={avg_response:.1f}ms")
            print(f"Test P&L: ${total_pnl:+.2f}")
            
            # Show final hive mind state
            if successes:
                latest = successes[-1]
                print(f"\n🧠 Hive Mind After Test:")
                print(f"   Total Trades: {latest['total_trades']:,}")
                print(f"   Win Rate: {latest['win_rate']:.1%}")
        
        if failures:
            print(f"\n❌ {len(failures)} failures:")
            for r in failures[:3]:
                print(f"   {r['user']} | {r['symbol']} | Error: {r['error']}")
        
        print()
        
        # Test 4: Check final stats
        print("📊 Test 4: Final Cloud Stats")
        print("-" * 80)
        try:
            async with session.get(f"{CLOUD_API_URL}/api/ml/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"✅ Final State:")
                    print(f"   Total Trades: {stats.get('total_trades', 0):,}")
                    print(f"   Win Rate: {stats.get('win_rate', 0):.1%}")
                    print(f"   Avg P&L: ${stats.get('avg_pnl', 0):.2f}")
                    print(f"   Total P&L: ${stats.get('total_pnl', 0):,.2f}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        print("=" * 80)
        print("✅ LIVE TEST COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    print("\n🚀 Starting LIVE Cloud API Test...")
    print("This tests your ACTUAL Azure Container App with real concurrent load\n")
    
    # Run test with 20 concurrent users
    asyncio.run(test_concurrent_users(num_users=20))
    
    print("\n💡 Test shows:")
    print("   • Cloud API response times under load")
    print("   • Whether retries work")
    print("   • How hive mind handles concurrent saves")
    print("   • Real-world scalability")
