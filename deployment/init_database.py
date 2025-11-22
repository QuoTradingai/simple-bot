"""
Initialize PostgreSQL Database with Schema and Admin User
"""
import psycopg2
from psycopg2 import sql

# Database connection details
DB_HOST = "quotrading-db.postgres.database.azure.com"
DB_NAME = "quotrading"
DB_USER = "quotradingadmin"
DB_PASSWORD = "QuoTrade2024!SecureDB"

def init_database():
    """Initialize database with tables and admin user"""
    print("🔌 Connecting to PostgreSQL...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require'
        )
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL!")
        
        # Read and execute SQL file
        print("\n📋 Creating tables...")
        with open('db_init.sql', 'r') as f:
            sql_script = f.read()
        
        cursor.execute(sql_script)
        conn.commit()
        print("✅ Tables created successfully!")
        
        # Verify admin user
        print("\n🔍 Verifying admin user...")
        cursor.execute("SELECT license_key, email, license_type, license_status FROM users WHERE license_key = 'ADMIN-DEV-KEY-2024'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"✅ Admin user found:")
            print(f"   License: {admin[0]}")
            print(f"   Email: {admin[1]}")
            print(f"   Type: {admin[2]}")
            print(f"   Status: {admin[3]}")
        else:
            print("❌ Admin user not found!")
        
        # Count tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"\n📊 Total tables: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    init_database()
