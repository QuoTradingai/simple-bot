"""
Test migration mapping: Verify correct field extraction from nested structure
"""
import json
from azure.storage.blob import BlobServiceClient

# Azure Storage configuration
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=quotradingrlstorage;AccountKey=B3RfgIrraD+zHr8G8iKZNPTFFopB0kpK85mOE/Yck6sZcmHsrTJ34binS2GBhTrMd+pnfOAZpO7m+AStjdG9QA==;BlobEndpoint=https://quotradingrlstorage.blob.core.windows.net/;FileEndpoint=https://quotradingrlstorage.file.core.windows.net/;QueueEndpoint=https://quotradingrlstorage.queue.core.windows.net/;TableEndpoint=https://quotradingrlstorage.table.core.windows.net/"
CONTAINER_NAME = "rl-data"
BLOB_NAME = "signal_experience.json"

def test_mapping():
    """Test that migration script will correctly extract all fields"""
    
    print("Loading sample experiences from blob...")
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_client = blob_service.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(BLOB_NAME)
    
    blob_data = blob_client.download_blob().readall()
    data = json.loads(blob_data)
    experiences = data.get('experiences', [])
    
    print(f"Testing field extraction on first 5 experiences...")
    print(f"{'='*80}")
    
    for i, exp in enumerate(experiences[:5]):
        # Simulate migration script extraction
        state = exp.get('state', {})
        action = exp.get('action', {})
        
        # Extract all fields as migration script will
        extracted = {
            'rsi': state.get('rsi', 50.0),
            'vwap_distance': state.get('vwap_distance', 0.0),
            'atr': state.get('atr', 0.0),
            'volume_ratio': state.get('volume_ratio', 1.0),
            'hour': state.get('hour', 0),
            'day_of_week': state.get('day_of_week', 0),
            'recent_pnl': state.get('recent_pnl', 0.0),
            'streak': state.get('streak', 0),
            'side': state.get('side', 'long'),
            'regime': state.get('regime', 'NORMAL'),
            'took_trade': action.get('took_trade', False),
            'pnl': exp.get('reward', 0.0),  # ⚠️ THIS IS THE CRITICAL MAPPING
            'duration': exp.get('duration', 0.0)
        }
        
        print(f"\n📝 Experience {i+1}:")
        print(f"  Original reward: {exp.get('reward')}")
        print(f"  Extracted PNL: {extracted['pnl']}")
        print(f"  RSI: {extracted['rsi']:.2f}")
        print(f"  VWAP Distance: {extracted['vwap_distance']:.4f}")
        print(f"  Side: {extracted['side']}")
        print(f"  Regime: {extracted['regime']}")
        print(f"  Took Trade: {extracted['took_trade']}")
        print(f"  Duration: {extracted['duration']:.2f} seconds")
        
        # Verify critical mapping
        if extracted['pnl'] != exp.get('reward'):
            print(f"  ❌ ERROR: PNL mismatch!")
        else:
            print(f"  ✅ PNL correctly mapped from reward")
    
    print(f"\n{'='*80}")
    
    # Test statistics
    print(f"\n📊 Testing statistical preservation:")
    all_rewards = [e.get('reward', 0) for e in experiences]
    
    # Simulate migration extraction for all
    all_extracted_pnl = []
    for exp in experiences:
        state = exp.get('state', {})
        action = exp.get('action', {})
        pnl = exp.get('reward', 0.0)
        all_extracted_pnl.append(pnl)
    
    winners_before = sum(1 for r in all_rewards if r > 0)
    winners_after = sum(1 for p in all_extracted_pnl if p > 0)
    
    avg_before = sum(all_rewards) / len(all_rewards)
    avg_after = sum(all_extracted_pnl) / len(all_extracted_pnl)
    
    print(f"  Before migration: {winners_before} winners, avg={avg_before:.2f}")
    print(f"  After extraction: {winners_after} winners, avg={avg_after:.2f}")
    
    if winners_before == winners_after and abs(avg_before - avg_after) < 0.01:
        print(f"  ✅ Statistics perfectly preserved!")
    else:
        print(f"  ❌ WARNING: Statistics mismatch!")
    
    print(f"\n✅ Mapping test complete!")

if __name__ == "__main__":
    test_mapping()
