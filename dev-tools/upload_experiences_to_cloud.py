"""
Upload local experiences to cloud PostgreSQL database.
One-time migration script to sync 11k+ local experiences to cloud.
"""

import json
import asyncio
import aiohttp
import os
from datetime import datetime
from typing import List, Dict, Any

# Cloud API configuration
CLOUD_API_URL = os.getenv("CLOUD_ML_API_URL", "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io")
USER_ID = os.getenv("USER_ID", "dev_user_001")

# File paths
SIGNAL_EXPERIENCES_FILE = "data/local_experiences/signal_experiences_v2.json"
EXIT_EXPERIENCES_FILE = "data/local_experiences/exit_experiences_v2.json"


async def upload_signal_experiences(session: aiohttp.ClientSession, experiences: List[Dict]) -> int:
    """
    Upload signal experiences to cloud API.
    
    Args:
        session: aiohttp session
        experiences: List of signal experiences
        
    Returns:
        Number successfully uploaded
    """
    successful = 0
    failed = 0
    
    print(f"\n📤 Uploading {len(experiences):,} signal experiences...")
    
    # Upload in batches of 50 for better performance
    batch_size = 50
    for i in range(0, len(experiences), batch_size):
        batch = experiences[i:i+batch_size]
        
        # Upload each experience in the batch
        tasks = []
        for exp in batch:
            # Prepare payload matching cloud API expectations
            payload = {
                "user_id": USER_ID,
                "symbol": exp.get("symbol", "ES"),
                "experience_type": "signal",
                "rl_state": exp,  # Full experience as rl_state
                "outcome": {
                    "pnl": exp.get("pnl", 0.0),
                    "outcome": exp.get("outcome", "UNKNOWN"),
                    "took_trade": exp.get("took_trade", True),
                    "confidence": exp.get("confidence", 0.5)
                },
                "quality_score": 1.0 if exp.get("took_trade", True) else 0.5,
                "timestamp": exp.get("timestamp", datetime.utcnow().isoformat())
            }
            
            tasks.append(
                session.post(
                    f"{CLOUD_API_URL}/api/ml/save_experience",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                )
            )
        
        # Execute batch
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for resp in responses:
                if isinstance(resp, Exception):
                    failed += 1
                elif resp.status == 200:
                    successful += 1
                else:
                    failed += 1
            
            # Progress update
            print(f"  Progress: {i+len(batch):,}/{len(experiences):,} "
                  f"(✅ {successful:,} | ❌ {failed:,})", end='\r')
            
            # Small delay between batches to avoid rate limiting
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"\n  ❌ Batch upload error: {e}")
            failed += len(batch)
    
    print()  # New line after progress
    return successful


async def upload_exit_experiences(session: aiohttp.ClientSession, experiences: List[Dict]) -> int:
    """
    Upload exit experiences to cloud API.
    
    Args:
        session: aiohttp session
        experiences: List of exit experiences
        
    Returns:
        Number successfully uploaded
    """
    successful = 0
    failed = 0
    
    print(f"\n📤 Uploading {len(experiences):,} exit experiences...")
    
    # Upload in batches of 25 (exit experiences are larger)
    batch_size = 25
    for i in range(0, len(experiences), batch_size):
        batch = experiences[i:i+batch_size]
        
        tasks = []
        for exp in batch:
            # Prepare payload matching cloud API expectations
            payload = {
                "user_id": USER_ID,
                "regime": exp.get("regime", "UNKNOWN"),
                "exit_params": exp.get("exit_params", {}),
                "outcome": exp.get("outcome", {}),
                "market_state": exp.get("market_state", {}),
                "partial_exits": exp.get("partial_exits", []),
                "timestamp": exp.get("timestamp", datetime.utcnow().isoformat()),
                "quality_score": 1.0 if exp.get("win", False) else 0.5
            }
            
            tasks.append(
                session.post(
                    f"{CLOUD_API_URL}/api/ml/save_exit_experience",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                )
            )
        
        # Execute batch
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for resp in responses:
                if isinstance(resp, Exception):
                    failed += 1
                elif resp.status == 200:
                    successful += 1
                else:
                    failed += 1
            
            # Progress update
            print(f"  Progress: {i+len(batch):,}/{len(experiences):,} "
                  f"(✅ {successful:,} | ❌ {failed:,})", end='\r')
            
            # Small delay between batches
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"\n  ❌ Batch upload error: {e}")
            failed += len(batch)
    
    print()  # New line after progress
    return successful


async def main():
    """Main upload orchestration."""
    print("=" * 70)
    print("🚀 UPLOADING LOCAL EXPERIENCES TO CLOUD DATABASE")
    print("=" * 70)
    print(f"Cloud API: {CLOUD_API_URL}")
    print(f"User ID: {USER_ID}")
    print()
    
    # Load signal experiences
    print("📂 Loading signal experiences...")
    try:
        with open(SIGNAL_EXPERIENCES_FILE, 'r') as f:
            signal_data = json.load(f)
            signal_experiences = signal_data.get('experiences', [])
        print(f"  ✅ Loaded {len(signal_experiences):,} signal experiences")
    except FileNotFoundError:
        print(f"  ❌ File not found: {SIGNAL_EXPERIENCES_FILE}")
        signal_experiences = []
    except Exception as e:
        print(f"  ❌ Error loading signals: {e}")
        signal_experiences = []
    
    # Load exit experiences
    print("📂 Loading exit experiences...")
    try:
        with open(EXIT_EXPERIENCES_FILE, 'r') as f:
            exit_data = json.load(f)
            exit_experiences = exit_data.get('experiences', [])
        print(f"  ✅ Loaded {len(exit_experiences):,} exit experiences")
    except FileNotFoundError:
        print(f"  ❌ File not found: {EXIT_EXPERIENCES_FILE}")
        exit_experiences = []
    except Exception as e:
        print(f"  ❌ Error loading exits: {e}")
        exit_experiences = []
    
    if not signal_experiences and not exit_experiences:
        print("\n❌ No experiences to upload!")
        return
    
    total_experiences = len(signal_experiences) + len(exit_experiences)
    print(f"\n📊 Total experiences to upload: {total_experiences:,}")
    print()
    
    # Confirm before uploading
    response = input("Continue with upload? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Upload cancelled")
        return
    
    # Upload using persistent session
    start_time = datetime.now()
    async with aiohttp.ClientSession() as session:
        signal_uploaded = 0
        exit_uploaded = 0
        
        # Upload signals
        if signal_experiences:
            signal_uploaded = await upload_signal_experiences(session, signal_experiences)
        
        # Upload exits
        if exit_experiences:
            exit_uploaded = await upload_exit_experiences(session, exit_experiences)
    
    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    total_uploaded = signal_uploaded + exit_uploaded
    
    print("\n" + "=" * 70)
    print("📊 UPLOAD SUMMARY")
    print("=" * 70)
    print(f"Signal experiences: {signal_uploaded:,}/{len(signal_experiences):,} uploaded")
    print(f"Exit experiences:   {exit_uploaded:,}/{len(exit_experiences):,} uploaded")
    print(f"Total uploaded:     {total_uploaded:,}/{total_experiences:,}")
    print(f"Duration:           {duration:.1f}s ({total_uploaded/duration:.1f} exp/sec)")
    print()
    
    if total_uploaded == total_experiences:
        print("✅ ALL EXPERIENCES SUCCESSFULLY UPLOADED!")
    elif total_uploaded > 0:
        print(f"⚠️  PARTIAL SUCCESS: {total_experiences - total_uploaded:,} failed")
    else:
        print("❌ UPLOAD FAILED - No experiences uploaded")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
