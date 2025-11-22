#!/bin/bash
# Run this in Azure Cloud Shell to initialize the database

echo "Installing psycopg2..."
pip install psycopg2-binary

echo "Running database initialization..."
python3 << 'EOF'
import os
import psycopg2

DB_HOST = "quotrading-db.postgres.database.azure.com"
DB_NAME = "quotrading"
DB_USER = "quotradingadmin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "Mrkevins15@")

sql_commands = """
CREATE TABLE IF NOT EXISTS rl_experiences (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rsi FLOAT,
    vwap_distance FLOAT,
    atr FLOAT,
    volume_ratio FLOAT,
    side VARCHAR(10),
    regime VARCHAR(20),
    took_trade BOOLEAN NOT NULL,
    pnl FLOAT,
    duration_minutes FLOAT,
    win BOOLEAN,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_license_key ON rl_experiences(license_key);
CREATE INDEX IF NOT EXISTS idx_symbol ON rl_experiences(symbol);
CREATE INDEX IF NOT EXISTS idx_created_at ON rl_experiences(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_took_trade ON rl_experiences(took_trade);
CREATE INDEX IF NOT EXISTS idx_side ON rl_experiences(side);
CREATE INDEX IF NOT EXISTS idx_regime ON rl_experiences(regime);
CREATE INDEX IF NOT EXISTS idx_composite_similarity ON rl_experiences(symbol, rsi, vwap_distance, atr, volume_ratio, side, regime);

GRANT ALL PRIVILEGES ON TABLE rl_experiences TO quotradingadmin;
GRANT ALL PRIVILEGES ON SEQUENCE rl_experiences_id_seq TO quotradingadmin;
"""

print(f"Connecting to {DB_HOST}...")
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    sslmode='require'
)

try:
    cursor = conn.cursor()
    print("Creating rl_experiences table...")
    cursor.execute(sql_commands)
    conn.commit()
    print("✅ Database initialized successfully!")
    cursor.close()
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
    raise
finally:
    conn.close()
EOF

echo "Done!"
