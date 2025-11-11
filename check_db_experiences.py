#!/usr/bin/env python3
"""Check how many RL experiences exist in PostgreSQL database"""
import psycopg2

DB_URL = "postgresql://quotadmin:QuoTrading2025!Secure@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require"

def check_experiences():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Count signal experiences
        cur.execute("SELECT COUNT(*) FROM rl_experiences WHERE experience_type='SIGNAL'")
        signal_count = cur.fetchone()[0]
        print(f"✅ Signal experiences in database: {signal_count:,}")
        
        # Count exit experiences
        cur.execute("SELECT COUNT(*) FROM rl_experiences WHERE experience_type='EXIT'")
        exit_count = cur.fetchone()[0]
        print(f"✅ Exit experiences in database: {exit_count:,}")
        
        # Total
        cur.execute("SELECT COUNT(*) FROM rl_experiences")
        total_count = cur.fetchone()[0]
        print(f"✅ TOTAL experiences in database: {total_count:,}")
        
        # Sample one experience to see structure
        if signal_count > 0:
            cur.execute("SELECT * FROM rl_experiences WHERE experience_type='SIGNAL' LIMIT 1")
            cols = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            print(f"\n📊 Sample experience structure:")
            for col, val in zip(cols, row):
                print(f"   {col}: {val}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_experiences()
