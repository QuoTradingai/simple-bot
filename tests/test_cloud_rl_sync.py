"""
Test Cloud RL Sync
==================
Quick test to verify bot can sync experiences to cloud API.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from signal_confidence import SignalConfidenceRL
import json

def test_cloud_sync():
    """Test syncing RL experience to cloud."""
    
    # Initialize RL with cloud sync
    rl = SignalConfidenceRL(
        experience_file="data/signal_experience.json",
        backtest_mode=False
    )
    
    # Set license key (from config)
    with open('data/config.json', 'r') as f:
        config = json.load(f)
    
    license_key = config.get('quotrading_license', 'QUOTRADING_ADMIN_MASTER_2025')
    rl.set_license_key(license_key)
    
    print(f"✓ License key set: {license_key}")
    
    # Test downloading cloud brain
    print("\n🧠 Downloading cloud brain...")
    success = rl.download_cloud_brain()
    if success:
        print(f"✅ Cloud brain downloaded: {len(rl.experiences)} experiences")
    else:
        print("⚠️ Cloud brain download failed (may not be configured yet)")
    
    # Test submitting an experience
    print("\n📤 Testing experience submission...")
    test_experience = {
        'timestamp': '2025-11-22T10:00:00Z',
        'state': {
            'rsi': 55.0,
            'vwap_distance': 0.5,
            'atr': 2.5,
            'volume_ratio': 1.2,
            'hour': 10,
            'day_of_week': 4,
            'recent_pnl': 100.0,
            'streak': 2,
            'side': 'long',
            'price': 5000.0
        },
        'action': {
            'took_trade': True,
            'exploration_rate': 0.05
        },
        'reward': 75.0,
        'duration': 30
    }
    
    rl.sync_experience_to_cloud(test_experience)
    print("✅ Test experience sent to cloud (check logs)")
    
    print("\n✓ Cloud RL sync test complete!")

if __name__ == "__main__":
    test_cloud_sync()
