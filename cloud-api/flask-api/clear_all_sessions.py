"""
Clear all existing sessions - one-time migration
Run this after deploying new fingerprint logic (removed PID from fingerprint)
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in environment")
    exit(1)

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

try:
    with conn.cursor() as cursor:
        # Clear all sessions
        cursor.execute("""
            UPDATE users 
            SET device_fingerprint = NULL,
                last_heartbeat = NULL
            WHERE device_fingerprint IS NOT NULL
        """)
        
        rows_affected = cursor.rowcount
        conn.commit()
        
        print(f"✅ Cleared {rows_affected} session(s)")
        print("All users can now log in with new fingerprint format")
        
finally:
    conn.close()
    print("Done!")
