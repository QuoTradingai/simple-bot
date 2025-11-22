"""
Test License System Locally
Tests PostgreSQL license validation without Azure Function
"""
import psycopg2
from datetime import datetime

# Database connection
DB_HOST = "quotrading-db.postgres.database.azure.com"
DB_NAME = "quotrading"
DB_USER = "quotradingadmin"
DB_PASSWORD = "QuoTrade2024!SecureDB"

def test_license(license_key):
    """Test if a license key is valid"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require'
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT license_key, email, license_type, license_status, license_expiration
            FROM users
            WHERE license_key = %s
        """, (license_key,))
        
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ License key '{license_key}' not found")
            return False
        
        license_key, email, license_type, status, expiration = user
        
        print(f"\n✅ License Found:")
        print(f"   Key: {license_key}")
        print(f"   Email: {email}")
        print(f"   Type: {license_type}")
        print(f"   Status: {status}")
        print(f"   Expiration: {expiration}")
        
        if status != 'active':
            print(f"\n❌ License is {status}")
            return False
        
        if expiration and expiration < datetime.now():
            print(f"\n❌ License expired on {expiration}")
            return False
        
        print(f"\n✅ License is VALID!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("QuoTrading License Validation Test")
    print("=" * 50)
    
    # Test admin key
    print("\n1. Testing ADMIN key...")
    test_license("ADMIN-DEV-KEY-2024")
    
    # Test invalid key
    print("\n2. Testing INVALID key...")
    test_license("FAKE-KEY-123")
    
    print("\n" + "=" * 50)
