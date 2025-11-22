"""
Verify migrated data in PostgreSQL
"""
import psycopg2

# PostgreSQL configuration
DB_HOST = "quotrading-db.postgres.database.azure.com"
DB_NAME = "quotrading"
DB_USER = "quotradingadmin"
DB_PASSWORD = "QuoTrade2024!SecureDB"

def verify_migration():
    """Verify data migrated correctly"""
    
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winners,
            SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losers,
            AVG(pnl) as avg_pnl,
            MIN(pnl) as min_pnl,
            MAX(pnl) as max_pnl,
            SUM(pnl) as total_pnl
        FROM rl_experiences 
        WHERE symbol='ES'
    """)
    
    row = cursor.fetchone()
    
    total = int(row[0])
    winners = int(row[1]) if row[1] else 0
    losers = int(row[2]) if row[2] else 0
    avg_pnl = float(row[3]) if row[3] else 0.0
    min_pnl = float(row[4]) if row[4] else 0.0
    max_pnl = float(row[5]) if row[5] else 0.0
    total_pnl = float(row[6]) if row[6] else 0.0
    
    print(f"\n📊 MIGRATED DATA VERIFICATION")
    print(f"{'='*60}")
    print(f"Total experiences: {total}")
    print(f"Winners: {winners} ({winners/total*100:.1f}%)")
    print(f"Losers: {losers} ({losers/total*100:.1f}%)")
    print(f"Average PNL: {avg_pnl:.2f}")
    print(f"Min PNL: {min_pnl:.2f}")
    print(f"Max PNL: {max_pnl:.2f}")
    print(f"Total PNL: {total_pnl:.2f}")
    
    # Get sample records
    cursor.execute("""
        SELECT rsi, vwap_distance, side, regime, took_trade, pnl, duration
        FROM rl_experiences
        WHERE symbol='ES' AND pnl > 0
        LIMIT 3
    """)
    
    print(f"\n✅ Sample Winners:")
    for row in cursor.fetchall():
        print(f"  RSI={row[0]:.2f}, VWAP={row[1]:.4f}, Side={row[2]}, "
              f"Regime={row[3]}, Trade={row[4]}, PNL={row[5]:.2f}, Duration={row[6]:.0f}s")
    
    cursor.execute("""
        SELECT rsi, vwap_distance, side, regime, took_trade, pnl, duration
        FROM rl_experiences
        WHERE symbol='ES' AND pnl < 0
        LIMIT 3
    """)
    
    print(f"\n❌ Sample Losers:")
    for row in cursor.fetchall():
        print(f"  RSI={row[0]:.2f}, VWAP={row[1]:.4f}, Side={row[2]}, "
              f"Regime={row[3]}, Trade={row[4]}, PNL={row[5]:.2f}, Duration={row[6]:.0f}s")
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")
    
    # Compare with expected blob stats
    expected_winners = 4233
    expected_avg = 176.95
    
    actual_winners = winners
    actual_avg = avg_pnl
    
    if actual_winners == expected_winners and abs(actual_avg - expected_avg) < 1.0:
        print(f"✅ Migration verification PASSED!")
        print(f"   Winners match: {actual_winners} == {expected_winners}")
        print(f"   Average PNL match: {actual_avg:.2f} ≈ {expected_avg:.2f}")
    else:
        print(f"❌ Migration verification FAILED!")
        print(f"   Expected {expected_winners} winners, got {actual_winners}")
        print(f"   Expected avg {expected_avg:.2f}, got {actual_avg:.2f}")

if __name__ == "__main__":
    verify_migration()
