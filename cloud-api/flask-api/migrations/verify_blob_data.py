"""
Verification script: Check blob data before migration
"""
import json
from azure.storage.blob import BlobServiceClient

# Azure Storage configuration
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=quotradingrlstorage;AccountKey=B3RfgIrraD+zHr8G8iKZNPTFFopB0kpK85mOE/Yck6sZcmHsrTJ34binS2GBhTrMd+pnfOAZpO7m+AStjdG9QA==;BlobEndpoint=https://quotradingrlstorage.blob.core.windows.net/;FileEndpoint=https://quotradingrlstorage.file.core.windows.net/;QueueEndpoint=https://quotradingrlstorage.queue.core.windows.net/;TableEndpoint=https://quotradingrlstorage.table.core.windows.net/"
CONTAINER_NAME = "rl-data"
BLOB_NAME = "signal_experience.json"

def verify_blob_data():
    """Verify blob data structure and statistics"""
    
    print("Connecting to Azure Blob Storage...")
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_client = blob_service.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(BLOB_NAME)
    
    print("Downloading blob data...")
    blob_data = blob_client.download_blob().readall()
    data = json.loads(blob_data)
    experiences = data.get('experiences', [])
    
    print(f"\n📊 BLOB DATA VERIFICATION")
    print(f"{'='*60}")
    print(f"Total experiences: {len(experiences)}")
    
    if not experiences:
        print("❌ No experiences found!")
        return
    
    # Check structure of first experience
    first_exp = experiences[0]
    print(f"\n📝 First experience structure:")
    print(f"  Keys: {list(first_exp.keys())}")
    
    if 'state' in first_exp:
        print(f"  State keys: {list(first_exp['state'].keys())}")
    if 'action' in first_exp:
        print(f"  Action keys: {list(first_exp['action'].keys())}")
    
    # Calculate statistics
    rewards = [e.get('reward', 0) for e in experiences]
    winners = sum(1 for r in rewards if r > 0)
    losers = sum(1 for r in rewards if r <= 0)
    total_reward = sum(rewards)
    avg_reward = total_reward / len(rewards) if rewards else 0
    
    print(f"\n💰 Reward Statistics:")
    print(f"  Winners: {winners} ({winners/len(experiences)*100:.1f}%)")
    print(f"  Losers: {losers} ({losers/len(experiences)*100:.1f}%)")
    print(f"  Average reward: {avg_reward:.2f}")
    print(f"  Min reward: {min(rewards):.2f}")
    print(f"  Max reward: {max(rewards):.2f}")
    print(f"  Total reward: {total_reward:.2f}")
    
    # Show sample experiences
    print(f"\n📋 Sample Experiences:")
    print(f"{'='*60}")
    
    # Show first winner
    winner = next((e for e in experiences if e.get('reward', 0) > 0), None)
    if winner:
        print(f"\n✅ Sample Winner (reward={winner.get('reward')}):")
        print(f"  State: RSI={winner.get('state', {}).get('rsi')}, "
              f"VWAP={winner.get('state', {}).get('vwap_distance'):.4f}, "
              f"Side={winner.get('state', {}).get('side')}, "
              f"Regime={winner.get('state', {}).get('regime')}")
        print(f"  Action: took_trade={winner.get('action', {}).get('took_trade')}")
        print(f"  Duration: {winner.get('duration')} seconds")
    
    # Show first loser
    loser = next((e for e in experiences if e.get('reward', 0) < 0), None)
    if loser:
        print(f"\n❌ Sample Loser (reward={loser.get('reward')}):")
        print(f"  State: RSI={loser.get('state', {}).get('rsi')}, "
              f"VWAP={loser.get('state', {}).get('vwap_distance'):.4f}, "
              f"Side={loser.get('state', {}).get('side')}, "
              f"Regime={loser.get('state', {}).get('regime')}")
        print(f"  Action: took_trade={loser.get('action', {}).get('took_trade')}")
        print(f"  Duration: {loser.get('duration')} seconds")
    
    print(f"\n{'='*60}")
    print(f"✅ Blob data verification complete!")

if __name__ == "__main__":
    verify_blob_data()
