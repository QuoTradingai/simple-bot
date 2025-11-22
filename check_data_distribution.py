"""
Check data distribution in PostgreSQL
"""
import psycopg2

conn = psycopg2.connect(
    host="quotrading-db.postgres.database.azure.com",
    database="quotrading",
    user="quotradingadmin",
    password="QuoTrade2024!SecureDB",
    sslmode='require'
)
cursor = conn.cursor()

# Get RSI distribution
cursor.execute("""
    SELECT 
        MIN(rsi), MAX(rsi), AVG(rsi),
        MIN(vwap_distance), MAX(vwap_distance), AVG(vwap_distance),
        MIN(atr), MAX(atr), AVG(atr)
    FROM rl_experiences 
    WHERE symbol='ES'
""")
row = cursor.fetchone()

print("DATA DISTRIBUTION:")
print(f"RSI: {row[0]:.1f} to {row[1]:.1f}, avg {row[2]:.1f}")
print(f"VWAP: {row[3]:.4f} to {row[4]:.4f}, avg {row[5]:.4f}")
print(f"ATR: {row[6]:.2f} to {row[7]:.2f}, avg {row[8]:.2f}")

# Check RSI buckets for winners vs losers
cursor.execute("""
    SELECT 
        CASE 
            WHEN rsi < 30 THEN 'Oversold <30'
            WHEN rsi < 50 THEN 'Low 30-50'
            WHEN rsi < 70 THEN 'High 50-70'
            ELSE 'Overbought >70'
        END as rsi_bucket,
        COUNT(*) as total,
        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winners,
        AVG(pnl) as avg_pnl
    FROM rl_experiences
    WHERE symbol='ES'
    GROUP BY rsi_bucket
    ORDER BY rsi_bucket
""")

print("\nRSI BUCKETS:")
for row in cursor.fetchall():
    wr = (row[2] / row[1] * 100) if row[1] > 0 else 0
    print(f"  {row[0]}: {row[1]} trades, {wr:.1f}% WR, ${row[3]:.2f} avg")

cursor.close()
conn.close()
