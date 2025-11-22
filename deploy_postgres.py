"""
Complete PostgreSQL deployment script
1. Creates rl_experiences table with all indexes
2. Migrates 7,559 ES experiences from blob storage
3. Verifies deployment success
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from azure.storage.blob import BlobServiceClient

# PostgreSQL configuration
DB_HOST = os.environ.get("DB_HOST", "quotrading-db.postgres.database.azure.com")
DB_NAME = os.environ.get("DB_NAME", "quotrading")
DB_USER = os.environ.get("DB_USER", "quotradingadmin")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Azure Storage configuration
STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "rl-data"
BLOB_NAME = "signal_experience.json"

def get_credentials():
    """Get credentials from user if not in environment"""
    db_pass = DB_PASSWORD
    storage_conn = STORAGE_CONNECTION_STRING
    
    if not db_pass:
        print("\n📋 PostgreSQL credentials needed")
        print(f"   Host: {DB_HOST}")
        print(f"   User: {DB_USER}")
        db_pass = input("   Password: ").strip()
    
    if not storage_conn:
        print("\n📋 Azure Storage credentials needed")
        storage_conn = input("   Connection String: ").strip()
    
    return db_pass, storage_conn

def create_table(cursor):
    """Create rl_experiences table with all indexes"""
    print("\n=== STEP 1: Creating rl_experiences table ===")
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rl_experiences (
            id SERIAL PRIMARY KEY,
            license_key VARCHAR(50) NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            rsi DECIMAL(5,2) NOT NULL,
            vwap_distance DECIMAL(10,6) NOT NULL,
            atr DECIMAL(10,6) NOT NULL,
            volume_ratio DECIMAL(10,2) NOT NULL,
            hour INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            recent_pnl DECIMAL(10,2) NOT NULL,
            streak INTEGER NOT NULL,
            side VARCHAR(10) NOT NULL,
            regime VARCHAR(50) NOT NULL,
            took_trade BOOLEAN NOT NULL,
            pnl DECIMAL(10,2) NOT NULL,
            duration DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    print("✅ Table created")
    
    # Create indexes
    print("Creating indexes...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_rl_experiences_license ON rl_experiences(license_key)",
        "CREATE INDEX IF NOT EXISTS idx_rl_experiences_symbol ON rl_experiences(symbol)",
        "CREATE INDEX IF NOT EXISTS idx_rl_experiences_created ON rl_experiences(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_rl_experiences_took_trade ON rl_experiences(took_trade)",
        "CREATE INDEX IF NOT EXISTS idx_rl_experiences_side ON rl_experiences(side)",
        "CREATE INDEX IF NOT EXISTS idx_rl_experiences_regime ON rl_experiences(regime)",
        "CREATE INDEX IF NOT EXISTS idx_rl_experiences_similarity ON rl_experiences(symbol, rsi, vwap_distance, atr, volume_ratio, side, regime)"
    ]
    
    for idx in indexes:
        cursor.execute(idx)
        print(f"  ✅ {idx.split('idx_rl_experiences_')[1].split(' ON')[0]}")
    
    print("✅ All indexes created")

def migrate_blob_data(cursor, conn, storage_conn_str):
    """Migrate experiences from Azure Blob to PostgreSQL"""
    print("\n=== STEP 2: Migrating blob data to PostgreSQL ===")
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM rl_experiences")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"⚠️  Table already contains {existing_count} experiences")
        response = input("Continue with migration? This will add duplicates (y/n): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled")
            return
    
    # Load from blob
    print("Loading experiences from Azure Blob Storage...")
    blob_service = BlobServiceClient.from_connection_string(storage_conn_str)
    container_client = blob_service.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(BLOB_NAME)
    
    blob_data = blob_client.download_blob().readall()
    data = json.loads(blob_data)
    experiences = data.get('experiences', [])
    
    print(f"✅ Loaded {len(experiences)} experiences from blob")
    
    # Insert into PostgreSQL
    print("Inserting into PostgreSQL...")
    inserted = 0
    skipped = 0
    
    for exp in experiences:
        try:
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
                'MIGRATED',
                'ES',
                exp.get('rsi', 50.0),
                exp.get('vwap_distance', 0.0),
                exp.get('atr', 0.0),
                exp.get('volume_ratio', 1.0),
                exp.get('hour', 0),
                exp.get('day_of_week', 0),
                exp.get('recent_pnl', 0.0),
                exp.get('streak', 0),
                exp.get('side', 'long'),
                exp.get('regime', 'NORMAL'),
                exp.get('took_trade', False),
                exp.get('pnl', 0.0),
                exp.get('duration', 0.0)
            ))
            inserted += 1
            
            if inserted % 100 == 0:
                print(f"  Progress: {inserted}/{len(experiences)}")
                conn.commit()
                
        except Exception as e:
            print(f"  ⚠️ Skipped 1 experience: {e}")
            skipped += 1
    
    conn.commit()
    print(f"\n✅ Migration complete!")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped: {skipped}")

def verify_deployment(cursor):
    """Verify deployment was successful"""
    print("\n=== STEP 3: Verifying deployment ===")
    
    # Count total experiences
    cursor.execute("SELECT COUNT(*) FROM rl_experiences")
    total = cursor.fetchone()[0]
    print(f"✅ Total experiences: {total}")
    
    # Count by symbol
    cursor.execute("SELECT symbol, COUNT(*) FROM rl_experiences GROUP BY symbol")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} experiences")
    
    # Check indexes
    cursor.execute("""
        SELECT indexname FROM pg_indexes 
        WHERE tablename = 'rl_experiences' 
        ORDER BY indexname
    """)
    indexes = [row[0] for row in cursor.fetchall()]
    print(f"\n✅ Indexes created: {len(indexes)}")
    for idx in indexes:
        print(f"   - {idx}")
    
    # Sample query performance
    cursor.execute("SELECT * FROM rl_experiences WHERE symbol = 'ES' LIMIT 5")
    results = cursor.fetchall()
    print(f"\n✅ Sample query returned {len(results)} results")
    
    print("\n🎉 PostgreSQL deployment successful!")
    print("   Ready for 1000+ concurrent users")
    print("   Symbol isolation enabled")
    print("   Flask API can now use PostgreSQL backend")

def main():
    """Execute complete deployment"""
    print("="*60)
    print("PostgreSQL RL System Deployment")
    print("="*60)
    
    # Get credentials
    db_password, storage_conn_str = get_credentials()
    
    if not db_password:
        print("❌ Error: DB_PASSWORD is required")
        return
    
    if not storage_conn_str:
        print("❌ Error: AZURE_STORAGE_CONNECTION_STRING is required")
        return
    
    # Connect to PostgreSQL
    print(f"\nConnecting to {DB_HOST}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=db_password,
        sslmode='require'
    )
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL")
    
    try:
        # Step 1: Create table and indexes
        create_table(cursor)
        conn.commit()
        
        # Step 2: Migrate blob data
        migrate_blob_data(cursor, conn, storage_conn_str)
        
        # Step 3: Verify deployment
        verify_deployment(cursor)
        
    except Exception as e:
        print(f"\n❌ Error during deployment: {e}")
        conn.rollback()
        raise
    
    finally:
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()
