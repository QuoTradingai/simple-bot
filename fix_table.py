import psycopg2

# Database connection
DB_HOST = "quotrading-db.postgres.database.azure.com"
DB_NAME = "quotrading"
DB_USER = "quotradingadmin"
DB_PASSWORD = "QuoTrade2024!SecureDB"

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )
    cursor = conn.cursor()
    
    print("Dropping old table...")
    cursor.execute("DROP TABLE IF EXISTS rl_experiences;")
    
    print("Creating new table with correct schema...")
    cursor.execute("""
        CREATE TABLE rl_experiences (
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
        );
    """)
    
    print("Creating indexes...")
    cursor.execute("CREATE INDEX idx_rl_experiences_license ON rl_experiences(license_key);")
    cursor.execute("CREATE INDEX idx_rl_experiences_symbol ON rl_experiences(symbol);")
    cursor.execute("CREATE INDEX idx_rl_experiences_created ON rl_experiences(created_at DESC);")
    cursor.execute("CREATE INDEX idx_rl_experiences_took_trade ON rl_experiences(took_trade);")
    cursor.execute("CREATE INDEX idx_rl_experiences_side ON rl_experiences(side);")
    cursor.execute("CREATE INDEX idx_rl_experiences_regime ON rl_experiences(regime);")
    cursor.execute("""
        CREATE INDEX idx_rl_experiences_similarity ON rl_experiences(
            symbol, rsi, vwap_distance, atr, volume_ratio, side, regime
        );
    """)
    
    conn.commit()
    print("✅ Table created successfully with all required columns!")
    
    # Verify structure
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'rl_experiences'
        ORDER BY ordinal_position;
    """)
    
    print("\nTable structure:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
