"""
One-time migration script: Copy RL experiences from Azure Blob to PostgreSQL
Run this ONCE after creating the rl_experiences table
"""
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from azure.storage.blob import BlobServiceClient

# Azure Storage configuration
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=quotradingrlstorage;AccountKey=B3RfgIrraD+zHr8G8iKZNPTFFopB0kpK85mOE/Yck6sZcmHsrTJ34binS2GBhTrMd+pnfOAZpO7m+AStjdG9QA==;BlobEndpoint=https://quotradingrlstorage.blob.core.windows.net/;FileEndpoint=https://quotradingrlstorage.file.core.windows.net/;QueueEndpoint=https://quotradingrlstorage.queue.core.windows.net/;TableEndpoint=https://quotradingrlstorage.table.core.windows.net/"
CONTAINER_NAME = "rl-data"
BLOB_NAME = "signal_experience.json"

# PostgreSQL configuration
DB_HOST = "quotrading-db.postgres.database.azure.com"
DB_NAME = "quotrading"
DB_USER = "quotradingadmin"
DB_PASSWORD = "QuoTrade2024!SecureDB"

def migrate_experiences():
    """Migrate experiences from blob to PostgreSQL"""
    
    print("Starting migration...")
    
    # Step 1: Load experiences from Azure Blob
    print("Loading experiences from Azure Blob Storage...")
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_client = blob_service.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(BLOB_NAME)
    
    blob_data = blob_client.download_blob().readall()
    data = json.loads(blob_data)
    experiences = data.get('experiences', [])
    
    print(f"✅ Loaded {len(experiences)} experiences from blob")
    
    # Step 2: Connect to PostgreSQL
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )
    cursor = conn.cursor()
    
    # Step 3: Insert experiences into database
    print("Inserting experiences into PostgreSQL...")
    inserted = 0
    skipped = 0
    
    for exp in experiences:
        try:
            # Extract from nested structure
            state = exp.get('state', {})
            action = exp.get('action', {})
            
            cursor.execute("""
                INSERT INTO rl_experiences (
                    license_key,
                    symbol,
                    rsi,
                    vwap_distance,
                    atr,
                    volume_ratio,
                    hour,
                    day_of_week,
                    recent_pnl,
                    streak,
                    side,
                    regime,
                    took_trade,
                    pnl,
                    duration,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                'MIGRATED',  # Use placeholder license key for old data
                'ES',  # All existing data is from ES trading
                state.get('rsi', 50.0),
                state.get('vwap_distance', 0.0),
                state.get('atr', 0.0),
                state.get('volume_ratio', 1.0),
                state.get('hour', 0),
                state.get('day_of_week', 0),
                state.get('recent_pnl', 0.0),
                state.get('streak', 0),
                state.get('side', 'long'),
                state.get('regime', 'NORMAL'),
                action.get('took_trade', False),
                exp.get('reward', 0.0),  # reward is the PNL value
                exp.get('duration', 0.0)
            ))
            inserted += 1
            
            if inserted % 100 == 0:
                print(f"  Inserted {inserted} experiences...")
                conn.commit()
                
        except Exception as e:
            # Rollback the transaction on error and continue
            conn.rollback()
            print(f"  ⚠️ Skipped 1 experience: {e}")
            skipped += 1
    
    # Final commit
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Migration complete!")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped: {skipped}")
    print(f"   Total: {inserted + skipped}")

if __name__ == "__main__":
    migrate_experiences()
